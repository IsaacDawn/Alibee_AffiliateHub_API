#!/usr/bin/env python3
"""
Test currency conversion endpoint
"""

import requests
import json

def test_currency_endpoint():
    """Test currency conversion endpoint"""
    print("Testing Currency Conversion Endpoint...")
    
    try:
        response = requests.post('http://localhost:8000/api/currency/convert', json={
            'price': 100.0,
            'from_currency': 'CNY',
            'to_currency': 'USD'
        })
        
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Success: {data["original_price"]} {data["from_currency"]} = {data["converted_price"]} {data["to_currency"]}')
            return True
        else:
            print(f'Error: {response.text}')
            return False
    except Exception as e:
        print(f'Exception: {e}')
        return False

def test_multiple_currencies():
    """Test multiple currency conversions"""
    print("\nTesting Multiple Currency Conversions...")
    
    test_cases = [
        (100.0, 'CNY', 'USD'),
        (100.0, 'CNY', 'EUR'),
        (100.0, 'CNY', 'ILS'),
        (100.0, 'INR', 'USD'),
        (100.0, 'MYR', 'EUR'),
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
                print(f'OK {from_curr} -> {to_curr}: {data["original_price"]} {data["from_currency"]} = {data["converted_price"]} {data["to_currency"]}')
                success_count += 1
            else:
                print(f'FAIL {from_curr} -> {to_curr}: {response.status_code} - {response.text}')
        except Exception as e:
            print(f'ERROR {from_curr} -> {to_curr}: {e}')
    
    print(f'\nSuccess Rate: {success_count}/{len(test_cases)}')
    return success_count == len(test_cases)

def main():
    """Main test function"""
    print("Starting Currency Endpoint Tests...\n")
    
    # Test single conversion
    single_success = test_currency_endpoint()
    
    # Test multiple conversions
    multiple_success = test_multiple_currencies()
    
    if single_success and multiple_success:
        print("\nAll currency endpoint tests passed!")
        return 0
    else:
        print("\nSome currency endpoint tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
