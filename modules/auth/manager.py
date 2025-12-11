from typing import Optional, Dict
import httpx
import uuid
from fastapi import HTTPException, status
from .schemas import UserCreate, UserResponse, UserLogin
from .security import get_password_hash, verify_password, create_access_token
from utils.logger import logger

# Mock Database for demonstration
# In a real app, this would be a database session/repository
fake_users_db: Dict[str, dict] = {}

class AuthManager:
    """
    Manages user authentication and registration including third-party providers.
    """

    async def register_email(self, user_in: UserCreate) -> UserResponse:
        """Register a new user with email and password."""
        if self._get_user_by_email(user_in.email):
            logger.warning(f"Registration failed: Email {user_in.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_in.password)
        
        user_data = {
            "id": user_id,
            "email": user_in.email,
            "hashed_password": hashed_password,
            "is_active": True,
            "auth_provider": "email"
        }
        
        fake_users_db[user_in.email] = user_data
        logger.info(f"User registered: {user_in.email}")
        
        return UserResponse(**user_data)

    async def login_email(self, user_in: UserLogin) -> dict:
        """Authenticate user with email and password and return token."""
        user = self._get_user_by_email(user_in.email)
        if not user or not verify_password(user_in.password, user["hashed_password"]):
            logger.warning(f"Login failed for {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user["email"]})
        return {"access_token": access_token, "token_type": "bearer"}

    async def authenticate_google(self, token: str) -> dict:
        """
        Verify Google token and login/register user.
        Assumes 'token' is an ID token or Access token that can be validated against Google's UserInfo endpoint.
        """
        google_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(google_url, headers=headers)
                response.raise_for_status()
                google_data = response.json()
            except Exception as e:
                logger.error(f"Google auth failed: {e}")
                raise HTTPException(status_code=400, detail="Invalid Google token")

        email = google_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in Google data")

        return await self._social_login_get_token(email, "google")

    async def authenticate_github(self, code: str) -> dict:
        """
        Exchange GitHub code for token and login/register user.
        """
        # Note: In a real app, CLIENT_ID and CLIENT_SECRET must be configured
        # This is a placeholder structure
        CLIENT_ID = "YOUR_GITHUB_CLIENT_ID" 
        CLIENT_SECRET = "YOUR_GITHUB_CLIENT_SECRET"
        
        # 1. Exchange code for access token
        token_url = "https://github.com/login/oauth/access_token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code
        }
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient() as client:
            try:
                # This call will fail without real credentials, handling gracefully for structure
                # response = await client.post(token_url, json=payload, headers=headers)
                # response.raise_for_status()
                # access_token = response.json().get("access_token")
                
                # Mocking for the sake of the class structure without real creds
                access_token = "mock_github_access_token" 
                
                # 2. Get User Info
                user_url = "https://api.github.com/user"
                # user_resp = await client.get(user_url, headers={"Authorization": f"Bearer {access_token}"})
                # user_data = user_resp.json()
                
                # Mock email
                email = "mock_github@example.com" 
                
            except Exception as e:
                logger.error(f"GitHub auth failed: {e}")
                raise HTTPException(status_code=400, detail="GitHub authentication failed")

        return await self._social_login_get_token(email, "github")

    async def _social_login_get_token(self, email: str, provider: str) -> dict:
        """Helper to find or create a user from social login and return a JWT."""
        user = self._get_user_by_email(email)
        
        if not user:
            # Auto-register
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "email": email,
                "hashed_password": "", # No password for social users
                "is_active": True,
                "auth_provider": provider
            }
            fake_users_db[email] = user_data
            logger.info(f"User auto-registered via {provider}: {email}")
        
        access_token = create_access_token(data={"sub": email})
        return {"access_token": access_token, "token_type": "bearer"}

    def _get_user_by_email(self, email: str) -> Optional[dict]:
        return fake_users_db.get(email)

auth_manager = AuthManager()
