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
from datetime import datetime
import mongoengine


class KeyValue(mongoengine.EmbeddedDocument):
    encrypted = mongoengine.BooleanField(default=True)
    value = mongoengine.StringField()


class Key(mongoengine.Document):
    name = mongoengine.EmbeddedDocumentField(KeyValue)
    url = mongoengine.EmbeddedDocumentField(KeyValue)
    ip = mongoengine.EmbeddedDocumentField(KeyValue)
    login = mongoengine.EmbeddedDocumentField(KeyValue)
    password = mongoengine.EmbeddedDocumentField(KeyValue)
    informations = mongoengine.EmbeddedDocumentField(KeyValue)

    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    updated_at = mongoengine.DateTimeField(default=datetime.utcnow)

    folder = mongoengine.ReferenceField(
        Folder,
        reverse_delete_rule=mongoengine.CASCADE
    )
