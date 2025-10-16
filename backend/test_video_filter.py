#!/usr/bin/env python3
"""
Test script for video filter in comprehensive search
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_video_filter():
    """Test video filter functionality"""
    
    print("🧪 Testing Video Filter in Comprehensive Search")
    print("=" * 50)
    
    # Test without video filter
    print("\n1. Test WITHOUT video filter (only_with_video=0):")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/search/comprehensive",
            params={
                "q": "demo",
                "page": 1,
                "pageSize": 10,
                "only_with_video": 0,
                "use_api": "false"  # Use demo data
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ Total products: {len(items)}")
            
            for i, product in enumerate(items, 1):
                video_status = "Yes" if product.get("video_link") and product.get("video_link").strip() else "No"
                print(f"   {i}. {product.get('product_title', 'N/A')[:40]}... - Video: {video_status}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with video filter
    print("\n2. Test WITH video filter (only_with_video=1):")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/search/comprehensive",
            params={
                "q": "demo",
                "page": 1,
                "pageSize": 10,
                "only_with_video": 1,
                "use_api": "false"  # Use demo data
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ Total products with video: {len(items)}")
            
            if len(items) == 0:
                print("⚠️  No products with video found!")
            else:
                for i, product in enumerate(items, 1):
                    video_status = "Yes" if product.get("video_link") and product.get("video_link").strip() else "No"
                    print(f"   {i}. {product.get('product_title', 'N/A')[:40]}... - Video: {video_status}")
                    
                    # Verify all products have video
                    if not (product.get("video_link") and product.get("video_link").strip()):
                        print(f"   ❌ ERROR: Product {i} should have video but doesn't!")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with real API (if available)
    print("\n3. Test with real API (only_with_video=1):")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/search/comprehensive",
            params={
                "q": "electronics",
                "page": 1,
                "pageSize": 5,
                "only_with_video": 1,
                "use_api": "true"  # Use real API
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ Total products with video from API: {len(items)}")
            
            if len(items) == 0:
                print("⚠️  No products with video found from API!")
            else:
                for i, product in enumerate(items, 1):
                    video_status = "Yes" if product.get("video_link") and product.get("video_link").strip() else "No"
                    print(f"   {i}. {product.get('product_title', 'N/A')[:40]}... - Video: {video_status}")
                    
                    # Verify all products have video
                    if not (product.get("video_link") and product.get("video_link").strip()):
                        print(f"   ❌ ERROR: Product {i} should have video but doesn't!")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Video Filter Test Completed")

if __name__ == "__main__":
    print("🚀 Starting Video Filter Tests")
    print("Make sure the server is running on http://127.0.0.1:8080")
    print()
    
    test_video_filter()
    
    print("\n✨ All tests completed!")
