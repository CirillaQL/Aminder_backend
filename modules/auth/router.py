from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from .schemas import UserCreate, UserLogin, UserResponse, Token, OAuthLogin
from .manager import AuthManager

router = APIRouter(prefix="/auth", tags=["Auth"])

async def get_auth_manager(db: AsyncSession = Depends(get_db)) -> AuthManager:
    """Dependency to get AuthManager with active DB session."""
    return AuthManager(db)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, 
    manager: AuthManager = Depends(get_auth_manager)
):
    """
    Register a new user with email and password.
    """
    return await manager.register_email(user_in)

@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin, 
    manager: AuthManager = Depends(get_auth_manager)
):
    """
    Login with email and password.
    """
    return await manager.login_email(user_in)

@router.post("/login/google", response_model=Token)
async def login_google(
    data: OAuthLogin, 
    manager: AuthManager = Depends(get_auth_manager)
):
    """
    Login or Register using Google ID Token.
    Expects 'code_or_token' to be the Google ID Token.
    """
    return await manager.authenticate_google(data.code_or_token)

@router.post("/login/github", response_model=Token)
async def login_github(
    data: OAuthLogin, 
    manager: AuthManager = Depends(get_auth_manager)
):
    """
    Login or Register using GitHub Authorization Code.
    Expects 'code_or_token' to be the GitHub auth code.
    """
    return await manager.authenticate_github(data.code_or_token)
