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

from apps.secret.schema import BankSchema, LoginSchema, PhoneSchema, ServerSchema
from .schema import EditFolderSchema, FolderSchema, FolderStats
from apps.secret.models import Login, Server, Bank, Phone
from fastapi import APIRouter, Depends, status, Body
from apps.config.schema import PasswordPolicySchema
from toolkits.workspace import WorkspaceUtils
from apps.config.models import PasswordPolicy
from fastapi.exceptions import HTTPException
from apps.auth.tools import get_current_user
from apps.workspace.models import Workspace
from toolkits.history import create_history
from apps.auth.schema import LoggedUser
from fastapi.responses import Response
from toolkits.crypto import CryptoUtils
from toolkits.folder import FolderUtils
from settings import settings
from toolkits import const
from .models import Folder
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get(
    path="/{folder_id}",
    summary="Get a folder",
    response_model=FolderSchema
)
async def get_folder(
    folder_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> FolderSchema:
    try:

        folder: Folder = Folder.objects(pk=folder_id).get()
        workspace, _ = WorkspaceUtils.get_workspace(
            folder.workspace.pk,
            user
        )
        WorkspaceUtils.have_rights(workspace, user)

        parent = None
        if folder.parent:
            parent = folder.parent.pk

        password_policy = None
        if folder.password_policy:
            password_policy = PasswordPolicySchema(**folder.password_policy.to_mongo())

        logger.info(f"[FOLDER][{str(folder.workspace.pk)}][{folder.workspace.name}] {user.in_db.email} retreive folder {folder.name}")
        return FolderSchema(
            name=folder.name,
            icon=folder.icon,
            password_policy=password_policy,
            workspace=folder.workspace.pk,
            created_at=folder.created_at,
            created_by=folder.created_by.pk,
            parent=parent
        )
    
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a folder in a workspace"
)
async def create_folder(
    folder_def: EditFolderSchema,
    user: LoggedUser = Depends(get_current_user)
) -> str:
    workspace, _ = WorkspaceUtils.get_workspace(
        folder_def.workspace,
        user
    )
    WorkspaceUtils.have_rights(workspace, user)

    password_policy = None
    if folder_def.password_policy:
        password_policy = PasswordPolicy(**folder_def.password_policy.dict())

    folder = Folder(
        name=folder_def.name,
        icon=folder_def.icon,
        workspace=workspace,
        created_by=user.id,
        password_policy=password_policy
    )

    if folder_def.parent:
        try:
            folder_parent = Folder.objects(pk=folder_def.parent).get()
            folder.parent = folder_parent
        except Folder.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent folder not found"
            )

    folder.save()
    logger.info(f"[FOLDER][{str(folder.workspace.pk)}][{folder.workspace.name}] {user.in_db.email} create folder {folder_def.name}")

    create_history(
        user=user.in_db.email,
        workspace=workspace.name,
        workspace_owner=workspace.owner.email,
        action=f"Create folder {folder.name}"
    )
    return Response(
        content=str(folder.id),
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    path="/{folder_id}",
    summary="Update a folder",
    status_code=status.HTTP_202_ACCEPTED
)
async def update_folder(
    folder_id: str,
    folder_def: EditFolderSchema,
    user: LoggedUser = Depends(get_current_user)
) -> str:

    WorkspaceUtils.have_rights(folder_def.workspace, user)

    try:
        folder: Folder = Folder.objects(pk=folder_id).get()
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    folder.name = folder_def.name
    folder.icon = folder_def.icon
    if folder_def.password_policy:
        folder.password_policy = PasswordPolicy(**folder_def.password_policy.dict())

    if folder_def.parent:
        try:
            folder_parent = Folder.objects(id=folder_def.parent).get()
            folder.parent = folder_parent
        except Folder.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent folder not found"
            )
    elif folder_def.moved:
        folder.parent = None

    folder.save()
    logger.info(f"[FOLDER][{str(folder.workspace.pk)}][{folder.workspace.name}] {user.in_db.email} update folder {folder_def.name}")

    create_history(
        user=user.in_db.email,
        workspace=folder.workspace.name,
        workspace_owner=folder.workspace.owner.email,
        action=f"Update folder {folder.name}"
    )

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post(
    path="/{folder_id}/copy",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Copy a folder to another Workspace"
)
async def copy_folder(
    folder_id: str,
    to_workspace_id: str = Body(...),
    user: LoggedUser = Depends(get_current_user)
):
    try:
        folder: Folder = Folder.objects(pk=folder_id).get()
        WorkspaceUtils.have_rights(str(folder.workspace.pk), user)

        # Check if user has rights on the other workspace
        to_workspace: Workspace = Workspace.objects(pk=to_workspace_id).get()
        WorkspaceUtils.have_rights(to_workspace_id, user)

        _, sym_key = WorkspaceUtils.get_workspace(folder.workspace.pk, user)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        WorkspaceUtils.copy_folder_to_other_workspace(
            user,
            folder,
            folder.workspace,
            to_workspace,
            decrypted_sym_key
        )

        create_history(
            user=user.in_db.email,
            workspace=folder.workspace.name,
            workspace_owner=folder.workspace.owner.email,
            action=f"Folder {folder.name} copied to workspace {to_workspace.name}"
        )

        return Response(status_code=status.HTTP_202_ACCEPTED)
    
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    except Workspace.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )


# @router.delete(
#     path="/{folder_id}",
#     summary="Delete a folder",
#     status_code=status.HTTP_204_NO_CONTENT
# )
# async def delete_folder(
#     folder_id: str,
#     user: LoggedUser = Depends(get_current_user)
# ): 
#     try:
#         folder: Folder = Folder.objects(pk=folder_id).get()
#         WorkspaceUtils.have_rights(str(folder.workspace.pk), user)

#         logger.info(f"[FOLDER][{str(folder.workspace.pk)}][{folder.workspace.name}] {user.in_db.email} delete folder {folder.name}")
#         folder.delete()

#         create_history(
#             user=user.in_db.email,
#             workspace=folder.workspace.name,
#             workspace_owner=folder.workspace.owner.email,
#             action=f"Folder {folder.name} deleted"
#         )

#         return Response(status_code=status.HTTP_204_NO_CONTENT)
#     except Folder.DoesNotExist:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Folder not found"
#         )

@router.delete(
    path="/{folder_id}/trash",
    summary="Move a folder to trash",
    status_code=status.HTTP_204_NO_CONTENT
)
async def move_trash_folder(
    folder_id: str,
    user: LoggedUser = Depends(get_current_user)
):
    try:
        folder: Folder = Folder.objects(pk=folder_id).get()

        WorkspaceUtils.have_rights(folder.workspace, user)
        trash : Trash = WorkspaceUtils.get_trash_folder(folder.workspace)
        FolderUtils.move_to_trash(folder, trash, user)
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

@router.get(
    path="/{folder_id}/stats",
    summary="Get stats of a folder",
    response_model=FolderStats,
    dependencies=[Depends(get_current_user)]
)
async def get_folder_stats(
    folder_id: str
) -> FolderStats:
    try:
        folder: Folder = Folder.objects(pk=folder_id).get()
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    stats: FolderStats = FolderStats(
        login=Login.objects(folder=folder).count(),
        server=Server.objects(folder=folder).count(),
        bank=Bank.objects(folder=folder).count(),
        phone=Phone.objects(folder=folder).count()
    )

    return stats


@router.get(
    path="/{folder_id}/secrets",
    summary="Get all secrets in folder",
    response_model=list[LoginSchema] | list[ServerSchema] | list[BankSchema] | list[PhoneSchema]
)
async def get_secrets(
    folder_id: str,
    category: str,
    user: LoggedUser = Depends(get_current_user)
):
    try:
        folder: Folder = Folder.objects(pk=folder_id).get()
        secrets = FolderUtils.get_secrets(folder_id,category, user)
        logger.info(f"[FOLDER][{str(folder.workspace.pk)}][{folder.workspace.name}] {user.in_db.email} retreive secrets in folder {folder.name}")
        return secrets
    except Folder.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
