import mongoengine
from apps.workspace.models import Workspace
from datetime import datetime

class Trash(mongoengine.Document):
    workspace = mongoengine.ReferenceField(
        Workspace,
        reverse_delete_rule=mongoengine.CASCADE
    )
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
