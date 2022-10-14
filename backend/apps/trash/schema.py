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

__author__ = "Romain Lefebvre"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from bson import ObjectId
from datetime import datetime
from apps.secret.schema import GlobalSecretSchema
from toolkits.paginate import PaginationResponseSchema

class TrashStats(BaseModel):
    login: int = 0
    server: int = 0
    phone: int = 0
    bank: int = 0

class TrashTableSchema(PaginationResponseSchema):
    data: list[GlobalSecretSchema]
    class Config:
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }