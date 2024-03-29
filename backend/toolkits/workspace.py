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

from apps.secret.schema import SecretListValueSchema, SecretValueSchema
from apps.secret.models import Login, SecretListValue, SecretValue
from apps.config.schema import PasswordPolicySchema
from apps.workspace.schema import EditShareSchema
from apps.config.models import PasswordPolicy
from apps.workspace.models import Workspace
from apps.folder.schema import FolderSchema
from fastapi.exceptions import HTTPException
from fastapi import status, BackgroundTasks
from mongoengine.queryset.visitor import Q
from apps.auth.tools import hash_password
from apps.auth.schema import LoggedUser
from apps.workspace.models import Share
from toolkits.schema import RSASchema

# from pykeepass import create_database
import xml.etree.ElementTree as xml
from apps.folder.models import Folder
from apps.trash.models import Trash
from .const import WHITELIST_RIGHTS
from toolkits.mail import MailUtils
from apps.user.models import User
from .crypto import CryptoUtils
from datetime import datetime
from settings import settings
from toolkits import const
from bson import ObjectId
import logging.config
import pykeepass
import logging
import base64
import json
import os

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")
logger_security = logging.getLogger("security")


class WorkspaceUtils:
    @classmethod
    def get_workspace(
        cls, workspace_id: str | ObjectId, user: LoggedUser
    ) -> list[Workspace, str]:
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
            share = Share.objects(workspace=workspace_id, user=user.in_db).get()

            workspace = share.workspace
            sym_key = share.sym_key
            return workspace, sym_key
        except Share.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

    @classmethod
    def is_owner(cls, workspace: Workspace, user: LoggedUser) -> bool:
        try:
            Share.objects(workspace=workspace, user=user.in_db, is_owner=True).get()
            return True
        except Share.DoesNotExist:
            return False

    @classmethod
    def have_rights(
        cls, workspace: str | Workspace, user: LoggedUser, right: str = "can_write"
    ) -> bool:
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

        if cls.is_owner(workspace, user):
            # User is the owner, he have all rights
            return True

        share = Share.objects(workspace=workspace, user=user.in_db).get()
        if right in WHITELIST_RIGHTS and getattr(share, right):
            return True

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed"
        )

    @classmethod
    def create_workspace(
        cls,
        user: User,
        workspace_name: str,
        workspace_icon: str,
        password_policy: PasswordPolicySchema,
    ) -> str:
        workspace_symkey: str = CryptoUtils.generate_sim()
        encrypted_symkey = CryptoUtils.rsa_encrypt(workspace_symkey, user.public_key)

        if password_policy:
            password_policy = PasswordPolicy(**password_policy.dict())

        workspace = Workspace(
            name=workspace_name, icon=workspace_icon, password_policy=password_policy
        )

        workspace.save()

        Share.objects.create(
            user=user, workspace=workspace, sym_key=encrypted_symkey, is_owner=True
        )

        Trash.objects.create(workspace=workspace)

        Folder.objects.create(
            name="Web", icon="mdi-earth", workspace=workspace, created_by=user
        )

        user.save()
        return str(workspace.pk)

    @classmethod
    def share_workspace(
        cls,
        user: LoggedUser,
        workspace: Workspace,
        share_def: EditShareSchema,
        background_task: BackgroundTasks,
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
        share = Share.objects(workspace=workspace, user=user.in_db).get()
        encrypted_sym_key = share.sym_key

        sym_key: str = CryptoUtils.rsa_decrypt(
            encrypted_sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user),
        )

        for tmp in share_def.users:
            try:
                tmp_user = User.objects(pk=tmp).get()
                encrypted_sym_key = CryptoUtils.rsa_encrypt(
                    sym_key, tmp_user.public_key
                )

                Share.objects.create(
                    can_write=share_def.can_write,
                    can_share=share_def.can_share,
                    can_export=share_def.can_export,
                    can_share_external=share_def.can_share_external,
                    sym_key=encrypted_sym_key,
                    expire_at=share_def.expire_at,
                    workspace=workspace,
                    user=tmp_user,
                )

                # Send email to warn user
                context: dict = {
                    "workspace_name": workspace.name,
                    "shared_by": user.in_db.email,
                }

                background_task.add_task(
                    MailUtils.send_mail,
                    [tmp_user.email],
                    "",
                    "workspace_shared",
                    context,
                )

                logger.info(
                    f"[SHARE][{str(workspace.pk)}][{workspace.name}] Shared by {user.in_db.email} to {user.email}"
                )
            except User.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

    @classmethod
    def encrypt_secret(
        cls, user: LoggedUser, encrypted_sym_key: str, secret_def
    ) -> Login:
        """Encrypt Key information using Workspace Symetric key
        Decrypt Workspace symetric key with user's Private RSA key
        Encrypt all key informations using the symetric key

        Args:
            user (LoggedUser): Current logged user
            encrypted_sym_key (str): Encrypted symetric key
            secret_def: Secret information

        Returns:
            Secret: Encrypted secret schema
        """

        sym_key: str = CryptoUtils.rsa_decrypt(
            encrypted_sym_key,
            user.in_db.private_key,
            CryptoUtils.decrypt_password(user),
        )

        encrypted_secret = const.MAPPING_SECRET[secret_def.secret_type]()
        ignored_fields = [
            "_id",
            "folder",
            "created_at",
            "updated_at",
            "secret_type",
            "folder_name",
            "workspace_name",
            "trash",
        ]

        for property in secret_def.schema()["properties"].keys():
            if property not in ignored_fields:
                property_class = getattr(secret_def, property)

                if isinstance(property_class, SecretValueSchema):
                    value: str = property_class.value
                    if property_class.encrypted:
                        setattr(
                            encrypted_secret,
                            property,
                            SecretValue(
                                encrypted=True,
                                value=CryptoUtils.sym_encrypt(value, sym_key),
                            ),
                        )
                    else:
                        setattr(
                            encrypted_secret,
                            property,
                            SecretValue(encrypted=False, value=value),
                        )
                elif isinstance(property_class, SecretListValueSchema):
                    value: list[str] = property_class.value
                    if property_class.encrypted:
                        tmp = []
                        for val in value:
                            tmp.append(CryptoUtils.sym_encrypt(val, sym_key))

                        setattr(
                            encrypted_secret,
                            property,
                            SecretListValue(encrypted=True, value=tmp),
                        )
                    else:
                        setattr(
                            encrypted_secret,
                            property,
                            SecretListValue(encrypted=False, value=value),
                        )

        return encrypted_secret

    @classmethod
    def decrypt_secret(
        cls, sym_key: str, secret_def, get_protected_fields: bool = False
    ):
        """Decrypt Key information using the workspace symetric key

        Args:
            sym_key (str): Decrypted workspace symetric key
            secret_def: Schema
            get_protected_fields (bool, optional): Decrypt also protected fields. Defaults to False.
            mode: temporary parameter, to migrate over GCM encryption

        Returns:
            SecretSchema: Key Schema
        """

        decrypted_secret = secret_def.copy()
        ignored_fields = [secret_def.Base().protected_fields]
        ignored_fields.extend(
            [
                "_id",
                "folder",
                "created_at",
                "updated_at",
                "created_by",
                "updated_by",
                "secret_type",
                "folder_name",
                "workspace_name",
                "password_last_change",
                "package_name",
                "trash",
            ]
        )

        for property in secret_def.schema()["properties"].keys():
            if property not in ignored_fields:
                property_class = getattr(secret_def, property)
                if isinstance(property_class, SecretValueSchema):
                    value: str = property_class.value
                    if property_class.encrypted:
                        tmp = SecretValueSchema(
                            encrypted=True,
                            value=CryptoUtils.sym_decrypt(value, sym_key),
                        )
                        setattr(decrypted_secret, property, tmp)
                elif isinstance(property_class, SecretListValueSchema):
                    value: list[str] = property_class.value
                    if property_class.encrypted:
                        tmp = []
                        for val in value:
                            tmp.append(CryptoUtils.sym_decrypt(val, sym_key))
                        setattr(
                            decrypted_secret,
                            property,
                            SecretListValueSchema(encrypted=True, value=tmp),
                        )
                    else:
                        setattr(
                            decrypted_secret,
                            property,
                            SecretListValueSchema(encrypted=False, value=value),
                        )

        if get_protected_fields:
            for field in secret_def.Base().protected_fields:
                value: str = getattr(secret_def, field).value
                setattr(
                    decrypted_secret,
                    field,
                    SecretValueSchema(value=CryptoUtils.sym_decrypt(value, sym_key)),
                )

        decrypted_secret.folder = secret_def.folder
        return decrypted_secret

    @classmethod
    def copy_folder_to_other_workspace(
        cls,
        user: LoggedUser,
        to_folder: Folder,
        from_workspace: Workspace,
        to_workspace: Workspace,
        sym_key: str,
    ):
        """Copy an entire folder to an other workspace

        Args:
            user (LoggedUser): Current logged user
            to_folder (Folder): Target folder
            from_workspace (Workspace): From workspace
            to_workspace (Workspace): New workspace
            sym_key (str): Symetric key to decrypt data
        """

        def copy_secrets(from_folder, to_folder):
            for model_ in const.MAPPING_SECRET.values():
                for secret in model_.objects(folder=from_folder):
                    secret_schema = secret.schema()
                    decrypted_secret = cls.decrypt_secret(
                        sym_key, secret_schema, get_protected_fields=True
                    )

                    share = Share.objects(workspace=to_workspace, user=user.in_db).get()

                    encrypted_secret = cls.encrypt_secret(
                        user, share.sym_key, decrypted_secret
                    )

                    encrypted_secret.pk = None
                    encrypted_secret.folder = to_folder
                    encrypted_secret.created_by = user.id
                    encrypted_secret.save()

        def copy_child_folders(old_parent, new_parent):
            childs = Folder.objects(parent=old_parent)
            for child in childs:
                old_id = child.pk
                child.pk = None
                child.parent = new_parent
                child.workspace = to_workspace
                child.save()

                copy_secrets(old_id, child.pk)
                copy_child_folders(old_id, child.pk)

        old_folder_id = to_folder.pk
        to_folder.pk = None
        to_folder.parent = None
        to_folder.workspace = to_workspace
        to_folder.save()

        # Copy folder content
        copy_secrets(old_folder_id, to_folder.pk)

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
        new_password: str,
        background_task: BackgroundTasks,
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
        shares = Share.objects(user=user)

        old_sym_keys = []
        for share in shares:
            sym_key = CryptoUtils.rsa_decrypt(
                share.sym_key, user.private_key, old_password
            )

            old_sym_keys.append({"workspace": share, "sym_key": sym_key})

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

            encrypted_sym_key = CryptoUtils.rsa_encrypt(sym_key, user.public_key)
            objet.sym_key = encrypted_sym_key
            objet.save()

        background_task.add_task(
            MailUtils.send_mail, [user.email], None, "password_change"
        )

    @classmethod
    def recover_account(
        cls,
        user: User,
        sym_key: str,
        new_password: str,
        background_tasks: BackgroundTasks,
    ):
        try:
            decrypted_password: str = CryptoUtils.sym_decrypt(
                user.encrypted_password, base64.b64decode(sym_key)
            )
            cls.update_password(
                user, decrypted_password, new_password, background_tasks
            )
        except Exception as err:
            print(err)
            logger.info(f"Recovery failed for user {user.email}: Invalid Recovery Key")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Recovery Key"
            )

    @classmethod
    def get_folders(
        cls, workspace_id: str | ObjectId, user: LoggedUser
    ) -> list[FolderSchema]:
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
                    **folder.password_policy.to_mongo()
                )

            created_by = None
            if folder.created_by:
                created_by = folder.created_by.pk

            folders.append(
                FolderSchema(
                    id=folder.pk,
                    parent=parent,
                    icon=folder.icon,
                    name=folder.name,
                    created_by=created_by,
                    created_at=folder.created_at,
                    password_policy=password_policy,
                    workspace=workspace.pk,
                )
            )

        return folders

    @classmethod
    def export_workspace(
        cls, workspace_id: str | ObjectId, user: LoggedUser, password: str
    ):
        workspace, sym_key = WorkspaceUtils.get_workspace(workspace_id, user)

        folders: list[FolderSchema] = WorkspaceUtils.get_folders(workspace_id, user)

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key, user.in_db.private_key, CryptoUtils.decrypt_password(user)
        )
        field_name = ["Title", "UserName", "Password", "URL", "Notes"]
        teamlock_field = ["name", "login", "password", "urls", "informations"]

        kp = pykeepass.create_database(
            f"/var/tmp/{workspace.pk}.kdbx", password=password
        )

        def fill_db_from_folder(folder: FolderSchema, current_group=None):
            children = Folder.objects(parent=folder.id)
            if folder is None:
                return

            if current_group is None:
                group = kp.add_group(kp.root_group, folder.name)
            else:
                group = kp.add_group(current_group, folder.name)

            keys = Login.objects(folder=folder.id)
            for key in keys:
                if key.name.value == "":
                    continue

                key_schema = key.schema()
                decrypted_secret = WorkspaceUtils.decrypt_secret(
                    decrypted_sym_key, key_schema, True
                )

                try:
                    kp.add_entry(
                        group,
                        decrypted_secret.name.value,
                        decrypted_secret.login.value,
                        decrypted_secret.password.value,
                        ",".join(decrypted_secret.urls.value),
                        decrypted_secret.informations.value,
                    )
                except Exception as err:
                    if "already exists in" in str(err):
                        kp.add_entry(
                            group,
                            decrypted_secret.name.value + str(key.pk),
                            decrypted_secret.login.value,
                            decrypted_secret.password.value,
                            ",".join(decrypted_secret.urls.value),
                            decrypted_secret.informations.value,
                        )
                    else:
                        logger.critical(err, exc_info=1)

            if len(children) > 0:
                for child in children:
                    fill_db_from_folder(child, group)

        for folder in folders:
            if not folder.parent:
                fill_db_from_folder(folder)

        kp.save()
        # with open(f"/var/tmp/{workspace.pk}.xml", "w") as f:
        #     f.write(kp.xml())

        # base = xml.Element("KeePassFile")
        # meta = xml.SubElement(base, "Meta")
        # xml.SubElement(meta, "DatabaseName").text = workspace.name

        # root = xml.SubElement(base, "Root")
        # root_group = xml.SubElement(root, "Group")
        # xml.SubElement(root_group, "Name").text = workspace.name

        # def fill_db_from_folder(folder: FolderSchema, current_group=None):
        #     children = Folder.objects(parent=folder.id)
        #     if folder != None:
        #         if current_group is not None:
        #             group = xml.SubElement(current_group, "Group")
        #         else:
        #             group = xml.SubElement(root_group, "Group")

        #         xml.SubElement(group, "Name").text = folder.name
        #         keys = Login.objects(folder=folder.id)
        #         for key in keys:
        #             if key.name.value != "":
        #                 key_schema = key.schema()
        #                 decrypted_secret = WorkspaceUtils.decrypt_secret(
        #                     decrypted_sym_key, key_schema, True
        #                 )
        #                 entry = xml.SubElement(group, "Entry")

        #                 for i, value in enumerate(field_name):
        #                     string = xml.SubElement(entry, "String")
        #                     xml.SubElement(string, "Key").text = value

        #                     value = getattr(decrypted_secret, teamlock_field[i])
        #                     if isinstance(value, list):
        #                         value = ",".join(value)

        #                     xml.SubElement(string, "Value").text = getattr(
        #                         decrypted_secret, teamlock_field[i]
        #                     ).value

        #         if len(children) != 0:
        #             for child in children:
        #                 fill_db_from_folder(child, group)

        # for folder in folders:
        #     if not folder.parent:
        #         fill_db_from_folder(folder)

        # xml.ElementTree(base).write(f"/var/tmp/{workspace.pk}.xml")

    @classmethod
    def delete_tmp_file(cls, path):
        if os.path.exists(path):
            os.remove(path)

    @classmethod
    def get_trash_folder(cls, workspace_id: str | ObjectId) -> Trash:
        try:
            return Trash.objects(workspace=workspace_id).get()
        except Trash.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Trash not found"
            )

    @classmethod
    def search(cls, workspace, search, user, category, order="name"):
        workspace, sym_key = cls.get_workspace(workspace, user)
        folders: list[Folder] = Folder.objects(workspace=workspace)

        query: Q = Q(folder__in=folders)

        if search:
            urls_query: Q = Q()
            if "://" in search:
                tmp_list = search.split("://")
                protocol: str = tmp_list[0]

                s = ""
                for index, sub_domain in enumerate(tmp_list[1].split(".")[::-1]):
                    if index == 0:
                        s += sub_domain
                    else:
                        s = f"{sub_domain}.{s}"
                        url = f"{protocol}://{s}"
                        urls_query |= Q(urls__value__icontains=url)
            else:
                urls_query = Q(urls__value__icontains=search)

            name_query: Q = Q(name__value__icontains=search)

            if category == "login":
                login_query = Q(login__value__icontains=search)
                ip_query = Q(ip__value__icontains=search)

                query &= name_query | urls_query | login_query | ip_query

            elif category == "server":
                ip_query = Q(ip__value__icontains=search)
                os_type_query = Q(os_type__value__icontains=search)
                login_query = Q(login__value__icontains=search)

                query &= name_query | ip_query | os_type_query | login_query

            elif category == "bank":
                owner_query = Q(owner__value__icontains=search)
                bank_name_query = Q(bank_name__value__icontains=search)
                iban_query = Q(iban__value__icontains=search)
                bic_query = Q(bic__value__icontains=search)
                card_number_query = Q(card_number__value__icontains=search)

                query &= (
                    name_query
                    | owner_query
                    | bank_name_query
                    | iban_query
                    | bic_query
                    | card_number_query
                )

            elif category == "phone":
                number_query = Q(number__icontains=search)
                query &= name_query | number_query

        model_ = const.MAPPING_SECRET[category]

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key, user.in_db.private_key, CryptoUtils.decrypt_password(user)
        )

        keys: list = []
        for tmp in model_.objects(query).order_by(order):
            schema = tmp.schema()
            tmp = cls.decrypt_secret(decrypted_sym_key, schema)

            tmp.folder_name = Folder.objects(pk=tmp.folder).get().name
            tmp.workspace_name = workspace.name
            keys.append(tmp)

        return keys
