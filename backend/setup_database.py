#!/usr/bin/env python3
"""
Database setup script for Alibee Affiliate
Run this script to initialize the database and run migrations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.migrations import migration
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main setup function"""
    print("🚀 Alibee Affiliate Database Setup")
    print("=" * 50)
    
    # Check database configuration
    print("📋 Checking database configuration...")
    db_config = settings.get_database_config()
    print(f"   Host: {db_config['host']}")
    print(f"   Port: {db_config['port']}")
    print(f"   Database: {db_config['database']}")
    print(f"   User: {db_config['user']}")
    print()
    
    # Run migrations
    print("🔧 Running database migrations...")
    try:
        success = migration.run_migrations()
        if success:
            print("✅ Database migrations completed successfully!")
        else:
            print("❌ Database migrations failed!")
            return False
    except Exception as e:
        print(f"❌ Error during migrations: {e}")
        return False
    
    print()
    
    # Get database info
    print("📊 Getting database information...")
    try:
        db_info = migration.get_database_info()
        print(f"   Database: {db_info.get('database_name', 'Unknown')}")
        print(f"   MySQL Version: {db_info.get('mysql_version', 'Unknown')}")
        print(f"   Tables: {', '.join(db_info.get('tables', []))}")
        print(f"   Saved Products: {db_info.get('saved_products_count', 0)}")
        print(f"   Status: {db_info.get('status', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error getting database info: {e}")
        return False
    
    print()
    print("🎉 Database setup completed successfully!")
    print("   You can now start the application with: python -m uvicorn app:app --reload --port 8080")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
