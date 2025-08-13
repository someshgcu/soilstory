from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class SoilPhotoBase(BaseModel):
    """Base schema for soil photo entries"""
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    location: Optional[Dict[str, float]] = None  # {"latitude": float, "longitude": float}
    tags: Optional[List[str]] = None

class SoilPhotoCreate(SoilPhotoBase):
    """Schema for creating a new soil photo entry"""
    # No additional fields needed - file will be handled separately
    pass

class SoilPhotoUpdate(SoilPhotoBase):
    """Schema for updating a soil photo entry"""
    # Only allow updating metadata, not the image itself
    pass

class SoilAnalysisResult(BaseModel):
    """Schema for soil analysis results"""
    soil_type: str
    ph_level: float
    nutrients: Dict[str, str]  # e.g., {"nitrogen": "Medium", "phosphorus": "High"}
    organic_matter: str  # e.g., "5%"
    moisture: str  # e.g., "30%"
    health_score: float  # 0-100
    recommendations: List[str]
    suitable_plants: List[str]
    analysis_confidence: str  # e.g., "85%"

class SoilPhotoInDB(SoilPhotoBase):
    """Schema for soil photo entry as stored in the database"""
    id: str
    user_id: str
    image_url: HttpUrl
    image_path: str  # Path in Firebase Storage
    created_at: datetime
    updated_at: datetime
    analysis_results: Optional[SoilAnalysisResult] = None
    story_ids: Optional[List[str]] = None

class SoilPhotoResponse(SoilPhotoBase):
    """Schema for soil photo entry response"""
    id: str
    user_id: str
    image_url: HttpUrl
    created_at: datetime
    updated_at: datetime
    analysis_results: Optional[SoilAnalysisResult] = None
    story_ids: Optional[List[str]] = None

class SoilAnalysisRequest(BaseModel):
    """Schema for requesting soil analysis"""
    soil_photo_id: str
    analysis_preferences: Optional[Dict[str, Any]] = None