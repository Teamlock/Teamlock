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

from toolkits.mongo import connect_to_database
from datetime import datetime
from settings import settings


def migrate_0_2(db):
    """Remove template_registration field on config model"""
    db.config.update({}, {"$unset": {"template_registration": 1}})

def migrate_0_3(db):
    """Add first_seen field on users"""
    db.user.update_many({}, {"$set": {"first_seen": datetime.utcnow()}})

def migrate_0_52(db):
    """Remove Favorite Workspace in user"""
    db.user.update_many({}, {"$unset": {"favorite_workspace": 1}})

def migrate_0_6(db):
    """Create trashs Folders"""
    db.config.update({}, {
        "$set": {
            "twilio": {
                "enabled": False,
                "account_sid": "",
                "auth_token": "",
                "phone_number": ""
            }
        }
    })

    workspaces = db.workspace.find()
    for workspace in workspaces:
        try:
            print(f"Creating Trash folder for Workspace { workspace['name'] }")
            db.folder.insert_one({
                "name": "Trash",
                "icon": "mdi-delete",
                "created_by": workspace["owner"],
                "is_trash": True,
                "workspace": workspace["_id"]
            })
        except KeyError:
            db.workspace.remove({"_id": workspace["_id"]})

def migrate_0_7(db):
    db.config.update({}, {"$unset": {"enforce_totp": 1}})



class Migrations:
    MIGRATIONS_DICT: dict = {
        0.2: migrate_0_2,
        0.3: migrate_0_3,
        0.52: migrate_0_52,
        0.6: migrate_0_6,
        0.7: migrate_0_7
    }

    def __init__(self):
        self.db = connect_to_database(as_pymongo=True)
        config = self.db.config.find_one()

        if config:
            self.STORED_VERSION: float = config.get("version", 0.1)
            self.CURRENT_VERSION: float = settings.VERSION

            if self.CURRENT_VERSION > self.STORED_VERSION:
                print("New version, chech if any migrations is required")
                self.execute_migration()
            else:
                print("No migrations to apply")

            self.db.config.update({}, {"$set": {"version": self.CURRENT_VERSION}})
        
    def execute_migration(self):
        for key in self.MIGRATIONS_DICT.keys():
            if key <= self.CURRENT_VERSION and key > self.STORED_VERSION:
                print(f"Executing migration for version {key}")
                self.MIGRATIONS_DICT[key](self.db)
