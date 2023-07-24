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

from pydantic import BaseModel
from datetime import datetime
from settings import settings
import logging.config
import logging

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class PaginationParamsSchema(BaseModel):
    search: str = ""
    sort: str | None
    page: int = 1
    per_page: int = 10
    search: str | None


class UserPaginationSchema(PaginationParamsSchema):
    adminUsers: bool = False
    lockedUsers: bool = False
    notConfiguredUsers: bool = False


class HistoryPaginationParamsSchema(PaginationParamsSchema):
    date_from: datetime
    date_to: datetime
    users: list[str]
    workspaces: list[str]


class PaginationResponseSchema(BaseModel):
    start: int
    to: int
    total: int
    current_page: int
    last_pages: int


def get_order(sort) -> dict:
    order_dir: dict = {"desc": -1, "asc": 1}

    sort_field, order = sort.split("|")

    return {"$sort": {sort_field: order_dir.get(order, -1)}}
