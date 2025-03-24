from enum import Enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict, model_validator
from app.db.tables import TaskStatus
import json


class TaskSchema(BaseModel):
    id: UUID
    error: str | None = None
    status: TaskStatus = TaskStatus.queued
    result_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ImageSize(Enum):
    square_hd = "square_hd"
    square = "square"
    portrait_4_3 = "portrait_4_3"
    portrait_16_9 = "portrait_16_9"
    landscape_4_3 = "landscape_4_3"
    landscape_16_9 = "landscape_16_9"


class TaskImageCreateSchema(BaseModel):
    prompt: str
    user_id: str
    app_bundle: str
    aspect_ratio: ImageSize
    model_id: UUID | None = None


class TaskVideoCreateSchema(BaseModel):
    user_id: str
    app_bundle: str
    model_id: UUID | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

