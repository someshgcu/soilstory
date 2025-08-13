from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import Dict, Any, List, Optional

from app.core.auth import get_current_user
from app.schemas.story import StoryCreate, StoryUpdate, StoryResponse, StoryGenerationRequest
from app.services.db_service import db_service
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def generate_story(
    story_request: StoryGenerationRequest = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate a story based on soil analysis results
    
    Args:
        story_request: Story generation request parameters
        current_user: The authenticated user from the token
        
    Returns:
        The generated story
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get soil entry from database
        entry_id = story_request.soil_entry_id
        entry = await db_service.get_soil_entry(entry_id, user_id)
        
        # Check if entry has analysis results
        analysis_results = entry.get("analysis_results")
        if not analysis_results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Soil entry does not have analysis results. Please analyze the soil first."
            )
        
        # Generate story
        story_content = await ai_service.generate_story(analysis_results, story_request.preferences)
        
        # Create story title from the first line if it starts with #
        title = None
        content_lines = story_content.split('\n')
        if content_lines and content_lines[0].startswith('#'):
            title = content_lines[0].lstrip('#').strip()
        
        # Create story data
        story_data = {
            "title": title or "The Story of Your Soil",
            "content": story_content,
            "metadata": {
                "preferences": story_request.preferences,
                "analysis_results": analysis_results
            },
            "soil_entry_id": entry_id
        }
        
        # Create story in database
        story_id = await db_service.create_story(user_id, entry_id, story_data)
        
        # Get the created story
        story = await db_service.get_story(story_id)
        
        # Update soil entry with story ID
        story_ids = entry.get("story_ids", [])
        if not story_ids:
            story_ids = []
        story_ids.append(story_id)
        await db_service.update_soil_entry(entry_id, {"story_ids": story_ids}, user_id)
        
        return StoryResponse(**story)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate story: {str(e)}"
        )

@router.get("/stories", response_model=List[StoryResponse])
async def get_my_stories(
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all stories for the current user
    
    Args:
        limit: Maximum number of stories to return
        current_user: The authenticated user from the token
        
    Returns:
        List of stories
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get stories from database
        stories = await db_service.get_user_stories(user_id, limit)
        
        return [StoryResponse(**story) for story in stories]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stories: {str(e)}"
        )

@router.get("/soil-photos/{entry_id}/stories", response_model=List[StoryResponse])
async def get_stories_for_soil_entry(
    entry_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all stories for a soil entry
    
    Args:
        entry_id: The ID of the soil entry
        current_user: The authenticated user from the token
        
    Returns:
        List of stories
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get stories from database
        stories = await db_service.get_stories_for_entry(entry_id, user_id)
        
        return [StoryResponse(**story) for story in stories]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stories: {str(e)}"
        )

@router.get("/stories/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a story by ID
    
    Args:
        story_id: The ID of the story to get
        current_user: The authenticated user from the token
        
    Returns:
        The story
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get story from database
        story = await db_service.get_story(story_id, user_id)
        
        return StoryResponse(**story)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get story: {str(e)}"
        )

@router.put("/stories/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: str,
    story_data: StoryUpdate = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a story
    
    Args:
        story_id: The ID of the story to update
        story_data: Updated story data
        current_user: The authenticated user from the token
        
    Returns:
        The updated story
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        # Get existing story to check authorization
        existing_story = await db_service.get_story(story_id, user_id)
        
        # Update story in database
        story_dict = story_data.model_dump(exclude_unset=True)
        
        # Note: We don't allow updating the content field
        if "content" in story_dict:
            del story_dict["content"]
        
        # Update the document
        await db_service.update_document("stories", story_id, story_dict)
        
        # Get the updated story
        updated_story = await db_service.get_story(story_id)
        
        return StoryResponse(**updated_story)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update story: {str(e)}"
        )