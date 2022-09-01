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

from apps.key.schema import CreateKeySchema, KeySchema, KeyValueSchema, TMPKeySchema
from apps.config.schema import PasswordPolicySchema
from apps.workspace.schema import EditShareSchema
from apps.config.models import PasswordPolicy
from apps.workspace.models import Workspace
from apps.folder.schema import FolderSchema
from fastapi.exceptions import HTTPException
from mongoengine.queryset.visitor import Q
from apps.key.models import Key, KeyValue
from apps.auth.tools import hash_password
from apps.auth.schema import LoggedUser
from apps.workspace.models import Share
from .const import WHITELIST_RIGHTS
from toolkits.schema import RSASchema
from pykeepass import create_database
from apps.folder.models import Folder
from toolkits.mail import MailUtils
from apps.user.models import User
from .crypto import CryptoUtils
from datetime import datetime
from settings import settings
from bson import ObjectId
from fastapi import status
import logging.config
import logging
import base64
import json
import os

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")
logger_security = logging.getLogger("security")

FULL_KEY_ATTRS: tuple = (
    "name", "url", "ip", "login",
    "informations", "password"
)
KEY_ATTRS: tuple = ("name", "url", "ip", "login", "informations")


class WorkspaceUtils:
    @classmethod
    def get_workspace(cls, workspace_id: str | ObjectId, user: LoggedUser) -> list[Workspace, str]:
        """Return the workspace and the associated symmetric key
        If the workspace is a shared workspace, the symmetric key is stored in the Share schema
        instead of the workspace schema

        Args:
            workspace_id (str | ObjectId): Workspace
            user (LoggedUser): User informations

        Raises:
            HTTPException: Workspace not found

        Returns:
            list[Workspace, str]: Workspace object, symmetric key
        """
        try:
            workspace = Workspace.objects(
                pk=workspace_id, owner=user.in_db
            ).get()
            sym_key: str = workspace.sym_key
        except Workspace.DoesNotExist:
            try:
                share = Share.objects(
                    workspace=workspace_id, user=user.in_db
                ).get()

                workspace = share.workspace
                sym_key: str = share.sym_key
            except Share.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workspace not found"
                )

        return workspace, sym_key

    @classmethod
    def have_rights(cls, workspace: str | Workspace, user: LoggedUser, right: str="can_write") -> bool:
        """Check if the user has the correct rights on the workspace

        Args:
            workspace (str | Workspace): Workspace
            user (LoggedUser): User information
            right (str): the right you want to check

        Raises:
            HTTPException: Not allowed

        Returns:
            bool: User has right or not
        """
        if not isinstance(workspace, Workspace):
            workspace, _ = cls.get_workspace(workspace, user)

        if workspace.owner == user.in_db:
            # User is the owner, he have all rights
            return True

        share = Share.objects(workspace=workspace, user=user.in_db).get()
        if right in WHITELIST_RIGHTS and getattr(share, right):
            return True

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed"
        )

    @classmethod
    def create_workspace(
        cls,
        user: User,
        workspace_name: str,
        workspace_icon: str,
        password_policy: PasswordPolicySchema
    ) -> str:
        workspace_symkey: str = CryptoUtils.generate_sim()
        encrypted_symkey = CryptoUtils.rsa_encrypt(
            workspace_symkey, user.public_key)

        if password_policy:
            password_policy = PasswordPolicy(**password_policy.dict())

        workspace = Workspace(
            owner=user,
            name=workspace_name,
            icon=workspace_icon,
            sym_key=encrypted_symkey,
            password_policy=password_policy
        )

        workspace.save()

        Folder.objects.create(
            name="Trash",
            icon="mdi-delete",
            created_by=user,
            is_trash=True,
            workspace=workspace
        )


        Folder.objects.create(
            name="Web",
            icon="mdi-earth",
            workspace=workspace,
            created_by=user
        )

        user.save()
        return str(workspace.pk)


    @classmethod
    def share_workspace(
        cls,
        user: LoggedUser,
        workspace: Workspace,
        share_def: EditShareSchema
    ) -> None:
        """Share a workspace to an other user
            Will encrypt the worskapce symetric key with the user public RSA key

        Args:
            user (LoggedUser): Current logged user
            workspace (Workspace): Workspace to share
            share_def (EditShareSchema): Share informations (user & rights)

        Raises:
            HTTPException: Raise error if user does not exists
        """
        sym_key: str = CryptoUtils.rsa_decrypt(
            workspace.sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        for tmp in share_def.users:
            try:
                tmp_user = User.objects(pk=tmp).get()
                encrypted_sym_key = CryptoUtils.rsa_encrypt(
                    sym_key, tmp_user.public_key)

                Share.objects.create(
                    can_write=share_def.can_write,
                    can_share=share_def.can_share,
                    can_export=share_def.can_export,
                    can_share_external=share_def.can_share_external,
                    sym_key=encrypted_sym_key,
                    expire_at=share_def.expire_at,
                    workspace=workspace,
                    user=tmp_user
                )

                # Send email to warn user
                context: dict = {
                    "workspace_name": workspace.name,
                    "shared_by": user.in_db.email
                }
                MailUtils.send_mail([tmp_user.email], "", "workspace_shared", context)

                logger.info(
                    f"[SHARE][{str(workspace.pk)}][{workspace.name}] Shared by {user.in_db.email} to {user.email}"
                )
            except User.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

    @classmethod
    def encrypt_key(
        cls,
        user: LoggedUser,
        encrypted_sym_key: str,
        key_def: CreateKeySchema,
        mode: str = "GCM"
    ) -> Key:
        """Encrypt Key information using Workspace Symetric key
        Decrypt Workspace symetric key with user's Private RSA key
        Encrypt all key informations using the symetric key

        Args:
            user (LoggedUser): Current logged user
            encrypted_sym_key (str): Encrypted symetric key
            key_def (CreateKeySchema): Key information

        Returns:
            Key: Encrypted key schema
        """

        sym_key: str = CryptoUtils.rsa_decrypt(
            encrypted_sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        encrypted_key: Key = Key()

        for attr in FULL_KEY_ATTRS:
            value: str = getattr(key_def, attr).value
            if getattr(key_def, attr).encrypted:
                setattr(encrypted_key, attr, KeyValue(
                    encrypted=True,
                    value=CryptoUtils.sym_encrypt(value, sym_key, mode)
                ))
            else:
                setattr(encrypted_key, attr, KeyValue(
                    encrypted=False,
                    value=value
                ))

        return encrypted_key

    @classmethod
    def decrypt_key(
        cls,
        sym_key: str,
        key_def: KeySchema,
        get_password: bool = False,
        mode: str = "GCM"
    ) -> KeySchema:
        """Decrypt Key information using the workspace symetric key

        Args:
            sym_key (str): Decrypted workspace symetric key
            key_def (KeySchema): Key schema
            get_password (bool, optional): Decrypt also the password. Defaults to False.
            mode: temporary parameter, to migrate over GCM encryption

        Returns:
            KeySchema: Key Schema
        """

        decrypted_key: KeySchema = KeySchema(
            id=key_def.id,
            created_at=key_def.created_at,
            updated_at=key_def.updated_at
        )

        for attr in KEY_ATTRS:
            value: str = getattr(key_def, attr).value
            if getattr(key_def, attr).encrypted:
                tmp = KeyValueSchema(
                    encrypted=True,
                    value=CryptoUtils.sym_decrypt(value, sym_key, mode)
                )
                setattr(decrypted_key, attr, tmp)
            else:
                tmp = KeyValueSchema(
                    encrypted=False,
                    value=value
                )
                setattr(decrypted_key, attr, tmp)

        if get_password:
            decrypted_key.password = KeyValueSchema(
                value=CryptoUtils.sym_decrypt(key_def.password.value, sym_key, mode)
            )

        decrypted_key.folder = key_def.folder
        return decrypted_key

    @classmethod
    def copy_folder_to_other_workspace(
        cls,
        user: LoggedUser,
        to_folder: Folder,
        from_workspace: Workspace,
        to_workspace: Workspace,
        sym_key: str
    ):
        """Copy an entire folder to an other workspace

        Args:
            user (LoggedUser): Current logged user
            to_folder (Folder): Target folder
            from_workspace (Workspace): From workspace
            to_workspace (Workspace): New workspace
            sym_key (str): Symetric key to decrypt data
        """
        def copy_keys(from_folder, to_folder):
            for key in Key.objects(folder=from_folder):
                decrypted_key = cls.decrypt_key(
                    sym_key,
                    KeySchema(**key.to_mongo()),
                    get_password=True
                )

                encrypted_key = cls.encrypt_key(
                    user, to_workspace.sym_key, decrypted_key)

                encrypted_key.pk = None
                encrypted_key.folder = to_folder
                encrypted_key.created_by = user.id
                encrypted_key.save()

        def copy_child_folders(old_parent, new_parent):
            childs = Folder.objects(parent=old_parent)
            for child in childs:
                old_id = child.pk
                child.pk = None
                child.parent = new_parent
                child.workspace = to_workspace
                child.save()

                copy_keys(old_id, child.pk)
                copy_child_folders(old_id, child.pk)

        old_folder_id = to_folder.pk
        to_folder.pk = None
        to_folder.parent = None
        to_folder.workspace = to_workspace
        to_folder.save()

        # Copy folder content
        copy_keys(old_folder_id, to_folder.pk)

        # Copy child folders
        copy_child_folders(old_folder_id, to_folder.pk)
        logger.info(
            f"Folder {to_folder.name} copied from Workspace {from_workspace.name} to {to_workspace.name}"
        )

    @classmethod
    def update_password(
        cls,
        user: User,
        old_password: str,
        new_password: str
    ):
        """Update password for an user
        With the new password, we generate new RSA Private & Public Key
        Then we need to decrypt all workspaces symetric key with the old private key
        And then encrypt with the new public key

        Args:
            user (User): Current user
            old_password (str): Old password
            new_password (str): New password
        """
        workspaces = Workspace.objects(owner=user)
        shares = Share.objects(user=user)

        old_sym_keys = []
        for workspace in workspaces:
            sym_key = CryptoUtils.rsa_decrypt(
                workspace.sym_key,
                user.private_key,
                old_password
            )

            old_sym_keys.append({
                "workspace": workspace,
                "sym_key": sym_key
            })

        for share in shares:
            sym_key = CryptoUtils.rsa_decrypt(
                share.sym_key,
                user.private_key,
                old_password
            )

            old_sym_keys.append({
                "workspace": share,
                "sym_key": sym_key
            })

        # Generate new RSA Keys:
        rsa_pubpriv: RSASchema = CryptoUtils.generate_rsa_keys(new_password)
        user.private_key = rsa_pubpriv.privkey
        user.public_key = rsa_pubpriv.pubkey
        user.last_passwords.append(user.password)

        if len(user.last_passwords) > 5:
            # We store only the last 5 password
            user.last_passwords = user.last_passwords[1:]

        user.password = hash_password(new_password)
        user.encrypted_password = ""
        user.recovery_key_downloaded = False
        user.last_change_pass = datetime.utcnow()
        user.save()

        for keys in old_sym_keys:
            objet = keys["workspace"]
            sym_key = keys["sym_key"]

            encrypted_sym_key = CryptoUtils.rsa_encrypt(
                sym_key, user.public_key
            )
            objet.sym_key = encrypted_sym_key
            objet.save()
         
        MailUtils.send_mail([user.email], None, "password_change")

    @classmethod
    def migrate_workspace(cls, user: LoggedUser, password: str, workspace: Workspace):
        """Migrate Workspace encryption from CBC to GCM"""
        folders = Folder.objects(workspace=workspace)

        sym_key = CryptoUtils.rsa_decrypt(
            workspace.sym_key,
            user.in_db.private_key,
            password
        )

        for key in Key.objects(folder__in=folders):
            key_schema = KeySchema(**key.to_mongo())
            decrypted_key_schema = cls.decrypt_key(sym_key, key_schema, get_password=True, mode="CBC")
            encrypted_key = cls.encrypt_key(user, workspace.sym_key, decrypted_key_schema)
            encrypted_key.pk = key.pk
            encrypted_key.save()
        
        logger.info(f"[WORKSPACE][{workspace.name}] migrated to GCM encryption")
        workspace.migrated = True
        workspace.save()

    @classmethod
    def recover_account(cls, user: User, sym_key: str, new_password: str):
        try:
            decrypted_password: str = CryptoUtils.sym_decrypt(
                user.encrypted_password,
                base64.b64decode(sym_key)
            )
            cls.update_password(user, decrypted_password, new_password)
        except Exception:
            logger.info(
                f"Recovery failed for user {user.email}: Invalid Recovery Key"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Recovery Key"
            )

    @classmethod
    def get_folders(cls, workspace_id: str | ObjectId, user: LoggedUser) -> list[FolderSchema]:
        workspace, _ = cls.get_workspace(workspace_id, user)
        folders: list = []

        query: Q = Q(workspace=workspace.pk)
        for folder in Folder.objects(query).order_by("name"):
            parent = None
            if folder.parent:
                parent = folder.parent.pk

            password_policy = None
            if folder.password_policy:
                password_policy = PasswordPolicySchema(
                    **folder.password_policy.to_mongo())

            folders.append(FolderSchema(
                id=folder.pk,
                parent=parent,
                icon=folder.icon,
                name=folder.name,
                is_trash=folder.is_trash, 
                in_trash=folder.in_trash,  
                created_by=folder.created_by.pk,
                created_at=folder.created_at,
                password_policy=password_policy,
                workspace=workspace.pk
            ))

        return folders

    @classmethod
    def export_workspace(cls, workspace_id: str | ObjectId, user: LoggedUser) -> None:
        workspace, sym_key = WorkspaceUtils.get_workspace(workspace_id, user)
        kp = create_database(
            f"/var/tmp/{workspace.name}.kdbx", password=None, keyfile=None, transformed_key=None)
        del workspace
        folders: list[FolderSchema] = WorkspaceUtils.get_folders(
            workspace_id, user)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        def fill_database(folder, current_group):
            children = Folder.objects(parent=folder.id)
            if folder != None:
                group = kp.add_group(current_group, folder.name)
                # encrypted keys
                keys = Key.objects(folder=folder.id)
                for key in keys:
                    if key.name.value != "":  # error because there were various entries with name== ""
                        key_schema = TMPKeySchema(**key.to_mongo())
                        decrypted_key: KeySchema = WorkspaceUtils.decrypt_key(
                            decrypted_sym_key,
                            key_schema,
                            get_password=True
                        )
                        kp.add_entry(
                            group, title=decrypted_key.name.value,
                            username=decrypted_key.login.value,
                            password=decrypted_key.password.value,
                            url=decrypted_key.url.value,
                            notes=decrypted_key.informations.value
                        )

                if children != None:
                    for child in children:
                        fill_database(child, group)

        for folder in folders:
            if not folder.parent:
                fill_database(folder, kp.root_group)
        kp.save()

    @classmethod
    def delete_tmp_file(cls,path):
        if os.path.exists(path):
            os.remove(path)
    
    @classmethod
    def get_trash_folder(cls,workspace_id : str | ObjectId) -> Folder:
        try:
            return Folder.objects(is_trash=True,workspace=workspace_id).get()
        except Folder.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
    
    @classmethod
    def search(cls, workspace, search, user):
        workspace, sym_key = cls.get_workspace(workspace, user)
        cls.have_rights(workspace, user)
        folders: list[Folder] = Folder.objects(workspace=workspace)

        in_folder_query: Q =Q(folder__in=folders)
        name_query: Q = Q(name__value__icontains=search)
        url_query: Q = Q(url__value__icontains=search)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user)
        )

        keys: list = []
        for tmp in Key.objects(in_folder_query & (name_query | url_query)):
            tmp: TMPKeySchema = TMPKeySchema(**tmp.to_mongo())
            keys.append(cls.decrypt_key(decrypted_sym_key, tmp))

        return keys
