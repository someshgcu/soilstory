import os
import uuid
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
from app.core.config import settings
from app.core.firebase import upload_file, delete_file

def validate_image(file: UploadFile) -> bool:
    """Validate that the uploaded file is an image with allowed extension
    
    Args:
        file: The uploaded file
        
    Returns:
        True if the file is valid, False otherwise
    """
    # Check file extension
    ext = file.filename.split('.')[-1].lower() if file.filename else ''
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False
    
    # Check content type
    if not file.content_type.startswith('image/'):
        return False
    
    return True

async def save_upload_file(file: UploadFile, user_id: str) -> Tuple[str, str]:
    """Save an uploaded file to Firebase Storage
    
    Args:
        file: The uploaded file
        user_id: The ID of the user uploading the file
        
    Returns:
        Tuple of (file_path, public_url)
        
    Raises:
        HTTPException: If the file cannot be saved
    """
    try:
        # Validate the file
        if not validate_image(file):
            raise HTTPException(status_code=400, detail="Invalid file format. Only JPG, JPEG, and PNG are allowed.")
        
        # Read file content
        contents = await file.read()
        
        # Generate a unique filename
        ext = file.filename.split('.')[-1].lower() if file.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{ext}"
        
        # Define the path in Firebase Storage
        file_path = f"soil_photos/{user_id}/{filename}"
        
        # Upload to Firebase Storage
        public_url = upload_file(contents, file_path)
        
        return file_path, public_url
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {str(e)}")

async def process_image(file: UploadFile) -> bytes:
    """Process an image file for AI analysis
    
    Args:
        file: The uploaded image file
        
    Returns:
        Processed image data as bytes
        
    Raises:
        HTTPException: If the image cannot be processed
    """
    try:
        # Read file content
        contents = await file.read()
        
        # Reset file pointer for future reads
        await file.seek(0)
        
        # Open image with PIL
        img = Image.open(io.BytesIO(contents))
        
        # Resize if needed (e.g., for AI model requirements)
        max_size = 1024  # Maximum dimension
        if max(img.size) > max_size:
            # Calculate new dimensions while preserving aspect ratio
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Convert to RGB if needed (in case of RGBA or other formats)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        processed_image = output.getvalue()
        
        return processed_image
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not process image: {str(e)}")

def extract_image_metadata(file: UploadFile) -> dict:
    """Extract metadata from an image file
    
    Args:
        file: The uploaded image file
        
    Returns:
        Dictionary containing image metadata
    """
    metadata = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": 0  # Will be updated with actual size
    }
    
    try:
        # Get file size
        file_object = file.file
        position = file_object.tell()
        file_object.seek(0, os.SEEK_END)
        metadata["size"] = file_object.tell()
        file_object.seek(position)  # Reset position
        
        # Additional metadata could be extracted here, such as EXIF data
        # This would require reading the file and using a library like PIL's ExifTags
        
    except Exception as e:
        print(f"Error extracting metadata: {e}")
    
    return metadata