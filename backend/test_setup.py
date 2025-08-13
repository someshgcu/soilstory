import os
import sys
import importlib.util
from dotenv import load_dotenv

def check_module(module_name):
    """Check if a Python module is installed"""
    return importlib.util.find_spec(module_name) is not None

def check_env_file():
    """Check if .env file exists"""
    return os.path.exists(".env")

def check_firebase_config():
    """Check if Firebase configuration is set up"""
    load_dotenv()
    required_vars = [
        "FIREBASE_API_KEY",
        "FIREBASE_AUTH_DOMAIN",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_STORAGE_BUCKET"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing Firebase environment variables: {', '.join(missing)}")
        return False
    
    # Check for service account key
    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    if not service_account:
        # Check for file in default location
        if not os.path.exists("firebase-service-account.json"):
            print("⚠️ Firebase service account key not found. Some features may not work.")
    
    return True

def check_ai_config():
    """Check if AI service configuration is set up"""
    load_dotenv()
    ai_provider = os.getenv("AI_SERVICE_PROVIDER", "").lower()
    
    if ai_provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️ OpenAI API key not found. AI features will use simulated results.")
            return False
    elif ai_provider == "gemini":
        if not os.getenv("GEMINI_API_KEY"):
            print("⚠️ Gemini API key not found. AI features will use simulated results.")
            return False
    else:
        print(f"⚠️ Unknown AI provider: {ai_provider}. AI features will use simulated results.")
        return False
    
    return True

def main():
    """Run setup checks"""
    print("🔍 Checking SoilStory API setup...\n")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
    else:
        print("✅ Python version OK")
    
    # Check required packages
    required_packages = [
        "fastapi",
        "uvicorn",
        "firebase_admin",
        "pyrebase4",
        "python-dotenv",
        "pydantic",
        "python-multipart",
        "pillow"
    ]
    
    missing_packages = []
    for package in required_packages:
        if not check_module(package.replace("-", "_")):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
    else:
        print("✅ All required packages installed")
    
    # Check .env file
    if check_env_file():
        print("✅ .env file found")
    else:
        print("❌ .env file not found. Copy .env.example to .env and fill in your credentials.")
    
    # Check Firebase configuration
    if check_firebase_config():
        print("✅ Firebase configuration OK")
    else:
        print("❌ Firebase configuration incomplete")
    
    # Check AI service configuration
    if check_ai_config():
        print("✅ AI service configuration OK")
    else:
        print("⚠️ AI service configuration incomplete (will use simulated results)")
    
    # Check directory structure
    required_dirs = [
        "app",
        "app/core",
        "app/routers",
        "app/schemas",
        "app/services",
        "app/utils"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"❌ Missing required directories: {', '.join(missing_dirs)}")
    else:
        print("✅ Directory structure OK")
    
    print("\n🔍 Setup check complete!")
    
    # Summary
    if not missing_packages and check_env_file() and check_firebase_config() and not missing_dirs:
        print("\n✅ Your SoilStory API is ready to run!")
        print("   Start the server with: python main.py")
        print("   Or: uvicorn main:app --reload")
        print("   Then visit: http://localhost:8000/api/docs")
    else:
        print("\n⚠️ Please fix the issues above before running the API.")

if __name__ == "__main__":
    main()