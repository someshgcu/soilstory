from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from app.core.firebase import firebase_auth, verify_token
from app.core.auth import get_current_user
from app.schemas.user import UserCreate, UserResponse, UserInDB
from app.services.db_service import db_service

router = APIRouter()
security = HTTPBearer()

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate = Body(...)):
    """Register a new user with Firebase Auth and create a user profile in Firestore
    
    This endpoint expects that the user has already been created in Firebase Auth
    and is now registering their profile in our application database.
    
    Args:
        user_data: User registration data including Firebase UID
        
    Returns:
        The created user profile
    """
    try:
        # Check if user already exists in our database
        try:
            existing_user = await db_service.get_user_profile(user_data.uid)
            if existing_user:
                return UserResponse(**existing_user)
        except HTTPException as e:
            if e.status_code != status.HTTP_404_NOT_FOUND:
                raise
        
        # Create user profile in Firestore
        user_dict = user_data.model_dump()
        user_id = await db_service.create_user_profile(user_data.uid, user_dict)
        
        # Get the created user profile
        user_profile = await db_service.get_user_profile(user_id)
        
        return UserResponse(**user_profile)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )

@router.post("/auth/verify-token", response_model=Dict[str, Any])
async def verify_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify a Firebase ID token and return the decoded token
    
    Args:
        credentials: The HTTP Authorization header containing the Firebase ID token
        
    Returns:
        The decoded token containing user information
    """
    try:
        token = credentials.credentials
        decoded_token = verify_token(token)
        return {"valid": True, "user": decoded_token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get the current user's profile
    
    Args:
        current_user: The authenticated user from the token
        
    Returns:
        The user's profile
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user profile from database
        user_profile = await db_service.get_user_profile(user_id)
        
        return UserResponse(**user_profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )