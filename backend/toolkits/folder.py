from fastapi.exceptions import HTTPException
from apps.folder.models import Folder
from bson import ObjectId
from fastapi import status

class FolderUtils:
    @classmethod
    def get_children(cls,folder_id: str | ObjectId) -> list[Folder]:
        """Get all the children folder of the folder id 

        Args:
            folder_id (str | ObjectId): id of the folder
        """ 
        children_list : list = []
        def fill_children(id):
            children = Folder.objects(parent=id)
            children_list.extend(children)
            if id and children:
                for child in children:
                    fill_children(child.pk)
        fill_children(folder_id)
        return children_list

    @classmethod
    def move_to_trash(cls,folder: Folder,to_trash: bool = True):
        """Move to trash or restore a folder and its children

        Args:
            folder_id (str | ObjectId): id of the folder
            to_trash (bool): specify if we put the folders in the trash or not
        """ 
        children = cls.get_children(folder.pk)
        folder.in_trash = to_trash
        for child in children:
            child.in_trash = to_trash
            child.save()

    @classmethod
    def restore(cls,folder:Folder):
        """Restore a folder from the trash (wrapper of move_to_trash)

        Args:
            folder_id (str | ObjectId): id of the folder
        """ 
        cls.move_to_trash(folder,to_trash=False)

    @classmethod
    def get_root_children(cls,folder_id: str | ObjectId) -> list[Folder]:
        """Get the first children (1st layer) of a folder

        Args:
            folder_id (str | ObjectId): id of the folder
        """ 
        try:
            return Folder.objects(parent=folder_id)
        except Folder.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
        
        
                
