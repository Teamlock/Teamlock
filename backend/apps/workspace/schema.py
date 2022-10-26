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
along with Teamlock.  If not, see <http://www.gnu.org/licenses>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from apps.config.schema import PasswordPolicySchema
from apps.user.schema import UserSchema
from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from bson import ObjectId
import datetime


class WorkspaceSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    icon: str | None
    created_at: datetime.datetime
    last_change: datetime.datetime
    password_policy: PasswordPolicySchema | None = Field(
        alias="password_policy")
    nb_folders: int | None
    nb_secrets: int | None
    import_in_progress: bool = False

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class EditWorkspaceSchema(BaseModel):
    name: str
    icon: str | None
    password_policy: PasswordPolicySchema | None


class SharedWorkspaceSchema(WorkspaceSchema):
    is_owner: bool = False
    can_write: bool = False
    can_share: bool = False
    can_export: bool = False
    can_share_external: bool = False


class ShareSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    expire_at = datetime.date | None
    can_write: bool = False
    can_share: bool = False
    can_export: bool = False
    can_share_external: bool = False
    shared_by: UserSchema
    workspace: WorkspaceSchema
    user: UserSchema

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class UsersWorkspace(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user: PyObjectId
    expire_at: datetime.date | None
    user_email: str
    is_owner: bool
    can_write: bool
    can_share: bool
    can_export: bool
    can_share_external: bool

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class EditShareSchema(BaseModel):
    expire_at: datetime.date | None
    can_write: bool = False
    can_share: bool = False
    can_export: bool = False
    can_share_external: bool = False
    users: list[PyObjectId]


class UpdateShareSchema(BaseModel):
    can_write: bool = False
    can_share: bool = False
    can_export: bool = False
    can_share_external: bool = False


class ImportXMLFileSchema(BaseModel):
    encrypt_name: bool = False
    encrypt_url: bool = False
    encrypt_login: bool = False
    encrypt_password: bool = True
    encrypt_informations: bool = True
