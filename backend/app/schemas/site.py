from pydantic import BaseModel, Field

class SiteCreateSchema(BaseModel):
    project_id: int
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude must be between -180 and 180")
    area_sq_meters: float = Field(..., gt=0.0, description="Area must be a positive number greater than 0")

    class Config:
        from_attributes = True