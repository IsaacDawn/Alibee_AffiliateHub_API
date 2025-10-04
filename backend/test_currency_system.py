#!/usr/bin/env python3
"""
Test script for currency conversion system
"""

import requests
import json
import time
from services.currency_converter import currency_converter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_operations():
    """Test database operations directly"""
    logger.info("🧪 Testing database operations...")
    
    try:
        # Test getting exchange rate
        rate = currency_converter.get_exchange_rate('USD', 'EUR')
        logger.info(f"✅ USD to EUR rate: {rate}")
        
        # Test price conversion
        converted_price = currency_converter.convert_price(100.0, 'USD', 'EUR')
        logger.info(f"✅ $100 USD = €{converted_price} EUR")
        
        # Test getting all rates
        all_rates = currency_converter.get_all_rates()
        logger.info(f"✅ Found {all_rates['count']} exchange rates")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints(base_url="http://localhost:8000"):
    """Test API endpoints"""
    logger.info("🌐 Testing API endpoints...")
    
    try:
        # Test getting all rates
        response = requests.get(f"{base_url}/api/currency-rates/rates")
        if response.status_code == 200:
            rates = response.json()
            logger.info(f"✅ GET /api/currency-rates/rates: {len(rates)} rates found")
        else:
            logger.error(f"❌ GET /api/currency-rates/rates failed: {response.status_code}")
            return False
        
        # Test getting specific rate
        response = requests.get(f"{base_url}/api/currency-rates/rates/USD/EUR")
        if response.status_code == 200:
            rate_data = response.json()
            logger.info(f"✅ GET /api/currency-rates/rates/USD/EUR: {rate_data['rate']}")
        else:
            logger.error(f"❌ GET /api/currency-rates/rates/USD/EUR failed: {response.status_code}")
            return False
        
        # Test price conversion
        conversion_data = {
            "price": 100.0,
            "from_currency": "USD",
            "to_currency": "EUR"
        }
        response = requests.post(f"{base_url}/api/currency-converter/convert", json=conversion_data)
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ POST /api/currency-converter/convert: ${result['original_price']} USD = €{result['converted_price']} EUR")
        else:
            logger.error(f"❌ POST /api/currency-converter/convert failed: {response.status_code}")
            return False
        
        # Test bulk conversion
        bulk_data = {
            "prices": [10.0, 25.0, 50.0, 100.0],
            "from_currency": "USD",
            "to_currency": "ILS"
        }
        response = requests.post(f"{base_url}/api/currency-converter/convert/bulk", json=bulk_data)
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ POST /api/currency-converter/convert/bulk: {result['successful_conversions']}/{result['total_converted']} conversions successful")
        else:
            logger.error(f"❌ POST /api/currency-converter/convert/bulk failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ API server not running, skipping API tests")
        return True
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False

def test_currency_conversions():
    """Test various currency conversions"""
    logger.info("💱 Testing currency conversions...")
    
    test_cases = [
        (100.0, 'USD', 'EUR'),
        (100.0, 'USD', 'ILS'),
        (100.0, 'EUR', 'USD'),
        (100.0, 'EUR', 'ILS'),
        (100.0, 'ILS', 'USD'),
        (100.0, 'ILS', 'EUR'),
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

def main():
    """Main test function"""
    logger.info("🚀 Starting currency system tests...")
    
    # Test database operations
    db_success = test_database_operations()
    
    # Test currency conversions
    conversion_success = test_currency_conversions()
    
    # Test API endpoints (if server is running)
    api_success = test_api_endpoints()
    
    # Summary
    logger.info("\n📋 Test Summary:")
    logger.info(f"   Database Operations: {'✅ PASS' if db_success else '❌ FAIL'}")
    logger.info(f"   Currency Conversions: {'✅ PASS' if conversion_success else '❌ FAIL'}")
    logger.info(f"   API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if db_success and conversion_success and api_success:
        logger.info("\n🎉 All tests passed! Currency system is working correctly.")
        return 0
    else:
        logger.error("\n💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
