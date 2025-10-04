#!/usr/bin/env python3
"""
Script to add new currency exchange rates to the database
"""

import mysql.connector
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_new_currency_rates():
    """Add new currency exchange rates to the database"""
    try:
        # Get database configuration
        db_config = settings.get_database_config()
        
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # New currency rates to add
        new_rates = [
            # USD conversions
            ('USD', 'CNY', 7.20),   # 1 USD = 7.20 CNY (Chinese Yuan)
            ('USD', 'INR', 83.50),  # 1 USD = 83.50 INR (Indian Rupee)
            ('USD', 'MYR', 4.70),   # 1 USD = 4.70 MYR (Malaysian Ringgit)
            ('USD', 'THB', 36.50),  # 1 USD = 36.50 THB (Thai Baht)
            ('USD', 'VND', 24500),  # 1 USD = 24500 VND (Vietnamese Dong)
            ('USD', 'IDR', 15500),  # 1 USD = 15500 IDR (Indonesian Rupiah)
            ('USD', 'PHP', 56.50),  # 1 USD = 56.50 PHP (Philippine Peso)
            ('USD', 'SGD', 1.35),   # 1 USD = 1.35 SGD (Singapore Dollar)
            
            # EUR conversions
            ('EUR', 'CNY', 8.50),   # 1 EUR = 8.50 CNY
            ('EUR', 'INR', 98.50),  # 1 EUR = 98.50 INR
            ('EUR', 'MYR', 5.55),   # 1 EUR = 5.55 MYR
            
            # ILS conversions
            ('ILS', 'CNY', 1.97),   # 1 ILS = 1.97 CNY
            ('ILS', 'INR', 22.90),  # 1 ILS = 22.90 INR
            ('ILS', 'MYR', 1.29),   # 1 ILS = 1.29 MYR
            
            # CNY conversions
            ('CNY', 'USD', 0.14),   # 1 CNY = 0.14 USD
            ('CNY', 'EUR', 0.12),   # 1 CNY = 0.12 EUR
            ('CNY', 'ILS', 0.51),   # 1 CNY = 0.51 ILS
            ('CNY', 'INR', 11.60),  # 1 CNY = 11.60 INR
            ('CNY', 'MYR', 0.65),   # 1 CNY = 0.65 MYR
            
            # INR conversions
            ('INR', 'USD', 0.012),  # 1 INR = 0.012 USD
            ('INR', 'EUR', 0.010),  # 1 INR = 0.010 EUR
            ('INR', 'ILS', 0.044),  # 1 INR = 0.044 ILS
            ('INR', 'CNY', 0.086),  # 1 INR = 0.086 CNY
            ('INR', 'MYR', 0.056),  # 1 INR = 0.056 MYR
            
            # MYR conversions
            ('MYR', 'USD', 0.21),   # 1 MYR = 0.21 USD
            ('MYR', 'EUR', 0.18),   # 1 MYR = 0.18 EUR
            ('MYR', 'ILS', 0.78),   # 1 MYR = 0.78 ILS
            ('MYR', 'CNY', 1.53),   # 1 MYR = 1.53 CNY
            ('MYR', 'INR', 17.80),  # 1 MYR = 17.80 INR
            
            # Additional conversions for other currencies
            ('THB', 'USD', 0.027),  # 1 THB = 0.027 USD
            ('VND', 'USD', 0.000041), # 1 VND = 0.000041 USD
            ('IDR', 'USD', 0.000065), # 1 IDR = 0.000065 USD
            ('PHP', 'USD', 0.018),  # 1 PHP = 0.018 USD
            ('SGD', 'USD', 0.74),   # 1 SGD = 0.74 USD
        ]
        
        # Insert new rates (ignore duplicates)
        insert_query = """
        INSERT IGNORE INTO currency_rate (from_currency, to_currency, rate, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        """
        
        cursor.executemany(insert_query, new_rates)
        conn.commit()
        
        logger.info(f"✅ Added {len(new_rates)} new exchange rates")
        
        # Show current rates count
        cursor.execute("SELECT COUNT(*) FROM currency_rate")
        total_rates = cursor.fetchone()[0]
        logger.info(f"📊 Total exchange rates in database: {total_rates}")
        
        # Show some examples
        cursor.execute("SELECT from_currency, to_currency, rate FROM currency_rate WHERE from_currency IN ('CNY', 'INR', 'MYR') ORDER BY from_currency, to_currency LIMIT 10")
        examples = cursor.fetchall()
        
        logger.info("📋 Example new rates:")
        for example in examples:
            logger.info(f"   {example[0]} → {example[1]}: {example[2]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"❌ MySQL error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error adding new currency rates: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Adding new currency exchange rates...")
    
    success = add_new_currency_rates()
    
    if success:
        logger.info("✅ New currency rates added successfully!")
        logger.info("💡 Now supporting currencies from:")
        logger.info("   🇨🇳 China (CNY)")
        logger.info("   🇮🇳 India (INR)")
        logger.info("   🇲🇾 Malaysia (MYR)")
        logger.info("   🇹🇭 Thailand (THB)")
        logger.info("   🇻🇳 Vietnam (VND)")
        logger.info("   🇮🇩 Indonesia (IDR)")
        logger.info("   🇵🇭 Philippines (PHP)")
        logger.info("   🇸🇬 Singapore (SGD)")
    else:
        logger.error("❌ Failed to add new currency rates")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
