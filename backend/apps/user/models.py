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

from datetime import datetime
import mongoengine
import json


class OTP(mongoengine.EmbeddedDocument):
    enabled = mongoengine.BooleanField(default=False)
    secret = mongoengine.StringField(default="")
    need_configure = mongoengine.BooleanField(default=False)


class User(mongoengine.Document):
    email = mongoengine.EmailField(unique=True)
    password = mongoengine.StringField()
    encrypted_password = mongoengine.StringField(default="")
    recovery_key_downloaded = mongoengine.BooleanField(default=False)

    public_key = mongoengine.StringField()
    private_key = mongoengine.StringField()

    remember_key = mongoengine.ListField(mongoengine.StringField())
    otp = mongoengine.EmbeddedDocumentField(OTP)

    last_change_pass = mongoengine.DateField(default=datetime.utcnow)
    last_passwords = mongoengine.ListField(mongoengine.StringField())
    is_configured = mongoengine.BooleanField(default=False)
    is_locked = mongoengine.BooleanField(default=False)
    is_admin = mongoengine.BooleanField(default=False)

    known_ip_addresses = mongoengine.ListField(mongoengine.StringField(), default=[])

    first_seen = mongoengine.DateTimeField(default=datetime.utcnow)
    last_seen = mongoengine.DateTimeField(default=None, null=True)

    recovery_enabled = mongoengine.BooleanField(default=False)

    def encrypt_password_for_current_session(self, password: str, key: str) -> str:
        from toolkits.crypto import CryptoUtils

        sha512_password: str = CryptoUtils.prepare_password(password)
        encrypted_password: str = CryptoUtils.sym_encrypt(sha512_password, key)

        return json.dumps(encrypted_password)


class UserSession(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    ip_address = mongoengine.StringField()
    date = mongoengine.DateTimeField(default=datetime.utcnow)
    os = mongoengine.StringField()
    user_agent = mongoengine.StringField()
    country = mongoengine.StringField(default="")
    city = mongoengine.StringField(default="")
