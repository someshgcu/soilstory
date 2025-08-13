from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    uid: str
    
class UserUpdate(BaseModel):
    """Schema for updating a user"""
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserInDB(UserBase):
    """Schema for user as stored in the database"""
    uid: str
    created_at: datetime
    updated_at: datetime
    preferences: Optional[Dict[str, Any]] = None
    
class UserResponse(UserBase):
    """Schema for user response"""
    uid: str
    created_at: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None