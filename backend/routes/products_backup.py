# backend/routes/products.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from services.aliexpress import AliExpressService
from services.currency_converter import currency_converter
from database.connection import db_ops
import mysql.connector
from config.settings import settings
import logging

router = APIRouter()

def get_custom_titles_for_products(products: List[Dict[str, Any]]) -> Dict[str, str]:
    """Get custom titles for products from saved_products table"""
    try:
        if not products:
            return {}
        
        # Extract product IDs and convert to string
        product_ids = [str(product.get("product_id")) for product in products if product.get("product_id")]
        
        if not product_ids:
            return {}
        
        # Get custom titles from database
        custom_titles = {}
        with db_ops.db.get_cursor() as (cursor, connection):
            placeholders = ','.join(['%s' for _ in product_ids])
            query = f"""
                SELECT product_id, custom_title 
                FROM saved_products 
                WHERE product_id IN ({placeholders}) AND custom_title IS NOT NULL AND custom_title != ''
            """
            cursor.execute(query, product_ids)
            rows = cursor.fetchall()
            
            for row in rows:
                custom_titles[row[0]] = row[1]
        
        logging.info(f"Retrieved {len(custom_titles)} custom titles for {len(product_ids)} products")
        return custom_titles
        
    except Exception as e:
        logging.error(f"Error getting custom titles: {e}")
        return {}

def add_custom_titles_to_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add custom titles to products"""
    try:
        if not products:
            return products
        
        # Get custom titles for all products
        custom_titles = get_custom_titles_for_products(products)
        
        # Add custom_title to each product
        for product in products:
            product_id = product.get("product_id")
            if product_id and str(product_id) in custom_titles:
                product["custom_title"] = custom_titles[str(product_id)]
            else:
                product["custom_title"] = None
        
        return products
        
    except Exception as e:
        logging.error(f"Error adding custom titles to products: {e}")
        return products

@router.get("/products/initial")
def get_initial_products(
    limit: int = Query(150, ge=1, le=200),
    use_api: str = Query("true"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """Get initial random products for homepage - Returns 10 products by default"""
    
    # Use AliExpress API if use_api=true
    if use_api.lower() == "true":
        try:
            aliexpress_service = AliExpressService()
            # Get popular/trending products for initial load
            result = aliexpress_service.search_products_with_filters(
                query="electronics",  # Popular category for initial load
                page=1,
                page_size=limit,
                sort="volume_desc",
                has_video=(only_with_video == 1)
            )
            
            if result and result.get("items"):
                # Transform AliExpress data to match frontend format
                transformed_items = []
                for item in result.get("items", []):
                    # Extract additional images from AliExpress response
                    additional_images = []
                    if item.get("product_small_image_urls"):
                        if isinstance(item.get("product_small_image_urls"), list):
                            additional_images = item.get("product_small_image_urls", [])
                        elif isinstance(item.get("product_small_image_urls"), dict) and "string" in item.get("product_small_image_urls", {}):
                            additional_images = item.get("product_small_image_urls", {}).get("string", [])
                    elif item.get("images_link"):
                        if isinstance(item.get("images_link"), list):
                            additional_images = item.get("images_link", [])
                        elif isinstance(item.get("images_link"), dict) and "string" in item.get("images_link", {}):
                            additional_images = item.get("images_link", {}).get("string", [])
                    
                    # Extract video link if available
                    video_link = item.get("video_link", "")
                    
                    transformed_item = {
                        "id": item.get("product_id", ""),
                        "title": item.get("product_title", ""),
                        "price": float(item.get("sale_price", 0)),
                        "originalPrice": float(item.get("original_price", 0)) if item.get("original_price") else None,
                        "currency": "USD",
                        "originalPriceCurrency": item.get("original_price_currency", "USD"),
                        "image": item.get("product_main_image_url", ""),
                        "images": additional_images,
                        "video": video_link if video_link else None,
                        "rating": float(item.get("rating", 0)),
                        "reviewCount": int(item.get("review_count", 0)),
                        "url": item.get("product_detail_url", ""),
                        "category": item.get("category", ""),
                        "discount": None
                    }
                    # Calculate discount if original price exists
                    if transformed_item["originalPrice"] and transformed_item["originalPrice"] > transformed_item["price"]:
                        discount = ((transformed_item["originalPrice"] - transformed_item["price"]) / transformed_item["originalPrice"]) * 100
                        transformed_item["discount"] = round(discount)
                    transformed_items.append(transformed_item)
                
                # Add custom titles to products
                transformed_items = add_custom_titles_to_products(transformed_items)
                
                return {
                    "success": True,
                    "data": transformed_items,
                    "page": 1,
                    "limit": limit,
                    "hasMore": result.get("hasMore", False),
                    "total": len(transformed_items),
                    "message": f"Found {len(transformed_items)} initial products"
                }
            else:
                print(f"AliExpress API failed for initial load: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error for initial load: {str(e)}")
    
    # Demo products for initial load (fallback or when use_api=false)
    demo_products = [
        {
            "id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "price": 29.99,
            "originalPrice": 49.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "rating": 4.5,
            "reviewCount": 1250,
            "url": "https://example.com/product/1005010032093800",
            "category": "Electronics",
            "discount": 40
        },
        {
            "id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "price": 89.99,
            "originalPrice": 129.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "rating": 4.3,
            "reviewCount": 890,
            "url": "https://example.com/product/1005010032093801",
            "category": "Watches",
            "discount": 31
        },
        {
            "id": "1005010032093802",
            "title": "Portable Phone Charger 20000mAh",
            "price": 19.99,
            "originalPrice": 29.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "rating": 4.7,
            "reviewCount": 2100,
            "url": "https://example.com/product/1005010032093802",
            "category": "Phone Accessories",
            "discount": 33
        },
        {
            "id": "1005010032093803",
            "title": "LED Desk Lamp with USB Charging Port",
            "price": 24.99,
            "originalPrice": 39.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "rating": 4.4,
            "reviewCount": 680,
            "url": "https://example.com/product/1005010032093803",
            "category": "Home & Garden",
            "discount": 37
        },
        {
            "id": "1005010032093804",
            "title": "Bluetooth Speaker Waterproof",
            "price": 34.99,
            "originalPrice": 59.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "rating": 4.6,
            "reviewCount": 1450,
            "url": "https://example.com/product/1005010032093804",
            "category": "Electronics",
            "discount": 42
        },
        {
            "id": "1005010032093805",
            "title": "Wireless Mouse Ergonomic Design",
            "price": 15.99,
            "originalPrice": 25.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse",
            "rating": 4.2,
            "reviewCount": 920,
            "url": "https://example.com/product/1005010032093805",
            "category": "Computer Accessories",
            "discount": 38
        },
        {
            "id": "1005010032093806",
            "title": "Car Phone Mount Dashboard",
            "price": 12.99,
            "originalPrice": 19.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount",
            "rating": 4.5,
            "reviewCount": 1650,
            "url": "https://example.com/product/1005010032093806",
            "category": "Automotive",
            "discount": 35
        },
        {
            "id": "1005010032093807",
            "title": "Kitchen Scale Digital Display",
            "price": 18.99,
            "originalPrice": 28.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "rating": 4.3,
            "reviewCount": 750,
            "url": "https://example.com/product/1005010032093807",
            "category": "Home & Garden",
            "discount": 34
        }
    ]
    
    # Return limited number of products
    limited_products = demo_products[:limit]
    
    # Add custom titles to demo products
    limited_products = add_custom_titles_to_products(limited_products)
    
    # Filter products with video if only_with_video=1
    if only_with_video == 1:
        limited_products = [product for product in limited_products if product.get("video_link") and product.get("video_link").strip()]
    
    return {
        "success": True,
        "data": limited_products,
        "page": 1,
        "limit": limit,
        "hasMore": True,  # Always true for demo
        "total": len(limited_products),
        "message": f"Loaded {len(limited_products)} initial products"
    }

@router.get("/products/search")
def search_products(
    query: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(150, ge=1, le=200),  # Changed default to 150 for better performance
    minPrice: Optional[float] = Query(None, ge=0),
    maxPrice: Optional[float] = Query(None, ge=0),
    category: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("price"),
    sortOrder: Optional[str] = Query("asc"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)"),
    target_currency: Optional[str] = Query(None, description="Target currency for price conversion"),
    use_api: str = Query("true")
):
    """Search products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Use AliExpress API if use_api=true and query is provided
    if use_api.lower() == "true" and query.strip():
        try:
            aliexpress_service = AliExpressService()
            
            # Use AliExpress API with video filter if needed
            result = aliexpress_service.search_products_with_filters(
                query=query.strip(),
                page=page,
                page_size=limit,
                sort="volume_desc",
                has_video=(only_with_video == 1)
            )
            
            if result and result.get("items"):
                # Transform AliExpress data to match frontend format
                transformed_items = []
                for item in result.get("items", []):
                    # Extract additional images from AliExpress response
                    additional_images = []
                    if item.get("product_small_image_urls"):
                        if isinstance(item.get("product_small_image_urls"), list):
                            additional_images = item.get("product_small_image_urls", [])
                        elif isinstance(item.get("product_small_image_urls"), dict) and "string" in item.get("product_small_image_urls", {}):
                            additional_images = item.get("product_small_image_urls", {}).get("string", [])
                    elif item.get("images_link"):
                        if isinstance(item.get("images_link"), list):
                            additional_images = item.get("images_link", [])
                        elif isinstance(item.get("images_link"), dict) and "string" in item.get("images_link", {}):
                            additional_images = item.get("images_link", {}).get("string", [])
                    
                    # Extract video link if available
                    video_link = item.get("video_link", "")
                    
                    transformed_item = {
                        "id": item.get("product_id", ""),
                        "title": item.get("product_title", ""),
                        "price": float(item.get("sale_price", 0)),
                        "originalPrice": float(item.get("original_price", 0)) if item.get("original_price") else None,
                        "currency": "USD",
                        "originalPriceCurrency": item.get("original_price_currency", "USD"),
                        "image": item.get("product_main_image_url", ""),
                        "images": additional_images,
                        "video": video_link,
                        "rating": float(item.get("rating", 0)),
                        "reviewCount": int(item.get("review_count", 0)),
                        "url": item.get("product_detail_url", ""),
                        "category": item.get("category", ""),
                        "discount": None
                    }
                    # Calculate discount if original price exists
                    if transformed_item["originalPrice"] and transformed_item["originalPrice"] > transformed_item["price"]:
                        discount = ((transformed_item["originalPrice"] - transformed_item["price"]) / transformed_item["originalPrice"]) * 100
                        transformed_item["discount"] = round(discount)
                    
                    transformed_items.append(transformed_item)
                
                # Add custom titles to products
                transformed_items = add_custom_titles_to_products(transformed_items)
                
                return {
                    "success": True,
                    "data": transformed_items,
                    "page": page,
                    "limit": limit,
                    "hasMore": result.get("hasMore", False),
                    "total": len(transformed_items),
                    "message": f"Found {len(transformed_items)} products for '{query}'"
                }
            else:
                print(f"AliExpress API failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
    
    # Demo products for search (fallback or when use_api=false)
    demo_products = [
        {
            "id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "price": 29.99,
            "originalPrice": 49.99,
            "currency": "USD",
            "originalPriceCurrency": "USD",
            "rating": 4.5,
            "reviewCount": 1250,
            "image": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "images": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "video": "https://example.com/video/headphones.mp4",
            "url": "https://example.com/product/1005010032093800",
            "category": "Electronics",
            "discount": 40,
            "is_saved": False
        },
        {
            "id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "price": 89.99,
            "originalPrice": 129.99,
            "currency": "USD",
            "originalPriceCurrency": "USD",
            "rating": 4.3,
            "reviewCount": 890,
            "image": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "images": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "video": "",  # No video for this product
            "url": "https://example.com/product/1005010032093801",
            "category": "Watches",
            "discount": 31,
            "is_saved": False
        }
    ]
    
    # Filter by video if specified
    if only_with_video == 1:
        demo_products = [p for p in demo_products if p.get("video") and p.get("video").strip()]
    
    # Apply search filter
    if query.strip():
        filtered_products = [p for p in demo_products if query.lower() in p["title"].lower()]
    else:
        filtered_products = demo_products
    
    # Apply pagination
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_products = filtered_products[start_index:end_index]
    
    # Add custom titles to demo products
    paginated_products = add_custom_titles_to_products(paginated_products)
    
    return {
        "success": True,
        "data": paginated_products,
        "page": page,
        "limit": limit,
        "hasMore": end_index < len(filtered_products),
        "total": len(filtered_products),
        "message": f"Found {len(paginated_products)} products for '{query}'" if query.strip() else "Demo products loaded"
    }
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "rating": 4.5,
            "reviewCount": 1250,
            "url": "https://example.com/product/1005010032093800",
            "category": "Electronics",
            "discount": 40,
            "video": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        },
        {
            "id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "price": 89.99,
            "originalPrice": 129.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "rating": 4.3,
            "reviewCount": 890,
            "url": "https://example.com/product/1005010032093801",
            "category": "Watches",
            "discount": 31
        },
        {
            "id": "1005010032093802",
            "title": "Portable Phone Charger 20000mAh",
            "price": 19.99,
            "originalPrice": 29.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "rating": 4.7,
            "reviewCount": 2100,
            "url": "https://example.com/product/1005010032093802",
            "category": "Phone Accessories",
            "discount": 33
        },
        {
            "id": "1005010032093803",
            "title": "LED Desk Lamp with USB Charging Port",
            "price": 24.99,
            "originalPrice": 39.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "rating": 4.4,
            "reviewCount": 680,
            "url": "https://example.com/product/1005010032093803",
            "category": "Home & Garden",
            "discount": 37
        },
        {
            "id": "1005010032093804",
            "title": "Bluetooth Speaker Waterproof",
            "price": 34.99,
            "originalPrice": 59.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "rating": 4.6,
            "reviewCount": 1450,
            "url": "https://example.com/product/1005010032093804",
            "category": "Electronics",
            "discount": 42
        },
        {
            "id": "1005010032093805",
            "title": "Wireless Mouse Ergonomic Design",
            "price": 15.99,
            "originalPrice": 25.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse",
            "rating": 4.2,
            "reviewCount": 920,
            "url": "https://example.com/product/1005010032093805",
            "category": "Computer Accessories",
            "discount": 38
        },
        {
            "id": "1005010032093806",
            "title": "Car Phone Mount Dashboard",
            "price": 12.99,
            "originalPrice": 19.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount",
            "rating": 4.5,
            "reviewCount": 1650,
            "url": "https://example.com/product/1005010032093806",
            "category": "Automotive",
            "discount": 35
        },
        {
            "id": "1005010032093807",
            "title": "Kitchen Scale Digital Display",
            "price": 18.99,
            "originalPrice": 28.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "rating": 4.3,
            "reviewCount": 750,
            "url": "https://example.com/product/1005010032093807",
            "category": "Home & Garden",
            "discount": 34
        },
        {
            "id": "1005010032093808",
            "title": "Gaming Mechanical Keyboard RGB",
            "price": 79.99,
            "originalPrice": 119.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Gaming+Keyboard",
            "rating": 4.8,
            "reviewCount": 2100,
            "url": "https://example.com/product/1005010032093808",
            "category": "Gaming",
            "discount": 33
        },
        {
            "id": "1005010032093809",
            "title": "Wireless Gaming Mouse 16000 DPI",
            "price": 45.99,
            "originalPrice": 69.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Gaming+Mouse",
            "rating": 4.6,
            "reviewCount": 1800,
            "url": "https://example.com/product/1005010032093809",
            "category": "Gaming",
            "discount": 34
        },
        {
            "id": "1005010032093810",
            "title": "USB-C Hub 7-in-1 Adapter",
            "price": 32.99,
            "originalPrice": 49.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/059669/FFFFFF?text=USB+Hub",
            "rating": 4.4,
            "reviewCount": 950,
            "url": "https://example.com/product/1005010032093810",
            "category": "Computer Accessories",
            "discount": 34
        },
        {
            "id": "1005010032093811",
            "title": "Wireless Earbuds Noise Cancelling",
            "price": 59.99,
            "originalPrice": 89.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Wireless+Earbuds",
            "rating": 4.5,
            "reviewCount": 1350,
            "url": "https://example.com/product/1005010032093811",
            "category": "Electronics",
            "discount": 33
        },
        {
            "id": "1005010032093812",
            "title": "Laptop Stand Adjustable Aluminum",
            "price": 25.99,
            "originalPrice": 39.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Laptop+Stand",
            "rating": 4.3,
            "reviewCount": 720,
            "url": "https://example.com/product/1005010032093812",
            "category": "Computer Accessories",
            "discount": 35
        },
        {
            "id": "1005010032093813",
            "title": "Phone Case Clear Transparent",
            "price": 8.99,
            "originalPrice": 14.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Phone+Case",
            "rating": 4.2,
            "reviewCount": 2100,
            "url": "https://example.com/product/1005010032093813",
            "category": "Phone Accessories",
            "discount": 40
        },
        {
            "id": "1005010032093814",
            "title": "Tablet Stand Foldable Portable",
            "price": 16.99,
            "originalPrice": 24.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Tablet+Stand",
            "rating": 4.4,
            "reviewCount": 680,
            "url": "https://example.com/product/1005010032093814",
            "category": "Tablet Accessories",
            "discount": 32
        },
        {
            "id": "1005010032093815",
            "title": "Webcam HD 1080p with Microphone",
            "price": 39.99,
            "originalPrice": 59.99,
            "currency": "USD",
            "image": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Webcam",
            "rating": 4.5,
            "reviewCount": 1100,
            "url": "https://example.com/product/1005010032093815",
            "category": "Computer Accessories",
            "discount": 33
        }
    ]
    
    # Filter by query if provided
    if query.strip():
        filtered_products = [p for p in demo_products if query.lower() in p["title"].lower()]
    else:
        filtered_products = demo_products
    
    # Filter by video if specified
    if only_with_video == 1:
            # For demo purposes, simulate video availability based on product ID
            # Products with even IDs have videos, odd IDs don't
            filtered_products = [p for p in filtered_products if int(p["id"]) % 2 == 0]
            
            # If we don't have enough products with videos, we need to simulate fetching more pages
            if len(filtered_products) < limit:
                # Simulate additional products with videos by creating more demo products
                additional_products = []
                for i in range(limit - len(filtered_products)):
                    additional_id = f"1005010032093{800 + len(filtered_products) + i}"
                    additional_product = {
                        "id": additional_id,
                        "title": f"Demo Product with Video {len(filtered_products) + i + 1}",
                        "price": 29.99 + (i * 5),
                        "originalPrice": 49.99 + (i * 5),
                        "currency": "USD",
                        "image": f"https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Video+Product+{i+1}",
                        "rating": 4.5,
                        "reviewCount": 1250 + (i * 100),
                        "url": f"https://example.com/product/{additional_id}",
                        "category": "Electronics",
                        "discount": 40,
                        "video": f"https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
                    }
                    additional_products.append(additional_product)
                
                filtered_products.extend(additional_products)
        else:
            # Filter out products with videos
            filtered_products = [p for p in filtered_products if int(p["id"]) % 2 != 0]
    
    # Calculate pagination
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_products = filtered_products[start_index:end_index]
    
    # Add custom titles to products
    paginated_products = add_custom_titles_to_products(paginated_products)
    
    # For demo purposes, always return hasMore=true when no query is provided
    # This allows infinite scrolling to work with demo data
    has_more = end_index < len(filtered_products) if query.strip() else True
    
    return {
        "success": True,
        "data": paginated_products,
        "page": page,
        "limit": limit,
        "hasMore": has_more,
        "total": len(filtered_products),
        "message": f"Found {len(paginated_products)} products for '{query}'" if query.strip() else "Demo products loaded"
    }

@router.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    pageSize: int = Query(150, ge=1, le=200),
    use_api: str = Query("true"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """List products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Use AliExpress API if use_api=true
    if use_api.lower() == "true":
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.search_products_with_filters(
                query=None,  # No specific query for homepage
                page=page,
                page_size=pageSize,
                hot=True,  # Get hot/popular products for homepage
                sort="volume_desc"
            )
            
            if result and result.get("items"):
                return {
                    "items": result.get("items", []),
                    "page": page,
                    "pageSize": pageSize,
                    "hasMore": True,  # Always return True for testing infinite scroll
                    "total": len(result.get("items", [])),
                    "message": f"Found {len(result.get('items', []))} hot products from AliExpress API"
                }
            else:
                # Fallback to demo products if API fails
                print(f"AliExpress API failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
            # Fallback to demo products if API fails
    
    # Demo products for initial load (fallback or when use_api=false)
    demo_products = [
        {
            "product_id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "price": 29.99,
            "original_price": 49.99,
            "rating": 4.5,
            "review_count": 1250,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300&h=300&fit=crop"
            ],
            "volume": 5000,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "price": 89.99,
            "original_price": 129.99,
            "rating": 4.3,
            "review_count": 890,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=300&h=300&fit=crop"
            ],
            "video_link": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
            "volume": 3200,
            "category": "Watches",
            "is_saved": False
        },
        {
            "product_id": "1005010032093802",
            "title": "Portable Phone Charger 20000mAh",
            "price": 19.99,
            "original_price": 29.99,
            "rating": 4.7,
            "review_count": 2100,
            "image_url": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop"
            ],
            "volume": 7500,
            "category": "Phone Accessories",
            "is_saved": False
        },
        {
            "product_id": "1005010032093803",
            "title": "LED Desk Lamp with USB Charging Port",
            "price": 24.99,
            "original_price": 39.99,
            "rating": 4.4,
            "review_count": 680,
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop"
            ],
            "volume": 1800,
            "category": "Home & Garden",
            "is_saved": False
        },
        {
            "product_id": "1005010032093804",
            "title": "Bluetooth Speaker Waterproof",
            "price": 34.99,
            "original_price": 59.99,
            "rating": 4.6,
            "review_count": 1450,
            "image_url": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "product_main_image_url": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "images_link": ["https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker"],
            "volume": 4200,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093805",
            "title": "Wireless Mouse Ergonomic Design",
            "price": 15.99,
            "original_price": 25.99,
            "rating": 4.2,
            "review_count": 920,
            "image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse",
            "product_main_image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse",
            "images_link": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse"],
            "volume": 2800,
            "category": "Computer Accessories",
            "is_saved": False
        },
        {
            "product_id": "1005010032093806",
            "title": "Car Phone Mount Dashboard",
            "price": 12.99,
            "original_price": 19.99,
            "rating": 4.5,
            "review_count": 1650,
            "image_url": "https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount",
            "product_main_image_url": "https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount",
            "images_link": ["https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount"],
            "volume": 6200,
            "category": "Automotive",
            "is_saved": False
        },
        {
            "product_id": "1005010032093807",
            "title": "Kitchen Scale Digital Display",
            "price": 18.99,
            "original_price": 28.99,
            "rating": 4.3,
            "review_count": 750,
            "image_url": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "product_main_image_url": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "images_link": ["https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale"],
            "volume": 2100,
            "category": "Home & Garden",
            "is_saved": False
        }
    ]
    
    # Filter by video if specified
    if only_with_video == 1:
        demo_products = [p for p in demo_products if p.get("video_link") and p.get("video_link").strip()]
    
    # Calculate pagination
    start_index = (page - 1) * pageSize
    end_index = start_index + pageSize
    paginated_products = demo_products[start_index:end_index]
    
    return {
        "items": paginated_products,
        "page": page,
        "pageSize": pageSize,
        "hasMore": end_index < len(demo_products),
        "total": len(demo_products),
        "message": "Demo products loaded successfully"
    }

@router.get("/product/{product_id}")
def get_product_by_id(
    product_id: str,
    use_api: str = Query("true"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """Get product details by product ID"""
    
    # Use AliExpress API if use_api=true
    if use_api.lower() == "true":
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.get_product_by_id(product_id)
            
            if result and result.get("success") and result.get("items"):
                items = result.get("items", [])
                # Add custom titles to products
                items = add_custom_titles_to_products(items)
                
                # Filter products with video if only_with_video=1
                if only_with_video == 1:
                    items = [product for product in items if product.get("video_link") and product.get("video_link").strip()]
                
                return {
                    "success": True,
                    "product_id": product_id,
                    "items": items,
                    "total": result.get("total", 0),
                    "method": result.get("method", "aliexpress.affiliate.productdetail.get"),
                    "source": result.get("source", "aliexpress_api"),
                    "message": f"Found product {product_id} from AliExpress API"
                }
            else:
                # Return error response
                return {
                    "success": False,
                    "product_id": product_id,
                    "items": [],
                    "total": 0,
                    "error": result.get("error", "Product not found") if result else "API request failed",
                    "method": "aliexpress.affiliate.productdetail.get",
                    "source": "aliexpress_api"
                }
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
            return {
                "success": False,
                "product_id": product_id,
                "items": [],
                "total": 0,
                "error": f"API error: {str(e)}",
                "method": "aliexpress.affiliate.productdetail.get",
                "source": "aliexpress_api"
            }
    
    # Demo product for fallback (when use_api=false)
    demo_product = {
        "product_id": product_id,
        "product_title": f"Demo Product {product_id}",
        "sale_price": 29.99,
        "original_price": 49.99,
        "rating": 4.5,
        "review_count": 1250,
        "image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product",
        "product_main_image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product",
        "images_link": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product"],
        "product_small_image_urls": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product"],
        "volume": 5000,
        "category": "Electronics",
        "is_saved": False
    }
    
    # Add custom titles to demo product
    demo_items = add_custom_titles_to_products([demo_product])
    
    # Filter products with video if only_with_video=1
    if only_with_video == 1:
        demo_items = [product for product in demo_items if product.get("video_link") and product.get("video_link").strip()]
    
    return {
        "success": True,
        "product_id": product_id,
        "items": demo_items,
        "total": 1,
        "method": "demo_product",
        "source": "demo_data",
        "message": f"Demo product {product_id} loaded successfully"
    }

@router.put("/products/{product_id}/custom-title")
def save_custom_title(
    product_id: str,
    custom_title: str = Query(..., description="Custom product title")
):
    """Save custom title for a product - only if product exists in saved_products table"""
    
    if not custom_title.strip():
        raise HTTPException(status_code=400, detail="Custom title cannot be empty")
    
    if len(custom_title.strip()) > 500:
        raise HTTPException(status_code=400, detail="Custom title too long (max 500 characters)")
    
    try:
        connection = mysql.connector.connect(**settings.get_database_config())
        cursor = connection.cursor()
        
        # Check if product exists in saved_products table
        cursor.execute("SELECT product_id FROM saved_products WHERE product_id = %s", (product_id,))
        existing_product = cursor.fetchone()
        
        if existing_product:
            # Update existing product's custom title
            cursor.execute(
                "UPDATE saved_products SET custom_title = %s, updated_at = CURRENT_TIMESTAMP WHERE product_id = %s",
                (custom_title.strip(), product_id)
            )
            connection.commit()
            cursor.close()
            connection.close()
            
            return {
                "success": True,
                "product_id": product_id,
                "custom_title": custom_title.strip(),
                "message": f"Custom title updated successfully for product {product_id}"
            }
        else:
            # Product not found in saved_products table
            cursor.close()
            connection.close()
            
            return {
                "success": False,
                "product_id": product_id,
                "error": "Product not found in saved_products table",
                "message": f"Product {product_id} is not saved, cannot update custom title"
            }
        
    except mysql.connector.Error as e:
        return {
            "success": False,
            "product_id": product_id,
            "error": f"Database error: {str(e)}",
            "message": "Failed to save custom title"
        }
    except Exception as e:
        return {
            "success": False,
            "product_id": product_id,
            "error": f"Unexpected error: {str(e)}",
            "message": "Failed to save custom title"
        }

@router.get("/products/{product_id}/custom-title")
def get_custom_title(product_id: str):
    """Get custom title for a product from saved_products table"""
    
    try:
        connection = mysql.connector.connect(**settings.get_database_config())
        cursor = connection.cursor()
        
        cursor.execute("SELECT custom_title FROM saved_products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result and result[0]:
            return {
                "success": True,
                "product_id": product_id,
                "custom_title": result[0],
                "message": f"Custom title found for product {product_id}"
            }
        else:
            return {
                "success": True,
                "product_id": product_id,
                "custom_title": None,
                "message": f"No custom title found for product {product_id}"
            }
        
    except mysql.connector.Error as e:
        return {
            "success": False,
            "product_id": product_id,
            "error": f"Database error: {str(e)}",
            "message": "Failed to get custom title"
        }
    except Exception as e:
        return {
            "success": False,
            "product_id": product_id,
            "error": f"Unexpected error: {str(e)}",
            "message": "Failed to get custom title"
        }

@router.post("/products/batch/custom-titles")
def get_batch_custom_titles(product_ids: list[str]):
    """Get custom titles for multiple products at once"""
    
    if not product_ids or len(product_ids) == 0:
        return {
            "success": True,
            "custom_titles": {},
            "message": "No product IDs provided"
        }
    
    try:
        connection = mysql.connector.connect(**settings.get_database_config())
        cursor = connection.cursor()
        
        # Create placeholders for the IN clause
        placeholders = ','.join(['%s' for _ in product_ids])
        query = f"SELECT product_id, custom_title FROM saved_products WHERE product_id IN ({placeholders})"
        
        cursor.execute(query, product_ids)
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Build response object
        custom_titles = {}
        for row in results:
            product_id, custom_title = row
            if custom_title and custom_title.strip() != '':
                custom_titles[product_id] = custom_title.strip()
        
        return {
            "success": True,
            "custom_titles": custom_titles,
            "total_found": len(custom_titles),
            "message": f"Found {len(custom_titles)} custom titles out of {len(product_ids)} products"
        }
        
    except mysql.connector.Error as e:
        return {
            "success": False,
            "custom_titles": {},
            "error": f"Database error: {str(e)}",
            "message": "Failed to get batch custom titles"
        }
    except Exception as e:
        return {
            "success": False,
            "custom_titles": {},
            "error": f"Unexpected error: {str(e)}",
            "message": "Failed to get batch custom titles"
        }