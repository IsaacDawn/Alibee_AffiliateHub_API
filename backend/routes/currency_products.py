from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from services.currency_converter import currency_converter
from services.aliexpress import AliExpressService
from database.connection import db_ops
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

def get_demo_products(limit: int = 150) -> List[Dict[str, Any]]:
    """Generate demo products for testing currency conversion"""
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
            "title": "Smart Watch with Health Monitoring",
            "sale_price": 79.99,
            "sale_price_currency": "USD",
            "original_price": 99.99,
            "original_price_currency": "USD",
            "rating": 4.3,
            "review_count": 890,
            "image_url": "https://via.placeholder.com/300x300/10B981/FFFFFF?text=Smart+Watch",
            "product_main_image_url": "https://via.placeholder.com/300x300/10B981/FFFFFF?text=Smart+Watch",
            "images_link": ["https://via.placeholder.com/300x300/10B981/FFFFFF?text=Smart+Watch"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/10B981/FFFFFF?text=Smart+Watch"],
            "volume": 3200,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093802",
            "title": "Portable Power Bank 20000mAh",
            "sale_price": 19.99,
            "sale_price_currency": "USD",
            "original_price": 29.99,
            "original_price_currency": "USD",
            "rating": 4.7,
            "review_count": 2100,
            "image_url": "https://via.placeholder.com/300x300/F59E0B/FFFFFF?text=Power+Bank",
            "product_main_image_url": "https://via.placeholder.com/300x300/F59E0B/FFFFFF?text=Power+Bank",
            "images_link": ["https://via.placeholder.com/300x300/F59E0B/FFFFFF?text=Power+Bank"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/F59E0B/FFFFFF?text=Power+Bank"],
            "volume": 8500,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093803",
            "title": "LED Strip Lights RGB 16.4ft",
            "sale_price": 12.99,
            "sale_price_currency": "USD",
            "original_price": 19.99,
            "original_price_currency": "USD",
            "rating": 4.2,
            "review_count": 1500,
            "image_url": "https://via.placeholder.com/300x300/EF4444/FFFFFF?text=LED+Strip",
            "product_main_image_url": "https://via.placeholder.com/300x300/EF4444/FFFFFF?text=LED+Strip",
            "images_link": ["https://via.placeholder.com/300x300/EF4444/FFFFFF?text=LED+Strip"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/EF4444/FFFFFF?text=LED+Strip"],
            "volume": 12000,
            "category": "Home & Garden",
            "is_saved": False
        },
        {
            "product_id": "1005010032093804",
            "title": "Bluetooth Speaker Waterproof",
            "sale_price": 24.99,
            "sale_price_currency": "USD",
            "original_price": 39.99,
            "original_price_currency": "USD",
            "rating": 4.4,
            "review_count": 3200,
            "image_url": "https://via.placeholder.com/300x300/8B5CF6/FFFFFF?text=Speaker",
            "product_main_image_url": "https://via.placeholder.com/300x300/8B5CF6/FFFFFF?text=Speaker",
            "images_link": ["https://via.placeholder.com/300x300/8B5CF6/FFFFFF?text=Speaker"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/8B5CF6/FFFFFF?text=Speaker"],
            "volume": 6800,
            "category": "Electronics",
            "is_saved": False
        }
    ]
    
    # Return limited number of products
    return demo_products[:limit]

@router.get("/products/search-with-currency")
async def search_products_with_currency_conversion(
    query: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(150, ge=1, le=200),
    pageSize: int = Query(150, ge=1, le=200, description="Number of products per page (alias for limit)"),
    target_currency: str = Query("USD", description="Target currency for price conversion"),
    minPrice: Optional[float] = Query(None, ge=0),
    maxPrice: Optional[float] = Query(None, ge=0),
    category: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("price"),
    sortOrder: Optional[str] = Query("asc"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)"),
    use_api: str = Query("true")
):
    """
    Search products and convert all prices to target currency
    """
    try:
        # Initialize AliExpress service
        aliexpress_service = AliExpressService()
        
        # Use pageSize if provided, otherwise use limit
        effective_limit = pageSize if pageSize != 150 else limit
        
        # Search products using existing service
        search_params = {
            "query": query,
            "page": page,
            "limit": effective_limit,
            "minPrice": minPrice,
            "maxPrice": maxPrice,
            "category": category,
            "sortBy": sortBy,
            "sortOrder": sortOrder,
            "hasVideo": (only_with_video == 1),
            "use_api": use_api
        }
        
        # Get products from AliExpress service
        if use_api.lower() == "true":
            try:
                logging.info(f"Calling AliExpress API with params: {search_params}")
                
                # Use the existing search method
                api_response = await aliexpress_service.search_products_with_filters(**search_params)
                logging.info(f"AliExpress API response: {api_response}")
                
                products = api_response.get("data", [])
                
                if not products:
                    logging.warning("No products from AliExpress API")
                    # Don't use demo data, return empty with error info
                    return {
                        "success": False,
                        "data": [],
                        "pagination": {
                            "page": page,
                            "limit": effective_limit,
                            "pageSize": effective_limit,
                            "total": 0,
                            "hasMore": False
                        },
                        "currency_conversion": {
                            "total_products": 0,
                            "successful_conversions": 0,
                            "failed_conversions": 0,
                            "target_currency": target_currency,
                            "conversion_errors": ["No products returned from AliExpress API"]
                        },
                        "api_debug": {
                            "aliexpress_response": api_response,
                            "search_params": search_params,
                            "api_configured": aliexpress_service.client.app_key is not None
                        },
                        "message": "No products found from AliExpress API"
                    }
            except Exception as e:
                logging.error(f"AliExpress API error: {e}")
                # Return error instead of demo data
                return {
                    "success": False,
                    "data": [],
                    "pagination": {
                        "page": page,
                        "limit": effective_limit,
                        "pageSize": effective_limit,
                        "total": 0,
                        "hasMore": False
                    },
                    "currency_conversion": {
                        "total_products": 0,
                        "successful_conversions": 0,
                        "failed_conversions": 0,
                        "target_currency": target_currency,
                        "conversion_errors": [f"AliExpress API error: {str(e)}"]
                    },
                    "api_debug": {
                        "error": str(e),
                        "search_params": search_params,
                        "api_configured": aliexpress_service.client.app_key is not None
                    },
                    "message": f"AliExpress API error: {str(e)}"
                }
        else:
            # If use_api=false, return error
            return {
                "success": False,
                "data": [],
                "pagination": {
                    "page": page,
                    "limit": effective_limit,
                    "pageSize": effective_limit,
                    "total": 0,
                    "hasMore": False
                },
                "currency_conversion": {
                    "total_products": 0,
                    "successful_conversions": 0,
                    "failed_conversions": 0,
                    "target_currency": target_currency,
                    "conversion_errors": ["API disabled (use_api=false)"]
                },
                "message": "API is disabled. Set use_api=true to use AliExpress API"
            }
        
        # Convert prices for each product
        converted_products = []
        conversion_stats = {
            "total_products": len(products),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "target_currency": target_currency,
            "conversion_errors": []
        }
        
        for product in products:
            try:
                converted_product = product.copy()
                
                # Get original currency from product
                original_currency = product.get("original_price_currency", "USD")
                
                # Convert sale_price if exists
                if "sale_price" in product and product["sale_price"]:
                    try:
                        converted_sale_price = currency_converter.convert_price(
                            product["sale_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_sale_price is not None:
                            converted_product["sale_price"] = round(converted_sale_price, 2)
                            converted_product["sale_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                        else:
                            conversion_stats["failed_conversions"] += 1
                            conversion_stats["conversion_errors"].append(f"Failed to convert sale_price for product {product.get('id', 'unknown')}")
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Sale price conversion error for product {product.get('id', 'unknown')}: {str(e)}")
                
                # Convert original_price if exists
                if "original_price" in product and product["original_price"]:
                    try:
                        converted_original_price = currency_converter.convert_price(
                            product["original_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_original_price is not None:
                            converted_product["original_price"] = round(converted_original_price, 2)
                            converted_product["original_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                        else:
                            conversion_stats["failed_conversions"] += 1
                            conversion_stats["conversion_errors"].append(f"Failed to convert original_price for product {product.get('id', 'unknown')}")
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Original price conversion error for product {product.get('id', 'unknown')}: {str(e)}")
                
                # Add conversion info to product
                converted_product["currency_conversion_info"] = {
                    "original_currency": original_currency,
                    "target_currency": target_currency,
                    "converted": True
                }
                
                converted_products.append(converted_product)
                
            except Exception as e:
                logging.error(f"Error processing product {product.get('id', 'unknown')}: {e}")
                conversion_stats["failed_conversions"] += 1
                conversion_stats["conversion_errors"].append(f"Product processing error: {str(e)}")
                # Add original product with error info
                product["currency_conversion_info"] = {
                    "original_currency": product.get("original_price_currency", "USD"),
                    "target_currency": target_currency,
                    "converted": False,
                    "error": str(e)
                }
                converted_products.append(product)
        
        # Add custom titles to products
        converted_products = add_custom_titles_to_products(converted_products)
        
        return {
            "success": True,
            "data": converted_products,
            "pagination": {
                "page": page,
                "limit": effective_limit,
                "pageSize": effective_limit,
                "total": len(converted_products),
                "hasMore": len(converted_products) >= effective_limit
            },
            "currency_conversion": conversion_stats,
            "message": f"Found {len(converted_products)} products with currency conversion to {target_currency}"
        }
        
    except Exception as e:
        logging.error(f"Search with currency conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Search with currency conversion failed: {str(e)}")

@router.get("/products/initial-with-currency")
async def get_initial_products_with_currency_conversion(
    limit: int = Query(150, ge=1, le=200),
    pageSize: int = Query(150, ge=1, le=200, description="Number of products per page (alias for limit)"),
    target_currency: str = Query("USD", description="Target currency for price conversion"),
    use_api: str = Query("true"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """
    Get initial products with currency conversion
    """
    try:
        # Initialize AliExpress service
        aliexpress_service = AliExpressService()
        
        # Use pageSize if provided, otherwise use limit
        effective_limit = pageSize if pageSize != 150 else limit
        
        # Get initial products
        if use_api.lower() == "true":
            try:
                logging.info(f"Calling AliExpress API for hot products with limit: {effective_limit}")
                
                api_response = await aliexpress_service.get_hot_products(limit=effective_limit)
                logging.info(f"AliExpress API response: {api_response}")
                
                products = api_response.get("items", [])
                
                if not products:
                    logging.warning("No products from AliExpress API")
                    # Don't use demo data, return empty with error info
                    return {
                        "success": False,
                        "items": [],
                        "pagination": {
                            "limit": effective_limit,
                            "pageSize": effective_limit,
                            "total": 0,
                            "hasMore": False
                        },
                        "currency_conversion": {
                            "total_products": 0,
                            "successful_conversions": 0,
                            "failed_conversions": 0,
                            "target_currency": target_currency,
                            "conversion_errors": ["No products returned from AliExpress API"]
                        },
                        "api_debug": {
                            "aliexpress_response": api_response,
                            "limit": effective_limit,
                            "api_configured": aliexpress_service.client.app_key is not None
                        },
                        "message": "No products found from AliExpress API"
                    }
            except Exception as e:
                logging.error(f"AliExpress API error: {e}")
                # Return error instead of demo data
                return {
                    "success": False,
                    "items": [],
                    "pagination": {
                        "limit": effective_limit,
                        "pageSize": effective_limit,
                        "total": 0,
                        "hasMore": False
                    },
                    "currency_conversion": {
                        "total_products": 0,
                        "successful_conversions": 0,
                        "failed_conversions": 0,
                        "target_currency": target_currency,
                        "conversion_errors": [f"AliExpress API error: {str(e)}"]
                    },
                    "api_debug": {
                        "error": str(e),
                        "limit": effective_limit,
                        "api_configured": aliexpress_service.client.app_key is not None
                    },
                    "message": f"AliExpress API error: {str(e)}"
                }
        else:
            # If use_api=false, return error
            return {
                "success": False,
                "items": [],
                "pagination": {
                    "limit": effective_limit,
                    "pageSize": effective_limit,
                    "total": 0,
                    "hasMore": False
                },
                "currency_conversion": {
                    "total_products": 0,
                    "successful_conversions": 0,
                    "failed_conversions": 0,
                    "target_currency": target_currency,
                    "conversion_errors": ["API disabled (use_api=false)"]
                },
                "message": "API is disabled. Set use_api=true to use AliExpress API"
            }
        
        # Convert prices for each product
        converted_products = []
        conversion_stats = {
            "total_products": len(products),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "target_currency": target_currency,
            "conversion_errors": []
        }
        
        for product in products:
            try:
                converted_product = product.copy()
                
                # Get original currency from product
                original_currency = product.get("original_price_currency", "USD")
                
                # Convert sale_price if exists
                if "sale_price" in product and product["sale_price"]:
                    try:
                        converted_sale_price = currency_converter.convert_price(
                            product["sale_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_sale_price is not None:
                            converted_product["sale_price"] = round(converted_sale_price, 2)
                            converted_product["sale_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Sale price conversion error: {str(e)}")
                
                # Convert original_price if exists
                if "original_price" in product and product["original_price"]:
                    try:
                        converted_original_price = currency_converter.convert_price(
                            product["original_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_original_price is not None:
                            converted_product["original_price"] = round(converted_original_price, 2)
                            converted_product["original_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Original price conversion error: {str(e)}")
                
                # Add conversion info to product
                converted_product["currency_conversion_info"] = {
                    "original_currency": original_currency,
                    "target_currency": target_currency,
                    "converted": True
                }
                
                converted_products.append(converted_product)
                
            except Exception as e:
                logging.error(f"Error processing product: {e}")
                conversion_stats["failed_conversions"] += 1
                conversion_stats["conversion_errors"].append(f"Product processing error: {str(e)}")
                # Add original product with error info
                product["currency_conversion_info"] = {
                    "original_currency": product.get("original_price_currency", "USD"),
                    "target_currency": target_currency,
                    "converted": False,
                    "error": str(e)
                }
                converted_products.append(product)
        
        # Add custom titles to products
        converted_products = add_custom_titles_to_products(converted_products)
        
        return {
            "success": True,
            "items": converted_products,
            "pagination": {
                "limit": effective_limit,
                "pageSize": effective_limit,
                "total": len(converted_products),
                "hasMore": len(converted_products) >= effective_limit
            },
            "currency_conversion": conversion_stats,
            "message": f"Loaded {len(converted_products)} initial products with currency conversion to {target_currency}"
        }
        
    except Exception as e:
        logging.error(f"Initial products with currency conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Initial products with currency conversion failed: {str(e)}")

@router.post("/products/bulk-currency-conversion")
async def bulk_currency_conversion(
    products: List[Dict[str, Any]],
    target_currency: str = Query("USD", description="Target currency for price conversion"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """
    Convert currency for a list of products
    """
    try:
        converted_products = []
        conversion_stats = {
            "total_products": len(products),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "target_currency": target_currency,
            "conversion_errors": []
        }
        
        for product in products:
            try:
                converted_product = product.copy()
                
                # Get original currency from product
                original_currency = product.get("original_price_currency", "USD")
                
                # Convert sale_price if exists
                if "sale_price" in product and product["sale_price"]:
                    try:
                        converted_sale_price = currency_converter.convert_price(
                            product["sale_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_sale_price is not None:
                            converted_product["sale_price"] = round(converted_sale_price, 2)
                            converted_product["sale_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Sale price conversion error: {str(e)}")
                
                # Convert original_price if exists
                if "original_price" in product and product["original_price"]:
                    try:
                        converted_original_price = currency_converter.convert_price(
                            product["original_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_original_price is not None:
                            converted_product["original_price"] = round(converted_original_price, 2)
                            converted_product["original_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Original price conversion error: {str(e)}")
                
                # Add conversion info to product
                converted_product["currency_conversion_info"] = {
                    "original_currency": original_currency,
                    "target_currency": target_currency,
                    "converted": True
                }
                
                converted_products.append(converted_product)
                
            except Exception as e:
                logging.error(f"Error processing product: {e}")
                conversion_stats["failed_conversions"] += 1
                conversion_stats["conversion_errors"].append(f"Product processing error: {str(e)}")
                # Add original product with error info
                product["currency_conversion_info"] = {
                    "original_currency": product.get("original_price_currency", "USD"),
                    "target_currency": target_currency,
                    "converted": False,
                    "error": str(e)
                }
                converted_products.append(product)
        
        # Add custom titles to products
        converted_products = add_custom_titles_to_products(converted_products)
        
        return {
            "success": True,
            "data": converted_products,
            "currency_conversion": conversion_stats,
            "message": f"Converted {len(converted_products)} products to {target_currency}"
        }
        
    except Exception as e:
        logging.error(f"Bulk currency conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk currency conversion failed: {str(e)}")

@router.get("/products/test-currency-conversion")
async def test_currency_conversion(
    target_currency: str = Query("EUR", description="Target currency for testing"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """
    Test endpoint to verify currency conversion is working
    """
    try:
        # Get demo products
        products = get_demo_products(3)  # Just 3 products for testing
        
        # Convert prices for each product
        converted_products = []
        conversion_stats = {
            "total_products": len(products),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "target_currency": target_currency,
            "conversion_errors": []
        }
        
        for product in products:
            try:
                converted_product = product.copy()
                
                # Get original currency from product
                original_currency = product.get("original_price_currency", "USD")
                
                # Convert sale_price if exists
                if "sale_price" in product and product["sale_price"]:
                    try:
                        converted_sale_price = currency_converter.convert_price(
                            product["sale_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_sale_price is not None:
                            converted_product["sale_price"] = round(converted_sale_price, 2)
                            converted_product["sale_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                        else:
                            conversion_stats["failed_conversions"] += 1
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Sale price conversion error: {str(e)}")
                
                # Convert original_price if exists
                if "original_price" in product and product["original_price"]:
                    try:
                        converted_original_price = currency_converter.convert_price(
                            product["original_price"], 
                            original_currency, 
                            target_currency
                        )
                        if converted_original_price is not None:
                            converted_product["original_price"] = round(converted_original_price, 2)
                            converted_product["original_price_currency"] = target_currency
                            conversion_stats["successful_conversions"] += 1
                        else:
                            conversion_stats["failed_conversions"] += 1
                    except Exception as e:
                        conversion_stats["failed_conversions"] += 1
                        conversion_stats["conversion_errors"].append(f"Original price conversion error: {str(e)}")
                
                # Add conversion info to product
                converted_product["currency_conversion_info"] = {
                    "original_currency": original_currency,
                    "target_currency": target_currency,
                    "converted": True
                }
                
                converted_products.append(converted_product)
                
            except Exception as e:
                logging.error(f"Error processing product: {e}")
                conversion_stats["failed_conversions"] += 1
                conversion_stats["conversion_errors"].append(f"Product processing error: {str(e)}")
                # Add original product with error info
                product["currency_conversion_info"] = {
                    "original_currency": product.get("original_price_currency", "USD"),
                    "target_currency": target_currency,
                    "converted": False,
                    "error": str(e)
                }
                converted_products.append(product)
        
        # Add custom titles to products
        converted_products = add_custom_titles_to_products(converted_products)
        
        return {
            "success": True,
            "data": converted_products,
            "currency_conversion": conversion_stats,
            "message": f"Test completed: {len(converted_products)} products converted to {target_currency}",
            "test_info": {
                "endpoint": "test-currency-conversion",
                "demo_products_used": True,
                "currency_converter_status": "working"
            }
        }
        
    except Exception as e:
        logging.error(f"Test currency conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Test currency conversion failed: {str(e)}")

@router.get("/products/api-status")
async def check_api_status():
    """
    Check AliExpress API configuration and status
    """
    try:
        aliexpress_service = AliExpressService()
        
        # Check if API is configured
        api_configured = aliexpress_service.client.app_key is not None and aliexpress_service.client.app_secret is not None
        
        # Try a simple API call to test connectivity
        api_working = False
        api_error = None
        test_response = None
        
        if api_configured:
            try:
                # Try to get hot products with limit 1
                test_response = await aliexpress_service.get_hot_products(limit=1)
                api_working = test_response is not None and test_response.get("items")
            except Exception as e:
                api_error = str(e)
        
        return {
            "success": True,
            "api_status": {
                "configured": api_configured,
                "working": api_working,
                "app_key": aliexpress_service.client.app_key[:10] + "..." if aliexpress_service.client.app_key else None,
                "app_secret": "***" if aliexpress_service.client.app_secret else None,
                "base_url": aliexpress_service.client.base_url,
                "error": api_error,
                "test_response": test_response
            },
            "message": "API status checked"
        }
        
    except Exception as e:
        logging.error(f"API status check error: {e}")
        return {
            "success": False,
            "api_status": {
                "configured": False,
                "working": False,
                "error": str(e)
            },
            "message": f"API status check failed: {str(e)}"
        }
