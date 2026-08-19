from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.auth.models import UserRole


class UserRegisterSchema(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)
    organization_id: Optional[str] = Field("1001", max_length=50)
    workspace_mode: Optional[str] = Field("create", max_length=20)  # "create" or "join"
    role: Optional[UserRole] = UserRole.ENERGY_PLANNER


class UserLoginSchema(BaseModel):
    username_or_email: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)
    organization_id: Optional[str] = Field(None, max_length=50)


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)
    organization_id: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=300)


class UserRoleUpdateSchema(BaseModel):
    role: UserRole


class UserResponseSchema(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    organization: Optional[str]
    organization_id: str = "1001"
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: int
    username: str
    full_name: Optional[str] = None
    organization: Optional[str] = None
    organization_id: str = "1001"