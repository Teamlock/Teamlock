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

from toolkits.mongo import connect_to_database
from apps.secret.models import Login
from datetime import datetime
from settings import settings


def migrate_1_0(db):
    config = db.config.find_one()
    if config.get("enforce_totp"):
        db.pro_config.insert_one({"enforce_totp": True})

    db.config.update({}, {"$unset": {"enforce_totp": 1}})


def migrate_1_1(db):
    db.workspace.update({}, {"$unset": {"migrated": 1}}, multi=True)

    keys = db.key.find()
    connect_to_database()

    new_keys: list = []
    for key in keys:
        del key["_id"]
        new_keys.append(Login(**key))

    Login.objects.insert(new_keys)
    db.key.drop()


def migrate_1_12(db):
    db.workspace.update({}, {"$unset": {"migrated": 1}}, multi=True)
    # Rename key collection
    db.key.rename("secret")

    # Apply cls on Secret
    db.secret.update({}, {"$set": {"_cls": "Secret.Login"}}, multi=True)


def migrate_1_15(db):
    secrets = db.secret.find({"_cls": "Secret.Login"})
    for secret in secrets:
        url = secret["url"]
        value = []
        if url["value"]:
            value.append(url["value"])

        db.secret.update(
            {"_id": secret["_id"]},
            {"$set": {"urls": {"encrypted": url["encrypted"], "value": value}}},
        )

    db.secret.update({"_cls": "Secret.Login"}, {"$unset": {"url": 1}}, multi=True)

    # Add a trash for each workspace
    for workspace in db.workspace.find():
        trash = db.trash.find_one({"workspace": workspace["_id"]})
        if not trash:
            trash = db.trash.insert_one(
                {"workspace": workspace["_id"], "created_at": datetime.utcnow()}
            )

            trash_id = trash.inserted_id
        else:
            trash_id = trash["_id"]

        # Put all the secrets that were in the previous trash into the new one
        for folder in db.folder.find({"$or": [{"in_trash": True}, {"is_trash": True}]}):
            db.secret.update_many(
                {"folder": folder["_id"]}, {"$set": {"trash": trash_id, "folder": None}}
            )

        # Delete the trash and all the folders which were in the trash
        db.folder.delete_many({"$or": [{"in_trash": True}, {"is_trash": True}]})

    # We remove the is_trash & in_trash fields in each folder
    db.folder.update_many({}, {"$unset": {"is_trash": "", "in_trash": ""}})


def migrate_1_154(db):
    workspaces = db.workspace.find()
    for workspace in workspaces:
        try:
            db.share.insert_one(
                {
                    "is_owner": True,
                    "expire_at": None,
                    "can_write": True,
                    "can_share": True,
                    "can_export": True,
                    "can_share_external": True,
                    "sym_key": workspace["sym_key"],
                    "workspace": workspace["_id"],
                    "user": workspace["owner"],
                }
            )

            db.workspace.update(
                {"_id": workspace["_id"]}, {"$unset": {"owner": True, "sym_key": True}}
            )
        except KeyError:
            # Workspace already migrated
            pass

    db.history.update_many({}, {"$unset": {"workspace_owner": True}})


class Migrations:
    MIGRATIONS_DICT: dict = {
        1.0: migrate_1_0,
        1.1: migrate_1_1,
        1.12: migrate_1_12,
        1.15: migrate_1_15,
        1.154: migrate_1_154,
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
