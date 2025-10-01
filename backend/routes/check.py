# backend/routes/check.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from database.connection import db_ops

router = APIRouter()

@router.get("/check/{product_id}")
def check_product_exists(product_id: str) -> Dict[str, Any]:
    """
    Check if a product exists in the saved products database
    For now, this is a simple implementation that always returns False
    """
    try:
        # Validate product_id format
        if not product_id or not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        # Check if product exists in database
        saved_products_info = db_ops.get_saved_products_info([product_id])
        
        if product_id in saved_products_info:
            product_info = saved_products_info[product_id]
            return {
                "success": True,
                "exists": True,
                "product_id": product_id,
                "saved_at": product_info['saved_at'].isoformat() if product_info['saved_at'] else None,
                "product_title": product_info['product_title'],
                "custom_title": product_info['custom_title'],
                "has_video": product_info['has_video'],
                "message": "Product found in saved products"
            }
        else:
            return {
                "success": True,
                "exists": False,
                "product_id": product_id,
                "saved_at": None,
                "message": "Product not found in saved products"
            }
        
    except Exception as e:
        # Log the error (in a real app, use proper logging)
        print(f"Error checking product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while checking product: {str(e)}"
        )
