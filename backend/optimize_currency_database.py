#!/usr/bin/env python3
"""
Script to optimize currency database - keep only necessary exchange rates
"""

import mysql.connector
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_currency_database():
    """Optimize currency database to keep only necessary rates"""
    try:
        # Get database configuration
        db_config = settings.get_database_config()
        
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Clear all existing rates
        logger.info("🗑️ Clearing existing exchange rates...")
        cursor.execute("DELETE FROM currency_rate")
        conn.commit()
        
        # Insert only necessary rates (USD as base currency)
        optimized_rates = [
            # USD to main currencies (for display)
            ('USD', 'EUR', 0.85),   # 1 USD = 0.85 EUR
            ('USD', 'ILS', 3.65),   # 1 USD = 3.65 ILS
            
            # Source currencies to USD (for conversion from any currency to USD)
            ('CNY', 'USD', 0.14),   # 1 CNY = 0.14 USD (Chinese Yuan)
            ('INR', 'USD', 0.012),  # 1 INR = 0.012 USD (Indian Rupee)
            ('MYR', 'USD', 0.21),   # 1 MYR = 0.21 USD (Malaysian Ringgit)
            ('THB', 'USD', 0.027),  # 1 THB = 0.027 USD (Thai Baht)
            ('VND', 'USD', 0.000041), # 1 VND = 0.000041 USD (Vietnamese Dong)
            ('IDR', 'USD', 0.000065), # 1 IDR = 0.000065 USD (Indonesian Rupiah)
            ('PHP', 'USD', 0.018),  # 1 PHP = 0.018 USD (Philippine Peso)
            ('SGD', 'USD', 0.74),   # 1 SGD = 0.74 USD (Singapore Dollar)
        ]
        
        # Insert optimized rates
        insert_query = """
        INSERT INTO currency_rate (from_currency, to_currency, rate, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        """
        
        cursor.executemany(insert_query, optimized_rates)
        conn.commit()
        
        logger.info(f"✅ Inserted {len(optimized_rates)} optimized exchange rates")
        
        # Show current rates
        cursor.execute("SELECT from_currency, to_currency, rate FROM currency_rate ORDER BY from_currency, to_currency")
        rates = cursor.fetchall()
        
        logger.info("📊 Optimized exchange rates:")
        for rate in rates:
            logger.info(f"   {rate[0]} → {rate[1]}: {rate[2]}")
        
        # Show conversion examples
        logger.info("\n💱 Conversion examples:")
        examples = [
            ("CNY", "USD", 100, "Chinese Yuan to USD"),
            ("INR", "USD", 1000, "Indian Rupee to USD"),
            ("MYR", "USD", 100, "Malaysian Ringgit to USD"),
            ("USD", "EUR", 100, "USD to Euro"),
            ("USD", "ILS", 100, "USD to Israeli Shekel"),
        ]
        
        for from_curr, to_curr, amount, description in examples:
            # Find the rate
            cursor.execute(
                "SELECT rate FROM currency_rate WHERE from_currency = %s AND to_currency = %s",
                (from_curr, to_curr)
            )
            result = cursor.fetchone()
            if result:
                converted = amount * result[0]
                logger.info(f"   {amount} {from_curr} = {converted:.2f} {to_curr} ({description})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"❌ MySQL error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error optimizing currency database: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Optimizing currency database...")
    
    success = optimize_currency_database()
    
    if success:
        logger.info("✅ Currency database optimized successfully!")
        logger.info("💡 Now using USD as base currency for all conversions")
        logger.info("🎯 Only converting to USD, EUR, and ILS")
        logger.info("📈 Reduced from 40+ rates to 10 essential rates")
        logger.info("\n🔄 Conversion flow:")
        logger.info("   Any Currency → USD → Target Currency (USD/EUR/ILS)")
    else:
        logger.error("❌ Failed to optimize currency database")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
