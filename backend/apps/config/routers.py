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

from .schema import ConfigSchema, PasswordPolicySchema
from apps.auth.tools import get_current_user, is_admin
from fastapi import APIRouter, Depends, status, Body
from fastapi.exceptions import HTTPException
from .models import Config, PasswordPolicy
from fastapi.responses import Response
from toolkits.utils import fetch_config
from settings import settings
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")

router: APIRouter = APIRouter()


@router.get(
    path="/",
    response_model=ConfigSchema,
    summary="Retreive Teamlock Configuration",
    dependencies=[Depends(is_admin)],
)
async def get_config() -> ConfigSchema:
    config: ConfigSchema = fetch_config(as_schema=True)
    return config


@router.post(
    path="/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update Teamlock Configuration",
    dependencies=[Depends(is_admin)]
)
async def edit_config(update_config: ConfigSchema = Body(...)) -> None:
    config: Config = fetch_config()

    config.password_policy = PasswordPolicy(**update_config.password_policy.dict())
    config.rsa_key_size = update_config.rsa_key_size
    config.password_duration = update_config.password_duration
    config.allow_self_registration = update_config.allow_self_registration
    config.allowed_email_addresses = update_config.allowed_email_addresses
    config.save()

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get(
    path="/registration",
    response_model=bool,
    include_in_schema=False,
    summary="Self registration is allowed ?"
)
async def get_self_registration() -> None:
    try:
        config: Config = fetch_config()
        return config.allow_self_registration
    except Config.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Teamlock not installed"
        )


@router.get(
    path="/policy",
    response_model=PasswordPolicySchema,
    summary="Retreive password policy for user's password",
)
async def get_password_policy() -> PasswordPolicySchema:
    try:
        config: Config = fetch_config()
        return PasswordPolicySchema(**config.password_policy.to_mongo())
    except Config.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Teamlock not installed"
        )


@router.get(
    path="/twilio",
    response_model=bool,
    include_in_schema=False,
    summary="Twilio is configured ?",
    dependencies=[Depends(get_current_user)]
)
async def twilio_enabled() -> bool:
    return settings.TWILIO_ENABLED
