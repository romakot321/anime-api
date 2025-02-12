from pydantic import BaseModel


class ExternalImageGeneration(BaseModel):
    id: str
    is_finished: bool
    is_invalid: bool
    image_url: str | None = None
    comment: str | None = None


class ExternalVideoGeneration(BaseModel):
    id: str
    user_id: str
    is_finished: bool
    is_invalid: bool

