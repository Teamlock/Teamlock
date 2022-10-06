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

from pydantic import BaseSettings
import dotenv
import pathlib
import os

dotenv.load_dotenv()

path = pathlib.Path(__file__).parent.resolve()

class AppSettings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    APP_URL: str = os.environ["APP_URL"]
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = os.environ.get("PORT", 8000)
    DEBUG: bool = os.environ.get("DEBUG", False)
    DEV_MODE: bool = os.environ.get("DEV_MODE") == True
    TOKEN_EXPIRE: int = os.environ.get("TOKEN_EXPIRE", 7200) # Default: 2 hours
    TOKEN_EXPIRE_BROWSER_EXT: int = os.environ.get("TOKEN_EXPIRE_BROWSER_EXT", 86400) # Default: 1 day
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    MAX_USERS: int = os.environ.get("MAX_USERS", 0)
    VERSION: float = float(os.environ["VERSION"])
    IP_HEADER: str = os.environ.get("IP_HEADER", "X-Forwarded-For")


class MongoSettings(BaseSettings):
    MONGO_HOST: str = os.environ["MONGO_HOST"]
    MONGO_DATABASE: str = os.environ["MONGO_DATABASE"]
    MONGO_USER: str = os.environ.get("MONGO_USER")
    MONGO_PASSWORD: str = os.environ.get("MONGO_PASSWORD")
    MONGO_AUTHSOURCE: str = os.environ.get("MONGO_AUTHSOURCE")
    MONGO_REPLICASET: str = os.environ.get("MONGO_REPLICASET")
    MONGO_TLS: bool = os.environ.get("MONGO_TLS") == True
    MONGO_CA_FILE: str = os.environ.get("MONGO_CA_FILE")
    MONGO_KEY_FILE: str = os.environ.get("MONGO_KEY_FILE")
    MONGO_ALLOW_INVALID_HOSTNAMES: bool = os.environ.get("MONGO_ALLOW_INVALID_HOSTNAMES") == True
    MONGO_ALLOW_INVALID_CERTIFICATES: bool = os.environ.get("MONGO_ALLOW_INVALID_CERTIFICATES") == True


class RedisSettings(BaseSettings):
    REDIS_HOST: str = os.environ["REDIS_HOST"]
    REDIS_PORT: int = os.environ["REDIS_PORT"]


class MailSettings(BaseSettings):
    SMTP_HOST: str = os.environ["SMTP_HOST"]
    SMTP_PORT: str = os.environ["SMTP_PORT"]
    SMTP_AUTH: bool = os.environ.get("SMTP_AUTH") == True
    SMTP_EMAIL: str = os.environ.get("SMTP_EMAIL")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD")
    SMTP_SSL: bool = os.environ.get("SMTP_SSL") == True


class TwilioSettings(BaseSettings):
    TWILIO_ENABLED: bool = os.environ.get("TWILIO_ENABLED") == True
    TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = os.environ.get("TWILIO_PHONE_NUMBER")


class LogSettings(BaseSettings):
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE: str = "/var/log/teamlock/teamlock.log"
    SECURITY_LOG_FILE: str = "/var/log/teamlock/security.log"
    LOGGING_FORMAT = '{"date": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "module":"%(module)s", "line_number": %(lineno)s, "message": "%(message)s"}'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            "verbose": {
                "format": LOGGING_FORMAT,
                "datefmt": "%Y-%m-%dT%H:%M:%S%z"
            },
            "simple": {
                "format": "[%(levelname)s] [<%(name)s>:%(module)s:%(lineno)s] "
                        "%(message)s"
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'debug': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': LOG_FILE,
                'formatter': 'verbose'
            },
            'api': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': LOG_FILE,
                'formatter': 'verbose'
            },
            "security": {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': SECURITY_LOG_FILE,
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'debug': {
                'handlers': ['debug', 'console'],
                'level': LOG_LEVEL
            },
            'api': {
                'handlers': ['api', 'console'],
                'level': LOG_LEVEL
            },
            'security': {
                'handlers': ['security', 'console'],
                'level': LOG_LEVEL
            }
        }
    }


class Settings(
    AppSettings,
    MongoSettings,
    RedisSettings,
    MailSettings,
    TwilioSettings,
    LogSettings
):
    pass


settings = Settings()
