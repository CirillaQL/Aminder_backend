from typing import Optional
import httpx
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from .schemas import UserCreate, UserResponse, UserLogin
from .models import User, OAuthAccount
from .security import get_password_hash, verify_password, create_access_token
from utils.logger import logger

class AuthManager:
    """
    Manages user authentication and registration using SQLAlchemy.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_email(self, user_in: UserCreate) -> UserResponse:
        """Register a new user with email and password."""
        # Check if email exists
        stmt = select(User).where(User.email == user_in.email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(f"Registration failed: Email {user_in.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_in.password)
        
        new_user = User(
            id=user_id,
            email=user_in.email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        logger.info(f"User registered: {user_in.email}")
        return new_user

    async def login_email(self, user_in: UserLogin) -> dict:
        """Authenticate user with email and password and return token."""
        stmt = select(User).where(User.email == user_in.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
            logger.warning(f"Login failed for {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    async def authenticate_google(self, token: str) -> dict:
        """
        Verify Google token and login/register user.
        """
        # 1. Verify token with Google (Mock/Real implementation)
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
        oauth_id = google_data.get("sub") # Google's unique ID for the user
        
        if not email or not oauth_id:
            raise HTTPException(status_code=400, detail="Invalid Google data (email or sub missing)")

        return await self._handle_oauth_login(email, "google", oauth_id, token)

    async def authenticate_github(self, code: str) -> dict:
        """
        Exchange GitHub code for token and login/register user.
        """
        # Placeholder credentials
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
        
        access_token = None
        
        async with httpx.AsyncClient() as client:
            try:
                # response = await client.post(token_url, json=payload, headers=headers)
                # response.raise_for_status()
                # access_token = response.json().get("access_token")
                
                # Mock logic
                access_token = "mock_github_access_token"
                
                # 2. Get User Info
                # user_resp = await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {access_token}"})
                # github_data = user_resp.json()
                
                github_data = {"email": "mock_github@example.com", "id": 123456}

            except Exception as e:
                logger.error(f"GitHub auth failed: {e}")
                raise HTTPException(status_code=400, detail="GitHub authentication failed")

        email = github_data.get("email")
        # GitHub ID is integer, convert to string
        oauth_id = str(github_data.get("id"))
        
        if not email:
             raise HTTPException(status_code=400, detail="Email not found in GitHub account")

        return await self._handle_oauth_login(email, "github", oauth_id, access_token)

    async def _handle_oauth_login(self, email: str, provider: str, oauth_id: str, access_token: str) -> dict:
        """
        Core logic for OAuth login/registration.
        1. Check if OAuthAccount exists.
        2. If not, check if User exists by email.
        3. Link or Create.
        """
        # 1. Check if this OAuth account is already linked
        stmt = select(OAuthAccount).where(
            OAuthAccount.oauth_name == provider,
            OAuthAccount.oauth_id == oauth_id
        )
        result = await self.db.execute(stmt)
        oauth_account = result.scalar_one_or_none()

        user = None

        if oauth_account:
            # Found linked account, get the user
            # We need to load the user. Since we didn't eager load, we can query or assume relationship
            # Let's query User to be safe and ensure it's active
            stmt_user = select(User).where(User.id == oauth_account.user_id)
            result_user = await self.db.execute(stmt_user)
            user = result_user.scalar_one_or_none()
            
            # Optional: Update access token if changed
            if oauth_account.access_token != access_token:
                oauth_account.access_token = access_token
                await self.db.commit()

        else:
            # OAuth account not found.
            # 2. Check if user with this email exists
            stmt_user = select(User).where(User.email == email)
            result_user = await self.db.execute(stmt_user)
            user = result_user.scalar_one_or_none()

            if user:
                # User exists, link new OAuth account
                logger.info(f"Linking new {provider} account to existing user {email}")
                new_oauth = OAuthAccount(
                    user_id=user.id,
                    oauth_name=provider,
                    oauth_id=oauth_id,
                    access_token=access_token
                )
                self.db.add(new_oauth)
                await self.db.commit()
            else:
                # User does not exist, create User AND OAuthAccount
                logger.info(f"Creating new user from {provider}: {email}")
                user_id = str(uuid.uuid4())
                user = User(
                    id=user_id,
                    email=email,
                    hashed_password=None, # No password
                    is_active=True
                )
                self.db.add(user)
                # Flush to ensure user.id is ready (though we set it manually)
                await self.db.flush() 
                
                new_oauth = OAuthAccount(
                    user_id=user_id,
                    oauth_name=provider,
                    oauth_id=oauth_id,
                    access_token=access_token
                )
                self.db.add(new_oauth)
                await self.db.commit()

        if not user:
             raise HTTPException(status_code=500, detail="Failed to retrieve or create user")
            
        if not user.is_active:
             raise HTTPException(status_code=400, detail="User is inactive")

        # Generate JWT
        access_token_jwt = create_access_token(data={"sub": user.email, "user_id": user.id})
        return {"access_token": access_token_jwt, "token_type": "bearer"}