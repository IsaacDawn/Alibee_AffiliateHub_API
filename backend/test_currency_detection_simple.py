#!/usr/bin/env python3
"""
Simple currency detection test
"""

import requests
import json

def test_currency_detection():
    """Test currency detection endpoint"""
    print("Testing Currency Detection...")
    
    test_cases = [
        "Wireless Bluetooth Headphones - $29.99",
        "Premium Quality Product - €45.50",
        "High-End Item - £75.00",
        "Chinese Product - ¥299",
        "Indian Goods - ₹450",
        "Made in China",
        "Japanese product",
        "Korean goods"
    ]
    
    for text in test_cases:
        try:
            response = requests.post('http://localhost:8000/api/currency/detect', json={
                'text': text
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f'OK: "{text}" -> {data["detected_currency"]} (confidence: {data["confidence"]})')
            else:
                print(f'FAIL: "{text}" -> {response.status_code} - {response.text}')
        except Exception as e:
            print(f'ERROR: "{text}" -> {e}')

def main():
    """Main test function"""
    print("Starting Currency Detection Test...\n")
    test_currency_detection()
    print("\nCurrency detection test completed!")

if __name__ == "__main__":
    main()
