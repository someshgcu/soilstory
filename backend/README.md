# SoilStory Backend API

This is the backend API for the SoilStory application, an AI-powered environmental storytelling platform that converts smartphone photos of garden soil into personalized, easy-to-understand soil health analysis and engaging narratives.

## Features

- **User Authentication**: Firebase Authentication integration for secure user management
- **Soil Photo Upload**: Accept and validate soil photo uploads from frontend clients
- **AI Integration**: Generate personalized soil health stories using AI services
- **Database Integration**: Firebase Firestore for secure data storage
- **Data Retrieval**: Fetch past soil entries and stories for authenticated users
- **Error Handling & Validation**: Robust error handling and input validation

## Tech Stack

- **Framework**: FastAPI
- **Authentication**: Firebase Authentication
- **Database**: Firebase Firestore
- **Storage**: Firebase Storage
- **AI Services**: OpenAI or Google Gemini (configurable)

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration and utilities
│   ├── routers/        # API route handlers
│   ├── schemas/        # Pydantic models for request/response validation
│   ├── services/       # Business logic and external service integrations
│   └── utils/          # Utility functions
├── .env.example        # Example environment variables
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Firebase project with Authentication, Firestore, and Storage enabled
- OpenAI API key or Google Gemini API key (optional for AI features)

### Installation

1. Clone the repository

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Firebase:
   - Create a Firebase project at https://console.firebase.google.com/
   - Enable Authentication, Firestore, and Storage
   - Generate a service account key (Project Settings > Service accounts > Generate new private key)
   - Save the key as `firebase-service-account.json` in the backend directory

5. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your Firebase and AI service credentials

### Running the API

1. Start the development server:
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

2. The API will be available at http://localhost:8000

3. Access the API documentation at http://localhost:8000/api/docs

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/verify-token` - Verify a Firebase ID token
- `GET /api/auth/me` - Get current user profile

### Users

- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile
- `GET /api/users/{user_id}` - Get a user profile by ID

### Soil Photos

- `POST /api/soil-photos` - Upload a new soil photo
- `GET /api/soil-photos` - Get all soil photos for current user
- `GET /api/soil-photos/{entry_id}` - Get a soil photo by ID
- `PUT /api/soil-photos/{entry_id}` - Update a soil photo
- `DELETE /api/soil-photos/{entry_id}` - Delete a soil photo
- `POST /api/soil-photos/{entry_id}/analyze` - Analyze a soil photo

### Stories

- `POST /api/stories` - Generate a new story
- `GET /api/stories` - Get all stories for current user
- `GET /api/soil-photos/{entry_id}/stories` - Get all stories for a soil photo
- `GET /api/stories/{story_id}` - Get a story by ID
- `PUT /api/stories/{story_id}` - Update a story

## Development

### Adding New Features

1. Create new schemas in `app/schemas/`
2. Implement business logic in `app/services/`
3. Add new endpoints in `app/routers/`
4. Update the main application in `main.py` if needed

### Testing

TODO: Add testing instructions

## Deployment

TODO: Add deployment instructions

## License

TODO: Add license information