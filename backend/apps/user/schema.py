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

from pydantic import BaseModel, Field, validator, ValidationError
from toolkits.paginate import PaginationResponseSchema
from toolkits.bson import PyObjectId
from datetime import datetime
from bson import ObjectId


class AdminUserSchema(BaseModel):
    email: str


class OTPSchema(BaseModel):
    enabled: bool = False
    need_configure: bool | None


class UpdateUserSchema(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @validator("confirm_password")
    def password_must_match(cls, v, values):
        if v != values["new_password"]:
            raise ValidationError("Passwords mismatch")
        return v


class LockUserSchema(BaseModel):
    is_locked: bool


class UpdateAdminUserSchema(BaseModel):
    is_admin: bool


class RecoveryModeSchema(BaseModel):
    enabled: bool


class NotConfigureUserSchema(BaseModel):
    email: str
    otp_image: str | None


class UserSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    first_seen: datetime
    last_seen: datetime | None
    otp: OTPSchema = OTPSchema()
    last_change_pass: datetime
    is_configured: bool = False
    is_admin: bool = False
    is_locked: bool = False
    recovery_enabled: bool = False
    need_change_password: bool = False
    recovery_key_downloaded: bool = False

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class UserProfileSchema(UserSchema):
    public_key: str
    private_key: str



class UserTableSchema(PaginationResponseSchema):
    data: list[UserSchema]
    total_not_configured_users: int = 0
    total_locked_users: int = 0
    total_admin_users: int = 0

    class Config:
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class EditUserSchema(BaseModel):
    email: str
    is_admin: bool = False


class ConfigureUserSchema(BaseModel):
    password: str
    confirm_password: str
    otp_value: str = ""
    
    class Config:
        schema_extra: dict = {
            "example": {
                "password": "Av€ryStr0ngP@5swOrd!",
                "confirm_password": "Av€ryStr0ngP@5swOrd!",
                "otp_value": ""
            }
        }

    @validator("confirm_password")
    def password_must_match(cls, v, values):
        if v != values["password"]:
            raise ValidationError("Passwords mismatch")
        return v


class UserSessionSchema(BaseModel):
    ip_address: str
    date: datetime
    os: str
    user_agent: str
    country: str = ""
    city: str = ""

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True


class ConfiguredUsers(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str

    class Config:
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class UserSessionTableSchema(PaginationResponseSchema):
    data: list[UserSessionSchema]

    class Config:
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }