from fastapi import APIRouter, HTTPException
from database.connection import db_ops
import mysql.connector
from config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/translations")
async def get_translations():
    """Get all translations from dictionary table"""
    try:
        # Get database config
        db_config = settings.get_database_config()
        
        # Add connection timeout to prevent hanging
        db_config['connection_timeout'] = 10
        db_config['autocommit'] = True
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get all translations
        cursor.execute("SELECT en, he, ar FROM dictionary ORDER BY id")
        rows = cursor.fetchall()
        
        # Convert to dictionary format
        translations = {
            'en': {},
            'he': {},
            'ar': {}
        }
        
        # Map translations to keys (we'll use the order from our previous data)
        keys = [
            'subtitle', 'searchPlaceholder', 'productsAvailable', 'forYou',
            'clothing', 'heels', 'car', 'mobile', 'buyNow', 'save', 'share',
            'loading', 'loadingMore', 'noImage', 'reviews', 'discount',
            'discountLabel', 'commissionLabel', 'ratingLabel', 
            'firstCategoryLabel', 'secondCategoryLabel', 'searching',
            'advancedSearch', 'searchByProduct', 'enterProductName', 'quickCategories',
            'all', 'electronic', 'luggage', 'sport', 'furniture', 'homeGarden',
            'jewelry', 'baby', 'videoFilter', 'onlyWithVideo', 'clearAll',
            'cancel', 'search', 'price', 'productId', 'originalPrice',
            'salesPrice', 'productLink', 'likeProduct', 'removeFromLiked',
            'saveChanges', 'cancelEditing', 'saving', 'clickToEdit', 'video',
            'image', 'previousMedia', 'nextMedia', 'goToVideo', 'goToImage',
            'backToTop'
        ]
        
        for i, row in enumerate(rows):
            if i < len(keys):
                key = keys[i]
                translations['en'][key] = row[0] or ''
                translations['he'][key] = row[1] or ''
                translations['ar'][key] = row[2] or ''
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "translations": translations
        }
        
    except Exception as e:
        logger.error(f"Error getting translations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get translations: {str(e)}")

@router.get("/translations/{language}")
async def get_translations_by_language(language: str):
    """Get translations for a specific language"""
    try:
        if language not in ['en', 'he', 'ar']:
            raise HTTPException(status_code=400, detail="Invalid language code")
        
        # Get database config
        db_config = settings.get_database_config()
        
        # Add connection timeout to prevent hanging
        db_config['connection_timeout'] = 10
        db_config['autocommit'] = True
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get translations for specific language
        if language == 'en':
            cursor.execute("SELECT en FROM dictionary ORDER BY id")
        elif language == 'he':
            cursor.execute("SELECT he FROM dictionary ORDER BY id")
        elif language == 'ar':
            cursor.execute("SELECT ar FROM dictionary ORDER BY id")
        
        rows = cursor.fetchall()
        
        # Map translations to keys
        keys = [
            'subtitle', 'searchPlaceholder', 'productsAvailable', 'forYou',
            'clothing', 'heels', 'car', 'mobile', 'buyNow', 'save', 'share',
            'loading', 'loadingMore', 'noImage', 'reviews', 'discount',
            'discountLabel', 'commissionLabel', 'ratingLabel', 
            'firstCategoryLabel', 'secondCategoryLabel', 'searching',
            'advancedSearch', 'searchByProduct', 'enterProductName', 'quickCategories',
            'all', 'electronic', 'luggage', 'sport', 'furniture', 'homeGarden',
            'jewelry', 'baby', 'videoFilter', 'onlyWithVideo', 'clearAll',
            'cancel', 'search', 'price', 'productId', 'originalPrice',
            'salesPrice', 'productLink', 'likeProduct', 'removeFromLiked',
            'saveChanges', 'cancelEditing', 'saving', 'clickToEdit', 'video',
            'image', 'previousMedia', 'nextMedia', 'goToVideo', 'goToImage',
            'backToTop'
        ]
        
        translations = {}
        for i, row in enumerate(rows):
            if i < len(keys):
                key = keys[i]
                translations[key] = row[0] or ''
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "language": language,
            "translations": translations
        }
        
    except Exception as e:
        logger.error(f"Error getting translations for {language}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get translations: {str(e)}")