import functools
from typing import Callable, Dict, Any
from flask import request, jsonify, session
import uuid

from ..config import AppConfig


def require_firebase_auth(view: Callable):
    """Simple local authentication - no Firebase needed."""
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        # Get user ID from session or create a new one
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
            session['email'] = f"user_{session['user_id'][:8]}@local"
        
        user = {
            "uid": session['user_id'],
            "email": session['email'],
        }
        return view(user=user, *args, **kwargs)
    return wrapper


