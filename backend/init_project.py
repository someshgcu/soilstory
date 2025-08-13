import os
import sys

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def create_empty_file(path):
    """Create an empty file if it doesn't exist"""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass
        print(f"Created empty file: {path}")
    else:
        print(f"File already exists: {path}")

def main():
    """Initialize project structure"""
    print("🚀 Initializing SoilStory API project structure...\n")
    
    # Create required directories
    directories = [
        "app",
        "app/core",
        "app/routers",
        "app/schemas",
        "app/services",
        "app/utils",
        "uploads",
        "uploads/soil_photos"
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        print("\nCreating .env file from .env.example...")
        with open(".env.example", "r") as example_file:
            with open(".env", "w") as env_file:
                env_file.write(example_file.read())
        print("✅ Created .env file. Please update it with your credentials.")
    
    print("\n🎉 Project structure initialized successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with your Firebase and AI service credentials")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the setup test: python test_setup.py")
    print("4. Start the server: python main.py")

if __name__ == "__main__":
    main()