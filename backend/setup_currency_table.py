#!/usr/bin/env python3
"""
Script to create currency_rate table in MySQL database
Run this script to set up the currency exchange rate table
"""

import mysql.connector
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_currency_rate_table():
    """Create currency_rate table in MySQL database"""
    try:
        # Get database configuration
        db_config = settings.get_database_config()
        
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Create currency_rate table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS currency_rate (
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
        
        # Insert some default exchange rates
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
        logger.error(f"❌ Error creating currency_rate table: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Setting up currency_rate table...")
    
    success = create_currency_rate_table()
    
    if success:
        logger.info("✅ Currency rate table setup completed successfully!")
        logger.info("💡 You can now use the currency conversion API endpoints:")
        logger.info("   - GET /api/currency-rates/rates")
        logger.info("   - POST /api/currency-rates/rates")
        logger.info("   - POST /api/currency-converter/convert")
        logger.info("   - POST /api/currency-converter/initialize-default-rates")
    else:
        logger.error("❌ Failed to setup currency rate table")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
