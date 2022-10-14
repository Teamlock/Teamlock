#!/usr/bin/python

"""This file is part of Teamlock.
Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from fastapi import APIRouter, Depends, status, Body, Request, BackgroundTasks
from toolkits.history import create_history, create_notification
from toolkits.utils import check_password_complexity
from apps.workspace.models import Workspace, Share
from apps.config.schema import PasswordPolicySchema
from toolkits.workspace import WorkspaceUtils
from toolkits.secret import SecretUtils
from fastapi.exceptions import HTTPException
from apps.auth.tools import get_current_user
from mongoengine.queryset.visitor import Q
from apps.auth.schema import LoggedUser
from toolkits.crypto import CryptoUtils
from fastapi.responses import Response
from apps.folder.models import Folder
from apps.workspace.models import Workspace
from .models import Login, Secret
from datetime import date, datetime
from settings import settings
from typing import Union
from . import schema
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get(
    path="/generate",
    summary="Generate a password",
    response_model=str,
    dependencies=[Depends(get_current_user)]
)
async def generate_password(folder_id: str) -> str:
    try:
        folder = Folder.objects(pk=folder_id).get()
        password_policy = folder.password_policy
        if password_policy is None:
            password_policy = folder.workspace.password_policy

        if password_policy:
            password_policy = PasswordPolicySchema(**password_policy.to_mongo())

        password: str = CryptoUtils.generate_password(password_policy)
        return password
    
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )


@router.get(
    path="/search",
    summary="Search Secrets",
    response_model=list[schema.BankSchema] | list[schema.ServerSchema] | list[schema.LoginSchema] | list[schema.PhoneSchema]
)
async def search_secrets(
    search: str,
    category: str,
    workspace: str,
    user: LoggedUser = Depends(get_current_user)
):
    try:
        return WorkspaceUtils.search(workspace, search, user, category)
    except Workspace.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )


@router.get(
    path="/global/search",
    summary="Search on all workspaces",
    response_model=list[schema.BankSchema] | list[schema.ServerSchema] | list[schema.LoginSchema] | list[schema.PhoneSchema] | schema.LoginSchema
)
async def global_search_keys(
    search: str = "",
    category: str = "login",
    package_name: str = "",
    user: LoggedUser = Depends(get_current_user)
):
    workspaces = list(Workspace.objects(owner=user.id))
    shared_query: Q = Q(user=user.id) & (Q(expire_at=None) | Q(expire_at__lte=datetime.utcnow()))

    shares = list(Share.objects(shared_query))
    workspaces.extend([s.workspace for s in shares])

    secrets: list = []
    for workspace in workspaces:
        secrets.extend(WorkspaceUtils.search(workspace.pk, search, user, category, package_name=package_name))
    
    if len(secrets) == 0:
        return []

    if package_name:
        return secrets[0]

    return secrets


@router.get(
    path="/{secret_id}",
    response_model=Union[schema.LoginSchema, schema.ServerSchema, schema.BankSchema, schema.PhoneSchema],
    summary="Retreive secret"
)
async def get_secret(
    secret_id: str,
    request: Request,
    background_task: BackgroundTasks,
    user: LoggedUser = Depends(get_current_user)
):
    try:
        secret = Secret.objects(pk=secret_id).get()
        secret_schema = secret.schema()

        workspace_pk = secret.folder.workspace.pk if secret.folder is not None else secret.trash.workspace.pk
        workspace, sym_key = WorkspaceUtils.get_workspace(workspace_pk, user)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        decrypted_secret = WorkspaceUtils.decrypt_secret(
            decrypted_sym_key,
            secret_schema,
            get_protected_fields=True
        )

        action = f"in folder {secret.folder.name}" if secret.folder is not None else "in trash"

        create_history(
            user=user.in_db.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Retreive secret for secret {decrypted_secret.name.value} {action}"
        )

        if user.email != decrypted_secret.created_by:
            create_notification(
                user=user.id,
                secret=secret,
                request=request,
                mail=True,
                background_task=background_task
            )

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} retreive secret {decrypted_secret.name.value}")
        if decrypted_secret.folder is not None:
            decrypted_secret.folder_name = Folder.objects(pk=decrypted_secret.folder).get().name
        else:
            decrypted_secret.folder_name = ""
        decrypted_secret.workspace_name = workspace.name
        return decrypted_secret

    except Secret.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found"
        )
    

@router.post(
    path="/",
    summary="Create a secret",
    status_code=status.HTTP_201_CREATED
)
async def create_secret(
    schema: schema.CreateSecretSchema,
    user: LoggedUser = Depends(get_current_user)
) -> str:
    try:
        folder: Folder = Folder.objects(pk=schema.secret.folder).get()
        workspace, sym_key = WorkspaceUtils.get_workspace(folder.workspace.pk, user)

        # Check if user is allowed to create a key in this workspace
        WorkspaceUtils.have_rights(workspace, user)

        policy = None
        if folder.password_policy:
            policy: PasswordPolicySchema = PasswordPolicySchema(**folder.password_policy.to_mongo())
        elif workspace.password_policy:
            policy: PasswordPolicySchema = PasswordPolicySchema(**workspace.password_policy.to_mongo())

        if policy:
            check_password_complexity(policy, schema.secret)
            
        encrypted_secret = WorkspaceUtils.encrypt_secret(user, sym_key, schema.secret)
        encrypted_secret.folder = folder
        encrypted_secret.package_name = schema.package_name

        encrypted_secret.created_by = user.in_db
        encrypted_secret.updated_by = user.in_db
        encrypted_secret.save()

        create_history(
            user=user.in_db.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Create secret {schema.secret.name.value} in folder {encrypted_secret.folder.name}"
        )

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} create secret {schema.secret.name.value}")
        return str(encrypted_secret.pk)

    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )


@router.post(
    path="/{secret_id}/move",
    summary="Move secret to an other folder",
    status_code=status.HTTP_202_ACCEPTED
)
async def move_key(
    secret_id: str,
    folder_id: str = Body(...),
    user: LoggedUser = Depends(get_current_user)
):
    try:
        secret: Secret = Secret.objects(pk=secret_id).get()
        workspace, _ = WorkspaceUtils.get_workspace(secret.folder.workspace.pk if secret.trash is None else secret.trash.workspace.pk, user)
        WorkspaceUtils.have_rights(workspace, user)
        new_folder: Folder = Folder.objects(pk=folder_id).get()

        if secret.trash is not None:
            secret.trash = None
        secret.folder = new_folder
        secret.save()

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} move secret {secret.name.value}")
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

    except Secret.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found"
        )

@router.put(
    path="/{secret_id}",
    summary="Edit a secret",
    status_code=status.HTTP_202_ACCEPTED
)
async def update_secret(
    secret_id: str,
    schema: schema.CreateSecretSchema,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    try:
        secret: Secret = Secret.objects(pk=secret_id).get()
        if secret.folder is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Secret is in trash"
            )
        workspace, sym_key = WorkspaceUtils.get_workspace(secret.folder.workspace.pk, user)

        WorkspaceUtils.have_rights(workspace, user)

        policy = None
        if secret.folder.password_policy:
            policy: PasswordPolicySchema = PasswordPolicySchema(**secret.folder.password_policy.to_mongo())
        elif workspace.password_policy:
            policy: PasswordPolicySchema = PasswordPolicySchema(**workspace.password_policy.to_mongo())

        if policy:
            check_password_complexity(policy, schema.secret)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )
        decrypted_secret = WorkspaceUtils.decrypt_secret(
            decrypted_sym_key,
            secret.schema(),
            get_protected_fields=True
        )

        encrypted_secret: Secret = WorkspaceUtils.encrypt_secret(user, sym_key, schema.secret)

        encrypted_secret.check_changes(decrypted_secret, schema.secret)

        encrypted_secret.folder = secret.folder
        encrypted_secret.pk = secret.pk

        if not encrypted_secret.created_by:
            encrypted_secret.created_by = user.in_db

        encrypted_secret.updated_by = user.in_db
        encrypted_secret.save()

        create_history(
            user=user.in_db.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Update secret {schema.secret.name.value} in folder {secret.folder.name}"
        )

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} update secret {schema.secret.name.value}")
        return Response(status_code=status.HTTP_202_ACCEPTED)

    except Login.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found"
        )
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )


@router.delete(
    path="/{secret_id}",
    summary="Delete a secret",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_secret(
    secret_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    try:
        secret: Secret = Secret.objects(pk=secret_id).get()

        if secret.folder is not None:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail="You have to first put the secret in the trash to delete it"
            )
        workspace: Workspace = secret.trash.workspace
        WorkspaceUtils.have_rights(workspace, user)
        secret.delete()

        create_history(
            user=user.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Delete secret {secret.name.value} in trash"
        )

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} delete secret {secret.name.value}")
    
    except Secret.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found"
        )



@router.delete(
    path="/{secret_id}/trash",
    summary="Move a secret to the trash",
    status_code=status.HTTP_204_NO_CONTENT
)
async def move_to_trash_secret(
    secret_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    try:
        secret: Secret = Secret.objects(pk=secret_id).get()
        if secret.trash is not None:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "The secret is alreay in the trash"
            )

        workspace : Workspace = secret.folder.workspace
        WorkspaceUtils.have_rights(workspace, user)
        trash : Trash = WorkspaceUtils.get_trash_folder(workspace)

        SecretUtils.move_to_trash(secret, trash)

        create_history(
            user=user.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Move secret {secret.name.value} in the trash"
        )

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} move secret {secret.name.value} to trash")
    
    except Secret.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found"
        )

@router.patch(
    path="/{secret_id}/restore",
    summary = "Restore a secret from the trash",
    status_code = status.HTTP_204_NO_CONTENT
)
async def restore(
    secret_id: str,
    user : LoggedUser = Depends(get_current_user)
) -> None:
    try:
        secret: Secret = Secret.objects(pk=secret_id).get()
    except Secret.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found"
        )

    if secret.trash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "The secret is not in the trash"    
        )

    workspace : Workspace = secret.trash.workspace
    WorkspaceUtils.have_rights(workspace, user)
    SecretUtils.restore(secret, workspace)

    create_history(
        user=user.email,
        workspace=workspace.name,
        workspace_owner=workspace.owner.email,
        action=f"Restored secret {secret.name.value}"
    )

    logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} restored secret {secret.name.value}")


