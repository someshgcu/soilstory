import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import pyrebase
import json
import os
from fastapi import HTTPException, status
from app.core.config import settings
from typing import Dict, Any, Optional

# Initialize Firebase Admin SDK
try:
    # Try to load from environment variable first (for production)
    if settings.FIREBASE_SERVICE_ACCOUNT_KEY:
        try:
            service_account_info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
            cred = credentials.Certificate(service_account_info)
        except json.JSONDecodeError:
            # If it's a file path instead of JSON string
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
    else:
        # Look for service account file (for development)
        service_account_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                          "firebase-service-account.json")
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        else:
            raise FileNotFoundError("Firebase service account file not found")
    
    # Initialize the app
    firebase_admin_app = firebase_admin.initialize_app(cred, {
        'storageBucket': settings.FIREBASE_STORAGE_BUCKET
    })
    
    # Initialize Firestore
    db = firestore.client()
    
    # Initialize Storage
    bucket = storage.bucket()
    
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    # For development, you might want to continue without Firebase
    firebase_admin_app = None
    db = None
    bucket = None

# Initialize Pyrebase for authentication
firebase_config = {
    "apiKey": settings.FIREBASE_API_KEY,
    "authDomain": settings.FIREBASE_AUTH_DOMAIN,
    "projectId": settings.FIREBASE_PROJECT_ID,
    "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
    "messagingSenderId": settings.FIREBASE_MESSAGING_SENDER_ID,
    "appId": settings.FIREBASE_APP_ID,
    "measurementId": settings.FIREBASE_MEASUREMENT_ID,
    "databaseURL": settings.FIREBASE_DATABASE_URL
}

try:
    firebase = pyrebase.initialize_app(firebase_config)
    firebase_auth = firebase.auth()
except Exception as e:
    print(f"Error initializing Pyrebase: {e}")
    firebase = None
    firebase_auth = None

# Firebase Authentication Functions
def verify_token(token: str) -> Dict[str, Any]:
    """Verify Firebase ID token and return user info"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from Firebase Auth"""
    try:
        user = auth.get_user_by_email(email)
        return user.__dict__
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_uid(uid: str) -> Optional[Dict[str, Any]]:
    """Get user by UID from Firebase Auth"""
    try:
        user = auth.get_user(uid)
        return user.__dict__
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        print(f"Error getting user by UID: {e}")
        return None

# Firestore Functions
def get_document(collection: str, document_id: str) -> Optional[Dict[str, Any]]:
    """Get a document from Firestore"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting document: {e}")
        return None

def add_document(collection: str, data: Dict[str, Any], document_id: Optional[str] = None) -> str:
    """Add a document to Firestore"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        if document_id:
            doc_ref = db.collection(collection).document(document_id)
            doc_ref.set(data)
            return document_id
        else:
            doc_ref = db.collection(collection).add(data)
            return doc_ref[1].id
    except Exception as e:
        print(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def update_document(collection: str, document_id: str, data: Dict[str, Any]) -> bool:
    """Update a document in Firestore"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        doc_ref = db.collection(collection).document(document_id)
        doc_ref.update(data)
        return True
    except Exception as e:
        print(f"Error updating document: {e}")
        return False

def delete_document(collection: str, document_id: str) -> bool:
    """Delete a document from Firestore"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        doc_ref = db.collection(collection).document(document_id)
        doc_ref.delete()
        return True
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False

def query_collection(collection: str, field: str, operator: str, value: Any, limit: int = 100) -> list:
    """Query a collection in Firestore"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = db.collection(collection).where(field, operator, value).limit(limit)
        results = query.stream()
        return [doc.to_dict() for doc in results]
    except Exception as e:
        print(f"Error querying collection: {e}")
        return []

# Firebase Storage Functions
def upload_file(file_data: bytes, destination_path: str) -> str:
    """Upload a file to Firebase Storage"""
    if not bucket:
        raise HTTPException(status_code=503, detail="Storage not available")
    
    try:
        blob = bucket.blob(destination_path)
        blob.upload_from_string(file_data)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

def delete_file(file_path: str) -> bool:
    """Delete a file from Firebase Storage"""
    if not bucket:
        raise HTTPException(status_code=503, detail="Storage not available")
    
    try:
        blob = bucket.blob(file_path)
        blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False