from pydantic import BaseModel
from pydantic import EmailStr

from uuid import UUID


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    is_verified: bool
    role: str

    class Config:
        from_attributes = True