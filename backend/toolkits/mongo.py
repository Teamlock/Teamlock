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

from pymongo.read_preferences import ReadPreference
from pymongo import MongoClient
from mongoengine import connect
from settings import settings

def connect_to_database(
    database_name: str =settings.MONGO_DATABASE,
    as_pymongo: bool=False
) -> MongoClient | None:

    params: dict = {
        "host": settings.MONGO_HOST,
    }

    if settings.MONGO_USER:
        auth_database_key: str = "authSource" if as_pymongo else "authentication_source"
        params.update({
            "username": settings.MONGO_USER,
            "password": settings.MONGO_PASSWORD,
            auth_database_key: settings.MONGO_AUTHSOURCE
        })

    if settings.MONGO_REPLICASET:
        params.update({
            "replicaSet": settings.MONGO_REPLICASET,
            "read_preference": ReadPreference.PRIMARY_PREFERRED
        })

    if settings.MONGO_TLS:
        params.update({
            "tls": True,
            "tlsCAFile": settings.MONGO_CA_FILE,
            "tlsCertificateKeyFile": settings.MONGO_KEY_FILE,
            "tlsAllowInvalidHostnames": settings.MONGO_ALLOW_INVALID_HOSTNAMES,
            "tlsAllowInvalidCertificates": settings.MONGO_ALLOW_INVALID_CERTIFICATES
        })

    # Connect to Database
    if not as_pymongo:
        params["alias"] = "default"
        connect(database_name, **params)
    else:
        return MongoClient(**params)[database_name]
