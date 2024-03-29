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

from apps.config.models import PasswordPolicy
from apps.workspace.models import Workspace
from apps.user.models import User
from datetime import datetime
import mongoengine


class Folder(mongoengine.Document):
    name = mongoengine.StringField()
    icon = mongoengine.StringField()
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    password_policy = mongoengine.EmbeddedDocumentField(PasswordPolicy)
    created_by = mongoengine.ReferenceField(
        User, reverse_delete_rule=mongoengine.NULLIFY
    )

    parent = mongoengine.ReferenceField(
        "Folder", null=True, reverse_delete_rule=mongoengine.CASCADE
    )

    workspace = mongoengine.ReferenceField(
        Workspace, reverse_delete_rule=mongoengine.CASCADE
    )
