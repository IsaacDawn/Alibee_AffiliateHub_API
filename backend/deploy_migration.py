#!/usr/bin/env python3
"""
Deploy migration script for Render.com
This script handles database setup and migrations during deployment
"""

import os
import sys
import time
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_database():
    """Setup database tables and initial data"""
    try:
        print("🔧 Setting up database...")
        
        # Import database connection
        from database.connection import db_ops
        
        # Test database connection
        print("📡 Testing database connection...")
        db_ops.test_connection()
        print("✅ Database connection successful")
        
        # Create tables if they don't exist
        print("📋 Creating database tables...")
        db_ops.create_tables()
        print("✅ Database tables created successfully")
        
        # Get initial stats
        stats = db_ops.get_stats()
        print(f"📊 Initial stats: {stats}")
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting deployment migration...")
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Check environment variables
    print("🔍 Checking environment variables...")
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("📝 Some features may not work properly")
    else:
        print("✅ All required environment variables are set")
    
    # Setup database
    if setup_database():
        print("✅ Deployment migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Deployment migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
