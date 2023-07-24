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

from apps.user.schema import UserSchema
from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from apps.user.models import User
from bson import ObjectId


class Login(BaseModel):
    token_type: str = "bearer"
    access_token: str
    remember_key: str | None


class TokenData(BaseModel):
    email: str
    expire: str


class LoggedUser(UserSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    session_key: str | None
    encrypted_password: str | None
    in_db: User | None

    class Config:
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {ObjectId: str}


class RegistrationSchema(BaseModel):
    email: str
