#!/usr/bin/env python3
"""
Test script for currency switching functionality
"""

import requests
import json

def test_currency_switching():
    """Test currency switching between USD, EUR, ILS"""
    print("Testing Currency Switching...")
    
    test_price = 100.0
    from_currency = 'CNY'
    
    target_currencies = ['USD', 'EUR', 'ILS']
    
    for to_currency in target_currencies:
        try:
            response = requests.post('http://localhost:8000/api/currency/convert', json={
                'price': test_price,
                'from_currency': from_currency,
                'to_currency': to_currency
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"OK {from_currency} -> {to_currency}: {data['original_price']} {data['from_currency']} = {data['converted_price']} {data['to_currency']}")
            else:
                print(f"FAIL {from_currency} -> {to_currency}: Failed - {response.status_code}")
                
        except Exception as e:
            print(f"ERROR {from_currency} -> {to_currency}: Error - {e}")

def test_multiple_currencies():
    """Test multiple source currencies"""
    print("\nTesting Multiple Source Currencies...")
    
    source_currencies = ['CNY', 'JPY', 'INR', 'MYR', 'THB', 'VND', 'IDR', 'PHP', 'SGD', 'HKD', 'TWD']
    target_currency = 'USD'
    
    for from_currency in source_currencies:
        try:
            response = requests.post('http://localhost:8000/api/currency/convert', json={
                'price': 100.0,
                'from_currency': from_currency,
                'to_currency': target_currency
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"OK {from_currency} -> {target_currency}: {data['original_price']} {data['from_currency']} = {data['converted_price']} {data['to_currency']}")
            else:
                print(f"FAIL {from_currency} -> {target_currency}: Failed - {response.status_code}")
                
        except Exception as e:
            print(f"ERROR {from_currency} -> {target_currency}: Error - {e}")

def main():
    """Main test function"""
    print("Starting Currency Switching Tests...\n")
    
    # Test currency switching
    test_currency_switching()
    
    # Test multiple currencies
    test_multiple_currencies()
    
    print("\nCurrency switching tests completed!")

if __name__ == "__main__":
    main()
