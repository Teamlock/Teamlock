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


from settings import settings
from redis import Redis
import logging.config
import logging
import json

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class RedisTools:
    @classmethod
    def __get_redis_client(cls) -> Redis:
        try:
            return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        except Exception as err:
            logger.critical("Can't connect to REDIS")
            logger.critical(err, exc_info=1)

    @classmethod
    def store(cls, key: str, value: str | int, expire: int = 0) -> None:
        redis_cli: Redis = cls.__get_redis_client()

        if isinstance(value, str):
            value = bytes(value, "utf-8")

        redis_cli.set(key, value)

        if expire:
            redis_cli.expire(key, expire)

    @classmethod
    def retreive(cls, key: str) -> dict | int:
        redis_cli: Redis = cls.__get_redis_client()
        data = redis_cli.get(key)

        if not data:
            return False

        try:
            return json.loads(data.decode("utf-8"))
        except ValueError:
            return data

    @classmethod
    def delete(cls, key: str) -> None:
        redis_cli: Redis = cls.__get_redis_client()
        redis_cli.delete(key)
