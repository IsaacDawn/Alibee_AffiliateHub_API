#!/usr/bin/env python3
"""
Test EUR and ILS currency conversion
"""

import requests
import json

def test_eur_ils_conversion():
    """Test currency conversion to EUR and ILS"""
    print("Testing Currency Conversion to EUR and ILS...")
    
    test_cases = [
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

def test_usd_base_rates():
    """Test USD base rates"""
    print("\nTesting USD Base Rates...")
    
    # Test direct USD conversions
    usd_rates = [
        (100.0, 'USD', 'EUR'),
        (100.0, 'USD', 'ILS'),
    ]
    
    for price, from_curr, to_curr in usd_rates:
        try:
            response = requests.post('http://localhost:8000/api/currency/convert', json={
                'price': price,
                'from_currency': from_curr,
                'to_currency': to_curr
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f'OK {from_curr} -> {to_curr}: {data["original_price"]} {data["from_currency"]} = {data["converted_price"]} {data["to_currency"]}')
            else:
                print(f'FAIL {from_curr} -> {to_curr}: {response.status_code} - {response.text}')
        except Exception as e:
            print(f'ERROR {from_curr} -> {to_curr}: {e}')

def main():
    """Main test function"""
    print("Starting EUR/ILS Conversion Tests...\n")
    
    # Test EUR/ILS conversions
    eur_ils_success = test_eur_ils_conversion()
    
    # Test USD base rates
    test_usd_base_rates()
    
    if eur_ils_success:
        print("\nAll EUR/ILS conversion tests passed!")
        return 0
    else:
        print("\nSome EUR/ILS conversion tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
