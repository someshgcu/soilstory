from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any

from app.core.auth import get_current_user
from app.schemas.user import UserUpdate, UserResponse
from app.services.db_service import db_service

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
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
                detail="Invalid user ID in token"
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

@router.put("/users/me", response_model=UserResponse)
async def update_my_profile(user_data: UserUpdate = Body(...), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Update the current user's profile
    
    Args:
        user_data: Updated user profile data
        current_user: The authenticated user from the token
        
    Returns:
        The updated user profile
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Update user profile in database
        user_dict = user_data.model_dump(exclude_unset=True)
        updated_profile = await db_service.update_user_profile(user_id, user_dict)
        
        return UserResponse(**updated_profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get a user's profile by ID
    
    Args:
        user_id: The ID of the user to get
        current_user: The authenticated user from the token
        
    Returns:
        The user's profile
    """
    try:
        # Get user profile from database
        user_profile = await db_service.get_user_profile(user_id)
        
        # Remove sensitive information if not the user themselves
        if current_user.get("uid") != user_id:
            # Filter out any sensitive fields if needed
            pass
        
        return UserResponse(**user_profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )