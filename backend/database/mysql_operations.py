# backend/database/mysql_operations.py
import mysql.connector
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MySQLOperations:
    """MySQL database operations for products and saved products"""
    
    def __init__(self):
        self.config = settings.get_database_config()
    
    @contextmanager
    def get_connection(self):
        """Get MySQL database connection with context manager"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"MySQL connection error: {e}")
            raise e
        finally:
            if connection:
                connection.close()
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor with context manager"""
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor, connection
            finally:
                cursor.close()
    
    def is_product_liked(self, product_id: str) -> bool:
        """Check if a product is already liked/saved"""
        try:
            with self.get_cursor() as (cursor, connection):
                cursor.execute("SELECT product_id FROM saved_products WHERE product_id = %s", (product_id,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Error checking if product is liked: {e}")
            return False
    
    def like_product(self, product_data: Dict[str, Any]) -> bool:
        """Like/save a product to the database"""
        try:
            with self.get_cursor() as (cursor, connection):
                # Check if product already exists
                cursor.execute("SELECT product_id FROM saved_products WHERE product_id = %s", (product_data['product_id'],))
                existing = cursor.fetchone()
                
                if existing:
                    # Product already exists, just update the timestamp
                    update_query = """
                        UPDATE saved_products SET
                            product_title = %s,
                            promotion_link = %s,
                            product_category = %s,
                            custom_title = %s,
                            has_video = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE product_id = %s
                    """
                    cursor.execute(update_query, (
                        product_data.get('product_title'),
                        product_data.get('promotion_link'),
                        product_data.get('product_category'),
                        product_data.get('custom_title'),
                        product_data.get('has_video', False),
                        product_data['product_id']
                    ))
                else:
                    # Insert new product
                    insert_query = """
                        INSERT INTO saved_products (
                            product_id, product_title, promotion_link, product_category, custom_title, has_video,
                            saved_at, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                    cursor.execute(insert_query, (
                        product_data['product_id'],
                        product_data.get('product_title'),
                        product_data.get('promotion_link'),
                        product_data.get('product_category'),
                        product_data.get('custom_title'),
                        product_data.get('has_video', False)
                    ))
                
                connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error liking product: {e}")
            return False
    
    def unlike_product(self, product_id: str) -> bool:
        """Unlike/remove a product from saved products"""
        try:
            with self.get_cursor() as (cursor, connection):
                cursor.execute("DELETE FROM saved_products WHERE product_id = %s", (product_id,))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error unliking product: {e}")
            return False
    
    def get_liked_products(self, product_ids: List[str]) -> Dict[str, bool]:
        """Get liked status for multiple products"""
        try:
            if not product_ids:
                return {}
            
            with self.get_cursor() as (cursor, connection):
                placeholders = ','.join(['%s'] * len(product_ids))
                query = f"SELECT product_id FROM saved_products WHERE product_id IN ({placeholders})"
                cursor.execute(query, product_ids)
                rows = cursor.fetchall()
                
                liked_products = {row[0]: True for row in rows}
                return {pid: liked_products.get(pid, False) for pid in product_ids}
        except Exception as e:
            logger.error(f"Error getting liked products: {e}")
            return {}
    
    def get_saved_products_count(self) -> int:
        """Get total count of saved products"""
        try:
            with self.get_cursor() as (cursor, connection):
                cursor.execute("SELECT COUNT(*) FROM saved_products")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting saved products count: {e}")
            return 0

# Create global MySQL operations instance
mysql_ops = MySQLOperations()
