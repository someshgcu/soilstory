# SoilStory

Flask + Firebase + local ML integration that uses models in `Machine Learning/Deployed models testing/` without changing that folder.

## Quickstart

1) Create and fill an `.env` (or set environment variables):

```
SECRET_KEY=dev-secret
FIREBASE_PROJECT_ID=...
FIREBASE_API_KEY=...
FIREBASE_CLIENT_EMAIL=...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
WEATHER_API_KEY=... # OpenWeather
OPENAI_API_KEY=...  # optional
GEMINI_API_KEY=...  # optional
TTS_PROVIDER=gtts   # or elevenlabs
```

2) Install deps:

```
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

3) Run:

```
set FLASK_APP=backend/app.py
python -m flask run
```

Frontend at `/`, APIs under `/api/*`.

## Notes

- ML models loaded from `Machine Learning/Deployed models testing/*.pkl` and image feature follows your `test.py` approach.
- Videos saved under `storage/media/` and served via `/media/<file>`.

### Video Generation

#### Gemini (Default) - Core Video Generation
- **Primary method**: Uses Gemini AI to generate educational videos from soil analysis stories
- Set env vars:
  - `VIDEO_PROVIDER=gemini` (default)
  - `GEMINI_API_KEY=your-gemini-api-key` (required)
  - `GEMINI_VIDEO_MODEL=gemini-1.5-flash-exp` (default)
- Features:
  - Generates 10-15 second educational videos
  - Creates content based on soil analysis and story
  - Professional, gardening-focused visuals
  - No additional dependencies needed

#### Alternative Options

##### Veo (Google) video generation
- Set env vars:
  - `VIDEO_PROVIDER=veo`
  - `GCP_PROJECT_ID=your-project`
  - `GCP_LOCATION=us-central1` (or your region)
  - `VEO_MODEL_NAME=veo` (default)
  - `GOOGLE_APPLICATION_CREDENTIALS=absolute\path\to\service-account.json`
- Install the extra dependency (if not already):
  - `pip install google-cloud-aiplatform>=1.64.0`

##### Local TTS + MoviePy (Fallback)
- Set env var: `VIDEO_PROVIDER=local`
- Creates videos with TTS narration over the uploaded soil image
- Requires ffmpeg for best results


