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

from .schema import (EditShareSchema, EditWorkspaceSchema, ImportXMLFileSchema,
                     SharedWorkspaceSchema, UpdateShareSchema, UsersWorkspace, WorkspaceSchema)
from fastapi import APIRouter, Depends, status, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
from mongoengine.errors import NotUniqueError
from pymongo.errors import DuplicateKeyError
from apps.config.models import PasswordPolicy
from toolkits.workspace import WorkspaceUtils
from toolkits.import_utils import ImportUtils
from fastapi.exceptions import HTTPException
from apps.folder.schema import FolderSchema
from apps.secret.models import Login, Secret, Server, Bank, Phone
from apps.auth.tools import get_current_user
from mongoengine.queryset.visitor import Q
from toolkits.folder import FolderUtils
from toolkits.crypto import CryptoUtils
from toolkits.secret import SecretUtils
from apps.auth.schema import LoggedUser
from fastapi.responses import Response
from .models import Workspace, Share
from apps.folder.models import Folder
from apps.secret.models import Secret
from apps.trash.schema import TrashSchema, TrashStats
from datetime import datetime
from settings import settings
from toolkits import const
import logging.config
import logging


logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get(
    path="/",
    response_model=list[SharedWorkspaceSchema],
    summary="Fetch list of workspaces"
)
async def get_workspaces(user: LoggedUser = Depends(get_current_user)) -> list[WorkspaceSchema]:
    workspaces = [SharedWorkspaceSchema(
        **data.to_mongo()) for data in Workspace.objects(owner=user.id)]

    shared_query: Q = Q(user=user.id) & (
        Q(expire_at=None) | Q(expire_at__lte=datetime.utcnow()))
    for tmp in Share.objects(shared_query):
        tmp_schema: dict = WorkspaceSchema(**tmp.workspace.to_mongo()).dict()
        tmp_schema.update({
            "shared": True,
            "can_write": tmp.can_write,
            "can_share": tmp.can_share,
            "can_export": tmp.can_export,
            "can_share_external": tmp.can_share_external
        })
        workspaces.append(SharedWorkspaceSchema(**tmp_schema))

    return workspaces


@router.get(
    path="/{workspace_id}",
    response_model=SharedWorkspaceSchema,
    summary="Fetch a workspace"
)
async def get_workspace(workspace_id: str, user: LoggedUser = Depends(get_current_user)) -> WorkspaceSchema:
    workspace = Workspace.objects(pk=workspace_id).get()
    workspace, _ = WorkspaceUtils.get_workspace(workspace_id, user)

    folders = Folder.objects(workspace=workspace).only("pk")

    nb_secrets: int = 0
    for model_ in const.MAPPING_SECRET.values():
        nb_secrets += model_.objects(folder__in=folders).count()

    schema = SharedWorkspaceSchema(**workspace.to_mongo())

    if workspace.owner != user.in_db:
        try:
            share = Share.objects(workspace=workspace, user=user.in_db).get()
            schema.shared = True
            schema.can_write = share.can_write
            schema.can_share = share.can_share
            schema.can_export = share.can_export
            schema.can_share_external = share.can_share_external
        except Share.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="WORKSPACENOTFOUND"
            )

    schema.nb_folders = len(folders)
    schema.nb_secrets = nb_secrets
    return schema


@router.post(
    path="/",
    summary="Create a workspace",
    status_code=status.HTTP_201_CREATED
)
async def create_workspace(
    workspace_def: EditWorkspaceSchema,
    user: LoggedUser = Depends(get_current_user)
) -> str:

    try:
        workspace_id: str = WorkspaceUtils.create_workspace(
            user.in_db,
            workspace_def.name,
            workspace_def.icon,
            workspace_def.password_policy
        )

        return Response(status_code=status.HTTP_201_CREATED, content=workspace_id)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workspace with this name already exists"
        )


@router.put(
    path="/{workspace_id}",
    summary="Edit a workspace",
    status_code=status.HTTP_202_ACCEPTED
)
async def edit_workspace(
    workspace_id: str,
    workspace_def: EditWorkspaceSchema,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    try:
        if not WorkspaceUtils.have_rights(workspace_id, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="NOTALLOWED"
            )

        workspace, _ = WorkspaceUtils.get_workspace(
            workspace_id,
            user
        )

        workspace.name = workspace_def.name
        workspace.icon = workspace_def.icon

        password_policy = None
        if workspace_def.password_policy:
            password_policy = PasswordPolicy(
                **workspace_def.password_policy.dict())

        workspace.password_policy = password_policy
        workspace.save()

        return Response(status_code=status.HTTP_202_ACCEPTED)
    except Workspace.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    except NotUniqueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workspace with this name already exists"
        )


@router.delete(
    path="/{workspace_id}",
    summary="Delete a workspace",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_workspace(
    workspace_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    try:
        if not WorkspaceUtils.have_rights(workspace_id, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="NOTALLOWED"
            )

        workspace: Workspace = Workspace.objects(
            pk=workspace_id, owner=user.in_db
        ).get()

        Share.objects(workspace=workspace).delete()
        workspace.delete()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Workspace.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )


@router.get(
    path="/{workspace_id}/share",
    response_model=list[UsersWorkspace],
    summary="Return list of users who has access to the workspace"
)
async def get_user_workspace(
    workspace_id: str,
    user: LoggedUser = Depends(get_current_user)
):
    workspace, _ = WorkspaceUtils.get_workspace(workspace_id, user)
    shares: list = []

    for share in Share.objects(workspace=workspace):
        shares.append({
            "_id": share.pk,
            "user": share.user.pk,
            "expire_at": share.expire_at,
            "user_email": share.user.email,
            "can_write": share.can_write,
            "can_share": share.can_share,
            "can_export": share.can_export,
            "can_share_external": share.can_share_external
        })

    return shares


@router.post(
    path="/{workspace_id}/share",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Share a workspace to new user",
    description="""This endpoint will share an existing Workspace to an other user
Only an user with the correct rights will be able to add an user.
"""
)
async def share_workspace(
    workspace_id: str,
    share_def: EditShareSchema,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    workspace, _ = WorkspaceUtils.get_workspace(workspace_id, user)

    WorkspaceUtils.share_workspace(
        user,
        workspace,
        share_def
    )


@router.put(
    path="/{workspace_id}/share/{share_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update a share object"
)
async def update_share(
    workspace_id: str,
    share_id: str,
    share_def: UpdateShareSchema,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    workspace, _ = WorkspaceUtils.get_workspace(workspace_id, user)

    WorkspaceUtils.have_rights(workspace, user, "can_share")

    try:
        share = Share.objects(pk=share_id).get()
        share.can_write = share_def.can_write
        share.can_share = share_def.can_share
        share.can_export = share_def.can_export
        share.can_share_external = share_def.can_share_external
        share.save()
    except Share.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )


@router.delete(
    path="/{workspace_id}/share/{share_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an user from a workspace"
)
async def delete_share(
    workspace_id: str,
    share_id: str,
    user: LoggedUser = Depends(get_current_user)
):
    if not WorkspaceUtils.have_rights(workspace_id, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="NOTALLOWED"
        )

    try:
        share = Share.objects(pk=share_id).get()
        share.delete()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Share.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared not found"
        )


@router.post(
    path="/{workspace_id}/import",
    status_code=status.HTTP_200_OK,
    summary="Import File",
    description="Fill Workspace data with a XML KeePass File or a TeamLock v1 Backup File"
)
async def import_keepass_file(
    background_task: BackgroundTasks,
    workspace_id: str,
    encrypt_name: bool = Form(...),
    encrypt_url: bool = Form(...),
    encrypt_login: bool = Form(...),
    encrypt_password: bool = Form(...),
    encrypt_informations: bool = Form(...),
    import_type: str = Form(...),
    file: UploadFile = File(...),
    user: LoggedUser = Depends(get_current_user)
):
    import_schema: ImportXMLFileSchema = ImportXMLFileSchema(
        encrypt_name=encrypt_name,
        encrypt_url=encrypt_url,
        encrypt_login=encrypt_login,
        encrypt_password=encrypt_password,
        encrypt_informations=encrypt_informations,
    )

    workspace, sym_key = WorkspaceUtils.get_workspace(workspace_id, user)
    workspace.import_in_progress = True
    workspace.save()

    content_file: bytes = await file.read()

    func_mapping: dict = {
        "keepass": ImportUtils.import_xml_keepass,
        "teamlock_v1": ImportUtils.import_teamlock_backup,
        "bitwarden": ImportUtils.import_json_bitwarden
    }

    background_task.add_task(
        func_mapping[import_type],
        user,
        workspace,
        sym_key,
        import_schema,
        content_file.decode("utf-8")
    )

    return Response(status_code=status.HTTP_200_OK)


@router.get(
    path="/{workspace_id}/folders",
    summary="Get all folders in a workspace",
    response_model=list[FolderSchema]
)
async def get_workspace_folders(
    workspace_id: str,
    user: LoggedUser = Depends(get_current_user)
) -> list[FolderSchema]:
    return WorkspaceUtils.get_folders(workspace_id, user)


@router.post(
    path="/{workspace_id}/export",
    summary="Export a workspace in keypass format"
)
async def export_workspace_file(
    background_tasks: BackgroundTasks,
    workspace_id: str,
    user: LoggedUser = Depends(get_current_user)
):

    workspace, _ = WorkspaceUtils.get_workspace(workspace_id,user)
    WorkspaceUtils.have_rights(workspace,user,"can_export")
    WorkspaceUtils.export_workspace(workspace_id, user)
    background_tasks.add_task(WorkspaceUtils.delete_tmp_file,f"/var/tmp/{workspace.name}.kdbx")
    
    return FileResponse(f"/var/tmp/{workspace.name}.kdbx")


@router.get(
    path="/{workspace_id}/trash",
    summary="Get the trash folder, and all its secrets depending on the category you want"
)
async def get_trash(
    workspace_id: str,
    category: str,
    user: LoggedUser = Depends(get_current_user)
) -> TrashSchema:
    trash = WorkspaceUtils.get_trash_folder(workspace_id)
    WorkspaceUtils.have_rights(workspace_id, user)

    model_ = const.MAPPING_SECRET[category]
    tmp_secrets: list = list(model_.objects(folder=None))
    secrets = []

    _, sym_key = WorkspaceUtils.get_workspace(workspace_id, user)
    decrypted_sym_key = CryptoUtils.rsa_decrypt(
        sym_key,
        user.in_db.private_key,
        CryptoUtils.decrypt_password(user)
    )

    for tmp in tmp_secrets:
            schema = tmp.schema()
            secrets.append(WorkspaceUtils.decrypt_secret(decrypted_sym_key, schema))


    logger.info(f"[FOLDER][{str(trash.workspace.pk)}][{trash.workspace.name}] {user.in_db.email} retreive trash")
    return TrashSchema(
        id = trash.pk,
        workspace = trash.workspace.pk, 
        created_at = trash.created_at,
        secrets = secrets
    )

@router.delete(
    path="/{workspace_id}/trash",
    summary="Delete all the content of the trash",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_trash_content(
    workspace_id: str,
    user: LoggedUser = Depends(get_current_user)
):
    workspace, _ = WorkspaceUtils.get_workspace(workspace_id,user)
    trash = WorkspaceUtils.get_trash_folder(workspace_id)
    WorkspaceUtils.have_rights(workspace_id, user)
    
    [secret.delete() for secret in Secret.objects(trash = trash)]

    return Response(status_code=status.HTTP_204_NO_CONTENT)
    

@router.get(
    path="/{workspace_id}/trash/stats",
    summary="Get stats of a trash",
    response_model=TrashStats,
    dependencies=[Depends(get_current_user)]
)
async def get_trash_stats(
    workspace_id: str
) -> TrashStats:
    trash = WorkspaceUtils.get_trash_folder(workspace_id)

    stats: TrashStats = TrashStats(
        login=Login.objects(folder=None, trash = trash).count(),
        server=Server.objects(folder=None, trash = trash).count(),
        bank=Bank.objects(folder=None, trash = trash).count(),
        phone=Phone.objects(folder=None, trash = trash).count()
    )

    return stats

@router.patch(
    path="/{workspace_id}/trash/restore",
    summary="Restore the trash entirely",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)]
)
async def restore_trash(
    workspace_id: str
) -> None:
    trash = WorkspaceUtils.get_trash_folder(workspace_id)

    [SecretUtils.restore(secret,trash.workspace) for secret in Secret.objects(trash = trash)]

    return Response(status_code=status.HTTP_204_NO_CONTENT)