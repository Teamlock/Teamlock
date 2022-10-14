from apps.secret.models import Secret
from apps.trash.models import Trash
from apps.folder.models import Folder
from apps.workspace.models import Workspace
from fastapi.exceptions import HTTPException

class SecretUtils:
    @classmethod
    def move_to_trash(cls,secret: Secret, trash: Trash) -> None:
        """Move to trash a secret

        Args:
            secret (Secret): secret to move
            trash (Trash): trash of the workspace
        """
        secret.folder = None
        secret.trash = trash.pk
        secret.save()

    @classmethod
    def restore(cls, secret: Secret, workspace: Workspace, user) -> None:
        """Restore a secret which was in the trash

        Args:
            secret (Secret): secret to restore
            workspace (Workspace): workspace where was the secret
            user (LoggedUser): user who restore the secret
        """
        #if there is no folders to put the secret in, we raise an Exception
        folders = Folder.objects(workspace=workspace)
        if (len(folders) == 0):
            # we create a default folder
            restore_folder = Folder(
                name="Restore",
                icon="mdi-file-restore",
                created_by=user.in_db,
                workspace=workspace,
                password_policy=None
            ).save()
            secret.folder = restore_folder 
        else:
            #we put the secret in the first folder of the workspace
            secret.folder = folders[0]

        secret.trash = None
        secret.save()
