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

from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from typing import Literal, Union
from datetime import datetime
from bson import ObjectId


class SecretValueSchema(BaseModel):
    encrypted: bool = True
    value: str = ""


class SecretListValueSchema(BaseModel):
    encrypted: bool = True
    value: list[str] = []


class BaseSecretSchema(BaseModel):
    name: SecretValueSchema = SecretValueSchema()
    informations: SecretValueSchema = SecretValueSchema()
    folder: PyObjectId = Field(default_factory=PyObjectId)


class GlobalSecretSchema(BaseSecretSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime
    folder_name: str = ""
    workspace_name: str = ""

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }


class BaseLoginSchema(BaseModel):
    urls: SecretListValueSchema = SecretListValueSchema()
    ip: SecretValueSchema = SecretValueSchema()
    login: SecretValueSchema = SecretValueSchema()
    password: SecretValueSchema = SecretValueSchema()

    class Base:
        protected_fields: tuple = ("password",)
        policy_field: tuple = ("password",)


class BaseServerSchema(BaseModel):
    ip: SecretValueSchema = SecretValueSchema()
    os_type: SecretValueSchema = SecretValueSchema()
    login: SecretValueSchema = SecretValueSchema()
    password: SecretValueSchema = SecretValueSchema()

    class Base:
        protected_fields: tuple = ("password",)
        policy_field: tuple = ("password",)


class BaseBankSchema(BaseModel):
    owner: SecretValueSchema = SecretValueSchema()
    bank_name: SecretValueSchema = SecretValueSchema()
    iban: SecretValueSchema = SecretValueSchema()
    bic: SecretValueSchema = SecretValueSchema()
    card_number: SecretValueSchema = SecretValueSchema()
    expiration_date: SecretValueSchema = SecretValueSchema()
    cvc: SecretValueSchema = SecretValueSchema()

    class Base:
        protected_fields: tuple = ("iban", "bic", "card_number", "expiration_date", "cvc")
        policy_field: tuple = ()


class BasePhoneSchema(BaseModel):
    number: SecretValueSchema = SecretValueSchema()
    pin_code: SecretValueSchema = SecretValueSchema()
    puk_code: SecretValueSchema = SecretValueSchema()

    class Base:
        protected_fields: tuple = ("pin_code", "puk_code")
        policy_field: tuple = ()


class LoginSchema(GlobalSecretSchema, BaseLoginSchema):
    secret_type: Literal["login"]


class CreateLoginSchema(BaseSecretSchema, BaseLoginSchema):
    secret_type: Literal["login"]


class ServerSchema(GlobalSecretSchema, BaseServerSchema):
    secret_type: Literal["server"]


class CreateServerSchema(BaseSecretSchema, BaseServerSchema):
    secret_type: Literal["server"]


class BankSchema(GlobalSecretSchema, BaseBankSchema):
    secret_type: Literal["bank"]


class CreateBankSchema(BaseSecretSchema, BaseBankSchema):
    secret_type: Literal["bank"]


class PhoneSchema(GlobalSecretSchema, BasePhoneSchema):
    secret_type: Literal["phone"]


class CreatePhoneSchema(BaseSecretSchema, BasePhoneSchema):
    secret_type: Literal["phone"]


class CreateSecretSchema(BaseModel):
    secret: Union[
        CreateLoginSchema,
        CreateServerSchema,
        CreateBankSchema,
        CreatePhoneSchema
    ] = Field(..., discriminator="secret_type")


class GetSecretSchema(BaseModel):
    __root__: Union[
        LoginSchema,
        ServerSchema,
        PhoneSchema,
        BankSchema
    ] = Field(..., discriminator="secret_type")
    
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }
