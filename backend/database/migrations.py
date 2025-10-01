# backend/database/migrations.py
"""
Database migration system for Alibee Affiliate
Handles database schema creation and updates
"""

import mysql.connector
from mysql.connector import pooling
from config.settings import settings
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Database migration manager"""
    
    def __init__(self):
        self.config = settings.get_database_config()
    
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            # Connect without specifying database
            temp_config = self.config.copy()
            temp_config.pop('database', None)
            
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            # Create database if not exists
            db_name = self.config['database']
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"Database '{db_name}' created or verified")
            
            cursor.close()
            connection.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            return False
    
    def create_tables(self):
        """Create all necessary tables"""
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()
            
            # Create saved_products table
            create_saved_products_table = """
            CREATE TABLE IF NOT EXISTS saved_products (
                product_id VARCHAR(255) NOT NULL PRIMARY KEY,
                product_title TEXT,
                promotion_link TEXT,
                product_category VARCHAR(255),
                custom_title TEXT,
                has_video BOOLEAN DEFAULT FALSE,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_saved_at (saved_at),
                INDEX idx_category (product_category),
                INDEX idx_updated_at (updated_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_saved_products_table)
            logger.info("Table 'saved_products' created or verified")
            
            # Create search_logs table for tracking searches (optional)
            create_search_logs_table = """
            CREATE TABLE IF NOT EXISTS search_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query VARCHAR(500),
                results_count INT DEFAULT 0,
                search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_query (query),
                INDEX idx_timestamp (search_timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_search_logs_table)
            logger.info("Table 'search_logs' created or verified")
            
            # Create system_stats table for tracking system statistics
            create_system_stats_table = """
            CREATE TABLE IF NOT EXISTS system_stats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stat_name VARCHAR(100) NOT NULL UNIQUE,
                stat_value VARCHAR(500),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_stat_name (stat_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_system_stats_table)
            logger.info("Table 'system_stats' created or verified")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def add_unique_constraints(self):
        """Add unique constraints and indexes"""
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()
            
            # Add unique constraint to product_id if not exists
            try:
                cursor.execute("ALTER TABLE saved_products ADD UNIQUE KEY unique_product_id (product_id)")
                logger.info("Unique constraint added to product_id")
            except mysql.connector.Error as e:
                if e.errno == 1061:  # Duplicate key name
                    logger.info("Unique constraint already exists on product_id")
                else:
                    raise
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add constraints: {e}")
            return False
    
    def run_migrations(self):
        """Run all migrations"""
        logger.info("Starting database migrations...")
        
        # Step 1: Create database
        if not self.create_database_if_not_exists():
            return False
        
        # Step 2: Create tables
        if not self.create_tables():
            return False
        
        # Step 3: Add constraints
        if not self.add_unique_constraints():
            return False
        
        logger.info("Database migrations completed successfully")
        return True
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and status"""
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()
            
            # Get database version
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            # Get table information
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            # Get saved_products count
            saved_count = 0
            if 'saved_products' in tables:
                cursor.execute("SELECT COUNT(*) FROM saved_products")
                saved_count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return {
                "database_name": self.config['database'],
                "mysql_version": version,
                "tables": tables,
                "saved_products_count": saved_count,
                "status": "connected"
            }
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Create global migration instance
migration = DatabaseMigration()
