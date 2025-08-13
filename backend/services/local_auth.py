import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from functools import wraps
from flask import request, jsonify, current_app

# Path to the credentials file
CREDENTIALS_FILE = Path(__file__).resolve().parents[2] / 'auth_credentials.json'

class LocalAuthService:
    """Local authentication service using JSON credentials file"""
    
    def __init__(self):
        self.users = []
        self.load_users()
    
    def load_users(self):
        """Load users from the JSON credentials file"""
        try:
            if CREDENTIALS_FILE.exists():
                with open(CREDENTIALS_FILE, 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', [])
                    print(f"Loaded {len(self.users)} users from credentials file")
            else:
                print(f"Credentials file not found at {CREDENTIALS_FILE}")
                # Fallback to default users
                self.users = self._get_default_users()
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = self._get_default_users()
    
    def _get_default_users(self) -> List[Dict]:
        """Fallback default users if JSON file can't be loaded"""
        return [
            {
                "id": 1,
                "username": "admin",
                "password": "admin123",
                "email": "admin@soilstory.com",
                "role": "administrator",
                "fullName": "System Administrator"
            },
            {
                "id": 2,
                "username": "scientist1",
                "password": "science2024",
                "email": "scientist1@soilstory.com",
                "role": "scientist",
                "fullName": "Dr. Sarah Johnson"
            },
            {
                "id": 3,
                "username": "gardener1",
                "password": "garden123",
                "email": "gardener1@soilstory.com",
                "role": "user",
                "fullName": "Mike Green"
            },
            {
                "id": 4,
                "username": "researcher",
                "password": "research456",
                "email": "researcher@soilstory.com",
                "role": "researcher",
                "fullName": "Prof. David Chen"
            },
            {
                "id": 5,
                "username": "farmer1",
                "password": "farm789",
                "email": "farmer1@soilstory.com",
                "role": "user",
                "fullName": "Lisa Thompson"
            },
            {
                "id": 6,
                "username": "student1",
                "password": "student123",
                "email": "student1@soilstory.com",
                "role": "student",
                "fullName": "Alex Rodriguez"
            },
            {
                "id": 7,
                "username": "consultant",
                "password": "consult789",
                "email": "consultant@soilstory.com",
                "role": "consultant",
                "fullName": "Emma Wilson"
            },
            {
                "id": 8,
                "username": "technician",
                "password": "tech456",
                "email": "technician@soilstory.com",
                "role": "technician",
                "fullName": "James Brown"
            },
            {
                "id": 9,
                "username": "volunteer",
                "password": "volunteer123",
                "email": "volunteer@soilstory.com",
                "role": "volunteer",
                "fullName": "Maria Garcia"
            },
            {
                "id": 10,
                "username": "demo",
                "password": "demo123",
                "email": "demo@soilstory.com",
                "role": "demo",
                "fullName": "Demo User"
            }
        ]
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user with username and password"""
        user = next((u for u in self.users if u['username'] == username and u['password'] == password), None)
        if user:
            # Don't return the password in the user object
            user_copy = user.copy()
            user_copy.pop('password', None)
            return user_copy
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        user = next((u for u in self.users if u['id'] == user_id), None)
        if user:
            user_copy = user.copy()
            user_copy.pop('password', None)
            return user_copy
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        user = next((u for u in self.users if u['username'] == username), None)
        if user:
            user_copy = user.copy()
            user_copy.pop('password', None)
            return user_copy
        return None
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        # Check if username or email already exists
        if any(u['username'] == user_data['username'] for u in self.users):
            raise ValueError("Username already exists")
        
        if any(u['email'] == user_data['email'] for u in self.users):
            raise ValueError("Email already exists")
        
        # Generate new ID
        new_id = max(u['id'] for u in self.users) + 1 if self.users else 1
        
        new_user = {
            "id": new_id,
            "username": user_data['username'],
            "password": user_data['password'],
            "email": user_data['email'],
            "role": user_data.get('role', 'user'),
            "fullName": user_data['fullName']
        }
        
        self.users.append(new_user)
        
        # Save to file
        self._save_users()
        
        # Return user without password
        user_copy = new_user.copy()
        user_copy.pop('password', None)
        return user_copy
    
    def _save_users(self):
        """Save users to the JSON file"""
        try:
            data = {"users": self.users}
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Users saved to {CREDENTIALS_FILE}")
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def update_user(self, user_id: int, user_data: Dict) -> Optional[Dict]:
        """Update an existing user"""
        user = next((u for u in self.users if u['id'] == user_id), None)
        if not user:
            return None
        
        # Update fields
        for key, value in user_data.items():
            if key != 'id' and key in user:
                user[key] = value
        
        # Save to file
        self._save_users()
        
        # Return updated user without password
        user_copy = user.copy()
        user_copy.pop('password', None)
        return user_copy
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = next((u for u in self.users if u['id'] == user_id), None)
        if not user:
            return False
        
        self.users.remove(user)
        self._save_users()
        return True
    
    def list_users(self) -> List[Dict]:
        """List all users (without passwords)"""
        return [self.get_user_by_id(u['id']) for u in self.users]

# Global instance
auth_service = LocalAuthService()

def require_local_auth(f):
    """Decorator to require local authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get credentials from request headers or JSON body
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Basic '):
            import base64
            try:
                credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = credentials.split(':', 1)
            except:
                return jsonify({"error": "Invalid authorization header"}), 401
        else:
            # Try to get from JSON body
            data = request.get_json(silent=True) or {}
            username = data.get('username')
            password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 401
        
        # Authenticate user
        user = auth_service.authenticate_user(username, password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get the current authenticated user from request context"""
    return getattr(request, 'current_user', None)
