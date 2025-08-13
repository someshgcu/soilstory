from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from app.core.firebase import (
    get_document, add_document, update_document, 
    delete_document, query_collection
)
from fastapi import HTTPException, status

class DatabaseService:
    """Service for handling database operations"""
    
    @staticmethod
    async def create_user_profile(user_id: str, user_data: Dict[str, Any]) -> str:
        """Create a new user profile in the database
        
        Args:
            user_id: Firebase user ID
            user_data: User profile data
            
        Returns:
            User ID of the created profile
        """
        try:
            # Add timestamp
            user_data["created_at"] = datetime.utcnow().isoformat()
            user_data["updated_at"] = user_data["created_at"]
            
            # Add the document with the user_id as the document ID
            add_document("users", user_data, user_id)
            return user_id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user profile: {str(e)}"
            )
    
    @staticmethod
    async def get_user_profile(user_id: str) -> Dict[str, Any]:
        """Get a user profile from the database
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            User profile data
            
        Raises:
            HTTPException: If user profile not found
        """
        user_data = get_document("users", user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return user_data
    
    @staticmethod
    async def update_user_profile(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user profile in the database
        
        Args:
            user_id: Firebase user ID
            user_data: Updated user profile data
            
        Returns:
            Updated user profile data
            
        Raises:
            HTTPException: If update fails
        """
        try:
            # Add updated timestamp
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update the document
            success = update_document("users", user_id, user_data)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user profile"
                )
            
            # Get the updated profile
            updated_profile = await DatabaseService.get_user_profile(user_id)
            return updated_profile
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user profile: {str(e)}"
            )
    
    @staticmethod
    async def create_soil_entry(user_id: str, soil_data: Dict[str, Any]) -> str:
        """Create a new soil entry in the database
        
        Args:
            user_id: Firebase user ID
            soil_data: Soil entry data including image URL, location, etc.
            
        Returns:
            ID of the created soil entry
        """
        try:
            # Add user ID and timestamps
            soil_data["user_id"] = user_id
            soil_data["created_at"] = datetime.utcnow().isoformat()
            soil_data["updated_at"] = soil_data["created_at"]
            
            # Add the document
            entry_id = add_document("soil_entries", soil_data)
            return entry_id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create soil entry: {str(e)}"
            )
    
    @staticmethod
    async def get_soil_entry(entry_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a soil entry from the database
        
        Args:
            entry_id: Soil entry ID
            user_id: Optional user ID for authorization check
            
        Returns:
            Soil entry data
            
        Raises:
            HTTPException: If soil entry not found or user not authorized
        """
        soil_data = get_document("soil_entries", entry_id)
        if not soil_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Soil entry not found"
            )
        
        # Check if the user is authorized to access this entry
        if user_id and soil_data.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this soil entry"
            )
        
        return soil_data
    
    @staticmethod
    async def get_user_soil_entries(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all soil entries for a user
        
        Args:
            user_id: Firebase user ID
            limit: Maximum number of entries to return
            
        Returns:
            List of soil entries
        """
        try:
            entries = query_collection("soil_entries", "user_id", "==", user_id, limit)
            
            # Sort by created_at in descending order (newest first)
            entries.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return entries
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get soil entries: {str(e)}"
            )
    
    @staticmethod
    async def update_soil_entry(entry_id: str, soil_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update a soil entry in the database
        
        Args:
            entry_id: Soil entry ID
            soil_data: Updated soil entry data
            user_id: Firebase user ID for authorization check
            
        Returns:
            Updated soil entry data
            
        Raises:
            HTTPException: If update fails or user not authorized
        """
        try:
            # First get the existing entry to check authorization
            existing_entry = await DatabaseService.get_soil_entry(entry_id, user_id)
            
            # Add updated timestamp
            soil_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update the document
            success = update_document("soil_entries", entry_id, soil_data)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update soil entry"
                )
            
            # Get the updated entry
            updated_entry = await DatabaseService.get_soil_entry(entry_id)
            return updated_entry
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update soil entry: {str(e)}"
            )
    
    @staticmethod
    async def delete_soil_entry(entry_id: str, user_id: str) -> bool:
        """Delete a soil entry from the database
        
        Args:
            entry_id: Soil entry ID
            user_id: Firebase user ID for authorization check
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If deletion fails or user not authorized
        """
        try:
            # First get the existing entry to check authorization
            existing_entry = await DatabaseService.get_soil_entry(entry_id, user_id)
            
            # Delete the document
            success = delete_document("soil_entries", entry_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete soil entry"
                )
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete soil entry: {str(e)}"
            )
    
    @staticmethod
    async def create_story(user_id: str, entry_id: str, story_data: Dict[str, Any]) -> str:
        """Create a new story in the database
        
        Args:
            user_id: Firebase user ID
            entry_id: Related soil entry ID
            story_data: Story data including content, metadata, etc.
            
        Returns:
            ID of the created story
        """
        try:
            # Add user ID, entry ID, and timestamps
            story_data["user_id"] = user_id
            story_data["soil_entry_id"] = entry_id
            story_data["created_at"] = datetime.utcnow().isoformat()
            story_data["updated_at"] = story_data["created_at"]
            
            # Add the document
            story_id = add_document("stories", story_data)
            return story_id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create story: {str(e)}"
            )
    
    @staticmethod
    async def get_story(story_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a story from the database
        
        Args:
            story_id: Story ID
            user_id: Optional user ID for authorization check
            
        Returns:
            Story data
            
        Raises:
            HTTPException: If story not found or user not authorized
        """
        story_data = get_document("stories", story_id)
        if not story_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        # Check if the user is authorized to access this story
        if user_id and story_data.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this story"
            )
        
        return story_data
    
    @staticmethod
    async def get_stories_for_entry(entry_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all stories for a soil entry
        
        Args:
            entry_id: Soil entry ID
            user_id: Firebase user ID for authorization check
            
        Returns:
            List of stories
        """
        try:
            # First check if the user is authorized to access this entry
            await DatabaseService.get_soil_entry(entry_id, user_id)
            
            # Query stories for this entry
            stories = query_collection("stories", "soil_entry_id", "==", entry_id)
            
            # Sort by created_at in descending order (newest first)
            stories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return stories
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get stories: {str(e)}"
            )
    
    @staticmethod
    async def get_user_stories(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all stories for a user
        
        Args:
            user_id: Firebase user ID
            limit: Maximum number of stories to return
            
        Returns:
            List of stories
        """
        try:
            stories = query_collection("stories", "user_id", "==", user_id, limit)
            
            # Sort by created_at in descending order (newest first)
            stories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return stories
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get stories: {str(e)}"
            )

# Create a singleton instance
db_service = DatabaseService()