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

from apps.folder.models import Folder
from apps.trash.models import Trash
from datetime import datetime
from . import schema
import mongoengine


class SecretValue(mongoengine.EmbeddedDocument):
    encrypted = mongoengine.BooleanField(default=True)
    value = mongoengine.StringField()


class Secret(mongoengine.Document):
    name = mongoengine.EmbeddedDocumentField(SecretValue)
    informations = mongoengine.EmbeddedDocumentField(SecretValue)

    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    updated_at = mongoengine.DateTimeField(default=datetime.utcnow)

    folder = mongoengine.ReferenceField(
        Folder,
        reverse_delete_rule=mongoengine.CASCADE
    )

    trash = mongoengine.ReferenceField(Trash, reverse_delete_rule=mongoengine.CASCADE)

    meta = {
        "allow_inheritance": True
    }


class Login(Secret):
    url = mongoengine.EmbeddedDocumentField(SecretValue)
    ip = mongoengine.EmbeddedDocumentField(SecretValue)
    login = mongoengine.EmbeddedDocumentField(SecretValue)
    password = mongoengine.EmbeddedDocumentField(SecretValue)
    
    def schema(self):
        data = self.to_mongo()
        data["secret_type"] = "login"
        return schema.LoginSchema(**data)


class Bank(Secret):
    owner = mongoengine.EmbeddedDocumentField(SecretValue)
    bank_name = mongoengine.EmbeddedDocumentField(SecretValue)
    iban = mongoengine.EmbeddedDocumentField(SecretValue)
    bic = mongoengine.EmbeddedDocumentField(SecretValue)
    card_number = mongoengine.EmbeddedDocumentField(SecretValue)
    expiration_date = mongoengine.EmbeddedDocumentField(SecretValue)
    cvc = mongoengine.EmbeddedDocumentField(SecretValue)

    def schema(self):
        data = self.to_mongo()
        data["secret_type"] = "bank"
        return schema.BankSchema(**data)


class Server(Secret):
    ip = mongoengine.EmbeddedDocumentField(SecretValue)
    os_type = mongoengine.EmbeddedDocumentField(SecretValue)
    login = mongoengine.EmbeddedDocumentField(SecretValue)
    password = mongoengine.EmbeddedDocumentField(SecretValue)

    def schema(self):
        data = self.to_mongo()
        data["secret_type"] = "server"
        return schema.ServerSchema(**data)


class Phone(Secret):
    number = mongoengine.EmbeddedDocumentField(SecretValue)
    pin_code = mongoengine.EmbeddedDocumentField(SecretValue)
    puk_code = mongoengine.EmbeddedDocumentField(SecretValue)

    def schema(self):
        data = self.to_mongo()
        data["secret_type"] = "phone"
        return schema.PhoneSchema(**data)
    