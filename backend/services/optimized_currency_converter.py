from typing import Optional, Dict, Any, List
import mysql.connector
from config.settings import settings
import logging
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

class OptimizedCurrencyConverter:
    """Optimized currency conversion service with caching and batch operations"""
    
    def __init__(self):
        self.db_config = settings.get_database_config()
        self._rate_cache = {}
        self._cache_timestamp = 0
        self._cache_duration = 300  # 5 minutes cache
        self._connection_pool = []
        self._max_pool_size = 5
    
    def _get_db_connection(self):
        """Get MySQL database connection with connection pooling"""
        try:
            if self._connection_pool:
                return self._connection_pool.pop()
            else:
                return mysql.connector.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Error getting database connection: {e}")
            return mysql.connector.connect(**self.db_config)
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        try:
            if len(self._connection_pool) < self._max_pool_size:
                self._connection_pool.append(conn)
            else:
                conn.close()
        except:
            pass
    
    def _load_all_rates(self):
        """Load all exchange rates into cache"""
        current_time = time.time()
        if current_time - self._cache_timestamp < self._cache_duration and self._rate_cache:
            return
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT from_currency, to_currency, rate FROM currency_rate"
            )
            rows = cursor.fetchall()
            
            self._rate_cache = {}
            for from_curr, to_curr, rate in rows:
                key = f"{from_curr}_{to_curr}"
                self._rate_cache[key] = float(rate)
            
            self._cache_timestamp = current_time
            logger.info(f"Loaded {len(self._rate_cache)} exchange rates into cache")
            
            cursor.close()
            self._return_connection(conn)
            
        except Exception as e:
            logger.error(f"Error loading exchange rates: {e}")
            self._rate_cache = {}
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get exchange rate from cache"""
        self._load_all_rates()
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency == to_currency:
            return 1.0
        
        key = f"{from_currency}_{to_currency}"
        return self._rate_cache.get(key)
    
    def convert_price(self, price: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert price using cached rates"""
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            if from_currency == to_currency:
                return price
            
            if to_currency not in ['USD', 'EUR', 'ILS']:
                logger.warning(f"Target currency {to_currency} not supported")
                return None
            
            # Try direct conversion first
            direct_rate = self.get_exchange_rate(from_currency, to_currency)
            if direct_rate is not None:
                return round(price * direct_rate, 2)
            
            # Convert via USD
            usd_rate = self.get_exchange_rate(from_currency, 'USD')
            if usd_rate is not None:
                usd_price = price * usd_rate
                target_rate = self.get_exchange_rate('USD', to_currency)
                if target_rate is not None:
                    return round(usd_price * target_rate, 2)
            
            logger.warning(f"No conversion path found from {from_currency} to {to_currency}")
            return None
            
        except Exception as e:
            logger.error(f"Error converting price: {e}")
            return None
    
    def batch_convert_prices(self, conversions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert multiple prices in batch for better performance"""
        self._load_all_rates()
        
        results = []
        for conversion in conversions:
            try:
                price = conversion['price']
                from_currency = conversion['from_currency'].upper()
                to_currency = conversion['to_currency'].upper()
                
                converted_price = self.convert_price(price, from_currency, to_currency)
                
                results.append({
                    'original': conversion,
                    'converted_price': converted_price,
                    'success': converted_price is not None
                })
                
            except Exception as e:
                logger.error(f"Error in batch conversion: {e}")
                results.append({
                    'original': conversion,
                    'converted_price': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        self._load_all_rates()
        
        return {
            'cached_rates_count': len(self._rate_cache),
            'cache_age_seconds': time.time() - self._cache_timestamp,
            'supported_currencies': ['USD', 'EUR', 'ILS'],
            'available_rates': list(self._rate_cache.keys())
        }

# Create global optimized currency converter instance
optimized_currency_converter = OptimizedCurrencyConverter()
