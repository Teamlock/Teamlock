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
__doc__ = ""

from pydantic import BaseSettings
import dotenv
import pathlib
import os

dotenv.load_dotenv()


class AppSettings(BaseSettings):
    BASE_DIR: str = str(pathlib.Path(__file__).parent.resolve())
    APP_URL: str = os.environ["APP_URL"]
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = os.environ.get("PORT", 8000)
    DEBUG: bool = os.environ.get("DEBUG", False)
    DEV_MODE: bool = os.environ.get("DEV_MODE") == True
    TOKEN_EXPIRE: int = os.environ.get("TOKEN_EXPIRE", 7200)  # Default: 2 hours
    END_DAY: int = os.environ.get("END_DAY", 20)  # the end of the day default : 20PM
    SECRET_KEY: str = os.environ.get("SECRET_KEY", os.environ.get("SECRET_KEY_FILE"))
    MAX_USERS: int = os.environ.get("MAX_USERS", 0)
    VERSION: float = float(os.environ["VERSION"])
    IP_HEADER: str = os.environ.get("IP_HEADER", "X-Forwarded-For")


class MongoSettings(BaseSettings):
    MONGO_HOST: str = os.environ.get("MONGO_HOST", os.environ.get("MONGO_HOST_FILE"))
    MONGO_DATABASE: str = os.environ.get(
        "MONGO_DATABASE", os.environ.get("MONGO_DATABASE_FILE")
    )
    MONGO_USER: str | None = os.environ.get(
        "MONGO_USER", os.environ.get("MONGO_USER_FILE")
    )
    MONGO_PASSWORD: str | None = os.environ.get(
        "MONGO_PASSWORD", os.environ.get("MONGO_PASSWORD_FILE")
    )
    MONGO_AUTHSOURCE: str | None = os.environ.get("MONGO_AUTHSOURCE")
    MONGO_REPLICASET: str | None = os.environ.get("MONGO_REPLICASET")
    MONGO_TLS: bool = os.environ.get("MONGO_TLS") == True
    MONGO_CA_FILE: str | None = os.environ.get("MONGO_CA_FILE")
    MONGO_KEY_FILE: str | None = os.environ.get("MONGO_KEY_FILE")
    MONGO_ALLOW_INVALID_HOSTNAMES: bool = (
        os.environ.get("MONGO_ALLOW_INVALID_HOSTNAMES") == True
    )
    MONGO_ALLOW_INVALID_CERTIFICATES: bool = (
        os.environ.get("MONGO_ALLOW_INVALID_CERTIFICATES") == True
    )


class RedisSettings(BaseSettings):
    REDIS_HOST: str = os.environ.get("REDIS_HOST", os.environ.get("REDIS_HOST_FILE"))
    REDIS_PORT: int = os.environ["REDIS_PORT"]


class MailSettings(BaseSettings):
    SMTP_HOST: str = os.environ.get("SMTP_HOST", os.environ.get("SMTP_HOST_FILE"))
    SMTP_PORT: str = os.environ["SMTP_PORT"]
    SMTP_AUTH: bool = os.environ.get("SMTP_AUTH") == True
    SMTP_EMAIL: str = os.environ.get("SMTP_EMAIL", os.environ.get("SMTP_EMAIL_FILE"))
    SMTP_PASSWORD: str = os.environ.get(
        "SMTP_PASSWORD", os.environ.get("SMTP_PASSWORD_FILE")
    )
    SMTP_SSL: bool = os.environ.get("SMTP_SSL") == True


class TwilioSettings(BaseSettings):
    TWILIO_ENABLED: bool = os.environ.get("TWILIO_ENABLED") == True
    TWILIO_ACCOUNT_SID: str | None = os.environ.get(
        "TWILIO_ACCOUNT_SID", os.environ.get("TWILIO_ACCOUNT_SID_FILE")
    )
    TWILIO_AUTH_TOKEN: str | None = os.environ.get(
        "TWILIO_AUTH_TOKEN", os.environ.get("TWILIO_AUTH_TOKEN_FILE")
    )
    TWILIO_PHONE_NUMBER: str | None = os.environ.get(
        "TWILIO_PHONE_NUMBER", os.environ.get("TWILIO_PHONE_NUMBER_FILE")
    )


class LogSettings(BaseSettings):
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE: str = "/var/log/teamlock/teamlock.log"
    SECURITY_LOG_FILE: str = "/var/log/teamlock/security.log"
    LOGGING_FORMAT: str = '{"date": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "module":"%(module)s", "line_number": %(lineno)s, "message": "%(message)s"}'

    LOGGING: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": LOGGING_FORMAT, "datefmt": "%Y-%m-%dT%H:%M:%S%z"},
            "simple": {
                "format": "[%(levelname)s] [<%(name)s>:%(module)s:%(lineno)s] "
                "%(message)s"
            },
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
            "debug": {
                "level": LOG_LEVEL,
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "formatter": "verbose",
            },
            "api": {
                "level": LOG_LEVEL,
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "formatter": "verbose",
            },
            "security": {
                "level": LOG_LEVEL,
                "class": "logging.FileHandler",
                "filename": SECURITY_LOG_FILE,
                "formatter": "verbose",
            },
        },
        "loggers": {
            "debug": {"handlers": ["debug", "console"], "level": LOG_LEVEL},
            "api": {"handlers": ["api", "console"], "level": LOG_LEVEL},
            "security": {"handlers": ["security", "console"], "level": LOG_LEVEL},
        },
    }


class Settings(
    AppSettings, MongoSettings, RedisSettings, MailSettings, TwilioSettings, LogSettings
):
    ...


settings = Settings()
