#!/usr/bin/env python3
"""
Complete currency system test
"""

import requests
import json

def test_complete_currency_system():
    """Test complete currency system"""
    print("Testing Complete Currency System...")
    
    # Test 1: Currency Detection
    print("\n1. Testing Currency Detection:")
    detection_tests = [
        "Wireless Bluetooth Headphones - $29.99",
        "Premium Quality Product - €45.50",
        "High-End Item - £75.00",
        "Chinese Product - ¥299",
        "Made in China",
        "Japanese product"
    ]
    
    for text in detection_tests:
        try:
            response = requests.post('http://localhost:8000/api/currency/detect', json={
                'text': text
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f'  OK: "{text}" -> {data["detected_currency"]} (confidence: {data["confidence"]})')
            else:
                print(f'  FAIL: "{text}" -> {response.status_code}')
        except Exception as e:
            print(f'  ERROR: "{text}" -> {e}')
    
    # Test 2: Currency Conversion
    print("\n2. Testing Currency Conversion:")
    conversion_tests = [
        (100.0, 'CNY', 'USD'),
        (100.0, 'CNY', 'EUR'),
        (100.0, 'CNY', 'ILS'),
        (100.0, 'INR', 'USD'),
        (100.0, 'INR', 'EUR'),
        (100.0, 'INR', 'ILS'),
        (100.0, 'MYR', 'USD'),
        (100.0, 'MYR', 'EUR'),
        (100.0, 'MYR', 'ILS'),
    ]
    
    success_count = 0
    for price, from_curr, to_curr in conversion_tests:
        try:
            response = requests.post('http://localhost:8000/api/currency/convert', json={
                'price': price,
                'from_currency': from_curr,
                'to_currency': to_curr
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f'  OK {from_curr} -> {to_curr}: {data["original_price"]} {data["from_currency"]} = {data["converted_price"]} {data["to_currency"]}')
                success_count += 1
            else:
                print(f'  FAIL {from_curr} -> {to_curr}: {response.status_code}')
        except Exception as e:
            print(f'  ERROR {from_curr} -> {to_curr}: {e}')
    
    print(f'\nConversion Success Rate: {success_count}/{len(conversion_tests)}')
    
    # Test 3: End-to-End Test
    print("\n3. Testing End-to-End Flow:")
    test_products = [
        {"title": "Wireless Bluetooth Headphones - $29.99", "price": 29.99, "expected_currency": "USD"},
        {"title": "Premium Quality Product - €45.50", "price": 45.50, "expected_currency": "EUR"},
        {"title": "Chinese Product - ¥299", "price": 299, "expected_currency": "JPY"},
        {"title": "Made in China", "price": 100, "expected_currency": "CNY"},
    ]
    
    for product in test_products:
        print(f'\n  Product: "{product["title"]}"')
        
        # Step 1: Detect currency
        try:
            response = requests.post('http://localhost:8000/api/currency/detect', json={
                'text': product["title"]
            })
            
            if response.status_code == 200:
                data = response.json()
                detected_currency = data["detected_currency"]
                print(f'    Detected Currency: {detected_currency}')
                
                # Step 2: Convert to all target currencies
                target_currencies = ['USD', 'EUR', 'ILS']
                for target_currency in target_currencies:
                    try:
                        response = requests.post('http://localhost:8000/api/currency/convert', json={
                            'price': product["price"],
                            'from_currency': detected_currency or 'USD',
                            'to_currency': target_currency
                        })
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f'    {detected_currency or "USD"} -> {target_currency}: {data["converted_price"]}')
                        else:
                            print(f'    {detected_currency or "USD"} -> {target_currency}: FAILED')
                    except Exception as e:
                        print(f'    {detected_currency or "USD"} -> {target_currency}: ERROR - {e}')
            else:
                print(f'    Currency Detection: FAILED')
        except Exception as e:
            print(f'    Currency Detection: ERROR - {e}')

def main():
    """Main test function"""
    print("Starting Complete Currency System Test...\n")
    test_complete_currency_system()
    print("\nComplete currency system test completed!")

if __name__ == "__main__":
    main()
