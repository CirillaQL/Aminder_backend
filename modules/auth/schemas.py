from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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

class OAuthAccountResponse(BaseModel):
    oauth_name: str
    oauth_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    # Optionally include linked accounts
    oauth_accounts: List[OAuthAccountResponse] = []

    class Config:
        from_attributes = True

class OAuthLogin(BaseModel):
    provider: str  # "google" or "github"
    code_or_token: str # Auth code or Access Token depending on flow