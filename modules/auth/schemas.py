from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    auth_provider: str  # e.g., "email", "google", "github"

    class Config:
        from_attributes = True

class OAuthLogin(BaseModel):
    provider: str  # "google" or "github"
    code_or_token: str # Auth code or Access Token depending on flow
