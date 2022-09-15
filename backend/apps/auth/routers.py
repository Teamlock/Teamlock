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

from .tools import (authenticate_user, create_access_token, get_current_user, 
    create_temp_otp_key, invalid_authentication)
from fastapi import (APIRouter, Depends, status, Header, Request, 
    UploadFile, File, Form, Header, BackgroundTasks)
from toolkits.utils import (create_user_toolkits, fetch_config, create_user_session)
from apps.user.schema import EditUserSchema, UserSchema, UserProfileSchema
from .schema import LoggedUser, Login, RegistrationSchema
from fastapi.security import OAuth2PasswordRequestForm
from exceptions import AuthenticationError, UserDontExist, UserLocked
from toolkits.exceptions import UserExistException
from toolkits.workspace import WorkspaceUtils
from fastapi.exceptions import HTTPException
from toolkits.history import create_history
from toolkits.redis_tools import RedisTools
from fastapi.responses import JSONResponse
from apps.config.schema import ConfigSchema
from apps.config.models import Config
from toolkits.mail import MailUtils
from apps.user.models import User
from settings import settings
import logging.config
import datetime
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")
logger_security = logging.getLogger("security")

router: APIRouter = APIRouter()


@router.post(
    path="/token",
    response_model=Login | dict,
    status_code=status.HTTP_200_OK,
    summary="Authenticate for Access Token"
)
async def login_for_access_token(
    request: Request,
    background_tasks: BackgroundTasks,
    x_teamlock_key: str | None = Header(None),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Login:

    try:
        user: User = await authenticate_user(form_data)
    except UserDontExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except AuthenticationError:
        invalid_authentication(form_data.username)

        log_message: str = f"[AUTH] Invalid authentication for Email {form_data.username}"
        logger.info(log_message)
        logger_security.info(log_message)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except UserLocked:
        logger.info(f"[AUTH] User {form_data.username} is locked by administrator")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account currently locked by administrator"
        )

    if RedisTools.retreive(f"{user.email}_locked"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Too many authentication failures"
        )

    login: Login = create_access_token(user, form_data.password, x_teamlock_key)

    # Check if user has TOTP Enabled
    if user.otp and user.otp.enabled:
        if x_teamlock_key not in user.remember_key:
            # Need to create temporary Session key for user to validate OTP
            token: str = create_temp_otp_key(login)
            return JSONResponse(content={
                "otp": True,
                "token": token
            })

    if (session := create_user_session(user, request)) and not settings.DEV_MODE:
        # Send an email if new connection and no DEV MODE
        logger.info(f"[AUTH] Sending security alert for user {user.email}")
        background_tasks.add_task(
            MailUtils.send_mail,
            [user.email],
            "/#/profile/sessions",
            "new_ip_address",
            session
        )

    log_message: str = f"[AUTH] User {form_data.username} successfully logged in"
    logger.info(log_message)
    logger_security.info(log_message)
    RedisTools.delete(f"{user.email}_invalid_auth")
    return login


@router.get(
    path="/verify",
    summary="Token verify",
    description="Endpoint to check if JWT Token is still valid",
    dependencies=[Depends(get_current_user)]
)
async def verify() -> bool:
    return True


@router.get(
    path="/me",
    summary="Get user profile",
    response_model=UserProfileSchema,
    status_code=status.HTTP_200_OK
)
async def get_me(user: LoggedUser = Depends(get_current_user)) -> UserSchema:
    tmp = user.in_db.to_mongo()

    config: Config = Config.objects.get()
    if config.password_duration != 0:
        delta = datetime.date.today() - user.in_db.last_change_pass
        if delta.days > config.password_duration:
            tmp["need_change_password"] = True

    return UserProfileSchema(**tmp)


@router.post(
    path="/register",
    summary="Register a new user"
)
async def register_user(registration_schema: RegistrationSchema) -> bool:
    config: Config = fetch_config()
    if not config.allow_self_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Allowed"
        )
    
    allowed: bool = False
    for email in config.allowed_email_addresses:
        if registration_schema.email.endswith(email):
            allowed = True
            break

    if not allowed:
        logger.info(f"[REGISTER] Email {registration_schema.email} not allowed to register")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed"
        )

    user_schema: EditUserSchema = EditUserSchema(
        email=registration_schema.email,
        is_admin=False
    )

    try:
        create_user_toolkits(user_schema)

        log_message: str = f"[REGISTER] Email {user_schema.email} registered"
        logger.info(log_message)
        logger_security.info(log_message)
    except UserExistException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    except Exception as err:
        logger.critical(err, exc_info=1)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error has occurred"
        )
    

@router.post(
    path="/recover",
    summary="Recover account",
    status_code=status.HTTP_200_OK
)
async def recover_user(
    request: Request,
    email: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    recover_file: UploadFile = File(...)
) -> bool:
    try:

        if confirm_password != new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords mismatch"
            )

        config: ConfigSchema = fetch_config(as_schema=True)

        error = config.password_policy.verify(new_password)
        if len(error) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": f"Password not allowed by policy",
                    "details": error
                }
            )

        user = User.objects(email=email).get()
        if not user.recovery_enabled:
            log_message: str = f"[RECOVER] User {email} attempts to recover, but recovery mode not enabled"
            logger.info(log_message)
            logger_security.info(log_message)

            try:
                from teamlock_pro.toolkits.proNotif import create_notification

                admins = User.objects(is_admin=True)
                create_notification(
                    request=request,
                    secret_id=None,
                    message="User recovery attempt",
                    user=user,
                    users=admins
                )

            except ImportError:
                pass

            create_history(
                user=email,
                action="Attempts to recover account, but recovery mode not enabled"
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN
            )

        sym_key: bytes = await recover_file.read()
        WorkspaceUtils.recover_account(user, sym_key.decode("utf-8"), new_password)
        user.recovery_enabled = False
        user.save()

        log_message: str = f"[RECOVER] User {email} successfully recovered"
        logger.info(log_message)
        logger_security.info(log_message)

        create_history(
            user=email,
            action="User recovered his account"
        )

    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
