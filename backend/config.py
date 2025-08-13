import os
from pathlib import Path


class AppConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    # Storage
    BASE_DIR = Path(__file__).resolve().parents[1]
    UPLOADS_DIR = os.environ.get('UPLOADS_DIR', str(BASE_DIR / 'storage' / 'uploads'))
    MEDIA_DIR = os.environ.get('MEDIA_DIR', str(BASE_DIR / 'storage' / 'media'))

    # Firebase
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL', '')
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', '')

    # External APIs
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')

    # Video/TTS
    TTS_PROVIDER = os.environ.get('TTS_PROVIDER', 'gtts')  # gtts or elevenlabs
    VIDEO_PROVIDER = os.environ.get('VIDEO_PROVIDER', 'gemini')  # gemini (default), local, or veo
    ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

    # Google Cloud / Vertex AI (for Veo)
    GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', '')
    GCP_LOCATION = os.environ.get('GCP_LOCATION', 'us-central1')
    VEO_MODEL_NAME = os.environ.get('VEO_MODEL_NAME', 'veo')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')

    # Gemini Video Generation
    GEMINI_VIDEO_MODEL = os.environ.get('GEMINI_VIDEO_MODEL', 'gemini-1.5-flash-exp')


