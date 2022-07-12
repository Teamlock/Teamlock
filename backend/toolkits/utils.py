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

from apps.config.schema import ConfigSchema, PasswordPolicySchema
from mongoengine.errors import NotUniqueError
from fastapi.exceptions import HTTPException
from apps.user.schema import EditUserSchema
from toolkits.redis_tools import RedisTools
from .exceptions import UserExistException
from apps.user.models import UserSession
from apps.config.models import Config
from apps.user.models import User
from toolkits.mail import MailUtils
from settings import settings
from fastapi import status
import logging.config
import geocoder
import datetime
import logging
import jinja2

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


def render_template(template: str, context: dict) -> str:
    j2_template = jinja2.Template(template)
    return j2_template.render(context)

def fetch_config(as_schema: bool = False) -> Config | ConfigSchema:
    config: Config = Config.objects.get()

    if as_schema:
        return ConfigSchema(**config.to_mongo())

    return config

def check_password_complexity(policy: PasswordPolicySchema, password):
    errors: list = policy.verify(
        password=password
    )

    if len(errors) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Password not allowed by internal policy",
                "details": errors
            }
        )


def create_user_toolkits(user_def: EditUserSchema) -> str:
    try:
        # Create User
        user: User = User(
            email=user_def.email,
            is_admin=user_def.is_admin
        )

        try:
            from teamlock_pro.toolkits.proUsers import add_otp_to_user
            user = add_otp_to_user(user)
        except ImportError:
            pass

        user.save()

        # Send mail to new user
        url: str = f"#/configure/{str(user.pk)}"
        if settings.SMTP_HOST:
            MailUtils.send_mail([user.email], url, "registration")

        return str(user.pk)

    except NotUniqueError:
        raise UserExistException()

    except Exception as err:
        logger.critical(err, exc_info=1)
        user.delete()
        raise


def create_user_session(user, request) -> None | dict:
    # Return true if a security alert email need to be sent
    send_security_alert_email: bool = False

    # Create user session
    os = request.headers.get("sec-ch-ua-platform", "").replace('"', '')
    user_agent = request.headers.get("user-agent", "")

    client_ip = request.headers.get(settings.IP_HEADER, request.client.host)

    try:
        geo = geocoder.ip(client_ip)
    except Exception:
        geo = None

    UserSession.objects.create(
        user=user,
        os=os,
        ip_address=client_ip,
        user_agent=user_agent,
        country=geo.country or "",
        city=geo.city or ""
    )

    if len(user.known_ip_addresses) == 0:
        user.known_ip_addresses.append(client_ip)

    if client_ip not in user.known_ip_addresses:
        send_security_alert_email = True
        user.known_ip_addresses.append(client_ip)

    # Keep only the last 30 days informations
    last_month = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    UserSession.objects(date__lte=last_month).delete()

    user.last_seen = datetime.datetime.utcnow()
    user.save()

    RedisTools.delete(f"{user.email}_invalid_auth")

    if send_security_alert_email:
        return {
            "ip_address": client_ip,
            "country": geo.country,
            "city": geo.city
        }
