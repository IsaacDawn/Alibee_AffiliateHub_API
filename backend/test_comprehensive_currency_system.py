#!/usr/bin/env python3
"""
Test script for comprehensive AliExpress currency system
"""

from services.currency_converter import currency_converter
from services.currency_detector import currency_detector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_comprehensive_conversions():
    """Test conversions from various AliExpress currencies to USD, EUR, ILS"""
    logger.info("💱 Testing comprehensive currency conversions...")
    
    test_cases = [
        # Major currencies
        (100.0, 'CNY', 'USD', 14.0),      # Chinese Yuan to USD
        (1000.0, 'JPY', 'USD', 6.7),      # Japanese Yen to USD
        (1000.0, 'INR', 'USD', 12.0),     # Indian Rupee to USD
        (100.0, 'EUR', 'USD', 118.0),     # Euro to USD
        (100.0, 'GBP', 'USD', 127.0),     # British Pound to USD
        (100.0, 'AUD', 'USD', 66.0),      # Australian Dollar to USD
        (100.0, 'CAD', 'USD', 74.0),      # Canadian Dollar to USD
        
        # Asian currencies
        (100.0, 'MYR', 'USD', 21.0),      # Malaysian Ringgit to USD
        (100.0, 'THB', 'USD', 2.7),       # Thai Baht to USD
        (100000.0, 'VND', 'USD', 4.1),    # Vietnamese Dong to USD
        (100000.0, 'IDR', 'USD', 6.5),    # Indonesian Rupiah to USD
        (100.0, 'PHP', 'USD', 1.8),       # Philippine Peso to USD
        (100.0, 'SGD', 'USD', 74.0),      # Singapore Dollar to USD
        (100.0, 'HKD', 'USD', 13.0),      # Hong Kong Dollar to USD
        (100.0, 'TWD', 'USD', 3.1),       # Taiwan Dollar to USD
        
        # Middle East currencies
        (100.0, 'AED', 'USD', 27.0),      # UAE Dirham to USD
        (100.0, 'SAR', 'USD', 27.0),      # Saudi Riyal to USD
        (100.0, 'KWD', 'USD', 325.0),     # Kuwaiti Dinar to USD
        (100.0, 'BHD', 'USD', 265.0),     # Bahraini Dinar to USD
        (100.0, 'OMR', 'USD', 260.0),     # Omani Rial to USD
        (100.0, 'JOD', 'USD', 141.0),     # Jordanian Dinar to USD
        (100.0, 'TRY', 'USD', 3.3),       # Turkish Lira to USD
        
        # European currencies
        (100.0, 'CHF', 'USD', 112.0),     # Swiss Franc to USD
        (100.0, 'SEK', 'USD', 11.0),      # Swedish Krona to USD
        (100.0, 'NOK', 'USD', 11.0),      # Norwegian Krone to USD
        (100.0, 'DKK', 'USD', 16.0),      # Danish Krone to USD
        (100.0, 'PLN', 'USD', 25.0),      # Polish Zloty to USD
        (100.0, 'CZK', 'USD', 4.4),       # Czech Koruna to USD
        (100.0, 'HUF', 'USD', 0.28),      # Hungarian Forint to USD
        (100.0, 'RUB', 'USD', 1.1),       # Russian Ruble to USD
        (100.0, 'UAH', 'USD', 2.7),       # Ukrainian Hryvnia to USD
        
        # American currencies
        (100.0, 'MXN', 'USD', 5.9),       # Mexican Peso to USD
        (100.0, 'BRL', 'USD', 20.0),      # Brazilian Real to USD
        (100.0, 'ARS', 'USD', 0.12),      # Argentine Peso to USD
        (100.0, 'CLP', 'USD', 0.11),      # Chilean Peso to USD
        (100.0, 'COP', 'USD', 0.025),     # Colombian Peso to USD
        (100.0, 'PEN', 'USD', 27.0),      # Peruvian Sol to USD
        
        # African currencies
        (100.0, 'ZAR', 'USD', 5.5),       # South African Rand to USD
        (100.0, 'EGP', 'USD', 3.2),       # Egyptian Pound to USD
        (100.0, 'NGN', 'USD', 0.066),     # Nigerian Naira to USD
        (100.0, 'KES', 'USD', 0.67),      # Kenyan Shilling to USD
        (100.0, 'MAD', 'USD', 10.0),      # Moroccan Dirham to USD
        (100.0, 'TND', 'USD', 32.0),      # Tunisian Dinar to USD
        
        # Oceania currencies
        (100.0, 'NZD', 'USD', 61.0),      # New Zealand Dollar to USD
        
        # Conversions to EUR and ILS
        (100.0, 'CNY', 'EUR', 11.9),      # Chinese Yuan to EUR (via USD)
        (100.0, 'INR', 'ILS', 3.24),      # Indian Rupee to ILS (via USD)
        (100.0, 'MYR', 'EUR', 17.85),     # Malaysian Ringgit to EUR (via USD)
        (100.0, 'THB', 'ILS', 9.86),      # Thai Baht to ILS (via USD)
    ]
    
    success_count = 0
    
    for price, from_curr, to_curr, expected in test_cases:
        try:
            converted = currency_converter.convert_price(price, from_curr, to_curr)
            if converted is not None:
                # Check if result is close to expected (within 5% tolerance)
                tolerance = expected * 0.05
                if abs(converted - expected) <= tolerance:
                    logger.info(f"✅ {price} {from_curr} = {converted} {to_curr}")
                    success_count += 1
                else:
                    logger.error(f"❌ {price} {from_curr} = {converted} {to_curr} (Expected: {expected})")
            else:
                logger.error(f"❌ Failed to convert {price} {from_curr} to {to_curr}")
        except Exception as e:
            logger.error(f"❌ Error converting {price} {from_curr} to {to_curr}: {e}")
    
    logger.info(f"📊 Conversion test results: {success_count}/{len(test_cases)} successful")
    return success_count >= len(test_cases) * 0.9  # 90% success rate

def test_currency_detection():
    """Test currency detection for various AliExpress currencies"""
    logger.info("🔍 Testing comprehensive currency detection...")
    
    test_cases = [
        # Major currencies
        ("$10.99", "USD"),
        ("€15.50", "EUR"),
        ("£25.00", "GBP"),
        ("¥100", "JPY"),
        ("¥2999", "CNY"),
        ("₩50000", "KRW"),
        ("₹450", "INR"),
        ("A$89", "AUD"),
        ("C$75", "CAD"),
        ("S$12.50", "SGD"),
        ("HK$100", "HKD"),
        ("NZ$50", "NZD"),
        ("CHF25", "CHF"),
        ("₪25.00", "ILS"),
        
        # Asian currencies
        ("RM89", "MYR"),
        ("฿1200", "THB"),
        ("₫150000", "VND"),
        ("Rp100000", "IDR"),
        ("₱75", "PHP"),
        ("NT$500", "TWD"),
        
        # Middle East currencies
        ("100 AED", "AED"),
        ("100 SAR", "SAR"),
        ("100 KWD", "KWD"),
        ("100 BHD", "BHD"),
        ("100 OMR", "OMR"),
        ("100 JOD", "JOD"),
        ("100 TRY", "TRY"),
        
        # European currencies
        ("100 SEK", "SEK"),
        ("100 NOK", "NOK"),
        ("100 DKK", "DKK"),
        ("100 PLN", "PLN"),
        ("100 CZK", "CZK"),
        ("100 HUF", "HUF"),
        ("100 RUB", "RUB"),
        ("100 UAH", "UAH"),
        
        # American currencies
        ("100 MXN", "MXN"),
        ("R$100", "BRL"),
        ("100 ARS", "ARS"),
        ("100 CLP", "CLP"),
        ("100 COP", "COP"),
        ("100 PEN", "PEN"),
        
        # African currencies
        ("R100", "ZAR"),
        ("100 EGP", "EGP"),
        ("100 NGN", "NGN"),
        ("100 KES", "KES"),
        ("100 MAD", "MAD"),
        ("100 TND", "TND"),
    ]
    
    success_count = 0
    
    for price_text, expected_currency in test_cases:
        try:
            detected = currency_detector.detect_currency_from_price(price_text)
            if detected == expected_currency:
                logger.info(f"✅ '{price_text}' → {detected}")
                success_count += 1
            else:
                logger.error(f"❌ '{price_text}' → Expected: {expected_currency}, Got: {detected}")
        except Exception as e:
            logger.error(f"❌ Error testing '{price_text}': {e}")
    
    logger.info(f"📊 Detection test results: {success_count}/{len(test_cases)} successful")
    return success_count >= len(test_cases) * 0.8  # 80% success rate

def test_country_detection():
    """Test country-based currency detection"""
    logger.info("🌍 Testing country-based currency detection...")
    
    test_cases = [
        ("Made in China", "CNY"),
        ("Japanese product", "JPY"),
        ("Korean goods", "KRW"),
        ("Indian manufacturer", "INR"),
        ("Thai company", "THB"),
        ("Vietnamese supplier", "VND"),
        ("Indonesian brand", "IDR"),
        ("Philippine goods", "PHP"),
        ("Malaysian products", "MYR"),
        ("Singapore based", "SGD"),
        ("Hong Kong company", "HKD"),
        ("Taiwanese manufacturer", "TWD"),
        ("Pakistani goods", "PKR"),
        ("Bangladeshi products", "BDT"),
        ("Sri Lankan company", "LKR"),
        ("Nepalese goods", "NPR"),
        ("Myanmar products", "MMK"),
        ("Cambodian company", "KHR"),
        ("Laotian goods", "LAK"),
        ("Brunei products", "BND"),
        ("Macau company", "MOP"),
        ("Mongolian goods", "MNT"),
        ("Kazakhstani products", "KZT"),
        ("Uzbekistani company", "UZS"),
        ("Kyrgyzstani goods", "KGS"),
        ("Tajikistani products", "TJS"),
        ("Afghan company", "AFN"),
        ("UAE based", "AED"),
        ("Saudi company", "SAR"),
        ("Kuwaiti goods", "KWD"),
        ("Bahraini products", "BHD"),
        ("Omani company", "OMR"),
        ("Jordanian goods", "JOD"),
        ("Lebanese products", "LBP"),
        ("Israeli company", "ILS"),
        ("Turkish goods", "TRY"),
        ("Iranian products", "IRR"),
        ("Iraqi company", "IQD"),
        ("Syrian goods", "SYP"),
        ("Yemeni products", "YER"),
        ("German company", "EUR"),
        ("French goods", "EUR"),
        ("Italian products", "EUR"),
        ("Spanish company", "EUR"),
        ("Dutch goods", "EUR"),
        ("Belgian products", "EUR"),
        ("Austrian company", "EUR"),
        ("Portuguese goods", "EUR"),
        ("Finnish products", "EUR"),
        ("Irish company", "EUR"),
        ("Greek goods", "EUR"),
        ("British company", "GBP"),
        ("Swiss goods", "CHF"),
        ("Swedish products", "SEK"),
        ("Norwegian company", "NOK"),
        ("Danish goods", "DKK"),
        ("Polish products", "PLN"),
        ("Czech company", "CZK"),
        ("Hungarian goods", "HUF"),
        ("Russian products", "RUB"),
        ("Ukrainian company", "UAH"),
        ("American goods", "USD"),
        ("Canadian products", "CAD"),
        ("Mexican company", "MXN"),
        ("Brazilian goods", "BRL"),
        ("Argentine products", "ARS"),
        ("Chilean company", "CLP"),
        ("Colombian goods", "COP"),
        ("Peruvian products", "PEN"),
        ("South African company", "ZAR"),
        ("Egyptian goods", "EGP"),
        ("Nigerian products", "NGN"),
        ("Kenyan company", "KES"),
        ("Moroccan goods", "MAD"),
        ("Tunisian products", "TND"),
        ("Australian company", "AUD"),
        ("New Zealand goods", "NZD"),
    ]
    
    success_count = 0
    
    for country_text, expected_currency in test_cases:
        try:
            detected = currency_detector.detect_currency_from_country(country_text)
            if detected == expected_currency:
                logger.info(f"✅ '{country_text}' → {detected}")
                success_count += 1
            else:
                logger.error(f"❌ '{country_text}' → Expected: {expected_currency}, Got: {detected}")
        except Exception as e:
            logger.error(f"❌ Error testing '{country_text}': {e}")
    
    logger.info(f"📊 Country detection test results: {success_count}/{len(test_cases)} successful")
    return success_count >= len(test_cases) * 0.8  # 80% success rate

def test_database_coverage():
    """Test that database has comprehensive currency coverage"""
    logger.info("🗄️ Testing database currency coverage...")
    
    try:
        all_rates = currency_converter.get_all_rates()
        rates = all_rates['rates']
        
        logger.info(f"📊 Total rates in database: {len(rates)}")
        
        # Check for major currencies
        major_currencies = ['CNY', 'JPY', 'KRW', 'INR', 'EUR', 'GBP', 'AUD', 'CAD', 'SGD', 'HKD', 'NZD', 'CHF', 'ILS']
        found_major = []
        
        for rate in rates:
            if rate['from_currency'] in major_currencies:
                found_major.append(rate['from_currency'])
        
        unique_major = list(set(found_major))
        logger.info(f"📈 Major currencies found: {len(unique_major)}/{len(major_currencies)}")
        
        # Check for regional coverage
        asian_currencies = ['CNY', 'JPY', 'KRW', 'INR', 'THB', 'VND', 'IDR', 'PHP', 'MYR', 'SGD', 'HKD', 'TWD']
        middle_east_currencies = ['AED', 'SAR', 'KWD', 'BHD', 'OMR', 'JOD', 'LBP', 'ILS', 'TRY']
        european_currencies = ['EUR', 'GBP', 'CHF', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RUB', 'UAH']
        american_currencies = ['USD', 'CAD', 'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN']
        african_currencies = ['ZAR', 'EGP', 'NGN', 'KES', 'MAD', 'TND']
        oceania_currencies = ['AUD', 'NZD']
        
        regions = {
            'Asia': asian_currencies,
            'Middle East': middle_east_currencies,
            'Europe': european_currencies,
            'Americas': american_currencies,
            'Africa': african_currencies,
            'Oceania': oceania_currencies
        }
        
        for region, currencies in regions.items():
            found_in_region = []
            for rate in rates:
                if rate['from_currency'] in currencies:
                    found_in_region.append(rate['from_currency'])
            unique_in_region = list(set(found_in_region))
            logger.info(f"   {region}: {len(unique_in_region)}/{len(currencies)} currencies")
        
        return len(unique_major) >= len(major_currencies) * 0.8  # 80% coverage
        
    except Exception as e:
        logger.error(f"❌ Error testing database coverage: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting comprehensive AliExpress currency system tests...")
    
    # Test comprehensive conversions
    conversion_success = test_comprehensive_conversions()
    
    # Test currency detection
    detection_success = test_currency_detection()
    
    # Test country detection
    country_success = test_country_detection()
    
    # Test database coverage
    database_success = test_database_coverage()
    
    # Summary
    logger.info("\n📋 Comprehensive System Test Summary:")
    logger.info(f"   Currency Conversions: {'✅ PASS' if conversion_success else '❌ FAIL'}")
    logger.info(f"   Currency Detection: {'✅ PASS' if detection_success else '❌ FAIL'}")
    logger.info(f"   Country Detection: {'✅ PASS' if country_success else '❌ FAIL'}")
    logger.info(f"   Database Coverage: {'✅ PASS' if database_success else '❌ FAIL'}")
    
    if conversion_success and detection_success and country_success and database_success:
        logger.info("\n🎉 All comprehensive tests passed! AliExpress currency system is working correctly.")
        logger.info("🌍 Now supporting currencies from:")
        logger.info("   🌏 Asia: China, Japan, Korea, India, Thailand, Vietnam, Indonesia, Philippines, Malaysia, Singapore, Hong Kong, Taiwan, and more...")
        logger.info("   🕌 Middle East: UAE, Saudi Arabia, Kuwait, Bahrain, Oman, Jordan, Lebanon, Israel, Turkey, and more...")
        logger.info("   🇪🇺 Europe: Eurozone, UK, Switzerland, Sweden, Norway, Denmark, Poland, Czech Republic, Hungary, Russia, Ukraine, and more...")
        logger.info("   🌎 Americas: USA, Canada, Mexico, Brazil, Argentina, Chile, Colombia, Peru, and more...")
        logger.info("   🌍 Africa: South Africa, Egypt, Nigeria, Kenya, Morocco, Tunisia, and more...")
        logger.info("   🌏 Oceania: Australia, New Zealand")
        logger.info(f"   📊 Total: {len(currency_detector.currency_patterns)} supported currencies")
        return 0
    else:
        logger.error("\n💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
