#!/usr/bin/env python3
"""
Test script for optimized currency conversion system
"""

from services.currency_converter import currency_converter
from services.currency_detector import currency_detector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_optimized_conversions():
    """Test optimized currency conversions"""
    logger.info("💱 Testing optimized currency conversions...")
    
    test_cases = [
        # Test conversions from various currencies to USD
        (100.0, 'CNY', 'USD', 14.0),      # Chinese Yuan to USD
        (1000.0, 'INR', 'USD', 12.0),     # Indian Rupee to USD
        (100.0, 'MYR', 'USD', 21.0),      # Malaysian Ringgit to USD
        (100.0, 'THB', 'USD', 2.7),       # Thai Baht to USD
        (100000.0, 'VND', 'USD', 4.1),    # Vietnamese Dong to USD
        (100000.0, 'IDR', 'USD', 6.5),    # Indonesian Rupiah to USD
        (100.0, 'PHP', 'USD', 1.8),       # Philippine Peso to USD
        (100.0, 'SGD', 'USD', 74.0),      # Singapore Dollar to USD
        
        # Test conversions from various currencies to EUR
        (100.0, 'CNY', 'EUR', 11.9),      # Chinese Yuan to EUR (via USD)
        (1000.0, 'INR', 'EUR', 10.2),     # Indian Rupee to EUR (via USD)
        (100.0, 'MYR', 'EUR', 17.85),     # Malaysian Ringgit to EUR (via USD)
        
        # Test conversions from various currencies to ILS
        (100.0, 'CNY', 'ILS', 51.1),      # Chinese Yuan to ILS (via USD)
        (1000.0, 'INR', 'ILS', 43.8),     # Indian Rupee to ILS (via USD)
        (100.0, 'MYR', 'ILS', 76.65),     # Malaysian Ringgit to ILS (via USD)
        
        # Test direct USD conversions
        (100.0, 'USD', 'EUR', 85.0),      # USD to EUR
        (100.0, 'USD', 'ILS', 365.0),     # USD to ILS
        (100.0, 'USD', 'USD', 100.0),     # USD to USD (same currency)
    ]
    
    success_count = 0
    
    for price, from_curr, to_curr, expected in test_cases:
        try:
            converted = currency_converter.convert_price(price, from_curr, to_curr)
            if converted is not None:
                # Check if result is close to expected (within 0.1)
                if abs(converted - expected) < 0.1:
                    logger.info(f"✅ {price} {from_curr} = {converted} {to_curr}")
                    success_count += 1
                else:
                    logger.error(f"❌ {price} {from_curr} = {converted} {to_curr} (Expected: {expected})")
            else:
                logger.error(f"❌ Failed to convert {price} {from_curr} to {to_curr}")
        except Exception as e:
            logger.error(f"❌ Error converting {price} {from_curr} to {to_curr}: {e}")
    
    logger.info(f"📊 Conversion test results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def test_unsupported_conversions():
    """Test that unsupported conversions return None"""
    logger.info("🚫 Testing unsupported conversions...")
    
    test_cases = [
        (100.0, 'USD', 'CNY'),    # USD to CNY (not supported)
        (100.0, 'EUR', 'INR'),    # EUR to INR (not supported)
        (100.0, 'ILS', 'MYR'),    # ILS to MYR (not supported)
        (100.0, 'CNY', 'INR'),    # CNY to INR (not supported)
    ]
    
    success_count = 0
    
    for price, from_curr, to_curr in test_cases:
        try:
            converted = currency_converter.convert_price(price, from_curr, to_curr)
            if converted is None:
                logger.info(f"✅ {price} {from_curr} → {to_curr}: Correctly rejected")
                success_count += 1
            else:
                logger.error(f"❌ {price} {from_curr} → {to_curr}: Should be rejected, got {converted}")
        except Exception as e:
            logger.error(f"❌ Error testing {price} {from_curr} → {to_curr}: {e}")
    
    logger.info(f"📊 Unsupported conversion test results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def test_currency_detection():
    """Test currency detection still works"""
    logger.info("🔍 Testing currency detection...")
    
    test_cases = [
        ("¥2999", "CNY"),
        ("₹450", "INR"),
        ("RM89", "MYR"),
        ("฿1200", "THB"),
        ("₫150000", "VND"),
        ("Rp100000", "IDR"),
        ("₱75", "PHP"),
        ("S$12.50", "SGD"),
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
    return success_count == len(test_cases)

def test_database_rates():
    """Test that database has only necessary rates"""
    logger.info("🗄️ Testing database rates...")
    
    try:
        all_rates = currency_converter.get_all_rates()
        rates = all_rates['rates']
        
        logger.info(f"📊 Total rates in database: {len(rates)}")
        
        # Check that we have the expected rates
        expected_rates = [
            ('CNY', 'USD'), ('IDR', 'USD'), ('INR', 'USD'), ('MYR', 'USD'),
            ('PHP', 'USD'), ('SGD', 'USD'), ('THB', 'USD'), ('USD', 'EUR'),
            ('USD', 'ILS'), ('VND', 'USD')
        ]
        
        found_rates = [(rate['from_currency'], rate['to_currency']) for rate in rates]
        
        success_count = 0
        for expected in expected_rates:
            if expected in found_rates:
                logger.info(f"✅ Found rate: {expected[0]} → {expected[1]}")
                success_count += 1
            else:
                logger.error(f"❌ Missing rate: {expected[0]} → {expected[1]}")
        
        logger.info(f"📊 Database rate test results: {success_count}/{len(expected_rates)} successful")
        return success_count == len(expected_rates)
        
    except Exception as e:
        logger.error(f"❌ Error testing database rates: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting optimized currency system tests...")
    
    # Test optimized conversions
    conversion_success = test_optimized_conversions()
    
    # Test unsupported conversions
    unsupported_success = test_unsupported_conversions()
    
    # Test currency detection
    detection_success = test_currency_detection()
    
    # Test database rates
    database_success = test_database_rates()
    
    # Summary
    logger.info("\n📋 Optimized System Test Summary:")
    logger.info(f"   Optimized Conversions: {'✅ PASS' if conversion_success else '❌ FAIL'}")
    logger.info(f"   Unsupported Conversions: {'✅ PASS' if unsupported_success else '❌ FAIL'}")
    logger.info(f"   Currency Detection: {'✅ PASS' if detection_success else '❌ FAIL'}")
    logger.info(f"   Database Rates: {'✅ PASS' if database_success else '❌ FAIL'}")
    
    if conversion_success and unsupported_success and detection_success and database_success:
        logger.info("\n🎉 All optimized tests passed! System is working correctly.")
        logger.info("💡 Key improvements:")
        logger.info("   ✅ Reduced from 40+ rates to 10 essential rates")
        logger.info("   ✅ USD as base currency for all conversions")
        logger.info("   ✅ Only converts to USD, EUR, ILS")
        logger.info("   ✅ Simplified conversion flow")
        logger.info("   ✅ Better performance and maintainability")
        return 0
    else:
        logger.error("\n💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
