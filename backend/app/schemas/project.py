from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    project_name: str = Field(..., min_length=1)
    description: str
    state: str

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)