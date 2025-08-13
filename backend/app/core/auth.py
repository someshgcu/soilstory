from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.firebase import verify_token, get_user_by_uid
from typing import Optional, Dict, Any

# Security scheme for Swagger UI
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user from Firebase token
    
    Args:
        credentials: The HTTP Authorization header containing the Firebase ID token
        
    Returns:
        Dict containing user information from the decoded token
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        token = credentials.credentials
        # Verify the token with Firebase
        decoded_token = verify_token(token)
        
        # Get additional user info if needed
        user_id = decoded_token.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # You can fetch more user details from Firebase if needed
        # user_details = get_user_by_uid(user_id)
        
        # Return the decoded token which contains user info
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    Dependency to get the current user if authenticated, but doesn't require authentication
    
    Args:
        authorization: The HTTP Authorization header containing the Firebase ID token
        
    Returns:
        Dict containing user information or None if not authenticated
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
        
    try:
        token = authorization.replace("Bearer ", "")
        decoded_token = verify_token(token)
        return decoded_token
    except Exception:
        return None

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to ensure the current user has admin privileges
    
    Args:
        current_user: The authenticated user from get_current_user dependency
        
    Returns:
        Dict containing user information if the user is an admin
        
    Raises:
        HTTPException: If the user is not an admin
    """
    # Check if user has admin claim
    if not current_user.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user