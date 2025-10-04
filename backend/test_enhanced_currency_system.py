#!/usr/bin/env python3
"""
Test script for enhanced currency conversion system with multiple currencies
"""

from services.currency_converter import currency_converter
from services.currency_detector import currency_detector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_currency_detection():
    """Test currency detection functionality"""
    logger.info("🔍 Testing currency detection...")
    
    test_cases = [
        # Price text tests
        ("$10.99", "USD"),
        ("€15.50", "EUR"),
        ("₪25.00", "ILS"),
        ("¥100", "CNY"),
        ("₹500", "INR"),
        ("RM20.50", "MYR"),
        ("฿150", "THB"),
        ("₫25000", "VND"),
        ("Rp100000", "IDR"),
        ("₱75.00", "PHP"),
        ("S$12.50", "SGD"),
        
        # Country text tests
        ("Made in China", "CNY"),
        ("Indian product", "INR"),
        ("Malaysian goods", "MYR"),
        ("Thai manufacturer", "THB"),
        ("Vietnamese company", "VND"),
        ("Indonesian supplier", "IDR"),
        ("Philippine brand", "PHP"),
        ("Singapore based", "SGD"),
    ]
    
    success_count = 0
    
    for test_input, expected_currency in test_cases:
        try:
            if "$" in test_input or "€" in test_input or "₪" in test_input or "¥" in test_input or "₹" in test_input or "RM" in test_input or "฿" in test_input or "₫" in test_input or "Rp" in test_input or "₱" in test_input or "S$" in test_input:
                detected = currency_detector.detect_currency_from_price(test_input)
            else:
                detected = currency_detector.detect_currency_from_country(test_input)
            
            if detected == expected_currency:
                logger.info(f"✅ '{test_input}' → {detected}")
                success_count += 1
            else:
                logger.error(f"❌ '{test_input}' → Expected: {expected_currency}, Got: {detected}")
        except Exception as e:
            logger.error(f"❌ Error testing '{test_input}': {e}")
    
    logger.info(f"📊 Detection test results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def test_currency_conversions():
    """Test currency conversions with new currencies"""
    logger.info("💱 Testing currency conversions...")
    
    test_cases = [
        # USD conversions
        (100.0, 'USD', 'CNY'),
        (100.0, 'USD', 'INR'),
        (100.0, 'USD', 'MYR'),
        (100.0, 'USD', 'THB'),
        (100.0, 'USD', 'VND'),
        (100.0, 'USD', 'IDR'),
        (100.0, 'USD', 'PHP'),
        (100.0, 'USD', 'SGD'),
        
        # CNY conversions
        (100.0, 'CNY', 'USD'),
        (100.0, 'CNY', 'EUR'),
        (100.0, 'CNY', 'ILS'),
        (100.0, 'CNY', 'INR'),
        (100.0, 'CNY', 'MYR'),
        
        # INR conversions
        (1000.0, 'INR', 'USD'),
        (1000.0, 'INR', 'EUR'),
        (1000.0, 'INR', 'ILS'),
        (1000.0, 'INR', 'CNY'),
        (1000.0, 'INR', 'MYR'),
        
        # MYR conversions
        (100.0, 'MYR', 'USD'),
        (100.0, 'MYR', 'EUR'),
        (100.0, 'MYR', 'ILS'),
        (100.0, 'MYR', 'CNY'),
        (100.0, 'MYR', 'INR'),
    ]
    
    success_count = 0
    
    for price, from_curr, to_curr in test_cases:
        try:
            converted = currency_converter.convert_price(price, from_curr, to_curr)
            if converted is not None:
                logger.info(f"✅ {price} {from_curr} = {converted} {to_curr}")
                success_count += 1
            else:
                logger.error(f"❌ Failed to convert {price} {from_curr} to {to_curr}")
        except Exception as e:
            logger.error(f"❌ Error converting {price} {from_curr} to {to_curr}: {e}")
    
    logger.info(f"📊 Conversion test results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def test_product_currency_detection():
    """Test currency detection from product data"""
    logger.info("🛍️ Testing product currency detection...")
    
    test_products = [
        {
            'product_title': 'Chinese Smartphone ¥2999',
            'sale_price': '¥2999',
            'shop_title': 'China Electronics Store'
        },
        {
            'product_title': 'Indian Spices ₹450',
            'sale_price': '₹450',
            'shop_title': 'Indian Spice Company'
        },
        {
            'product_title': 'Malaysian Handbag RM89',
            'sale_price': 'RM89',
            'shop_title': 'Malaysian Fashion'
        },
        {
            'product_title': 'Thai Rice Cooker ฿1200',
            'sale_price': '฿1200',
            'shop_title': 'Thai Kitchen Appliances'
        },
        {
            'product_title': 'Vietnamese Coffee ₫150000',
            'sale_price': '₫150000',
            'shop_title': 'Vietnamese Coffee Co'
        },
    ]
    
    success_count = 0
    
    for product in test_products:
        try:
            detected = currency_detector.detect_currency_from_product(product)
            if detected:
                logger.info(f"✅ Product: '{product['product_title']}' → {detected}")
                success_count += 1
            else:
                logger.error(f"❌ Failed to detect currency for: '{product['product_title']}'")
        except Exception as e:
            logger.error(f"❌ Error detecting currency for product: {e}")
    
    logger.info(f"📊 Product detection test results: {success_count}/{len(test_products)} successful")
    return success_count == len(test_products)

def main():
    """Main test function"""
    logger.info("🚀 Starting enhanced currency system tests...")
    
    # Test currency detection
    detection_success = test_currency_detection()
    
    # Test currency conversions
    conversion_success = test_currency_conversions()
    
    # Test product currency detection
    product_detection_success = test_product_currency_detection()
    
    # Summary
    logger.info("\n📋 Enhanced Test Summary:")
    logger.info(f"   Currency Detection: {'✅ PASS' if detection_success else '❌ FAIL'}")
    logger.info(f"   Currency Conversions: {'✅ PASS' if conversion_success else '❌ FAIL'}")
    logger.info(f"   Product Detection: {'✅ PASS' if product_detection_success else '❌ FAIL'}")
    
    if detection_success and conversion_success and product_detection_success:
        logger.info("\n🎉 All enhanced tests passed! Multi-currency system is working correctly.")
        logger.info("🌍 Now supporting currencies from:")
        logger.info("   🇺🇸 United States (USD)")
        logger.info("   🇪🇺 Europe (EUR)")
        logger.info("   🇮🇱 Israel (ILS)")
        logger.info("   🇨🇳 China (CNY)")
        logger.info("   🇮🇳 India (INR)")
        logger.info("   🇲🇾 Malaysia (MYR)")
        logger.info("   🇹🇭 Thailand (THB)")
        logger.info("   🇻🇳 Vietnam (VND)")
        logger.info("   🇮🇩 Indonesia (IDR)")
        logger.info("   🇵🇭 Philippines (PHP)")
        logger.info("   🇸🇬 Singapore (SGD)")
        return 0
    else:
        logger.error("\n💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
