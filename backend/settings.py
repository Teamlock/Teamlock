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

dotenv.load_dotenv()


class AppSettings(BaseSettings):
    BASE_DIR: str = str(pathlib.Path(__file__).parent.resolve())
    APP_URL: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    DEV_MODE: bool = False
    TOKEN_EXPIRE: int = 7200
    END_DAY: int = 20
    SECRET_KEY: str
    MAX_USERS: int = 0
    VERSION: float
    IP_HEADER: str = "X-Forwarded-For"


class MongoSettings(BaseSettings):
    MONGO_HOST: str
    MONGO_DATABASE: str
    MONGO_USER: str | None = None
    MONGO_PASSWORD: str | None = None
    MONGO_AUTHSOURCE: str | None = None
    MONGO_REPLICASET: str | None = None
    MONGO_TLS: bool = False
    MONGO_CA_FILE: str | None = None
    MONGO_KEY_FILE: str | None = None
    MONGO_ALLOW_INVALID_HOSTNAMES: bool = False
    MONGO_ALLOW_INVALID_CERTIFICATES: bool = False


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int = 6379


class SendGridSettings(BaseSettings):
    SENDGRID_API_KEY: str | None = None
    SMTP_FROM: str


class TwilioSettings(BaseSettings):
    TWILIO_ENABLED: bool = False
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None


class LogSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
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
    AppSettings,
    MongoSettings,
    RedisSettings,
    SendGridSettings,
    TwilioSettings,
    LogSettings,
):
    class Config:
        secrets_dir = "/run/secrets"


settings = Settings()
