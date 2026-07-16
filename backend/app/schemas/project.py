from pydantic import BaseModel, Field
from typing import Optional

class ProjectCreateSchema(BaseModel):
    # Field(...) means it is strictly required
    project_name: str = Field(..., min_length=1, description="Project name cannot be empty")
    description: Optional[str] = None
    state: str = Field(..., min_length=1, description="State/Location cannot be empty")
    
    # Boundary validation for coordinate points
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude must be between -180 and 180")

    class Config:
        # Permits your API to read SQLAlchemy objects directly when returning data
        from_attributes = True