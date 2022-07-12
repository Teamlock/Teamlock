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

from apps.key.schema import CreateKeySchema, KeySchema, TMPKeySchema
from apps.config.schema import PasswordPolicySchema
from toolkits.utils import check_password_complexity
from fastapi import APIRouter, Depends, status, Body
from toolkits.workspace import WorkspaceUtils
from apps.workspace.models import Workspace
from fastapi.exceptions import HTTPException
from apps.auth.tools import get_current_user
from mongoengine.queryset.visitor import Q
from apps.auth.schema import LoggedUser
from toolkits.history import create_history
from toolkits.crypto import CryptoUtils
from fastapi.responses import Response
from apps.folder.models import Folder
from settings import settings
from .models import Key
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get(
    path="/generate",
    summary="Generate a password",
    response_model=str
)
async def generate_password(
    folder_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> str:
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
    summary="Search Keys",
    response_model=list[KeySchema]
)
async def search_keys(
    search: str,
    workspace: str,
    user: LoggedUser = Depends(get_current_user)
):
    try:
        workspace, sym_key = WorkspaceUtils.get_workspace(workspace, user)
        WorkspaceUtils.have_rights(workspace, user)
        folders: list[Folder] = Folder.objects(workspace=workspace)

        in_folder_query: Q =Q(folder__in=folders)
        name_query: Q = Q(name__value__icontains=search)
        url_query: Q = Q(url__value__icontains=search)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        keys: list = []
        for tmp in Key.objects(in_folder_query & (name_query | url_query)):
            tmp: TMPKeySchema = TMPKeySchema(**tmp.to_mongo())
            keys.append(WorkspaceUtils.decrypt_key(decrypted_sym_key, tmp))

        return keys
    
    except Workspace.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )


@router.get(
    path="/{key_id}",
    response_model=KeySchema,
    summary="Retreive password for a key"
)
async def get_key(
    key_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> KeySchema:
    try:
        key = Key.objects(pk=key_id).get()
        key_schema = TMPKeySchema(**key.to_mongo())

        workspace, sym_key = WorkspaceUtils.get_workspace(key.folder.workspace.pk, user)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        decrypted_key: KeySchema = WorkspaceUtils.decrypt_key(
            decrypted_sym_key,
            key_schema,
            get_password=True
        )

        create_history(
            user=user.in_db.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Retreive password for key {decrypted_key.name.value} in folder {key.folder.name}"
        )

        logger.info(f"[KEY][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} retreive key {decrypted_key.name.value}")
        return decrypted_key.dict()

    except Key.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found"
        )
    

@router.post(
    path="/",
    summary="Create a key",
    status_code=status.HTTP_201_CREATED
)
async def create_key(
    key_def: CreateKeySchema,
    user: LoggedUser = Depends(get_current_user)
) -> str:
    try:
        folder: Folder = Folder.objects(pk=key_def.folder).get()
        if folder.in_trash or folder.is_trash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't create a key inside the trash"
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
            check_password_complexity(policy, key_def.password.value)
            
        encrypted_key: Key = WorkspaceUtils.encrypt_key(user, sym_key, key_def)
        encrypted_key.folder = folder

        encrypted_key.created_by = user.in_db
        encrypted_key.updated_by = user.in_db
        encrypted_key.save()

        create_history(
            user=user.in_db.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Create key {key_def.name.value} in folder {encrypted_key.folder.name}"
        )

        logger.info(f"[KEY][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} create key {key_def.name.value}")
        return str(encrypted_key.pk)

    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )


@router.post(
    path="/{key_id}/move",
    summary="Move key to an other folder",
    status_code=status.HTTP_202_ACCEPTED
)
async def move_key(
    key_id: str,
    folder_id: str = Body(...),
    user: LoggedUser = Depends(get_current_user)
):
    try:
        key: Key = Key.objects(pk=key_id).get()
        new_folder: Folder = Folder.objects(pk=folder_id).get()

        workspace, _ = WorkspaceUtils.get_workspace(key.folder.workspace.pk, user)
        WorkspaceUtils.have_rights(workspace, user)

        key.folder = new_folder
        key.save()

        logger.info(f"[KEY][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} move key {key.name.value}")
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

    except Key.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found"
        )

@router.put(
    path="/{key_id}",
    summary="Edit a key",
    status_code=status.HTTP_202_ACCEPTED
)
async def update_key(
    key_id: str,
    key_def: CreateKeySchema,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    try:
        key: Key = Key.objects(pk=key_id).get()
        if key.folder.in_trash or key.folder.is_trash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't edit a key inside the trash"
            )
        workspace, sym_key = WorkspaceUtils.get_workspace(key.folder.workspace.pk, user)

        WorkspaceUtils.have_rights(workspace, user)

        policy = None
        if key.folder.password_policy:
            policy: PasswordPolicySchema = PasswordPolicySchema(**key.folder.password_policy.to_mongo())
        elif workspace.password_policy:
            policy: PasswordPolicySchema = PasswordPolicySchema(**workspace.password_policy.to_mongo())

        if policy:
            check_password_complexity(policy, key_def.password.value)

        encrypted_key: Key = WorkspaceUtils.encrypt_key(user, sym_key, key_def)

        encrypted_key.folder = key.folder
        encrypted_key.pk = key.pk

        encrypted_key.updated_by = user.in_db
        encrypted_key.save()

        create_history(
            user=user.in_db.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Update key {key.name} in folder {key.folder.name}"
        )

        logger.info(f"[KEY][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} update key {key_def.name.value}")
        return Response(status_code=status.HTTP_202_ACCEPTED)

    except Key.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found"
        )
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )


@router.delete(
    path="/{key_id}",
    summary="Delete a key",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_key(
    key_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    try:
        key: Key = Key.objects(pk=key_id).get()
        workspace: Workspace = key.folder.workspace
        WorkspaceUtils.have_rights(workspace, user)
        key.delete()

        create_history(
            user=user.email,
            workspace=workspace.name,
            workspace_owner=workspace.owner.email,
            action=f"Delete key {key.name} in folder {key.folder.name}"
        )

        logger.info(f"[KEY][{str(workspace.pk)}][{workspace.name}] {user.in_db.email} delete key {key.name.value}")
    
    except Key.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found"
        )
