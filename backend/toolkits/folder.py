from fastapi.exceptions import HTTPException
from apps.folder.models import Folder
from apps.secret.models import Secret
from apps.trash.models import Trash
from toolkits.workspace import WorkspaceUtils
from toolkits.secret import SecretUtils
from toolkits.crypto import CryptoUtils
from toolkits import const
from bson import ObjectId
from fastapi import status


class FolderUtils:
    @classmethod
    def get_children(cls, folder_id: str | ObjectId) -> list[Folder]:
        """Get all the children folder of the folder id

        Args:
            folder_id (str | ObjectId): id of the folder
        """
        children_list: list = []

        def fill_children(id):
            children = Folder.objects(parent=id)
            children_list.extend(children)
            if id and children:
                for child in children:
                    fill_children(child.pk)

        fill_children(folder_id)
        return children_list

    @classmethod
    def move_to_trash(cls, folder: Folder, trash: Trash) -> int:
        """Move a folder to the trash

        Args:
            folder_id (str | ObjectId): id of the folder
            trash (Trash): trash of the workspace
            user (LoggedUser) : user who move the folder
        """

        def search_secret(folder: Folder):
            total_secrets: int = 0
            for cat in const.MAPPING_SECRET:  # get secrets for each category
                model_ = const.MAPPING_SECRET[cat]
                tmp_secrets: list = list(model_.objects(folder=folder))
                total_secrets += len(tmp_secrets)

                for secret in tmp_secrets:
                    SecretUtils.move_to_trash(secret, trash)

            return total_secrets

        total: int = 0
        children = cls.get_children(folder.pk)
        total += search_secret(folder)
        for child in children:
            total += search_secret(child)
            child.delete()

        folder.delete()
        return total

    @classmethod
    def get_root_children(cls, folder_id: str | ObjectId) -> list[Folder]:
        """Get the first children (1st layer) of a folder

        Args:
            folder_id (str | ObjectId): id of the folder
        """
        try:
            return Folder.objects(parent=folder_id)
        except Folder.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
            )

    @classmethod
    def get_secrets(
        cls, folder_id: str | ObjectId, category: str, user
    ) -> list[Secret]:
        """Get all secrets in a folder

        Args:
            folder_id (str | ObjectId): id of the folder
            category (str) category of the secret wanted
            user (LoggedUser): user who want to get the secrets
        """
        try:
            folder: Folder = Folder.objects(pk=folder_id).get()
        except Folder.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
            )

        _, sym_key = WorkspaceUtils.get_workspace(folder.workspace.pk, user)

        model_ = const.MAPPING_SECRET[category]
        tmp_secrets: list = list(model_.objects(folder=folder).order_by("name__value"))
        secrets: list = []

        decrypted_sym_key = CryptoUtils.rsa_decrypt(
            sym_key, user.in_db.private_key, CryptoUtils.decrypt_password(user)
        )

        for tmp in tmp_secrets:
            schema = tmp.schema()
            secrets.append(WorkspaceUtils.decrypt_secret(decrypted_sym_key, schema))
        return secrets
