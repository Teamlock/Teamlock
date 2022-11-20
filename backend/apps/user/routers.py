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

from toolkits.paginate import PaginationParamsSchema, UserPaginationSchema, get_order
from apps.auth.tools import get_current_user, hash_password, is_admin, check_password
from fastapi import APIRouter, status, Depends, Request, BackgroundTasks
from apps.workspace.models import Share, Workspace
from fastapi.responses import FileResponse, Response
from toolkits.exceptions import UserExistException
from starlette.background import BackgroundTask
from toolkits.utils import create_user_toolkits
from toolkits.workspace import WorkspaceUtils
from fastapi.exceptions import HTTPException
from apps.config.schema import ConfigSchema
from .models import OTP, User, UserSession
from apps.config.routers import fetch_config
from toolkits.crypto import CryptoUtils
from apps.auth.schema import LoggedUser
from toolkits.schema import RSASchema
from apps.config.models import Config
from datetime import datetime
from settings import settings
import logging.config
from . import schema
import logging
import math
import os

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=schema.UserTableSchema | list[schema.UserSchema],
    summary="Get users",
    dependencies=[Depends(is_admin)]
)
async def get_users(
    all: bool = False,
    paginate: UserPaginationSchema = Depends()
) -> schema.UserTableSchema:        
    if all:
        users: list = [schema.UserSchema(**obj.to_mongo()) for obj in User.objects.all()]
        return users

    if not paginate.sort:
        paginate.sort = "email|desc"
    
    aggs: list = []
    match: dict = {"$match": {}}
    if paginate.search:
        match["$match"]["email"] = {
            "$regex": paginate.search
        }

    if paginate.lockedUsers:
        match["$match"]["is_locked"] = True

    if paginate.notConfiguredUsers:
        match["$match"]["is_configured"] = False

    if paginate.adminUsers:
        match["$match"]["is_admin"] = True

    if len(match["$match"].values()) > 0:
        aggs.append(match)

    aggs.append(get_order(paginate.sort))
    skip: int = (paginate.page -1) * paginate.per_page
    if paginate.per_page != -1:
        aggs.append({"$skip": skip})
        aggs.append({"$limit": paginate.per_page})

    total_objects: int = User.objects.count()

    objects = User.objects.aggregate(*aggs)
    users: list = [schema.UserSchema(**tmp) for tmp in objects]

    return schema.UserTableSchema(
        start=skip,
        data=users,
        total=total_objects,
        to=skip + len(users),
        current_page=paginate.page,
        per_page=paginate.per_page,
        last_pages=math.ceil(total_objects / paginate.per_page),
        total_admin_users=User.objects(is_admin=True).count(),
        total_locked_users=User.objects(is_locked=True).count(),
        total_not_configured_users=User.objects(is_configured=False).count(),
    )


@router.get(
    path="/configured",
    response_model=list[schema.ConfiguredUsers],
    summary="Get list of configured users",
    description="Return all users who has no rights on a specific workspace"
)
async def get_configured_users(
    workspace_id: str,
    user: LoggedUser = Depends(get_current_user)
):
    workspace, _ = WorkspaceUtils.get_workspace(workspace_id, user)
    shares = [s.user.pk for s in Share.objects(workspace=workspace)]

    tmp_configured_users = [u.to_mongo() for u in User.objects(pk__nin=shares, is_configured=True).order_by("email")]
    return tmp_configured_users


@router.get(
    path="/sessions",
    summary="Get sessions of an User",
    response_model=schema.UserSessionTableSchema
)
async def get_sessions(
    paginate: PaginationParamsSchema = Depends(),
    user: LoggedUser = Depends(get_current_user)
):
    if not paginate.sort:
        paginate.sort = "date|desc"

    match: dict = {"$match": {
        "user": user.id
    }}

    aggs: list = [match]
    aggs.append(get_order(paginate.sort))
    skip: int = (paginate.page - 1) * paginate.per_page
    if paginate.per_page != -1:
        aggs.append({"$skip": skip})
        aggs.append({"$limit": paginate.per_page})

    total_objects: int = UserSession.objects(user=user.in_db).count()

    objects = UserSession.objects.aggregate(*aggs)
    sessions: list = [schema.UserSessionSchema(**tmp) for tmp in objects]
    return schema.UserSessionTableSchema(
        start=skip,
        data=sessions,
        total=total_objects,
        to=skip + len(sessions),
        current_page=paginate.page,
        per_page=paginate.per_page,
        last_pages=math.ceil(total_objects / paginate.per_page)
    )


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    summary="Endpoint to create an user",
    dependencies=[Depends(is_admin)]
)
async def create_user(user_def: schema.EditUserSchema, background_task: BackgroundTasks) -> str:
    try:
        if settings.MAX_USERS > 0:
            # Check if max users has been reached
            nb_users: int = User.objects.count()
            if nb_users >= settings.MAX_USERS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MAX USERS LIMIT"
                )

        user_id: str = create_user_toolkits(user_def, background_task)
        return user_id
    except UserExistException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
        )
    except Exception as err:
        raise HTTPException(
            detail=str(err),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post(
    path="/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Create several users",
    dependencies=[Depends(is_admin)]
)
async def bulk_create_user(users_def: list[schema.EditUserSchema]) -> list[str]:
    errors: list = []
    success: list = []

    users_id: list = []
    if settings.MAX_USERS > 0:
        # Check if max users has been reached
        nb_users: int = User.objects.count()
        if nb_users >= settings.MAX_USERS or len(users_def) + nb_users > settings.MAX_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MAX USERS LIMIT"
            )

    for user_def in users_def:
        try:
            users_id.append(create_user_toolkits(user_def))
            success.append(user_def.email)
        except UserExistException:
            errors.append({
                "email": user_def.email,
                "error": "EXISTS"
            })
        except Exception as err:
            raise HTTPException(
                detail=str(err),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return {
        "success": success,
        "errors": errors
    }


@router.put(
    path="/{user_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Change Admin status",
    dependencies=[Depends(is_admin)]
)
async def change_admin_status(
    user_id: str,
    admin_schema: schema.UpdateAdminUserSchema,
) -> None:
    try:
        user: User = User.objects(pk=user_id).get()
        user.is_admin = admin_schema.is_admin
        user.save()

        return Response(status_code=status.HTTP_202_ACCEPTED)
    
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.put(
    path="",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Edit an user"
)
async def update_user(
    password_update_schema: schema.UpdateUserSchema,
    background_tasks: BackgroundTasks,
    user: LoggedUser = Depends(get_current_user)
) -> None:
    if not check_password(password_update_schema.current_password, user.in_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )
    
    # Check if password is the same
    if check_password(password_update_schema.new_password, user.in_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Used password"
        )

        # Check if password has already been used
    for password in user.in_db.last_passwords:
        if check_password(password_update_schema.new_password, password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Used password"
            )
    
    # Check password complexity
    config: ConfigSchema = fetch_config(as_schema=True)    

    # Raise an error if password is not complex enough
    if (error := config.password_policy.verify(password_update_schema.new_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Password not allowed by policy",
                "details": error
            }
        )

    old_passphrase = CryptoUtils.prepare_password(password_update_schema.current_password)
    WorkspaceUtils.update_password(
        user.in_db,
        old_passphrase,
        password_update_schema.new_password,
        background_tasks
    )

    try:
        from teamlock_pro.toolkits.proRecovery import send_recovery_key
        send_recovery_key(user, password_update_schema.new_password)
    except ImportError:
        pass

    logger.info(f"User {user.in_db.email} has change his password")
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post(
    path="/recover/{user_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enable recovery mode for an user",
    dependencies=[Depends(is_admin)]
)
async def enable_disable_recovery_mode(
    user_id: str,
    recovery_schema: schema.RecoveryModeSchema
) -> None:
    try:
        user = User.objects(pk=user_id).get()
        user.recovery_enabled = recovery_schema.enabled
        user.save()

        logger.info(f"[USER] {user.email} Recovery Enabled by administrator")
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except User.DoesNotExist:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.post(
    path="/lock/{user_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Lock/Unlock an user",
    dependencies=[Depends(is_admin)]
)
async def lock_unlock_user(user_id: str, lock: schema.LockUserSchema) -> None:
    try:
        user = User.objects(pk=user_id).get()
        user.is_locked = lock.is_locked
        user.save()

        return Response(status_code=status.HTTP_202_ACCEPTED)
    except User.DoesNotExist:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an user",
    description="Delete all personal workspaces and delete the user",
    dependencies=[Depends(is_admin)]
)
async def delete_user(user_id: str) -> None:
    try:
        user = User.objects(pk=user_id).get()

        Share.objects(user=user, is_owner=False).delete()
        UserSession.objects(user=user).delete()

        shares = Share.objects(user=user, is_owner=True)
        for share in shares:
            share.is_owner = False
            share.save()

            # Define the first user found as the new owner
            # TODO: Modal with new owner selection
            s = Share.objects(workspace=share.workspace)[0]
            s.is_owner = True
            s.save()

        user.delete()

        logger.info(f"[USER] {user.email} deleted")
        return Response(status_code=status.HTTP_204_NO_CONTENT) 
    except User.DoesNotExist:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.get(
    path="/configure/{user_id}",
    summary="Check if user exists",
    response_model=schema.NotConfigureUserSchema
)
async def check_user(
    user_id: str
) -> schema.UserSchema:
    try:
        user = User.objects(pk=user_id, is_configured=False).get()
        tmp = user.to_mongo()

        try:
            from teamlock_pro.toolkits.proUsers import check_user_otp
            tmp = check_user_otp(user, tmp)
        except ImportError:
            pass

        return tmp
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already configured"
        )


@router.post(
    path="/configure/{user_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Endpoint to configure an user",
    description="Configure an user. Set up internal password and generate Public & Private RSA Keys"
)
async def configure_user(
    request: Request,
    user_id: str, 
    configure_schema: schema.ConfigureUserSchema
) -> None:
    try:
        config: Config = Config.objects.get()
        # First check if the user does exists
        user: User = User.objects(pk=user_id).get()
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exists"
        )
    
    try:
        from teamlock_pro.toolkits.proUsers import configure_otp
        user = configure_otp(user, configure_schema)
    except ImportError:
        pass

    # Check if user is locked
    if user.is_locked:
        logger.info(f"User {user.email} try to configure himself but he's locked")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account locked by administrator"
        )

    # Check if user is already configured
    if user.is_configured:
        logger.info(f"User {user.email} try to configure himself but he's already configured")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already configured"
        )
   
    # Check password complexity
    config: ConfigSchema = fetch_config(as_schema=True)
    # Raise an error if password is not complex enough

    error = config.password_policy.verify(configure_schema.password)
    if len(error) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Password not allowed by policy",
                "details": error
            }
        )

    # Generate User Private and Public RSA Keys
    rsa_pubpriv: RSASchema = CryptoUtils.generate_rsa_keys(configure_schema.password)

    # Save RSA keys into database
    user.public_key = rsa_pubpriv.pubkey
    user.private_key = rsa_pubpriv.privkey
    user.password = hash_password(configure_schema.password)

    # User is now configured
    user.is_configured = True
    user.last_change_pass = datetime.utcnow()

    client_ip = request.headers.get(settings.IP_HEADER, request.client.host)
    user.known_ip_addresses = [client_ip]

    try:
        from teamlock_pro.toolkits.proRecovery import send_recovery_key
        send_recovery_key(user, password=configure_schema.password)
    except ImportError:
        pass

    # Create Personal Workspace
    WorkspaceUtils.create_workspace(
        user,
        "Personal",
        "mdi-account",
        config.password_policy
    )

    user.save()


@router.get(
    path="/recovery",
    status_code=status.HTTP_200_OK,
    summary="Generate Recovery Key",
    description="Generate a file that can be used to recover an account when password is lost"
)
async def generate_recovery_key(user: LoggedUser = Depends(get_current_user)) -> FileResponse:
    res = CryptoUtils.generate_recovery_symkey(user)

    user.in_db.encrypted_password = res.encrypted_password
    user.in_db.recovery_key_downloaded = True
    user.in_db.save()

    filename: str = f"/tmp/{str(user.in_db.pk)}"
    with open(filename, "w") as tmp:
        tmp.write(res.encoded_sym_key)

    def cleanup_file(args):
        os.remove(args[0])
    
    return FileResponse(
        filename,
        background=BackgroundTask(cleanup_file, (filename,))
    )


@router.get(
    path="/certificates",
    summary="Download user certificate"
)
async def download_user_certificates(
    background_tasks: BackgroundTasks,
    user: LoggedUser = Depends(get_current_user)
) -> FileResponse:

    def delete_tmp_file(filename):
        os.remove(filename)

    filename: str = f"/var/tmp/{str(user.in_db.pk)}.pem"
    with open(filename, 'w') as f:
        f.write(f"{user.in_db.public_key}\n{user.in_db.private_key}")

    background_tasks.add_task(delete_tmp_file, (filename))
    return FileResponse(filename)

    