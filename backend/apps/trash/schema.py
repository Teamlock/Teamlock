from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from bson import ObjectId
from datetime import datetime
from apps.secret.schema import GlobalSecretSchema

class TrashSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    workspace : PyObjectId
    created_at : datetime
    secrets : list[GlobalSecretSchema] = []

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }

class TrashStats(BaseModel):
    login: int = 0
    server: int = 0
    phone: int = 0
    bank: int = 0