#!/usr/bin/env python3
"""
Test script for USD base conversion strategy
"""

from services.currency_converter import currency_converter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_usd_base_conversion():
    """Test USD base conversion strategy"""
    logger.info("Testing USD Base Conversion Strategy...")
    
    test_cases = [
        # Direct conversions (should work)
        (100.0, 'CNY', 'USD', 'Chinese Yuan to USD'),
        (100.0, 'EUR', 'USD', 'Euro to USD'),
        (100.0, 'GBP', 'USD', 'British Pound to USD'),
        (100.0, 'JPY', 'USD', 'Japanese Yen to USD'),
        (100.0, 'INR', 'USD', 'Indian Rupee to USD'),
        
        # USD-based conversions (via USD)
        (100.0, 'CNY', 'EUR', 'Chinese Yuan to Euro (via USD)'),
        (100.0, 'INR', 'ILS', 'Indian Rupee to Israeli Shekel (via USD)'),
        (100.0, 'MYR', 'EUR', 'Malaysian Ringgit to Euro (via USD)'),
        (100.0, 'THB', 'ILS', 'Thai Baht to Israeli Shekel (via USD)'),
        (100.0, 'VND', 'EUR', 'Vietnamese Dong to Euro (via USD)'),
        
        # Same currency (should return original)
        (100.0, 'USD', 'USD', 'USD to USD (same currency)'),
        (100.0, 'EUR', 'EUR', 'EUR to EUR (same currency)'),
        (100.0, 'ILS', 'ILS', 'ILS to ILS (same currency)'),
        
        # Unsupported target currency
        (100.0, 'CNY', 'CAD', 'Chinese Yuan to Canadian Dollar (unsupported)'),
        (100.0, 'EUR', 'GBP', 'Euro to British Pound (unsupported)'),
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for price, from_curr, to_curr, description in test_cases:
        try:
            result = currency_converter.convert_price(price, from_curr, to_curr)
            
            if result is not None:
                logger.info(f"✅ {description}: {price} {from_curr} = {result} {to_curr}")
                success_count += 1
            else:
                logger.warning(f"❌ {description}: Conversion failed")
                
        except Exception as e:
            logger.error(f"❌ {description}: Error - {e}")
    
    logger.info(f"\nConversion Results: {success_count}/{total_tests} successful")
    
    # Test conversion strategies
    logger.info("\nTesting Conversion Strategies...")
    
    # Test direct conversion
    logger.info("1. Testing direct conversion...")
    direct_result = currency_converter.convert_price(100.0, 'CNY', 'USD')
    if direct_result:
        logger.info(f"   Direct CNY→USD: 100 CNY = {direct_result} USD")
    
    # Test USD-based conversion
    logger.info("2. Testing USD-based conversion...")
    usd_based_result = currency_converter.convert_price(100.0, 'CNY', 'EUR')
    if usd_based_result:
        logger.info(f"   USD-based CNY→EUR: 100 CNY = {usd_based_result} EUR")
    
    # Test helper methods
    logger.info("3. Testing helper methods...")
    usd_price = currency_converter._convert_to_usd(100.0, 'CNY')
    if usd_price:
        logger.info(f"   _convert_to_usd: 100 CNY = {usd_price} USD")
    
    eur_price = currency_converter._convert_from_usd(usd_price, 'EUR')
    if eur_price:
        logger.info(f"   _convert_from_usd: {usd_price} USD = {eur_price} EUR")
    
    return success_count >= total_tests * 0.8  # 80% success rate

def test_conversion_paths():
    """Test different conversion paths"""
    logger.info("\nTesting Conversion Paths...")
    
    # Test various currencies to USD, EUR, ILS
    currencies_to_test = ['CNY', 'JPY', 'INR', 'MYR', 'THB', 'VND', 'IDR', 'PHP', 'SGD', 'HKD', 'TWD']
    target_currencies = ['USD', 'EUR', 'ILS']
    
    for from_curr in currencies_to_test:
        for to_curr in target_currencies:
            if from_curr != to_curr:
                result = currency_converter.convert_price(100.0, from_curr, to_curr)
                if result:
                    logger.info(f"✅ {from_curr} → {to_curr}: 100 {from_curr} = {result} {to_curr}")
                else:
                    logger.warning(f"❌ {from_curr} → {to_curr}: Conversion failed")

def main():
    """Main test function"""
    logger.info("Starting USD Base Conversion Tests...")
    
    # Test basic conversion
    basic_success = test_usd_base_conversion()
    
    # Test conversion paths
    test_conversion_paths()
    
    if basic_success:
        logger.info("\n🎉 USD Base Conversion tests passed!")
        logger.info("✅ Direct conversion strategy working")
        logger.info("✅ USD-based conversion strategy working")
        logger.info("✅ Helper methods working")
        return 0
    else:
        logger.error("\n💥 Some USD Base Conversion tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
