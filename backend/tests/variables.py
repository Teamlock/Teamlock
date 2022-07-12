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

USERNAME: str = "test@teamlock.io"
PASSWORD: str = "bonsoirdouze"

INSTALL_PARAMS: dict = {
    "config_schema": {
        "rsa_key_size": 2048,
        "enforce_totp": False,
        "password_policy": {
            "length": 8,
            "uppercase": 0,
            "numbers": 0,
            "special": 0
        }
    },
    "admin": {
        "email": USERNAME,
        "password": PASSWORD,
        "confirm_password": PASSWORD
    }
}

LOGIN_PARAMS: dict = {
    "username": USERNAME,
    "password": PASSWORD
}

CREATE_WORKSPACE_PARAMS: dict = {
    "name": "new_workspace",
    "policy": {
        "length": 12,
        "uppercase": 1,
        "numbers": 1,
        "special": 1
    }
}

CREATE_FOLDER_PARAMS: dict = {
    "name": "string",
    "icon": "string",
    "parent": "",
    "workspace_id": None,
    "password_policy": {
        "length": 12,
        "uppercase": 1,
        "numbers": 1,
        "special": 1
    }
}

CREATE_KEY_PARAMS: dict = {
    "name": {
        "encrypted": False,
        "value": "test_key"
    },
    "url": {
        "encrypted": True,
        "value": "teamlock.io"
    },
    "ip": {
        "encrypted": True,
        "value": "10.0.0.0"
    },
    "login": {
        "encrypted": True,
        "value": "login"
    },
    "password": {
        "encrypted": True,
        "value": "AVeryStrongPassword12$"
    },
    "informations": {
        "encrypted": True,
        "value": "None"
    },
    "folder": None
}