# SoilStory Frontend - Page Structure

## Overview
This document describes the new page structure for the SoilStory application with authentication integration.

## Page Flow

### 1. **index.html** - Landing Page
- **Purpose**: Public landing page introducing the application
- **Features**: 
  - Hero section with call-to-action
  - Feature overview
  - Statistics section
  - How it works guide
- **Navigation**: Contains "Get Started" button that leads to authentication
- **Access**: Public (no authentication required)

### 2. **auth.html** - Authentication Page
- **Purpose**: User login and registration
- **Features**:
  - Login form with username/password
  - Registration form for new users
  - Uses `auth_credentials.json` for user validation
  - Fallback to hardcoded users if JSON file unavailable
- **Authentication**: Validates against JSON credentials file
- **Redirect**: After successful login, redirects to `dashboard.html`
- **Access**: Public (no authentication required)

### 3. **dashboard.html** - User Dashboard
- **Purpose**: Main user interface after login
- **Features**:
  - User information display
  - Quick access to main features
  - Recent activity history
  - Navigation to other pages
- **Authentication**: Requires valid login session
- **Redirect**: If not authenticated, redirects to `auth.html`
- **Access**: Protected (authentication required)

### 4. **main.html** - Soil Analysis Interface
- **Purpose**: Main soil analysis functionality
- **Features**:
  - Photo upload interface
  - Soil analysis results
  - AI-generated stories
  - Video generation
- **Authentication**: Requires valid login session
- **Redirect**: If not authenticated, redirects to `auth.html`
- **Access**: Protected (authentication required)

## Authentication Flow

```
User visits index.html → Clicks "Get Started" → Goes to auth.html → 
Login/Register → Redirected to dashboard.html → Can access main.html
```

## User Credentials

The system uses `auth_credentials.json` with 10 predefined users:

- **Admin**: admin / admin123
- **Scientist**: scientist1 / science2024  
- **Gardener**: gardener1 / garden123
- **Demo**: demo / demo123
- **And 6 more users...**

## Technical Details

### Authentication Storage
- Uses `localStorage` to store user session
- Key: `currentUser` (stores user object)
- Key: `userHistory` (stores user activity)

### Security Features
- Password visibility toggle
- Form validation
- Session persistence
- Automatic logout on invalid sessions

### Responsive Design
- Mobile-friendly interface
- Bootstrap 5 framework
- Custom CSS animations
- Modern UI/UX patterns

## File Dependencies

- `auth_credentials.json` - User database
- `styles.css` - Custom styling (if exists)
- `script.js` - Additional functionality (if exists)
- Bootstrap CSS/JS - Framework dependencies
- Bootstrap Icons - Icon library

## Usage Instructions

1. **Start with index.html** - Landing page
2. **Navigate to auth.html** - Login/Register
3. **Access dashboard.html** - After authentication
4. **Use main.html** - For soil analysis features

## Notes

- All protected pages check for valid `currentUser` in localStorage
- Invalid sessions automatically redirect to authentication
- User data persists across browser sessions until logout
- Demo credentials are displayed on the authentication page for testing
