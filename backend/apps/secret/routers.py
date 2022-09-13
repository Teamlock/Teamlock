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

from toolkits.utils import check_password_complexity
from fastapi import APIRouter, Depends, status, Body
from apps.workspace.models import Workspace, Share
from apps.config.schema import PasswordPolicySchema
from toolkits.workspace import WorkspaceUtils
from fastapi.exceptions import HTTPException
from apps.auth.tools import get_current_user
from toolkits.history import create_history
from mongoengine.queryset.visitor import Q
from apps.auth.schema import LoggedUser
from toolkits.crypto import CryptoUtils
from fastapi.responses import Response
from apps.folder.models import Folder
from .models import Login, Secret
from datetime import datetime
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
    response_model=list[schema.BankSchema] | list[schema.ServerSchema] | list[schema.LoginSchema] | list[schema.PhoneSchema]
)
async def global_search_keys(
    search: str,
    category: str,
    user: LoggedUser = Depends(get_current_user)
):
    workspaces = list(Workspace.objects(owner=user.id))
    shared_query: Q = Q(user=user.id) & (Q(expire_at=None) | Q(expire_at__lte=datetime.utcnow()))
    workspaces.extend(list(Share.objects(shared_query)))

    keys: list = []
    for workspace in workspaces:
        keys.extend(WorkspaceUtils.search(workspace.pk, search, user, category))
    
    return keys


@router.get(
    path="/{secret_id}",
    response_model=Union[schema.LoginSchema, schema.ServerSchema, schema.BankSchema, schema.PhoneSchema],
    summary="Retreive secret"
)
async def get_secret(
    secret_id: str,
    user: LoggedUser = Depends(get_current_user)
):
    try:
        secret = Secret.objects(pk=secret_id).get()
        secret_schema = secret.schema()

        workspace, sym_key = WorkspaceUtils.get_workspace(secret.folder.workspace.pk, user)

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

        create_history(
            user=user.in_db.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Retreive secret for secret {decrypted_secret.name.value} in folder {secret.folder.name}"
        )

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} retreive secret {decrypted_secret.name.value}")
        
        # tmp = decrypted_secret.dict()
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
        if folder.in_trash or folder.is_trash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't create a secret inside the trash"
            )

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
        new_folder: Folder = Folder.objects(pk=folder_id).get()

        workspace, _ = WorkspaceUtils.get_workspace(secret.folder.workspace.pk, user)
        WorkspaceUtils.have_rights(workspace, user)

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
        if secret.folder.in_trash or secret.folder.is_trash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't edit a secret inside the trash"
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

        encrypted_secret: Secret = WorkspaceUtils.encrypt_secret(user, sym_key, schema.secret)

        encrypted_secret.folder = secret.folder
        encrypted_secret.pk = secret.pk

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
        workspace: Workspace = secret.folder.workspace
        WorkspaceUtils.have_rights(workspace, user)
        secret.delete()

        create_history(
            user=user.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Delete secret {secret.name.value} in folder {secret.folder.name}"
        )

        logger.info(f"[SECRET][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} delete secret {secret.name.value}")
    
    except Secret.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found"
        )
