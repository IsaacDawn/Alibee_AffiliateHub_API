# backend/routes/simple_search.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from services.aliexpress import AliExpressService
from services.online_currency_converter import online_currency_converter
from database.connection import db_ops
import logging

router = APIRouter()

def _safe_float(value):
    """Safely convert value to float, handling null/None/empty values as 0"""
    try:
        if value is None or value == '' or str(value).lower() in ['null', 'none']:
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def _calculate_discount_percentage(product):
    """Calculate discount percentage for a product"""
    try:
        original_price = product.get("originalPrice") or product.get("original_price")
        sale_price = product.get("price") or product.get("sale_price")
        
        if original_price and sale_price and original_price > 0 and sale_price < original_price:
            discount = ((original_price - sale_price) / original_price) * 100
            return round(discount, 2)
        return 0.0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0

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

@router.get("/search")
def search_products(
    q: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(150, ge=1, le=200),
    sort: Optional[str] = Query("volume_desc"),
    minPrice: Optional[float] = Query(None),
    maxPrice: Optional[float] = Query(None),
    target_currency: Optional[str] = Query("USD", description="Target currency for price conversion (USD, EUR, ILS)"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)"),
    use_api: str = Query("true")
):
    """Search products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Use AliExpress API if use_api=true and query is provided
    if use_api.lower() == "true" and q and q.strip():
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.search_products_with_filters(
                query=q,
                page=page,
                page_size=pageSize,
                sort=sort,
                min_price=minPrice,
                max_price=maxPrice,
                has_video=(only_with_video == 1)
            )
            
            if result and result.get("items"):
                # Convert currency if target_currency is specified
                products = result.get("items", [])
                conversion_stats = {
                    "total_products": len(products),
                    "successful_conversions": 0,
                    "failed_conversions": 0,
                    "target_currency": target_currency,
                    "conversion_errors": []
                }
                
                # Optimized currency conversion - batch process all products
                if target_currency and target_currency.upper() != "USD":
                    try:
                        logging.info(f"Starting optimized currency conversion for {len(products)} products to {target_currency}")
                        
                        # Prepare all conversion requests at once
                        conversion_requests = []
                        product_conversion_map = {}
                        
                        for i, product in enumerate(products):
                            original_currency = product.get("original_price_currency", "USD")
                            
                            # Add sale_price conversion request
                            if "sale_price" in product and product["sale_price"]:
                                conversion_requests.append({
                                    "price": product["sale_price"],
                                    "from_currency": original_currency,
                                    "to_currency": target_currency,
                                    "product_index": i,
                                    "price_type": "sale_price"
                                })
                            
                            # Add original_price conversion request
                            if "original_price" in product and product["original_price"]:
                                conversion_requests.append({
                                    "price": product["original_price"],
                                    "from_currency": original_currency,
                                    "to_currency": target_currency,
                                    "product_index": i,
                                    "price_type": "original_price"
                                })
                            
                            # Initialize product conversion map
                            if i not in product_conversion_map:
                                product_conversion_map[i] = {
                                    "product": product.copy(),
                                    "conversions": {}
                                }
                        
                        # Perform all conversions in batch using optimized converter
                        logging.info(f"Performing {len(conversion_requests)} currency conversions in batch")
                        
                        # Use online batch conversion
                        batch_results = online_currency_converter.batch_convert_prices(conversion_requests)
                        
                        for i, result in enumerate(batch_results):
                            request = conversion_requests[i]
                            if result["success"]:
                                product_conversion_map[request["product_index"]]["conversions"][request["price_type"]] = result["converted_price"]
                                conversion_stats["successful_conversions"] += 1
                            else:
                                conversion_stats["failed_conversions"] += 1
                                error_msg = result.get("error", "Unknown error")
                                conversion_stats["conversion_errors"].append(f"Failed to convert {request['price_type']} for product {request['product_index']}: {error_msg}")
                        
                        # Apply conversions to products
                        converted_products = []
                        for i, conversion_data in product_conversion_map.items():
                            try:
                                product = conversion_data["product"]
                                conversions = conversion_data["conversions"]
                                
                                # Apply sale_price conversion (keep original, add target)
                                if "sale_price" in conversions:
                                    product["sale_price_target"] = conversions["sale_price"]
                                    product["sale_price_currency_target"] = target_currency
                                
                                # Apply original_price conversion (keep original, add target)
                                if "original_price" in conversions:
                                    product["original_price_target"] = conversions["original_price"]
                                    product["original_price_currency_target"] = target_currency
                                
                                # Add conversion info
                                product["currency_conversion_info"] = {
                                    "original_currency": product.get("original_price_currency", "USD"),
                                    "target_currency": target_currency,
                                    "converted": True
                                }
                                
                                converted_products.append(product)
                                
                            except Exception as e:
                                logging.error(f"Error applying conversions to product {i}: {e}")
                                # Add original product with error info
                                original_product = conversion_data["product"]
                                original_product["currency_conversion_info"] = {
                                    "original_currency": original_product.get("original_price_currency", "USD"),
                                    "target_currency": target_currency,
                                    "converted": False,
                                    "error": str(e)
                                }
                                converted_products.append(original_product)
                        
                        products = converted_products
                        logging.info(f"Currency conversion completed: {conversion_stats['successful_conversions']} successful, {conversion_stats['failed_conversions']} failed")
                        
                    except Exception as e:
                        logging.error(f"Batch currency conversion error: {e}")
                        # Continue with original products if conversion fails
                        conversion_stats["conversion_errors"].append(f"Batch conversion failed: {str(e)}")
                elif target_currency and target_currency.upper() == "USD":
                    # If target currency is USD, just add conversion info without actual conversion
                    for product in products:
                        product["currency_conversion_info"] = {
                            "original_currency": product.get("original_price_currency", "USD"),
                            "target_currency": "USD",
                            "converted": False,
                            "reason": "Target currency is same as original"
                        }
                
                # Add custom titles to products
                products = add_custom_titles_to_products(products)
                
                return {
                    "page": page,
                    "pageSize": pageSize,
                    "hasMore": result.get("hasMore", False),
                    "total": result.get("total", 0),
                    "query": q,
                    "currency_conversion": conversion_stats,
                    "message": f"Found {len(products)} products from AliExpress API with currency conversion to {target_currency}",
                    "success": True,
                    "items": products
                }
            else:
                # Fallback to demo products if API fails
                print(f"AliExpress API failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
            # Fallback to demo products if API fails
    
    # Demo products for search (fallback or when use_api=false)
    demo_products = [
        {
            "product_id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "sale_price": 29.99,
            "sale_price_currency": "USD",
            "original_price": 49.99,
            "original_price_currency": "USD",
            "rating": 4.5,
            "review_count": 1250,
            "product_score_stars": 4.5,
            "image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "product_main_image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "images_link": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "video_link": "https://example.com/video/headphones.mp4",
            "volume": 5000,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "sale_price": 89.99,
            "sale_price_currency": "USD",
            "original_price": 129.99,
            "original_price_currency": "USD",
            "rating": 4.3,
            "product_score_stars": 4.3,
            "review_count": 890,
            "image_url": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "product_main_image_url": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "images_link": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "volume": 3200,
            "category": "Watches",
            "is_saved": False
        },
        {
            "product_id": "1005010032093802",
            "title": "Portable Phone Charger 20000mAh",
            "sale_price": 19.99,
            "sale_price_currency": "USD",
            "original_price": 29.99,
            "original_price_currency": "USD",
            "rating": 4.7,
            "product_score_stars": 4.7,
            "review_count": 2100,
            "image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank",
            "product_main_image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank",
            "images_link": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank"],
            "volume": 7500,
            "category": "Phone Accessories",
            "is_saved": False
        },
        {
            "product_id": "1005010032093803",
            "title": "LED Desk Lamp with USB Charging Port",
            "sale_price": 24.99,
            "sale_price_currency": "USD",
            "original_price": 39.99,
            "original_price_currency": "USD",
            "rating": 4.4,
            "product_score_stars": 4.4,
            "review_count": 680,
            "image_url": "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp",
            "product_main_image_url": "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp",
            "images_link": ["https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp"],
            "volume": 1800,
            "category": "Home & Garden",
            "is_saved": False
        },
        {
            "product_id": "1005010032093804",
            "title": "Bluetooth Speaker Waterproof",
            "sale_price": 34.99,
            "sale_price_currency": "USD",
            "original_price": 59.99,
            "original_price_currency": "USD",
            "rating": 4.6,
            "product_score_stars": 4.6,
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
            "sale_price": 15.99,
            "sale_price_currency": "USD",
            "original_price": 25.99,
            "original_price_currency": "USD",
            "rating": 4.2,
            "product_score_stars": 4.2,
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
            "sale_price": 12.99,
            "sale_price_currency": "USD",
            "original_price": 19.99,
            "original_price_currency": "USD",
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
            "sale_price": 18.99,
            "sale_price_currency": "USD",
            "original_price": 28.99,
            "original_price_currency": "USD",
            "rating": 4.3,
            "product_score_stars": 4.3,
            "review_count": 750,
            "image_url": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "product_main_image_url": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "images_link": ["https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale"],
            "volume": 2100,
            "category": "Home & Garden",
            "is_saved": False
        },
        {
            "product_id": "1005010032093808",
            "title": "Travel Backpack Waterproof",
            "sale_price": 45.99,
            "sale_price_currency": "USD",
            "original_price": 69.99,
            "rating": 4.4,
            "product_score_stars": 4.4,
            "review_count": 1100,
            "image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack",
            "product_main_image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack",
            "images_link": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack"],
            "volume": 3500,
            "category": "Travel",
            "is_saved": False
        },
        {
            "product_id": "1005010032093809",
            "title": "Running Shoes Lightweight",
            "sale_price": 79.99,
            "sale_price_currency": "USD",
            "original_price": 119.99,
            "original_price_currency": "USD",
            "rating": 4.6,
            "product_score_stars": 4.6,
            "review_count": 2300,
            "image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes",
            "product_main_image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes",
            "images_link": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes"],
            "volume": 4800,
            "category": "Sports",
            "is_saved": False
        }
    ]
    
    # Filter products based on search query
    filtered_products = demo_products
    if q and q.strip():
        query_lower = q.lower().strip()
        filtered_products = [
            product for product in demo_products
            if (query_lower in product["title"].lower() or 
                query_lower in product["category"].lower() or
                any(keyword in product["title"].lower() for keyword in query_lower.split()))
        ]
    
    # Apply price filters (use sale_price for filtering)
    if minPrice is not None:
        filtered_products = [p for p in filtered_products if p["sale_price"] >= minPrice]
    if maxPrice is not None:
        filtered_products = [p for p in filtered_products if p["sale_price"] <= maxPrice]
    
    # Apply sorting (use sale_price for price sorting)
    if sort == "volume_desc":
        filtered_products.sort(key=lambda x: x["volume"], reverse=True)
    elif sort == "volume_asc":
        filtered_products.sort(key=lambda x: x["volume"])
    elif sort == "price_asc":
        filtered_products.sort(key=lambda x: x["sale_price"])
    elif sort == "price_desc":
        filtered_products.sort(key=lambda x: x["sale_price"], reverse=True)
    elif sort == "rating_desc":
        filtered_products.sort(key=lambda x: _safe_float(x.get("product_score_stars", 0)), reverse=True)
    elif sort == "rating_asc":
        filtered_products.sort(key=lambda x: _safe_float(x.get("product_score_stars", 0)))
    elif sort == "discount_desc":
        filtered_products.sort(key=lambda x: _calculate_discount_percentage(x), reverse=True)
    elif sort == "discount_asc":
        filtered_products.sort(key=lambda x: _calculate_discount_percentage(x))
    
    # Calculate pagination
    start_index = (page - 1) * pageSize
    end_index = start_index + pageSize
    paginated_products = filtered_products[start_index:end_index]
    
    # Convert currency for demo products if target_currency is specified
    conversion_stats = {
        "total_products": len(paginated_products),
        "successful_conversions": 0,
        "failed_conversions": 0,
        "target_currency": target_currency,
        "conversion_errors": []
    }
    
    if target_currency and target_currency.upper() != "USD":
        try:
            logging.info(f"Starting optimized currency conversion for {len(paginated_products)} demo products to {target_currency}")
            
            # Prepare all conversion requests at once
            conversion_requests = []
            product_conversion_map = {}
            
            for i, product in enumerate(paginated_products):
                original_currency = product.get("original_price_currency", "USD")
                
                # Add sale_price conversion request
                if "sale_price" in product and product["sale_price"]:
                    conversion_requests.append({
                        "price": product["sale_price"],
                        "from_currency": original_currency,
                        "to_currency": target_currency,
                        "product_index": i,
                        "price_type": "sale_price"
                    })
                
                # Add original_price conversion request
                if "original_price" in product and product["original_price"]:
                    conversion_requests.append({
                        "price": product["original_price"],
                        "from_currency": original_currency,
                        "to_currency": target_currency,
                        "product_index": i,
                        "price_type": "original_price"
                    })
                
                # Initialize product conversion map
                if i not in product_conversion_map:
                    product_conversion_map[i] = {
                        "product": product.copy(),
                        "conversions": {}
                    }
            
            # Perform all conversions in batch using optimized converter
            logging.info(f"Performing {len(conversion_requests)} demo currency conversions in batch")
            
            # Use online batch conversion
            batch_results = online_currency_converter.batch_convert_prices(conversion_requests)
            
            for i, result in enumerate(batch_results):
                request = conversion_requests[i]
                if result["success"]:
                    product_conversion_map[request["product_index"]]["conversions"][request["price_type"]] = result["converted_price"]
                    conversion_stats["successful_conversions"] += 1
                else:
                    conversion_stats["failed_conversions"] += 1
                    error_msg = result.get("error", "Unknown error")
                    conversion_stats["conversion_errors"].append(f"Failed to convert {request['price_type']} for demo product {request['product_index']}: {error_msg}")
            
            # Apply conversions to products
            converted_products = []
            for i, conversion_data in product_conversion_map.items():
                try:
                    product = conversion_data["product"]
                    conversions = conversion_data["conversions"]
                    
                    # Apply sale_price conversion (keep original, add target)
                    if "sale_price" in conversions:
                        product["sale_price_target"] = conversions["sale_price"]
                        product["sale_price_currency_target"] = target_currency
                    
                    # Apply original_price conversion (keep original, add target)
                    if "original_price" in conversions:
                        product["original_price_target"] = conversions["original_price"]
                        product["original_price_currency_target"] = target_currency
                    
                    # Add conversion info
                    product["currency_conversion_info"] = {
                        "original_currency": product.get("original_price_currency", "USD"),
                        "target_currency": target_currency,
                        "converted": True
                    }
                    
                    converted_products.append(product)
                    
                except Exception as e:
                    logging.error(f"Error applying conversions to demo product {i}: {e}")
                    # Add original product with error info
                    original_product = conversion_data["product"]
                    original_product["currency_conversion_info"] = {
                        "original_currency": original_product.get("original_price_currency", "USD"),
                        "target_currency": target_currency,
                        "converted": False,
                        "error": str(e)
                    }
                    converted_products.append(original_product)
            
            paginated_products = converted_products
            logging.info(f"Demo currency conversion completed: {conversion_stats['successful_conversions']} successful, {conversion_stats['failed_conversions']} failed")
            
        except Exception as e:
            logging.error(f"Demo batch currency conversion error: {e}")
            # Continue with original products if conversion fails
            conversion_stats["conversion_errors"].append(f"Demo batch conversion failed: {str(e)}")
    elif target_currency and target_currency.upper() == "USD":
        # If target currency is USD, just add conversion info without actual conversion
        for product in paginated_products:
            product["currency_conversion_info"] = {
                "original_currency": product.get("original_price_currency", "USD"),
                "target_currency": "USD",
                "converted": False,
                "reason": "Target currency is same as original"
            }
    
    # Add custom titles to demo products
    paginated_products = add_custom_titles_to_products(paginated_products)
    
    return {
        "page": page,
        "pageSize": pageSize,
        "hasMore": end_index < len(filtered_products),
        "total": len(filtered_products),
        "query": q,
        "currency_conversion": conversion_stats,
        "message": f"Found {len(paginated_products)} products for '{q}' with currency conversion to {target_currency}",
        "success": True,
        "items": paginated_products
    }

@router.post("/search/bulk-currency-conversion")
async def bulk_currency_conversion(
    products: List[Dict[str, Any]],
    target_currency: str = Query("EUR", description="Target currency for price conversion")
):
    """
    Optimized bulk currency conversion for multiple products
    """
    try:
        logging.info(f"Starting bulk currency conversion for {len(products)} products to {target_currency}")
        
        conversion_stats = {
            "total_products": len(products),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "target_currency": target_currency,
            "conversion_errors": []
        }
        
        if target_currency.upper() == "USD":
            # If target currency is USD, just add conversion info
            for product in products:
                product["currency_conversion_info"] = {
                    "original_currency": product.get("original_price_currency", "USD"),
                    "target_currency": "USD",
                    "converted": False,
                    "reason": "Target currency is same as original"
                }
            
            return {
                "currency_conversion": conversion_stats,
                "message": f"Processed {len(products)} products (no conversion needed for USD)",
                "success": True,
                "data": products
            }
        
        # Prepare all conversion requests at once
        conversion_requests = []
        product_conversion_map = {}
        
        for i, product in enumerate(products):
            original_currency = product.get("original_price_currency", "USD")
            
            # Add sale_price conversion request
            if "sale_price" in product and product["sale_price"]:
                conversion_requests.append({
                    "price": product["sale_price"],
                    "from_currency": original_currency,
                    "to_currency": target_currency,
                    "product_index": i,
                    "price_type": "sale_price"
                })
            
            # Add original_price conversion request
            if "original_price" in product and product["original_price"]:
                conversion_requests.append({
                    "price": product["original_price"],
                    "from_currency": original_currency,
                    "to_currency": target_currency,
                    "product_index": i,
                    "price_type": "original_price"
                })
            
            # Initialize product conversion map
            if i not in product_conversion_map:
                product_conversion_map[i] = {
                    "product": product.copy(),
                    "conversions": {}
                }
        
        # Perform all conversions in batch using optimized converter
        logging.info(f"Performing {len(conversion_requests)} bulk currency conversions")
        
        # Use online batch conversion
        batch_results = online_currency_converter.batch_convert_prices(conversion_requests)
        
        for i, result in enumerate(batch_results):
            request = conversion_requests[i]
            if result["success"]:
                product_conversion_map[request["product_index"]]["conversions"][request["price_type"]] = result["converted_price"]
                conversion_stats["successful_conversions"] += 1
            else:
                conversion_stats["failed_conversions"] += 1
                error_msg = result.get("error", "Unknown error")
                conversion_stats["conversion_errors"].append(f"Failed to convert {request['price_type']} for product {request['product_index']}: {error_msg}")
        
        # Apply conversions to products
        converted_products = []
        for i, conversion_data in product_conversion_map.items():
            try:
                product = conversion_data["product"]
                conversions = conversion_data["conversions"]
                
                # Apply sale_price conversion (keep original, add target)
                if "sale_price" in conversions:
                    product["sale_price_target"] = conversions["sale_price"]
                    product["sale_price_currency_target"] = target_currency
                
                # Apply original_price conversion (keep original, add target)
                if "original_price" in conversions:
                    product["original_price_target"] = conversions["original_price"]
                    product["original_price_currency_target"] = target_currency
                
                # Add conversion info
                product["currency_conversion_info"] = {
                    "original_currency": product.get("original_price_currency", "USD"),
                    "target_currency": target_currency,
                    "converted": True
                }
                
                converted_products.append(product)
                
            except Exception as e:
                logging.error(f"Error applying conversions to product {i}: {e}")
                # Add original product with error info
                original_product = conversion_data["product"]
                original_product["currency_conversion_info"] = {
                    "original_currency": original_product.get("original_price_currency", "USD"),
                    "target_currency": target_currency,
                    "converted": False,
                    "error": str(e)
                }
                converted_products.append(original_product)
        
        logging.info(f"Bulk currency conversion completed: {conversion_stats['successful_conversions']} successful, {conversion_stats['failed_conversions']} failed")
        
        # Add custom titles to products
        converted_products = add_custom_titles_to_products(converted_products)
        
        return {
            "currency_conversion": conversion_stats,
            "message": f"Converted {len(converted_products)} products to {target_currency}",
            "success": True,
            "data": converted_products
        }
        
    except Exception as e:
        logging.error(f"Bulk currency conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk currency conversion failed: {str(e)}")

@router.get("/search/currency-stats")
async def get_currency_conversion_stats():
    """
    Get currency conversion statistics and performance info
    """
    try:
        stats = online_currency_converter.get_conversion_stats()
        return {
            "success": True,
            "currency_converter_stats": stats,
            "message": "Currency converter statistics retrieved successfully"
        }
    except Exception as e:
        logging.error(f"Error getting currency stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get currency stats: {str(e)}")

@router.get("/search/currency-test")
async def test_currency_api():
    """
    Test online currency API connection and get sample rates
    """
    try:
        test_result = online_currency_converter.test_api_connection()
        return {
            "success": test_result["success"],
            "test_result": test_result,
            "message": "Currency API test completed"
        }
    except Exception as e:
        logging.error(f"Error testing currency API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test currency API: {str(e)}")

@router.get("/search/sorted-by-price")
def search_products_sorted_by_price(
    q: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(150, ge=1, le=200),
    sort_order: str = Query("asc", description="Sort order: 'asc' for ascending, 'desc' for descending"),
    target_currency: Optional[str] = Query("USD", description="Target currency for price conversion (USD, EUR, ILS)"),
    use_api: str = Query("true"),
    price_field: str = Query("sale_price", description="Price field to sort by: 'sale_price' or 'original_price'"),
    min_price: Optional[float] = Query(0, ge=0, description="Minimum price filter - Default: 0"),
    max_price: Optional[float] = Query(1000000, ge=0, description="Maximum price filter - Default: 1000000"),
    sort_by_discount: bool = Query(False, description="Sort by discount percentage instead of price"),
    sort_by_volume: bool = Query(False, description="Sort by latest_volume instead of price"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """
    Search products and sort by price (ascending or descending)
    """
    try:
        # First get products using the main search endpoint
        aliexpress_service = AliExpressService()
        
        if use_api.lower() == "true" and q and q.strip():
            try:
                result = aliexpress_service.search_products_with_filters(
                    query=q.strip(),
                    page=page,
                    page_size=pageSize,
                    sort="price" if sort_order == "asc" else "price_desc",
                    has_video=(only_with_video == 1)
                )
                
                if result and result.get("items"):
                    products = result.get("items", [])
                else:
                    # Fallback to demo products
                    products = get_demo_products()
            except Exception as e:
                logging.error(f"AliExpress API error: {e}")
                products = get_demo_products()
        else:
            products = get_demo_products()
        
        # Convert currency if needed
        conversion_stats = {
            "total_products": len(products),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "target_currency": target_currency,
            "conversion_errors": []
        }
        
        if target_currency and target_currency.upper() != "USD":
            try:
                logging.info(f"Converting {len(products)} products to {target_currency}")
                
                conversion_requests = []
                product_conversion_map = {}
                
                for i, product in enumerate(products):
                    original_currency = product.get("original_price_currency", "USD")
                    
                    # Add sale_price conversion request
                    if "sale_price" in product and product["sale_price"]:
                        conversion_requests.append({
                            "price": product["sale_price"],
                            "from_currency": original_currency,
                            "to_currency": target_currency,
                            "product_index": i,
                            "price_type": "sale_price"
                        })
                    
                    # Add original_price conversion request
                    if "original_price" in product and product["original_price"]:
                        conversion_requests.append({
                            "price": product["original_price"],
                            "from_currency": original_currency,
                            "to_currency": target_currency,
                            "product_index": i,
                            "price_type": "original_price"
                        })
                    
                    if i not in product_conversion_map:
                        product_conversion_map[i] = {
                            "product": product.copy(),
                            "conversions": {}
                        }
                
                # Perform batch conversion
                if conversion_requests:
                    batch_results = online_currency_converter.batch_convert_prices(conversion_requests)
                    
                    for i, result in enumerate(batch_results):
                        request = conversion_requests[i]
                        if result["success"]:
                            product_conversion_map[request["product_index"]]["conversions"][request["price_type"]] = result["converted_price"]
                            conversion_stats["successful_conversions"] += 1
                        else:
                            conversion_stats["failed_conversions"] += 1
                            error_msg = result.get("error", "Unknown error")
                            conversion_stats["conversion_errors"].append(f"Failed to convert {request['price_type']} for product {request['product_index']}: {error_msg}")
                
                # Apply conversions
                converted_products = []
                for i, conversion_data in product_conversion_map.items():
                    product = conversion_data["product"]
                    conversions = conversion_data["conversions"]
                    
                    # Apply sale_price conversion
                    if "sale_price" in conversions:
                        product["sale_price_target"] = conversions["sale_price"]
                        product["sale_price_currency_target"] = target_currency
                    
                    # Apply original_price conversion
                    if "original_price" in conversions:
                        product["original_price_target"] = conversions["original_price"]
                        product["original_price_currency_target"] = target_currency
                    
                    product["currency_conversion_info"] = {
                        "original_currency": product.get("original_price_currency", "USD"),
                        "target_currency": target_currency,
                        "converted": True
                    }
                    
                    converted_products.append(product)
                
                products = converted_products
                
            except Exception as e:
                logging.error(f"Currency conversion error: {e}")
        
        # Sort products by price or discount
        def get_sort_price(product):
            # Use target price if available, otherwise use original price
            if f"{price_field}_target" in product and product[f"{price_field}_target"]:
                return product[f"{price_field}_target"]
            elif price_field in product and product[price_field]:
                return product[price_field]
            else:
                return 0
        
        def get_discount_percentage(product):
            """Calculate discount percentage"""
            try:
                # Get original price
                original_price = None
                if "original_price_target" in product and product["original_price_target"]:
                    original_price = product["original_price_target"]
                elif "original_price" in product and product["original_price"]:
                    original_price = product["original_price"]
                
                # Get sale price
                sale_price = None
                if "sale_price_target" in product and product["sale_price_target"]:
                    sale_price = product["sale_price_target"]
                elif "sale_price" in product and product["sale_price"]:
                    sale_price = product["sale_price"]
                
                # Calculate discount percentage
                if original_price and sale_price and original_price > 0 and sale_price < original_price:
                    discount = ((original_price - sale_price) / original_price) * 100
                    return round(discount, 2)
                else:
                    return 0
            except Exception as e:
                logging.error(f"Error calculating discount for product {product.get('product_id', 'unknown')}: {e}")
                return 0
        
        def get_volume(product):
            """Get latest volume for sorting"""
            try:
                # Try different volume field names
                volume_fields = ["latest_volume", "volume", "sales_volume", "total_volume"]
                
                for field in volume_fields:
                    if field in product and product[field] is not None:
                        volume = product[field]
                        # Convert to int if it's a string
                        if isinstance(volume, str):
                            try:
                                volume = int(volume.replace(',', ''))
                            except ValueError:
                                continue
                        return int(volume) if volume else 0
                
                return 0
            except Exception as e:
                logging.error(f"Error getting volume for product {product.get('product_id', 'unknown')}: {e}")
                return 0
        
        # Apply price filters (always apply since we have defaults)
        filtered_products = []
        for product in products:
            product_price = get_sort_price(product)
            
            # Skip products with no price
            if product_price <= 0:
                continue
            
            # Apply minimum price filter
            if product_price < min_price:
                continue
            
            # Apply maximum price filter
            if product_price > max_price:
                continue
            
            filtered_products.append(product)
        
        products = filtered_products
        logging.info(f"Applied price filters: min={min_price}, max={max_price}. Filtered to {len(products)} products")
        
        # Sort products by price, discount, or volume
        if sort_by_volume:
            # Sort by volume
            if sort_order.lower() == "desc":
                products.sort(key=get_volume, reverse=True)  # Highest volume first
            else:
                products.sort(key=get_volume, reverse=False)  # Lowest volume first
        elif sort_by_discount:
            # Sort by discount percentage
            if sort_order.lower() == "desc":
                products.sort(key=get_discount_percentage, reverse=True)  # Highest discount first
            else:
                products.sort(key=get_discount_percentage, reverse=False)  # Lowest discount first
        else:
            # Sort by price
            if sort_order.lower() == "desc":
                products.sort(key=get_sort_price, reverse=True)
            else:
                products.sort(key=get_sort_price, reverse=False)
        
        # Apply pagination
        start_index = (page - 1) * pageSize
        end_index = start_index + pageSize
        paginated_products = products[start_index:end_index]
        
        # Add custom titles to products
        paginated_products = add_custom_titles_to_products(paginated_products)
        
        # Calculate statistics
        total_products = len(products)
        if total_products > 0:
            prices = [get_sort_price(p) for p in products if get_sort_price(p) > 0]
            discounts = [get_discount_percentage(p) for p in products if get_discount_percentage(p) > 0]
            volumes = [get_volume(p) for p in products if get_volume(p) > 0]
            
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
            else:
                min_price = max_price = avg_price = 0
            
            if discounts:
                min_discount = min(discounts)
                max_discount = max(discounts)
                avg_discount = sum(discounts) / len(discounts)
            else:
                min_discount = max_discount = avg_discount = 0
            
            if volumes:
                min_volume = min(volumes)
                max_volume = max(volumes)
                avg_volume = sum(volumes) / len(volumes)
            else:
                min_volume = max_volume = avg_volume = 0
        else:
            min_price = max_price = avg_price = 0
            min_discount = max_discount = avg_discount = 0
            min_volume = max_volume = avg_volume = 0
        
        return {
            "page": page,
            "pageSize": pageSize,
            "hasMore": end_index < total_products,
            "total": total_products,
            "query": q,
            "sort_info": {
                "sort_by": "latest_volume" if sort_by_volume else ("discount_percentage" if sort_by_discount else price_field),
                "sort_order": sort_order,
                "target_currency": target_currency,
                "sort_by_discount": sort_by_discount,
                "sort_by_volume": sort_by_volume,
                "price_filters": {
                    "min_price_filter": min_price,
                    "max_price_filter": max_price,
                    "filters_applied": True,
                    "default_filters": min_price == 0 and max_price == 1000000
                },
                "price_statistics": {
                    "min_price": round(min_price, 2),
                    "max_price": round(max_price, 2),
                    "avg_price": round(avg_price, 2),
                    "total_products_with_price": len([p for p in products if get_sort_price(p) > 0])
                },
                "discount_statistics": {
                    "min_discount": round(min_discount, 2),
                    "max_discount": round(max_discount, 2),
                    "avg_discount": round(avg_discount, 2),
                    "total_products_with_discount": len([p for p in products if get_discount_percentage(p) > 0])
                },
                "volume_statistics": {
                    "min_volume": int(min_volume),
                    "max_volume": int(max_volume),
                    "avg_volume": int(avg_volume),
                    "total_products_with_volume": len([p for p in products if get_volume(p) > 0])
                }
            },
            "currency_conversion": conversion_stats,
            "message": f"Found {len(paginated_products)} products sorted by {'latest volume' if sort_by_volume else ('discount percentage' if sort_by_discount else price_field)} ({sort_order}) with currency conversion to {target_currency}" + 
                      (f" and price filters (min: {min_price}, max: {max_price})" if not (min_price == 0 and max_price == 1000000) else " with default price filters"),
            "success": True,
            "items": paginated_products
        }
        
    except Exception as e:
        logging.error(f"Error in price-sorted search: {e}")
        raise HTTPException(status_code=500, detail=f"Price-sorted search failed: {str(e)}")

def get_demo_products():
    """Get demo products for testing"""
    return [
        {
            "product_id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "sale_price": 29.99,
            "sale_price_currency": "USD",
            "original_price": 49.99,
            "original_price_currency": "USD",
            "rating": 4.5,
            "review_count": 1250,
            "image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "product_main_image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "images_link": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "volume": 5000,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "sale_price": 89.99,
            "sale_price_currency": "USD",
            "original_price": 129.99,
            "original_price_currency": "USD",
            "rating": 4.3,
            "product_score_stars": 4.3,
            "review_count": 890,
            "image_url": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "product_main_image_url": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "images_link": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "volume": 3200,
            "category": "Watches",
            "is_saved": False
        },
        {
            "product_id": "1005010032093802",
            "title": "Portable Phone Charger 20000mAh",
            "sale_price": 19.99,
            "sale_price_currency": "USD",
            "original_price": 29.99,
            "original_price_currency": "USD",
            "rating": 4.7,
            "product_score_stars": 4.7,
            "review_count": 2100,
            "image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank",
            "product_main_image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank",
            "images_link": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank"],
            "volume": 7500,
            "category": "Phone Accessories",
            "is_saved": False
        },
        {
            "product_id": "1005010032093803",
            "title": "LED Desk Lamp with USB Charging Port",
            "sale_price": 24.99,
            "sale_price_currency": "USD",
            "original_price": 39.99,
            "original_price_currency": "USD",
            "rating": 4.4,
            "product_score_stars": 4.4,
            "review_count": 680,
            "image_url": "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp",
            "product_main_image_url": "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp",
            "images_link": ["https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp"],
            "volume": 1800,
            "category": "Home & Garden",
            "is_saved": False
        },
        {
            "product_id": "1005010032093804",
            "title": "Bluetooth Speaker Waterproof",
            "sale_price": 34.99,
            "sale_price_currency": "USD",
            "original_price": 59.99,
            "original_price_currency": "USD",
            "rating": 4.6,
            "product_score_stars": 4.6,
            "review_count": 1450,
            "image_url": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "product_main_image_url": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "images_link": ["https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker"],
            "volume": 4200,
            "category": "Electronics",
            "is_saved": False
        }
    ]