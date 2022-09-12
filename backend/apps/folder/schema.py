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

from apps.config.schema import PasswordPolicySchema
from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from datetime import datetime
from bson import ObjectId


class EditFolderSchema(BaseModel):
    name: str
    icon: str
    parent: str | None
    workspace: PyObjectId = Field(default_factory=PyObjectId)
    password_policy: PasswordPolicySchema | None
    moved: bool = False


class FolderSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    icon: str
    is_trash: bool
    in_trash: bool
    parent: PyObjectId | None = None
    created_at: datetime
    created_by: PyObjectId = Field(default_factory=PyObjectId)
    password_policy: PasswordPolicySchema | None
    workspace: PyObjectId = Field(default_factory=PyObjectId)

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class FolderStats(BaseModel):
    login: int = 0
    server: int = 0
    phone: int = 0
    bank: int = 0
