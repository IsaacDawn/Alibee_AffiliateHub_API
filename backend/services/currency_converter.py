from typing import Optional, Dict, Any
import mysql.connector
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """Currency conversion service using database rates"""
    
    def __init__(self):
        self.db_config = settings.get_database_config()
    
    def _get_db_connection(self):
        """Get MySQL database connection"""
        return mysql.connector.connect(**self.db_config)
    
    def convert_price(self, price: float, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Convert price from one currency to another using database rates
        Uses USD as base currency with fallback strategy
        
        Strategy:
        1. Try direct conversion if available
        2. If not available, convert to USD first, then to target currency
        3. If USD conversion fails, try other major currencies as intermediates
        
        Args:
            price: The price to convert
            from_currency: Source currency code (e.g., 'CNY', 'INR', 'MYR')
            to_currency: Target currency code (USD, EUR, or ILS)
            
        Returns:
            Converted price or None if conversion fails
        """
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # If same currency, return original price
            if from_currency == to_currency:
                return price
            
            # Only support conversion to USD, EUR, or ILS
            if to_currency not in ['USD', 'EUR', 'ILS']:
                logger.warning(f"Target currency {to_currency} not supported. Only USD, EUR, ILS are supported.")
                return None
            
            # Strategy 1: Try direct conversion first
            direct_rate = self.get_exchange_rate(from_currency, to_currency)
            if direct_rate is not None:
                converted_price = price * direct_rate
                logger.info(f"Direct conversion: {price} {from_currency} = {converted_price} {to_currency}")
                return round(converted_price, 2)
            
            # Strategy 2: Convert via USD (base currency)
            usd_price = self._convert_to_usd(price, from_currency)
            if usd_price is not None:
                final_price = self._convert_from_usd(usd_price, to_currency)
                if final_price is not None:
                    logger.info(f"USD-based conversion: {price} {from_currency} → {usd_price} USD → {final_price} {to_currency}")
                    return final_price
            
            # Strategy 3: Try other major currencies as intermediates
            major_currencies = ['EUR', 'GBP', 'JPY', 'CNY']
            for intermediate in major_currencies:
                if intermediate == from_currency or intermediate == to_currency:
                    continue
                
                # Convert to intermediate currency
                intermediate_price = self._convert_to_usd(price, from_currency)
                if intermediate_price is not None:
                    # Convert from intermediate to target
                    final_price = self._convert_from_usd(intermediate_price, to_currency)
                    if final_price is not None:
                        logger.info(f"Intermediate conversion via {intermediate}: {price} {from_currency} → {final_price} {to_currency}")
                        return final_price
            
            logger.warning(f"No conversion path found from {from_currency} to {to_currency}")
            return None
            
        except Exception as e:
            logger.error(f"Error converting price from {from_currency} to {to_currency}: {e}")
            return None
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get exchange rate between two currencies
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate or None if not found
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT rate FROM currency_rate WHERE from_currency = %s AND to_currency = %s",
                (from_currency.upper(), to_currency.upper())
            )
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return float(result[0]) if result else None
            
        except Exception as e:
            logger.error(f"Error getting exchange rate from {from_currency} to {to_currency}: {e}")
            return None
    
    def _convert_to_usd(self, price: float, from_currency: str) -> Optional[float]:
        """
        Convert price to USD
        
        Args:
            price: Price to convert
            from_currency: Source currency code
            
        Returns:
            Price in USD or None if conversion fails
        """
        if from_currency == 'USD':
            return price
        
        rate = self.get_exchange_rate(from_currency, 'USD')
        if rate is not None:
            return round(price * rate, 2)
        
        return None
    
    def _convert_from_usd(self, usd_price: float, to_currency: str) -> Optional[float]:
        """
        Convert price from USD to target currency
        
        Args:
            usd_price: Price in USD
            to_currency: Target currency code
            
        Returns:
            Converted price or None if conversion fails
        """
        if to_currency == 'USD':
            return usd_price
        
        rate = self.get_exchange_rate('USD', to_currency)
        if rate is not None:
            return round(usd_price * rate, 2)
        
        return None
    
    def set_exchange_rate(self, from_currency: str, to_currency: str, rate: float) -> bool:
        """
        Set or update exchange rate between two currencies
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            rate: Exchange rate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Check if rate already exists
            cursor.execute(
                "SELECT id FROM currency_rate WHERE from_currency = %s AND to_currency = %s",
                (from_currency.upper(), to_currency.upper())
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing rate
                cursor.execute(
                    "UPDATE currency_rate SET rate = %s, updated_at = NOW() WHERE from_currency = %s AND to_currency = %s",
                    (rate, from_currency.upper(), to_currency.upper())
                )
            else:
                # Insert new rate
                cursor.execute(
                    "INSERT INTO currency_rate (from_currency, to_currency, rate, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
                    (from_currency.upper(), to_currency.upper(), rate)
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting exchange rate from {from_currency} to {to_currency}: {e}")
            return False
    
    def get_all_rates(self) -> Dict[str, Any]:
        """
        Get all available exchange rates
        
        Returns:
            Dictionary with all exchange rates
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT from_currency, to_currency, rate, updated_at FROM currency_rate ORDER BY from_currency, to_currency"
            )
            rows = cursor.fetchall()
            
            rates = [
                {
                    'from_currency': row[0],
                    'to_currency': row[1],
                    'rate': row[2],
                    'updated_at': row[3]
                }
                for row in rows
            ]
            
            cursor.close()
            conn.close()
            
            return {
                'rates': rates,
                'count': len(rates)
            }
            
        except Exception as e:
            logger.error(f"Error getting all exchange rates: {e}")
            return {'rates': [], 'count': 0}
    
    def initialize_default_rates(self) -> bool:
        """
        Initialize default exchange rates if none exist
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if any rates exist
            existing_rates = self.get_all_rates()
            if existing_rates['count'] > 0:
                logger.info("Exchange rates already exist, skipping initialization")
                return True
            
            # Optimized rates - only necessary conversions using USD as base
            default_rates = [
                # USD to main currencies (for display)
                ('USD', 'EUR', 0.85),   # 1 USD = 0.85 EUR
                ('USD', 'ILS', 3.65),   # 1 USD = 3.65 ILS
                
                # Source currencies to USD (for conversion from any currency to USD)
                ('CNY', 'USD', 0.14),   # 1 CNY = 0.14 USD (Chinese Yuan)
                ('INR', 'USD', 0.012),  # 1 INR = 0.012 USD (Indian Rupee)
                ('MYR', 'USD', 0.21),   # 1 MYR = 0.21 USD (Malaysian Ringgit)
                ('THB', 'USD', 0.027),  # 1 THB = 0.027 USD (Thai Baht)
                ('VND', 'USD', 0.000041), # 1 VND = 0.000041 USD (Vietnamese Dong)
                ('IDR', 'USD', 0.000065), # 1 IDR = 0.000065 USD (Indonesian Rupiah)
                ('PHP', 'USD', 0.018),  # 1 PHP = 0.018 USD (Philippine Peso)
                ('SGD', 'USD', 0.74),   # 1 SGD = 0.74 USD (Singapore Dollar)
            ]
            
            success_count = 0
            for from_curr, to_curr, rate in default_rates:
                if self.set_exchange_rate(from_curr, to_curr, rate):
                    success_count += 1
            
            logger.info(f"Initialized {success_count}/{len(default_rates)} default exchange rates")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error initializing default exchange rates: {e}")
            return False

# Create global currency converter instance
currency_converter = CurrencyConverter()
