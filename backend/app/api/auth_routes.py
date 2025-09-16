"""
Authentication routes for user management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.services.auth_service import AuthService
from app.services.analytics_service import AnalyticsService

# Create router
auth_router = APIRouter()

# Security scheme
security = HTTPBearer()

# Request/Response models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
    created_at: str

# Service dependencies
def get_auth_service() -> AuthService:
    return AuthService()

def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Get current authenticated user."""
    token = credentials.credentials
    return auth_service.get_current_user(token)

@auth_router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Register a new user."""
    try:
        # In a real application, you would:
        # 1. Check if user already exists
        # 2. Hash the password
        # 3. Store user in database
        # 4. Send verification email
        
        # For demo purposes, we'll create a simple user
        user_id = f"user_{user_data.email.replace('@', '_').replace('.', '_')}"
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        # Create access token
        access_token = auth_service.create_user_token(user_id, user_data.email)
        
        # Track registration
        await analytics_service.track_user_registration(user_id, user_data.email)
        
        return TokenResponse(
            access_token=access_token,
            user_id=user_id,
            email=user_data.email
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@auth_router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Login user and return access token."""
    try:
        # In a real application, you would:
        # 1. Verify user exists
        # 2. Verify password hash
        # 3. Check if account is active
        
        # For demo purposes, we'll accept any valid email/password
        user_id = f"user_{login_data.email.replace('@', '_').replace('.', '_')}"
        
        # Create access token
        access_token = auth_service.create_user_token(user_id, login_data.email)
        
        # Track login
        await analytics_service.track_user_login(user_id, login_data.email)
        
        return TokenResponse(
            access_token=access_token,
            user_id=user_id,
            email=login_data.email
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@auth_router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile."""
    return UserProfile(
        user_id=current_user["user_id"],
        email=current_user["email"],
        full_name=None,  # Would come from database
        created_at="2024-01-01T00:00:00Z"  # Would come from database
    )

@auth_router.post("/logout")
async def logout_user(
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Logout user (invalidate token on client side)."""
    # In a real application, you might:
    # 1. Add token to blacklist
    # 2. Store logout event
    
    await analytics_service.track_user_logout(current_user["user_id"])
    
    return {"message": "Successfully logged out"}
