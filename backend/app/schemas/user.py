from pydantic import BaseModel, EmailStr
from typing import List

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_name: str = "Planner" # Default role on registration

class UserOut(UserBase):
    id: int
    is_active: bool
    roles: List[str]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str = None
