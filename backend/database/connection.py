# backend/database/connection.py
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager
from config.settings import settings
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager with SQLite"""
    
    def __init__(self):
        self.db_path = "alibee_local.db"
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database"""
        try:
            # Create database file if it doesn't exist
            if not os.path.exists(self.db_path):
                with sqlite3.connect(self.db_path) as conn:
                    # Create saved_products table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS saved_products (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            product_id TEXT UNIQUE NOT NULL,
                            product_title TEXT,
                            promotion_link TEXT,
                            product_category TEXT,
                            custom_title TEXT,
                            has_video BOOLEAN DEFAULT 0,
                            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create currency_rate table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS currency_rate (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            from_currency TEXT NOT NULL,
                            to_currency TEXT NOT NULL,
                            rate REAL NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(from_currency, to_currency)
                        )
                    """)
                    conn.commit()
                logger.info("SQLite database initialized successfully")
            else:
                logger.info("SQLite database already exists")
                
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get SQLite database connection with context manager"""
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise e
        finally:
            if connection:
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary: bool = False):
        """Get database cursor with context manager"""
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor, connection
            finally:
                cursor.close()

class DatabaseOperations:
    """Database operations for products and saved products"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def save_product(self, product_data: Dict[str, Any]) -> bool:
        """Save a product to the database - Optimized version with only essential fields"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                # Check if product already exists
                cursor.execute("SELECT product_id FROM saved_products WHERE product_id = ?", (product_data['product_id'],))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing product
                    update_query = """
                        UPDATE saved_products SET
                            product_title = ?,
                            promotion_link = ?,
                            product_category = ?,
                            custom_title = ?,
                            has_video = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE product_id = ?
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
                        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
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
            print(f"Error saving product: {e}")
            return False
    
    def unsave_product(self, product_id: str) -> bool:
        """Remove a product from saved products"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                cursor.execute("DELETE FROM saved_products WHERE product_id = ?", (product_id,))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error unsaving product: {e}")
            return False
    
    def update_product_title(self, product_id: str, new_title: str) -> bool:
        """Update product custom title"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                cursor.execute(
                    "UPDATE saved_products SET custom_title = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?",
                    (new_title, product_id)
                )
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating product title: {e}")
            return False
    
    def get_saved_products(self, page: int = 1, page_size: int = 20, search_query: str = None, sort: str = "saved_at_desc") -> Tuple[List[Tuple], int]:
        """Get saved products with pagination"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                offset = (page - 1) * page_size
                where_conditions = ["1=1"]
                params = []
                
                if search_query:
                    where_conditions.append("(product_title LIKE ? OR custom_title LIKE ?)")
                    params.extend([f"%{search_query}%", f"%{search_query}%"])
                
                order_clause = {
                    "saved_at_desc": "saved_at DESC",
                    "saved_at_asc": "saved_at ASC",
                    "title_asc": "product_title ASC",
                    "title_desc": "product_title DESC",
                }.get(sort, "saved_at DESC")
                
                # Get total count
                count_query = f"SELECT COUNT(*) FROM saved_products WHERE {' AND '.join(where_conditions)}"
                cursor.execute(count_query, params)
                total = cursor.fetchone()[0]
                
                # Get products
                query = f"""
                    SELECT 
                        product_id, product_title, promotion_link, product_category, custom_title, has_video, saved_at
                    FROM saved_products 
                    WHERE {' AND '.join(where_conditions)}
                    ORDER BY {order_clause}
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, params + [page_size, offset])
                rows = cursor.fetchall()
                
                return rows, total
        except Exception as e:
            print(f"Error getting saved products: {e}")
            return [], 0
    
    def get_saved_products_info(self, product_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get saved products info for given product IDs"""
        try:
            if not product_ids:
                return {}
            
            with self.db.get_cursor() as (cursor, connection):
                placeholders = ','.join(['%s'] * len(product_ids))
                query = f"""
                    SELECT product_id, saved_at, product_title, custom_title, has_video 
                    FROM saved_products 
                    WHERE product_id IN ({placeholders})
                """
                cursor.execute(query, product_ids)
                rows = cursor.fetchall()
                
                return {row[0]: {'saved_at': row[1], 'product_title': row[2], 'custom_title': row[3], 'has_video': row[4]} for row in rows}
        except Exception as e:
            print(f"Error getting saved products info: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                stats = {}
                
                # Get saved products count
                cursor.execute("SELECT COUNT(*) FROM saved_products")
                stats['savedProducts'] = cursor.fetchone()[0]
                
                # Get total products count (if aliexpress_products table exists)
                try:
                    cursor.execute("SELECT COUNT(*) FROM aliexpress_products")
                    stats['totalProducts'] = cursor.fetchone()[0]
                except:
                    stats['totalProducts'] = 0
                
                return stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'savedProducts': 0, 'totalProducts': 0}
    
    def ensure_unique_constraint(self) -> Dict[str, str]:
        """Ensure unique constraint on product_id"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                try:
                    cursor.execute("ALTER TABLE saved_products ADD UNIQUE KEY unique_product_id (product_id)")
                    connection.commit()
                    return {"status": "success", "message": "Unique constraint added to product_id"}
                except Exception as e:  # mysql.connector.Error as e:  # Commented out to prevent database connection issues
                    if e.errno == 1061:  # Duplicate key name
                        return {"status": "success", "message": "Unique constraint already exists on product_id"}
                    elif e.errno == 1062:  # Duplicate entry
                        return {"status": "warning", "message": "Duplicate entries found, please clean up first"}
                    else:
                        raise
        except Exception as e:
            return {"status": "error", "message": f"Failed to add unique constraint: {str(e)}"}
    
    # Currency Rate Operations
    def get_currency_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get exchange rate between two currencies"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                cursor.execute(
                    "SELECT rate FROM currency_rate WHERE from_currency = ? AND to_currency = ?",
                    (from_currency, to_currency)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting currency rate: {e}")
            return None
    
    def set_currency_rate(self, from_currency: str, to_currency: str, rate: float) -> bool:
        """Set or update exchange rate between two currencies"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                # Check if rate already exists
                cursor.execute(
                    "SELECT id FROM currency_rate WHERE from_currency = ? AND to_currency = ?",
                    (from_currency, to_currency)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing rate
                    cursor.execute(
                        "UPDATE currency_rate SET rate = ?, updated_at = CURRENT_TIMESTAMP WHERE from_currency = ? AND to_currency = ?",
                        (rate, from_currency, to_currency)
                    )
                else:
                    # Insert new rate
                    cursor.execute(
                        "INSERT INTO currency_rate (from_currency, to_currency, rate, created_at, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                        (from_currency, to_currency, rate)
                    )
                
                connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting currency rate: {e}")
            return False
    
    def get_all_currency_rates(self) -> List[Dict[str, Any]]:
        """Get all currency exchange rates"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                cursor.execute(
                    "SELECT from_currency, to_currency, rate, updated_at FROM currency_rate ORDER BY from_currency, to_currency"
                )
                rows = cursor.fetchall()
                return [
                    {
                        'from_currency': row[0],
                        'to_currency': row[1],
                        'rate': row[2],
                        'updated_at': row[3]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting all currency rates: {e}")
            return []
    
    def delete_currency_rate(self, from_currency: str, to_currency: str) -> bool:
        """Delete a currency exchange rate"""
        try:
            with self.db.get_cursor() as (cursor, connection):
                cursor.execute(
                    "DELETE FROM currency_rate WHERE from_currency = ? AND to_currency = ?",
                    (from_currency, to_currency)
                )
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting currency rate: {e}")
            return False

# Create global database operations instance
db_ops = DatabaseOperations()

# Simple function for API endpoints to get database connection
def get_db_connection():
    """Get SQLite database connection for API endpoints"""
    return sqlite3.connect("alibee_local.db")