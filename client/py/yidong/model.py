from pydantic import BaseModel


class ResourceUploadResponse(BaseModel):
    id: str


class ResourceBase(BaseModel):
    id: str
    mime: str
    name: str = ""
    uploaded_at: str
    created_at: str | None = None
    updated_at: str | None = None
