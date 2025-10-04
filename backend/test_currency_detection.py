#!/usr/bin/env python3
"""
Test currency detection endpoint
"""

import requests
import json

def test_currency_detection():
    """Test currency detection endpoint"""
    print("Testing Currency Detection Endpoint...")
    
    test_cases = [
        "Wireless Bluetooth Headphones - $29.99",
        "Premium Quality Product - €45.50",
        "High-End Item - £75.00",
        "Chinese Product - ¥299",
        "Indian Goods - ₹450",
        "Malaysian Item - RM89",
        "Thai Product - ฿1200",
        "Vietnamese Goods - ₫150000",
        "Indonesian Item - Rp100000",
        "Philippine Product - ₱75",
        "Singapore Item - S$12.50",
        "Hong Kong Product - HK$100",
        "Taiwanese Goods - NT$500",
        "Made in China",
        "Japanese product",
        "Korean goods",
        "Indian manufacturer",
        "Thai company",
        "Vietnamese supplier",
        "Indonesian brand",
        "Philippine goods",
        "Malaysian products",
        "Singapore based",
        "Hong Kong company",
        "Taiwanese manufacturer",
        "Pakistani goods",
        "Bangladeshi products",
        "Sri Lankan company",
        "Nepalese goods",
        "Myanmar products",
        "Cambodian company",
        "Laotian goods",
        "Brunei products",
        "Macau company",
        "Mongolian goods",
        "Kazakhstani products",
        "Uzbekistani company",
        "Kyrgyzstani goods",
        "Tajikistani products",
        "Afghan company",
        "UAE based",
        "Saudi company",
        "Kuwaiti goods",
        "Bahraini products",
        "Omani company",
        "Jordanian goods",
        "Lebanese products",
        "Israeli company",
        "Turkish goods",
        "Iranian products",
        "Iraqi company",
        "Syrian goods",
        "Yemeni products",
        "German company",
        "French goods",
        "Italian products",
        "Spanish company",
        "Dutch goods",
        "Belgian products",
        "Austrian company",
        "Portuguese goods",
        "Finnish products",
        "Irish company",
        "Greek goods",
        "British company",
        "Swiss goods",
        "Swedish products",
        "Norwegian company",
        "Danish goods",
        "Polish products",
        "Czech company",
        "Hungarian goods",
        "Russian products",
        "Ukrainian company",
        "American goods",
        "Canadian products",
        "Mexican company",
        "Brazilian goods",
        "Argentine products",
        "Chilean company",
        "Colombian goods",
        "Peruvian products",
        "South African company",
        "Egyptian goods",
        "Nigerian products",
        "Kenyan company",
        "Moroccan goods",
        "Tunisian products",
        "Australian company",
        "New Zealand goods"
    ]
    
    success_count = 0
    
    for text in test_cases:
        try:
            response = requests.post('http://localhost:8000/api/currency/detect', json={
                'text': text
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f'OK: "{text}" -> {data["detected_currency"]} (confidence: {data["confidence"]})')
                success_count += 1
            else:
                print(f'FAIL: "{text}" -> {response.status_code} - {response.text}')
        except Exception as e:
            print(f'ERROR: "{text}" -> {e}')
    
    print(f'\nSuccess Rate: {success_count}/{len(test_cases)}')
    return success_count == len(test_cases)

def main():
    """Main test function"""
    print("Starting Currency Detection Tests...\n")
    
    success = test_currency_detection()
    
    if success:
        print("\nAll currency detection tests passed!")
        return 0
    else:
        print("\nSome currency detection tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
