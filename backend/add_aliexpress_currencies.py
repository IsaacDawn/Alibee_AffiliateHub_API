#!/usr/bin/env python3
"""
Script to add all possible AliExpress currencies to USD conversion rates
"""

import mysql.connector
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_aliexpress_currencies():
    """Add all possible AliExpress currencies to USD conversion rates"""
    try:
        # Get database configuration
        db_config = settings.get_database_config()
        
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Comprehensive list of AliExpress currencies to USD rates
        # These are approximate rates - should be updated regularly
        aliexpress_currencies = [
            # Major Asian currencies
            ('CNY', 'USD', 0.14),      # Chinese Yuan - 1 CNY = 0.14 USD
            ('JPY', 'USD', 0.0067),    # Japanese Yen - 1 JPY = 0.0067 USD
            ('KRW', 'USD', 0.00075),   # South Korean Won - 1 KRW = 0.00075 USD
            ('INR', 'USD', 0.012),     # Indian Rupee - 1 INR = 0.012 USD
            ('THB', 'USD', 0.027),     # Thai Baht - 1 THB = 0.027 USD
            ('VND', 'USD', 0.000041),  # Vietnamese Dong - 1 VND = 0.000041 USD
            ('IDR', 'USD', 0.000065),  # Indonesian Rupiah - 1 IDR = 0.000065 USD
            ('PHP', 'USD', 0.018),     # Philippine Peso - 1 PHP = 0.018 USD
            ('MYR', 'USD', 0.21),      # Malaysian Ringgit - 1 MYR = 0.21 USD
            ('SGD', 'USD', 0.74),      # Singapore Dollar - 1 SGD = 0.74 USD
            ('HKD', 'USD', 0.13),      # Hong Kong Dollar - 1 HKD = 0.13 USD
            ('TWD', 'USD', 0.031),     # Taiwan Dollar - 1 TWD = 0.031 USD
            
            # Middle East currencies
            ('AED', 'USD', 0.27),      # UAE Dirham - 1 AED = 0.27 USD
            ('SAR', 'USD', 0.27),      # Saudi Riyal - 1 SAR = 0.27 USD
            ('QAR', 'USD', 0.27),      # Qatari Riyal - 1 QAR = 0.27 USD
            ('KWD', 'USD', 3.25),      # Kuwaiti Dinar - 1 KWD = 3.25 USD
            ('BHD', 'USD', 2.65),      # Bahraini Dinar - 1 BHD = 2.65 USD
            ('OMR', 'USD', 2.60),      # Omani Rial - 1 OMR = 2.60 USD
            ('JOD', 'USD', 1.41),      # Jordanian Dinar - 1 JOD = 1.41 USD
            ('LBP', 'USD', 0.00066),   # Lebanese Pound - 1 LBP = 0.00066 USD
            ('ILS', 'USD', 0.27),      # Israeli Shekel - 1 ILS = 0.27 USD
            ('TRY', 'USD', 0.033),     # Turkish Lira - 1 TRY = 0.033 USD
            
            # European currencies
            ('EUR', 'USD', 1.18),      # Euro - 1 EUR = 1.18 USD
            ('GBP', 'USD', 1.27),      # British Pound - 1 GBP = 1.27 USD
            ('CHF', 'USD', 1.12),      # Swiss Franc - 1 CHF = 1.12 USD
            ('SEK', 'USD', 0.11),      # Swedish Krona - 1 SEK = 0.11 USD
            ('NOK', 'USD', 0.11),      # Norwegian Krone - 1 NOK = 0.11 USD
            ('DKK', 'USD', 0.16),      # Danish Krone - 1 DKK = 0.16 USD
            ('PLN', 'USD', 0.25),      # Polish Zloty - 1 PLN = 0.25 USD
            ('CZK', 'USD', 0.044),     # Czech Koruna - 1 CZK = 0.044 USD
            ('HUF', 'USD', 0.0028),    # Hungarian Forint - 1 HUF = 0.0028 USD
            ('RUB', 'USD', 0.011),     # Russian Ruble - 1 RUB = 0.011 USD
            ('UAH', 'USD', 0.027),     # Ukrainian Hryvnia - 1 UAH = 0.027 USD
            
            # American currencies
            ('CAD', 'USD', 0.74),      # Canadian Dollar - 1 CAD = 0.74 USD
            ('MXN', 'USD', 0.059),     # Mexican Peso - 1 MXN = 0.059 USD
            ('BRL', 'USD', 0.20),      # Brazilian Real - 1 BRL = 0.20 USD
            ('ARS', 'USD', 0.0012),    # Argentine Peso - 1 ARS = 0.0012 USD
            ('CLP', 'USD', 0.0011),    # Chilean Peso - 1 CLP = 0.0011 USD
            ('COP', 'USD', 0.00025),   # Colombian Peso - 1 COP = 0.00025 USD
            ('PEN', 'USD', 0.27),      # Peruvian Sol - 1 PEN = 0.27 USD
            
            # African currencies
            ('ZAR', 'USD', 0.055),     # South African Rand - 1 ZAR = 0.055 USD
            ('EGP', 'USD', 0.032),     # Egyptian Pound - 1 EGP = 0.032 USD
            ('NGN', 'USD', 0.00066),   # Nigerian Naira - 1 NGN = 0.00066 USD
            ('KES', 'USD', 0.0067),    # Kenyan Shilling - 1 KES = 0.0067 USD
            ('MAD', 'USD', 0.10),      # Moroccan Dirham - 1 MAD = 0.10 USD
            ('TND', 'USD', 0.32),      # Tunisian Dinar - 1 TND = 0.32 USD
            
            # Oceania currencies
            ('AUD', 'USD', 0.66),      # Australian Dollar - 1 AUD = 0.66 USD
            ('NZD', 'USD', 0.61),      # New Zealand Dollar - 1 NZD = 0.61 USD
            
            # Additional currencies that might appear on AliExpress
            ('PKR', 'USD', 0.0036),    # Pakistani Rupee - 1 PKR = 0.0036 USD
            ('BDT', 'USD', 0.0091),    # Bangladeshi Taka - 1 BDT = 0.0091 USD
            ('LKR', 'USD', 0.0033),    # Sri Lankan Rupee - 1 LKR = 0.0033 USD
            ('NPR', 'USD', 0.0075),    # Nepalese Rupee - 1 NPR = 0.0075 USD
            ('MMK', 'USD', 0.00048),   # Myanmar Kyat - 1 MMK = 0.00048 USD
            ('KHR', 'USD', 0.00024),   # Cambodian Riel - 1 KHR = 0.00024 USD
            ('LAK', 'USD', 0.000048),  # Lao Kip - 1 LAK = 0.000048 USD
            ('BND', 'USD', 0.74),      # Brunei Dollar - 1 BND = 0.74 USD
            ('MOP', 'USD', 0.12),      # Macanese Pataca - 1 MOP = 0.12 USD
            ('MNT', 'USD', 0.00029),   # Mongolian Tugrik - 1 MNT = 0.00029 USD
            ('KZT', 'USD', 0.0022),    # Kazakhstani Tenge - 1 KZT = 0.0022 USD
            ('UZS', 'USD', 0.000082),  # Uzbekistani Som - 1 UZS = 0.000082 USD
            ('KGS', 'USD', 0.011),     # Kyrgyzstani Som - 1 KGS = 0.011 USD
            ('TJS', 'USD', 0.091),     # Tajikistani Somoni - 1 TJS = 0.091 USD
            ('AFN', 'USD', 0.014),     # Afghan Afghani - 1 AFN = 0.014 USD
            ('IRR', 'USD', 0.000024),  # Iranian Rial - 1 IRR = 0.000024 USD
            ('IQD', 'USD', 0.00068),   # Iraqi Dinar - 1 IQD = 0.00068 USD
            ('SYP', 'USD', 0.00040),   # Syrian Pound - 1 SYP = 0.00040 USD
            ('YER', 'USD', 0.0040),    # Yemeni Rial - 1 YER = 0.0040 USD
        ]
        
        # Clear existing rates first
        logger.info("🗑️ Clearing existing exchange rates...")
        cursor.execute("DELETE FROM currency_rate")
        conn.commit()
        
        # Insert all AliExpress currencies
        insert_query = """
        INSERT INTO currency_rate (from_currency, to_currency, rate, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        """
        
        cursor.executemany(insert_query, aliexpress_currencies)
        conn.commit()
        
        logger.info(f"✅ Added {len(aliexpress_currencies)} AliExpress currency rates")
        
        # Show some examples
        cursor.execute("SELECT from_currency, to_currency, rate FROM currency_rate ORDER BY from_currency LIMIT 20")
        examples = cursor.fetchall()
        
        logger.info("📊 Sample AliExpress currency rates:")
        for example in examples:
            logger.info(f"   {example[0]} → {example[1]}: {example[2]}")
        
        # Show total count
        cursor.execute("SELECT COUNT(*) FROM currency_rate")
        total_rates = cursor.fetchone()[0]
        logger.info(f"📈 Total exchange rates in database: {total_rates}")
        
        # Show conversion examples
        logger.info("\n💱 Conversion examples:")
        test_conversions = [
            ("CNY", 100, "Chinese Yuan"),
            ("JPY", 1000, "Japanese Yen"),
            ("INR", 1000, "Indian Rupee"),
            ("EUR", 100, "Euro"),
            ("GBP", 100, "British Pound"),
            ("AUD", 100, "Australian Dollar"),
        ]
        
        for currency, amount, description in test_conversions:
            cursor.execute(
                "SELECT rate FROM currency_rate WHERE from_currency = %s AND to_currency = 'USD'",
                (currency,)
            )
            result = cursor.fetchone()
            if result:
                converted = amount * result[0]
                logger.info(f"   {amount} {currency} = ${converted:.2f} USD ({description})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"❌ MySQL error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error adding AliExpress currencies: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Adding all AliExpress currencies to USD...")
    
    success = add_aliexpress_currencies()
    
    if success:
        logger.info("✅ AliExpress currencies added successfully!")
        logger.info("🌍 Now supporting currencies from:")
        logger.info("   🇨🇳 China (CNY)")
        logger.info("   🇯🇵 Japan (JPY)")
        logger.info("   🇰🇷 South Korea (KRW)")
        logger.info("   🇮🇳 India (INR)")
        logger.info("   🇹🇭 Thailand (THB)")
        logger.info("   🇻🇳 Vietnam (VND)")
        logger.info("   🇮🇩 Indonesia (IDR)")
        logger.info("   🇵🇭 Philippines (PHP)")
        logger.info("   🇲🇾 Malaysia (MYR)")
        logger.info("   🇸🇬 Singapore (SGD)")
        logger.info("   🇭🇰 Hong Kong (HKD)")
        logger.info("   🇹🇼 Taiwan (TWD)")
        logger.info("   🇦🇪 UAE (AED)")
        logger.info("   🇸🇦 Saudi Arabia (SAR)")
        logger.info("   🇰🇼 Kuwait (KWD)")
        logger.info("   🇧🇭 Bahrain (BHD)")
        logger.info("   🇴🇲 Oman (OMR)")
        logger.info("   🇯🇴 Jordan (JOD)")
        logger.info("   🇱🇧 Lebanon (LBP)")
        logger.info("   🇮🇱 Israel (ILS)")
        logger.info("   🇹🇷 Turkey (TRY)")
        logger.info("   🇪🇺 Europe (EUR)")
        logger.info("   🇬🇧 United Kingdom (GBP)")
        logger.info("   🇨🇭 Switzerland (CHF)")
        logger.info("   🇸🇪 Sweden (SEK)")
        logger.info("   🇳🇴 Norway (NOK)")
        logger.info("   🇩🇰 Denmark (DKK)")
        logger.info("   🇵🇱 Poland (PLN)")
        logger.info("   🇨🇿 Czech Republic (CZK)")
        logger.info("   🇭🇺 Hungary (HUF)")
        logger.info("   🇷🇺 Russia (RUB)")
        logger.info("   🇺🇦 Ukraine (UAH)")
        logger.info("   🇨🇦 Canada (CAD)")
        logger.info("   🇲🇽 Mexico (MXN)")
        logger.info("   🇧🇷 Brazil (BRL)")
        logger.info("   🇦🇷 Argentina (ARS)")
        logger.info("   🇨🇱 Chile (CLP)")
        logger.info("   🇨🇴 Colombia (COP)")
        logger.info("   🇵🇪 Peru (PEN)")
        logger.info("   🇿🇦 South Africa (ZAR)")
        logger.info("   🇪🇬 Egypt (EGP)")
        logger.info("   🇳🇬 Nigeria (NGN)")
        logger.info("   🇰🇪 Kenya (KES)")
        logger.info("   🇲🇦 Morocco (MAD)")
        logger.info("   🇹🇳 Tunisia (TND)")
        logger.info("   🇦🇺 Australia (AUD)")
        logger.info("   🇳🇿 New Zealand (NZD)")
        logger.info("   And many more...")
    else:
        logger.error("❌ Failed to add AliExpress currencies")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
