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

from .schema import ConfigSchema
from settings import settings
import mongoengine


class PasswordPolicy(mongoengine.EmbeddedDocument):
    length = mongoengine.IntField(default=12)
    uppercase = mongoengine.IntField(default=1)
    numbers = mongoengine.IntField(default=1)
    special = mongoengine.IntField(default=1)



class Config(mongoengine.Document):
    version = mongoengine.FloatField(default=settings.VERSION)
    rsa_key_size = mongoengine.IntField(default=4096)
    password_duration = mongoengine.IntField(default=100)
    password_policy = mongoengine.EmbeddedDocumentField(PasswordPolicy)
    allow_self_registration = mongoengine.BooleanField(default=False)
    allowed_email_addresses = mongoengine.ListField(mongoengine.StringField())

    def to_schema(self):
        return ConfigSchema(**self.to_mongo())
