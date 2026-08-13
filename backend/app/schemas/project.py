from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True