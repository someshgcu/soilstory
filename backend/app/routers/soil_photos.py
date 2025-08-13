from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form, Query
from typing import Dict, Any, List, Optional
from uuid import uuid4

from app.core.auth import get_current_user
from app.schemas.soil import (
    SoilPhotoCreate, SoilPhotoUpdate, SoilPhotoResponse, 
    SoilAnalysisRequest, SoilAnalysisResult
)
from app.services.db_service import db_service
from app.services.ai_service import ai_service
from app.utils.file_utils import save_upload_file, process_image, extract_image_metadata

router = APIRouter()

@router.post("/soil-photos", response_model=SoilPhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_soil_photo(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload a soil photo and create a new soil entry
    
    Args:
        file: The soil photo file
        title: Optional title for the soil entry
        description: Optional description for the soil entry
        latitude: Optional latitude coordinate
        longitude: Optional longitude coordinate
        tags: Optional comma-separated tags
        current_user: The authenticated user from the token
        
    Returns:
        The created soil photo entry
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Save the file to Firebase Storage
        file_path, public_url = await save_upload_file(file, user_id)
        
        # Extract metadata
        metadata = extract_image_metadata(file)
        
        # Create soil photo entry data
        soil_data = {
            "title": title,
            "description": description,
            "image_url": public_url,
            "image_path": file_path,
            "metadata": metadata,
        }
        
        # Add location if provided
        if latitude is not None and longitude is not None:
            soil_data["location"] = {"latitude": latitude, "longitude": longitude}
        
        # Add tags if provided
        if tags:
            soil_data["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create soil entry in database
        entry_id = await db_service.create_soil_entry(user_id, soil_data)
        
        # Get the created entry
        soil_entry = await db_service.get_soil_entry(entry_id)
        
        return SoilPhotoResponse(**soil_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload soil photo: {str(e)}"
        )

@router.get("/soil-photos", response_model=List[SoilPhotoResponse])
async def get_my_soil_photos(
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all soil photos for the current user
    
    Args:
        limit: Maximum number of entries to return
        current_user: The authenticated user from the token
        
    Returns:
        List of soil photo entries
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get soil entries from database
        entries = await db_service.get_user_soil_entries(user_id, limit)
        
        return [SoilPhotoResponse(**entry) for entry in entries]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get soil photos: {str(e)}"
        )

@router.get("/soil-photos/{entry_id}", response_model=SoilPhotoResponse)
async def get_soil_photo(
    entry_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a soil photo entry by ID
    
    Args:
        entry_id: The ID of the soil entry to get
        current_user: The authenticated user from the token
        
    Returns:
        The soil photo entry
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get soil entry from database
        entry = await db_service.get_soil_entry(entry_id, user_id)
        
        return SoilPhotoResponse(**entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get soil photo: {str(e)}"
        )

@router.put("/soil-photos/{entry_id}", response_model=SoilPhotoResponse)
async def update_soil_photo(
    entry_id: str,
    soil_data: SoilPhotoUpdate = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a soil photo entry
    
    Args:
        entry_id: The ID of the soil entry to update
        soil_data: Updated soil entry data
        current_user: The authenticated user from the token
        
    Returns:
        The updated soil photo entry
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Update soil entry in database
        soil_dict = soil_data.model_dump(exclude_unset=True)
        updated_entry = await db_service.update_soil_entry(entry_id, soil_dict, user_id)
        
        return SoilPhotoResponse(**updated_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update soil photo: {str(e)}"
        )

@router.delete("/soil-photos/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_soil_photo(
    entry_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a soil photo entry
    
    Args:
        entry_id: The ID of the soil entry to delete
        current_user: The authenticated user from the token
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Delete soil entry from database
        await db_service.delete_soil_entry(entry_id, user_id)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete soil photo: {str(e)}"
        )

@router.post("/soil-photos/{entry_id}/analyze", response_model=SoilAnalysisResult)
async def analyze_soil_photo(
    entry_id: str,
    analysis_request: SoilAnalysisRequest = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze a soil photo and return soil health metrics
    
    Args:
        entry_id: The ID of the soil entry to analyze
        analysis_request: Analysis request parameters
        current_user: The authenticated user from the token
        
    Returns:
        Soil analysis results
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get soil entry from database
        entry = await db_service.get_soil_entry(entry_id, user_id)
        
        # Check if analysis already exists
        if entry.get("analysis_results"):
            return SoilAnalysisResult(**entry["analysis_results"])
        
        # Get image URL from entry
        image_url = entry.get("image_url")
        if not image_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Soil entry does not have an image URL"
            )
        
        # Create metadata for analysis
        metadata = {
            "entry_id": entry_id,
            "user_id": user_id,
            "random_seed": hash(entry_id) % 100,  # For deterministic simulation
            **analysis_request.model_dump()
        }
        
        # Analyze soil image
        analysis_results = await ai_service.analyze_soil_image(image_url, metadata)
        
        # Update soil entry with analysis results
        await db_service.update_soil_entry(entry_id, {"analysis_results": analysis_results}, user_id)
        
        return SoilAnalysisResult(**analysis_results)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze soil photo: {str(e)}"
        )