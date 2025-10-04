#!/usr/bin/env python3
"""
Script to check and fix database structure
"""

import mysql.connector
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_structure():
    """Check current database structure and fix if needed"""
    try:
        # Get database configuration
        db_config = settings.get_database_config()
        
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if currency_rate table exists
        cursor.execute("SHOW TABLES LIKE 'currency_rate'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            logger.info("✅ currency_rate table exists")
            
            # Check table structure
            cursor.execute("DESCRIBE currency_rate")
            columns = cursor.fetchall()
            
            logger.info("📋 Current table structure:")
            for column in columns:
                logger.info(f"   {column[0]} - {column[1]} - {column[2]}")
            
            # Check if we have the right columns
            column_names = [col[0] for col in columns]
            required_columns = ['from_currency', 'to_currency', 'rate']
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                logger.warning(f"⚠️ Missing columns: {missing_columns}")
                
                # Drop and recreate table
                logger.info("🔄 Dropping and recreating table...")
                cursor.execute("DROP TABLE IF EXISTS currency_rate")
                conn.commit()
                
                # Create new table
                create_table_query = """
                CREATE TABLE currency_rate (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    from_currency VARCHAR(3) NOT NULL,
                    to_currency VARCHAR(3) NOT NULL,
                    rate DECIMAL(10, 6) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_currency_pair (from_currency, to_currency),
                    INDEX idx_from_currency (from_currency),
                    INDEX idx_to_currency (to_currency)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                
                cursor.execute(create_table_query)
                conn.commit()
                logger.info("✅ Table recreated successfully")
            else:
                logger.info("✅ All required columns exist")
        else:
            logger.info("❌ currency_rate table does not exist, creating...")
            
            # Create table
            create_table_query = """
            CREATE TABLE currency_rate (
                id INT AUTO_INCREMENT PRIMARY KEY,
                from_currency VARCHAR(3) NOT NULL,
                to_currency VARCHAR(3) NOT NULL,
                rate DECIMAL(10, 6) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_currency_pair (from_currency, to_currency),
                INDEX idx_from_currency (from_currency),
                INDEX idx_to_currency (to_currency)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("✅ currency_rate table created successfully")
        
        # Insert default rates
        default_rates = [
            ('USD', 'EUR', 0.85),
            ('USD', 'ILS', 3.65),
            ('EUR', 'USD', 1.18),
            ('EUR', 'ILS', 4.30),
            ('ILS', 'USD', 0.27),
            ('ILS', 'EUR', 0.23),
        ]
        
        insert_query = """
        INSERT IGNORE INTO currency_rate (from_currency, to_currency, rate)
        VALUES (%s, %s, %s)
        """
        
        cursor.executemany(insert_query, default_rates)
        conn.commit()
        
        logger.info(f"✅ Inserted {len(default_rates)} default exchange rates")
        
        # Show current rates
        cursor.execute("SELECT from_currency, to_currency, rate, updated_at FROM currency_rate ORDER BY from_currency, to_currency")
        rates = cursor.fetchall()
        
        logger.info("📊 Current exchange rates:")
        for rate in rates:
            logger.info(f"   {rate[0]} → {rate[1]}: {rate[2]} (updated: {rate[3]})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"❌ MySQL error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    logger.info("🔍 Checking database structure...")
    
    success = check_database_structure()
    
    if success:
        logger.info("✅ Database structure check completed successfully!")
    else:
        logger.error("❌ Failed to check/fix database structure")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
