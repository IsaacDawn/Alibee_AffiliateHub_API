# backend/routes/save.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from database.connection import db_ops

router = APIRouter()

@router.post("/save")
def save_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save a product to the database
    """
    try:
        # Validate required fields
        if not product_data.get('product_id'):
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        # Save product to database
        success = db_ops.save_product(product_data)
        
        if success:
            return {
                "success": True,
                "message": "Product saved successfully",
                "product_id": product_data['product_id']
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save product")
            
    except Exception as e:
        print(f"Error saving product: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while saving product: {str(e)}"
        )

@router.delete("/save/{product_id}")
def unsave_product(product_id: str) -> Dict[str, Any]:
    """
    Remove a product from saved products
    """
    try:
        if not product_id or not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        # Remove product from database
        success = db_ops.unsave_product(product_id)
        
        if success:
            return {
                "success": True,
                "message": "Product removed successfully",
                "product_id": product_id
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found in saved products")
            
    except Exception as e:
        print(f"Error unsaving product: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while removing product: {str(e)}"
        )

@router.get("/saved")
def get_saved_products(
    page: int = 1,
    page_size: int = 20,
    search: str = None,
    sort: str = "saved_at_desc"
) -> Dict[str, Any]:
    """
    Get saved products with pagination
    """
    try:
        # Get saved products from database
        products, total = db_ops.get_saved_products(
            page=page,
            page_size=page_size,
            search_query=search,
            sort=sort
        )
        
        # Convert to list of dictionaries
        items = []
        for product in products:
            items.append({
                "product_id": product[0],
                "product_title": product[1],
                "promotion_link": product[2],
                "product_category": product[3],
                "custom_title": product[4],
                "has_video": product[5],
                "saved_at": product[6].isoformat() if product[6] else None
            })
        
        return {
            "success": True,
            "items": items,
            "page": page,
            "pageSize": page_size,
            "total": total,
            "hasMore": (page * page_size) < total
        }
        
    except Exception as e:
        print(f"Error getting saved products: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while getting saved products: {str(e)}"
        )

@router.put("/save/{product_id}/title")
def update_product_title(product_id: str, title_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Update product custom title
    """
    try:
        if not product_id or not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        new_title = title_data.get('title', '').strip()
        if not new_title:
            raise HTTPException(status_code=400, detail="Title is required")
        
        # Update product title in database
        success = db_ops.update_product_title(product_id, new_title)
        
        if success:
            return {
                "success": True,
                "message": "Product title updated successfully",
                "product_id": product_id,
                "new_title": new_title
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found in saved products")
            
    except Exception as e:
        print(f"Error updating product title: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while updating product title: {str(e)}"
        )
