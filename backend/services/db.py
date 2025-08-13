import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid


def _get_data_dir() -> Path:
    """Get the local data directory for storing analyses."""
    data_dir = Path('storage/data')
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def db_create_analysis(record: Dict[str, Any]) -> str:
    """Create a new analysis record in local JSON storage."""
    data_dir = _get_data_dir()
    
    # Generate unique ID
    analysis_id = str(uuid.uuid4())
    record['id'] = analysis_id
    
    # Save to JSON file
    file_path = data_dir / f"{analysis_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, default=str)
    
    return analysis_id


def db_get_analysis(doc_id: str) -> Optional[Dict[str, Any]]:
    """Get analysis by ID from local storage."""
    data_dir = _get_data_dir()
    file_path = data_dir / f"{doc_id}.json"
    
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def db_update_analysis_video(doc_id: str, data: Dict[str, Any]) -> None:
    """Update analysis with video data."""
    analysis = db_get_analysis(doc_id)
    if not analysis:
        return
    
    # Update the record
    analysis.update(data)
    
    # Save back to file
    data_dir = _get_data_dir()
    file_path = data_dir / f"{doc_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, default=str)


def db_get_user_history(uid: str) -> List[Dict[str, Any]]:
    """Get all analyses for a user from local storage."""
    data_dir = _get_data_dir()
    items = []
    
    # Read all JSON files in the data directory
    for file_path in data_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                record = json.load(f)
                if record.get('userId') == uid:
                    items.append(record)
        except Exception:
            continue
    
    # Sort by creation date (newest first)
    items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    return items[:50]  # Limit to 50 most recent


