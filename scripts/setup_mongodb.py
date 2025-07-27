#!/usr/bin/env python3
"""
MongoDB Setup Script for ResumeScan
This script helps initialize MongoDB connection and create necessary indexes.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to Python path so we can import from db/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_mongodb_connection():
    """Check if MongoDB is accessible."""
    try:
        from pymongo import MongoClient
        
        # Load environment variables
        load_dotenv()
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        
        print(f"🔍 Checking MongoDB connection to: {mongodb_uri}")
        
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        print("✅ MongoDB connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def setup_database():
    """Initialize database with proper indexes."""
    try:
        from db.connection import db_connection
        
        print("🔧 Setting up database indexes...")
        
        # The database connection automatically creates indexes
        collection = db_connection.get_collection()
        
        # Verify indexes were created
        indexes = list(collection.list_indexes())
        print(f"✅ Created {len(indexes)} indexes:")
        for index in indexes:
            print(f"   - {index['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = '.env'
    env_example = '.env.example'
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print(f"📝 Creating {env_file} from {env_example}")
            with open(env_example, 'r') as example:
                content = example.read()
            with open(env_file, 'w') as env:
                env.write(content)
            print(f"✅ Created {env_file}. Please update it with your MongoDB settings.")
        else:
            print(f"📝 Creating default {env_file}")
            default_content = """# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=resumescan
MONGODB_COLLECTION=cv_files

# Google AI Configuration (if needed)
GOOGLE_API_KEY=your_google_api_key_here
"""
            with open(env_file, 'w') as env:
                env.write(default_content)
            print(f"✅ Created default {env_file}")
    else:
        print(f"✅ {env_file} already exists")

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 ResumeScan MongoDB Setup")
    print("=" * 40)
    
    # Step 1: Create .env file
    create_env_file()
    
    # Step 2: Install requirements
    if not install_requirements():
        print("⚠️  Please install requirements manually: pip install -r requirements.txt")
    
    # Step 3: Check MongoDB connection
    if not check_mongodb_connection():
        print("\n❌ Setup incomplete!")
        print("Please ensure MongoDB is running and accessible.")
        print("For local MongoDB installation:")
        print("  - Windows: Download from https://www.mongodb.com/try/download/community")
        print("  - macOS: brew install mongodb-community")
        print("  - Linux: sudo apt-get install mongodb")
        print("\nOr use MongoDB Atlas (cloud): https://www.mongodb.com/atlas")
        return False
    
    # Step 4: Setup database
    if not setup_database():
        print("❌ Database setup failed!")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("You can now run the ResumeScan application with: streamlit run main.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
