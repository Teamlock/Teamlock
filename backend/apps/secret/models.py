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
from apps.user.models import User
from datetime import datetime
from . import schema
import mongoengine


class SecretValue(mongoengine.EmbeddedDocument):
    encrypted = mongoengine.BooleanField(default=True)
    value = mongoengine.StringField()


class SecretListValue(mongoengine.EmbeddedDocument):
    encrypted = mongoengine.BooleanField(default=True)
    value = mongoengine.ListField(mongoengine.StringField())


class Secret(mongoengine.Document):
    name = mongoengine.EmbeddedDocumentField(SecretValue)
    informations = mongoengine.EmbeddedDocumentField(SecretValue)

    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    updated_at = mongoengine.DateTimeField(default=datetime.utcnow)

    created_by = mongoengine.ReferenceField(
        User,
        null=True,
        reverse_delete_rule=mongoengine.NULLIFY
    )

    updated_by = mongoengine.ReferenceField(
        User,
        null=True,
        reverse_delete_rule=mongoengine.NULLIFY
    )

    password_last_change = mongoengine.DateTimeField(default=datetime.utcnow)

    folder = mongoengine.ReferenceField(
        Folder,
        reverse_delete_rule=mongoengine.CASCADE
    )

    meta = {
        "allow_inheritance": True
    }

    def schema(self, secret_type):
        created_by = None
        if self.created_by:
            created_by = self.created_by.email

        updated_by = None
        if self.updated_by:
            updated_by = self.updated_by.email

        return self.Config.schema(
            id=self.pk,
            name=schema.SecretValueSchema(**self.name.to_mongo()),
            secret_type=secret_type,
            informations=schema.SecretValueSchema(**self.informations.to_mongo()),
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=created_by,
            updated_by=updated_by,
            password_last_change=self.password_last_change,
            folder=str(self.folder.pk)
        )
    
    def check_changes(self, last, new):
        pass


class Login(Secret):
    urls = mongoengine.EmbeddedDocumentField(SecretListValue)
    ip = mongoengine.EmbeddedDocumentField(SecretValue)
    login = mongoengine.EmbeddedDocumentField(SecretValue)
    password = mongoengine.EmbeddedDocumentField(SecretValue)

    class Config:
        schema = schema.LoginSchema
    
    def schema(self):
        sch = super().schema("login")
        sch.urls = schema.SecretListValueSchema(**self.urls.to_mongo())
        sch.ip = schema.SecretValueSchema(**self.ip.to_mongo())
        sch.login = schema.SecretValueSchema(**self.login.to_mongo())
        sch.password = schema.SecretValueSchema(**self.password.to_mongo())
        return sch
    
    def check_changes(self, last, new):
        if last.password.value != new.password.value:
            self.password_last_change = datetime.utcnow()


class Bank(Secret):
    owner = mongoengine.EmbeddedDocumentField(SecretValue)
    bank_name = mongoengine.EmbeddedDocumentField(SecretValue)
    iban = mongoengine.EmbeddedDocumentField(SecretValue)
    bic = mongoengine.EmbeddedDocumentField(SecretValue)
    card_number = mongoengine.EmbeddedDocumentField(SecretValue)
    expiration_date = mongoengine.EmbeddedDocumentField(SecretValue)
    cvc = mongoengine.EmbeddedDocumentField(SecretValue)

    class Config:
        schema = schema.BankSchema
        
    def schema(self):
        sch = super().schema("bank")
        sch.owner = schema.SecretValueSchema(**self.owner.to_mongo())
        sch.bank_name = schema.SecretValueSchema(**self.bank_name.to_mongo())
        sch.iban = schema.SecretValueSchema(**self.iban.to_mongo())
        sch.bic = schema.SecretValueSchema(**self.bic.to_mongo())
        sch.card_number = schema.SecretValueSchema(**self.card_number.to_mongo())
        sch.expiration_date = schema.SecretValueSchema(**self.expiration_date.to_mongo())
        sch.cvc = schema.SecretValueSchema(**self.cvc.to_mongo())
        return sch


class Server(Secret):
    ip = mongoengine.EmbeddedDocumentField(SecretValue)
    os_type = mongoengine.EmbeddedDocumentField(SecretValue)
    login = mongoengine.EmbeddedDocumentField(SecretValue)
    password = mongoengine.EmbeddedDocumentField(SecretValue)

    class Config:
        schema = schema.ServerSchema

    def schema(self):
        sch = super().schema("server")
        sch.ip = schema.SecretValueSchema(**self.ip.to_mongo())
        sch.os_type = schema.SecretValueSchema(**self.os_type.to_mongo())
        sch.login = schema.SecretValueSchema(**self.login.to_mongo())
        sch.password = schema.SecretValueSchema(**self.password.to_mongo())
    
    def check_changes(self, last, new):
        if last.password.value != new.password.value:
            self.password_last_change = datetime.utcnow()


class Phone(Secret):
    number = mongoengine.EmbeddedDocumentField(SecretValue)
    pin_code = mongoengine.EmbeddedDocumentField(SecretValue)
    puk_code = mongoengine.EmbeddedDocumentField(SecretValue)

    class Config:
        schema = schema.PhoneSchema

    def schema(self):
        sch = super().schema("phoen")
        sch.number = schema.SecretValueSchema(**self.number.to_mongo())
        sch.pin_code = schema.SecretValueSchema(**self.pin_code.to_mongo())
        sch.puk_code = schema.SecretValueSchema(**self.puk_code.to_mongo())
        return sch
    