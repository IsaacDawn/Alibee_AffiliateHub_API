# backend/routes/database.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from database.migrations import migration
from database.connection import db_ops
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/database/info")
def get_database_info() -> Dict[str, Any]:
    """
    Get database information and status
    """
    try:
        db_info = migration.get_database_info()
        
        return {
            "success": True,
            "database_info": db_info,
            "message": "Database information retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to get database information: {str(e)}"
            }
        )

@router.post("/database/migrate")
def run_database_migrations() -> Dict[str, Any]:
    """
    Run database migrations
    """
    try:
        success = migration.run_migrations()
        
        if success:
            return {
                "success": True,
                "message": "Database migrations completed successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "message": "Database migrations failed"
                }
            )
            
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to run migrations: {str(e)}"
            }
        )

@router.post("/database/constraints")
def add_database_constraints() -> Dict[str, Any]:
    """
    Add database constraints and indexes
    """
    try:
        success = migration.add_unique_constraints()
        
        if success:
            return {
                "success": True,
                "message": "Database constraints added successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "message": "Failed to add database constraints"
                }
            )
            
    except Exception as e:
        logger.error(f"Error adding constraints: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to add constraints: {str(e)}"
            }
        )

@router.get("/info/{product_id}")
def get_product_info(product_id: str) -> Dict[str, Any]:
    """
    Get product information including custom title and save date
    """
    try:
        # Validate product_id format
        if not product_id or not product_id.strip():
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        # Get product info from database
        saved_products_info = db_ops.get_saved_products_info([product_id])
        
        if product_id in saved_products_info:
            product_info = saved_products_info[product_id]
            return {
                "success": True,
                "product_id": product_id,
                "saved_at": product_info['saved_at'].isoformat() if product_info['saved_at'] else None,
                "product_title": product_info['product_title'],
                "custom_title": product_info['custom_title'],
                "has_video": product_info['has_video'],
                "message": "Product information retrieved successfully"
            }
        else:
            return {
                "success": False,
                "product_id": product_id,
                "saved_at": None,
                "product_title": None,
                "custom_title": None,
                "has_video": False,
                "message": "Product not found in saved products"
            }
        
    except Exception as e:
        logger.error(f"Error getting product info for {product_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while getting product info: {str(e)}"
        )

@router.get("/database/stats")
def get_database_stats() -> Dict[str, Any]:
    """
    Get detailed database statistics
    """
    try:
        # Get basic stats from db_ops
        basic_stats = db_ops.get_stats()
        
        # Get database info
        db_info = migration.get_database_info()
        
        return {
            "success": True,
            "basic_stats": basic_stats,
            "database_info": db_info,
            "message": "Database statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to get database statistics: {str(e)}"
            }
        )
