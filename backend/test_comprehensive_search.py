#!/usr/bin/env python3
"""
Test script for comprehensive search endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_comprehensive_search():
    """Test comprehensive search endpoint with various filters"""
    
    print("🧪 Testing Comprehensive Search Endpoint")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Basic Search",
            "params": {
                "q": "shoes",
                "page": 1,
                "pageSize": 5
            }
        },
        {
            "name": "Search with Currency Conversion",
            "params": {
                "q": "headphones",
                "page": 1,
                "pageSize": 5,
                "target_currency": "EUR"
            }
        },
        {
            "name": "Search with Price Filter",
            "params": {
                "q": "watch",
                "page": 1,
                "pageSize": 5,
                "min_price": 20,
                "max_price": 100
            }
        },
        {
            "name": "Search with Sorting",
            "params": {
                "q": "phone",
                "page": 1,
                "pageSize": 5,
                "sort_by": "price_asc"
            }
        },
        {
            "name": "Search with Video Filter",
            "params": {
                "q": "electronics",
                "page": 1,
                "pageSize": 5,
                "only_with_video": 1
            }
        },
        {
            "name": "Search with Category Filter",
            "params": {
                "q": "accessories",
                "page": 1,
                "pageSize": 5,
                "category": "Electronics"
            }
        },
        {
            "name": "Comprehensive Search (All Filters)",
            "params": {
                "q": "bluetooth",
                "page": 1,
                "pageSize": 5,
                "target_currency": "ILS",
                "min_price": 10,
                "max_price": 50,
                "sort_by": "discount_desc",
                "only_with_video": 1,
                "category": "Electronics"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/search/comprehensive",
                params=test_case["params"],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Total Products: {data.get('total', 0)}")
                print(f"📄 Page: {data.get('page', 0)}")
                print(f"📏 Page Size: {data.get('pageSize', 0)}")
                print(f"🔄 Has More: {data.get('hasMore', False)}")
                print(f"🔍 Query: {data.get('query', '')}")
                print(f"🎯 Filters: {json.dumps(data.get('filters', {}), indent=2)}")
                
                # Show currency conversion stats
                currency_stats = data.get('currency_conversion', {})
                if currency_stats:
                    print(f"💱 Currency Conversion:")
                    print(f"   - Target: {currency_stats.get('target_currency', 'N/A')}")
                    print(f"   - Successful: {currency_stats.get('successful_conversions', 0)}")
                    print(f"   - Failed: {currency_stats.get('failed_conversions', 0)}")
                
                # Show first product if available
                items = data.get('items', [])
                if items:
                    first_product = items[0]
                    print(f"📦 First Product:")
                    print(f"   - ID: {first_product.get('product_id', 'N/A')}")
                    print(f"   - Title: {first_product.get('product_title', 'N/A')[:50]}...")
                    print(f"   - Price: {first_product.get('sale_price', 'N/A')} {first_product.get('sale_price_currency', 'N/A')}")
                    if 'sale_price_target' in first_product:
                        print(f"   - Converted Price: {first_product.get('sale_price_target', 'N/A')} {first_product.get('sale_price_currency_target', 'N/A')}")
                    print(f"   - Video: {'Yes' if first_product.get('video_link') else 'No'}")
                    print(f"   - Custom Title: {first_product.get('custom_title', 'None')}")
                
                print(f"💬 Message: {data.get('message', 'N/A')}")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"📝 Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Comprehensive Search Test Completed")

def test_demo_mode():
    """Test comprehensive search in demo mode"""
    
    print("\n🧪 Testing Comprehensive Search in Demo Mode")
    print("=" * 50)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/search/comprehensive",
            params={
                "q": "demo",
                "page": 1,
                "pageSize": 3,
                "target_currency": "EUR",
                "min_price": 20,
                "max_price": 100,
                "sort_by": "price_desc",
                "only_with_video": 1,
                "use_api": "false"  # Force demo mode
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Demo Mode Status: {response.status_code}")
            print(f"📊 Total Products: {data.get('total', 0)}")
            print(f"🎯 Filters: {json.dumps(data.get('filters', {}), indent=2)}")
            
            # Show currency conversion stats
            currency_stats = data.get('currency_conversion', {})
            if currency_stats:
                print(f"💱 Currency Conversion:")
                print(f"   - Target: {currency_stats.get('target_currency', 'N/A')}")
                print(f"   - Successful: {currency_stats.get('successful_conversions', 0)}")
                print(f"   - Failed: {currency_stats.get('failed_conversions', 0)}")
            
            # Show all products
            items = data.get('items', [])
            print(f"📦 Products ({len(items)}):")
            for i, product in enumerate(items, 1):
                print(f"   {i}. {product.get('product_title', 'N/A')}")
                print(f"      Price: {product.get('sale_price', 'N/A')} {product.get('sale_price_currency', 'N/A')}")
                if 'sale_price_target' in product:
                    print(f"      Converted: {product.get('sale_price_target', 'N/A')} {product.get('sale_price_currency_target', 'N/A')}")
                print(f"      Video: {'Yes' if product.get('video_link') else 'No'}")
                print(f"      Custom Title: {product.get('custom_title', 'None')}")
            
        else:
            print(f"❌ Demo Mode Status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Demo Mode Request Error: {e}")
    except Exception as e:
        print(f"❌ Demo Mode Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Search Tests")
    print("Make sure the server is running on http://127.0.0.1:8080")
    print()
    
    # Test comprehensive search
    test_comprehensive_search()
    
    # Test demo mode
    test_demo_mode()
    
    print("\n✨ All tests completed!")
