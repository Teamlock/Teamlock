from pydantic import BaseModel, Field
from toolkits.bson import PyObjectId
from bson import ObjectId
from datetime import datetime

class TrashSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    workspace : PyObjectId
    created_at : datetime
    secrets : list[PyObjectId] = []

    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True
        json_encoders: dict = {
            ObjectId: str
        }