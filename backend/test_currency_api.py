#!/usr/bin/env python3
"""
Test script for currency API endpoints
"""

import requests
import json

def test_currency_conversion():
    """Test currency conversion API"""
    print("🧪 Testing Currency Conversion API...")
    
    try:
        response = requests.post('http://localhost:8000/api/currency/convert', json={
            'price': 100.0,
            'from_currency': 'CNY',
            'to_currency': 'USD'
        })
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Original: {data['original_price']} {data['from_currency']}")
            print(f"✅ Converted: {data['converted_price']} {data['to_currency']}")
            print(f"✅ Rate: {data['exchange_rate']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_currency_detection():
    """Test currency detection API"""
    print("\n🔍 Testing Currency Detection API...")
    
    try:
        response = requests.post('http://localhost:8000/api/currency/detect', json={
            'text': '¥2999 Chinese Smartphone'
        })
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detected Currency: {data['detected_currency']}")
            print(f"✅ Detected Price: {data['detected_price']}")
            print(f"✅ Confidence: {data['confidence']}")
            print(f"✅ Method: {data['detection_method']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_multiple_conversions():
    """Test multiple currency conversions"""
    print("\n💱 Testing Multiple Currency Conversions...")
    
    test_cases = [
        (100.0, 'CNY', 'USD'),
        (100.0, 'EUR', 'USD'),
        (100.0, 'GBP', 'USD'),
        (100.0, 'JPY', 'USD'),
        (100.0, 'INR', 'USD'),
        (100.0, 'CNY', 'EUR'),
        (100.0, 'CNY', 'ILS'),
    ]
    
    success_count = 0
    
    for price, from_curr, to_curr in test_cases:
        try:
            response = requests.post('http://localhost:8000/api/currency/convert', json={
                'price': price,
                'from_currency': from_curr,
                'to_currency': to_curr
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {price} {from_curr} = {data['converted_price']} {to_curr}")
                success_count += 1
            else:
                print(f"❌ Failed: {price} {from_curr} → {to_curr}")
        except Exception as e:
            print(f"❌ Exception: {price} {from_curr} → {to_curr}: {e}")
    
    print(f"\n📊 Success Rate: {success_count}/{len(test_cases)}")
    return success_count == len(test_cases)

def main():
    """Main test function"""
    print("🚀 Starting Currency API Tests...\n")
    
    # Test currency conversion
    conversion_success = test_currency_conversion()
    
    # Test currency detection
    detection_success = test_currency_detection()
    
    # Test multiple conversions
    multiple_success = test_multiple_conversions()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   Currency Conversion: {'✅ PASS' if conversion_success else '❌ FAIL'}")
    print(f"   Currency Detection: {'✅ PASS' if detection_success else '❌ FAIL'}")
    print(f"   Multiple Conversions: {'✅ PASS' if multiple_success else '❌ FAIL'}")
    
    if conversion_success and detection_success and multiple_success:
        print("\n🎉 All currency API tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())
