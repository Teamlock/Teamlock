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

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from exceptions import AuthenticationError, UserLocked, UserDontExist
from fastapi import Depends, status, BackgroundTasks, Request
from .schema import LoggedUser, Login, TokenData
from fastapi.exceptions import HTTPException
from toolkits.redis_tools import RedisTools
from apps.user.schema import UserSchema
from toolkits.history import create_history
from passlib.context import CryptContext
from datetime import timedelta, datetime
from toolkits.crypto import CryptoUtils
from toolkits.mail import MailUtils
from apps.user.models import User
from jose import JWTError, jwt
from settings import settings
import logging.config
import logging
import secrets
import pyotp
import json

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")
logger_security = logging.getLogger("security")

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)
ALGORITHM: str = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def check_password(password_to_check: str, password_ref: str):
    return pwd_context.verify(password_to_check, password_ref)


async def authenticate_user(form_data: OAuth2PasswordRequestForm) -> User:
    try:
        user = User.objects(email=form_data.username).get()
    except User.DoesNotExist:
        logger.info(f"User {form_data.username} does not exists")
        raise UserDontExist()

    if user.is_locked:
        logger.info(f"User {user.email} is currently locked by administrator")
        raise UserLocked()

    if not check_password(form_data.password, user.password):
        raise AuthenticationError()

    logger.info(f"User {user.email} successfully logged in")
    return user    


def validate_otp(tmp_token: str, otp: int):
    try:
        if tmp_token is None:
            return False

        if not (access_token := RedisTools.retreive(tmp_token)):
            return False
        
        access_token = access_token["jwt"]
    except (KeyError, ValueError) as err:
        return False

    data = RedisTools.retreive(access_token)
    user: User = User.objects(pk=data["pk"]).get()
    
    # Check OTP
    totp = pyotp.TOTP(user.otp.secret)
    if not totp.verify(otp):
        return False

    user.save()
    data["otp"] = True
    RedisTools.store(access_token, json.dumps(data), expire=settings.TOKEN_EXPIRE)
    RedisTools.delete(tmp_token)
    return Login(
        access_token=access_token
    )


def create_access_token(user: User,
    password: str,
    x_teamlock_key: str|None,
    x_teamlock_app: str|None
) -> Login:

    expire: int = settings.TOKEN_EXPIRE
    if x_teamlock_app == "browser_ext":
        now = datetime.utcnow()
        end = datetime(now.year, now.month, now.day, settings.END_DAY)
        if now > end:
            end += timedelta(days=1)
        expire: int = int((end - now).seconds)

    access_token_expires: timedelta = timedelta(seconds=expire)
    expire = datetime.utcnow() + access_token_expires
    token_data: TokenData = TokenData(email=user.email, expire=expire.isoformat())

    encoded_jwt: str = jwt.encode(token_data.dict(), settings.SECRET_KEY, algorithm=ALGORITHM)

    session_key: str = CryptoUtils.generate_sim()
    encrypted_password: str = user.encrypt_password_for_current_session(password, session_key)

    tmp_user: dict = {
        "pk": str(user.pk),
        "email": user.email,
        "session_key": session_key,
        "encrypted_password": encrypted_password,
    }

    if user.otp and user.otp.enabled:
        tmp_user["otp"] = x_teamlock_key in user.remember_key

    # Store token into Redis
    RedisTools.store(encoded_jwt, json.dumps(tmp_user), expire=access_token_expires.seconds)
    return Login(
        access_token=encoded_jwt,
        expireAt=expire.isoformat()
    )


def create_temp_otp_key(login: Login):
    tmp_key: str = secrets.token_urlsafe(32)
    RedisTools.store(tmp_key, json.dumps({"jwt": login.access_token}))
    return tmp_key


async def get_current_user(token: str = Depends(oauth2_scheme)) -> LoggedUser:
    try:
        if token is None:
            raise AuthenticationError()

        if not (data := RedisTools.retreive(token)):
            raise AuthenticationError()

        session_key: str = data["session_key"]
        encrypted_password: str = data["encrypted_password"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        try:
            user = User.objects(email=payload["email"]).get()
        except User.DoesNotExist:
            raise AuthenticationError()

        if user.otp and user.otp.need_configure:
            raise AuthenticationError()

        if user.is_locked:
            raise UserLocked()

        # Check if user is locked
        if RedisTools.retreive(f"{user.email}_locked") > 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many authentication failures"
            )

        logged_user : LoggedUser = LoggedUser(**UserSchema(**user.to_mongo()).dict())
        logged_user.session_key = session_key
        logged_user.encrypted_password = encrypted_password
        logged_user.in_db = user
        return logged_user

    except (AuthenticationError, JWTError, User.DoesNotExist):
        # If incorrect JWT, or User does not exist, authentication failed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )    
    

def is_admin(user: UserSchema = Depends(get_current_user)) -> bool:
    if not user.is_admin:
        raise HTTPException(
            detail="Not Allowed",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


def invalid_authentication(email: str, background_tasks: BackgroundTasks, request: Request):
    redis_key: str = f"{email}_invalid_auth"
    nb_invalid_auth = RedisTools.retreive(redis_key) or 0
    nb_invalid_auth += 1

    if nb_invalid_auth > 2:# and not settings.DEV_MODE:
        # Send email and lock account for 10 minutes
        log_message: str = f"User {email}: Too many authentication failure. Lock account for 10 minutes"
        logger.info(log_message)
        logger_security.info(log_message)

        RedisTools.store(f"{email}_locked", 1, 60*10)
        RedisTools.delete(redis_key)

        create_history(
            user=email,
            action="Too many authentication failures. Lock account for 10 minutes"
        )

        try:
            from teamlock_pro.toolkits.proNotif import create_notification
            user = User.objects(email=email).get()
            admins = User.objects(is_admin=True)
            create_notification(
                request=request,
                secret_id=None,
                message="Too many authentication failed",
                user=user,
                users=admins
            )

        except ImportError:
            pass

        background_tasks.add_task(
            MailUtils.send_mail,
            [email],
            None,
            "too_many_auth_failures"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Too many authentication failures",
        )
    else:
        RedisTools.store(redis_key, nb_invalid_auth, 60)

def configure_otp_get_user(token: str = Depends(oauth2_scheme)) -> LoggedUser:
    try:
        if token is None:
            raise AuthenticationError()

        if not (data := RedisTools.retreive(token)):
            raise AuthenticationError()

        session_key: str = data["session_key"]
        encrypted_password: str = data["encrypted_password"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        try:
            user = User.objects(email=payload["email"]).get()
        except User.DoesNotExist:
            raise AuthenticationError()

       
        if user.is_locked:
            raise UserLocked()

        # Check if user is locked
        if RedisTools.retreive(f"{user.email}_locked") > 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many authentication failures"
            )

        logged_user : LoggedUser = LoggedUser(**UserSchema(**user.to_mongo()).dict())
        logged_user.session_key = session_key
        logged_user.encrypted_password = encrypted_password
        logged_user.in_db = user
        return logged_user

    except (AuthenticationError, JWTError, User.DoesNotExist):
            # If incorrect JWT, or User does not exist, authentication failed
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) 

        