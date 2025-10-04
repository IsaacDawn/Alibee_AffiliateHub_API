from typing import Optional, Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

class CurrencyDetector:
    """Service for detecting currency from product data"""
    
    def __init__(self):
        # Comprehensive currency patterns for AliExpress
        self.currency_patterns = {
            # Major currencies (ordered by priority)
            'USD': [
                r'(?<!S)(?<!HK)(?<!CA)(?<!AU)(?<!NZ)(?<!NT)\$\s*(\d+(?:\.\d+)?)',  # $10.99 (but not S$, HK$, CA$, AU$, NZ$, NT$)
                r'(\d+(?:\.\d+)?)\s*USD',  # 10.99 USD
                r'US\s*Dollar',  # US Dollar
                r'Dollar',  # Dollar
            ],
            'EUR': [
                r'€\s*(\d+(?:\.\d+)?)',  # €10.99
                r'(\d+(?:\.\d+)?)\s*EUR',  # 10.99 EUR
                r'Euro',  # Euro
            ],
            'GBP': [
                r'£\s*(\d+(?:\.\d+)?)',  # £10.99
                r'(\d+(?:\.\d+)?)\s*GBP',  # 10.99 GBP
                r'Pound',  # Pound
                r'British\s*Pound',  # British Pound
            ],
            'JPY': [
                r'¥\s*(\d+(?:\.\d+)?)',  # ¥10.99
                r'(\d+(?:\.\d+)?)\s*JPY',  # 10.99 JPY
                r'Yen',  # Yen
                r'Japanese\s*Yen',  # Japanese Yen
            ],
            'CNY': [
                r'¥\s*(\d+(?:\.\d+)?)',  # ¥10.99 (Chinese Yuan)
                r'(\d+(?:\.\d+)?)\s*CNY',  # 10.99 CNY
                r'Yuan',  # Yuan
                r'RMB',  # RMB
                r'Chinese\s*Yuan',  # Chinese Yuan
            ],
            'KRW': [
                r'₩\s*(\d+(?:\.\d+)?)',  # ₩10.99
                r'(\d+(?:\.\d+)?)\s*KRW',  # 10.99 KRW
                r'Won',  # Won
                r'Korean\s*Won',  # Korean Won
            ],
            'INR': [
                r'₹\s*(\d+(?:\.\d+)?)',  # ₹10.99
                r'(\d+(?:\.\d+)?)\s*INR',  # 10.99 INR
                r'Rupee',  # Rupee
                r'Indian\s*Rupee',  # Indian Rupee
            ],
            'AUD': [
                r'A\$\s*(\d+(?:\.\d+)?)',  # A$10.99
                r'(\d+(?:\.\d+)?)\s*AUD',  # 10.99 AUD
                r'Australian\s*Dollar',  # Australian Dollar
            ],
            'CAD': [
                r'C\$\s*(\d+(?:\.\d+)?)',  # C$10.99
                r'(\d+(?:\.\d+)?)\s*CAD',  # 10.99 CAD
                r'Canadian\s*Dollar',  # Canadian Dollar
            ],
            'SGD': [
                r'S\$\s*(\d+(?:\.\d+)?)',  # S$10.99
                r'(\d+(?:\.\d+)?)\s*SGD',  # 10.99 SGD
                r'Singapore\s*Dollar',  # Singapore Dollar
            ],
            'HKD': [
                r'HK\$\s*(\d+(?:\.\d+)?)',  # HK$10.99
                r'(\d+(?:\.\d+)?)\s*HKD',  # 10.99 HKD
                r'Hong\s*Kong\s*Dollar',  # Hong Kong Dollar
            ],
            'NZD': [
                r'NZ\$\s*(\d+(?:\.\d+)?)',  # NZ$10.99
                r'(\d+(?:\.\d+)?)\s*NZD',  # 10.99 NZD
                r'New\s*Zealand\s*Dollar',  # New Zealand Dollar
            ],
            'CHF': [
                r'CHF\s*(\d+(?:\.\d+)?)',  # CHF10.99
                r'(\d+(?:\.\d+)?)\s*CHF',  # 10.99 CHF
                r'Swiss\s*Franc',  # Swiss Franc
            ],
            'ILS': [
                r'₪\s*(\d+(?:\.\d+)?)',  # ₪10.99
                r'(\d+(?:\.\d+)?)\s*ILS',  # 10.99 ILS
                r'Shekel',  # Shekel
                r'Israeli\s*Shekel',  # Israeli Shekel
            ],
            'MYR': [
                r'RM\s*(\d+(?:\.\d+)?)',  # RM10.99
                r'(\d+(?:\.\d+)?)\s*MYR',  # 10.99 MYR
                r'Ringgit',  # Ringgit
                r'Malaysian\s*Ringgit',  # Malaysian Ringgit
            ],
            'THB': [
                r'฿\s*(\d+(?:\.\d+)?)',  # ฿10.99
                r'(\d+(?:\.\d+)?)\s*THB',  # 10.99 THB
                r'Baht',  # Baht
                r'Thai\s*Baht',  # Thai Baht
            ],
            'VND': [
                r'₫\s*(\d+(?:\.\d+)?)',  # ₫10.99
                r'(\d+(?:\.\d+)?)\s*VND',  # 10.99 VND
                r'Dong',  # Dong
                r'Vietnamese\s*Dong',  # Vietnamese Dong
            ],
            'IDR': [
                r'Rp\s*(\d+(?:\.\d+)?)',  # Rp10.99
                r'(\d+(?:\.\d+)?)\s*IDR',  # 10.99 IDR
                r'Rupiah',  # Rupiah
                r'Indonesian\s*Rupiah',  # Indonesian Rupiah
            ],
            'PHP': [
                r'₱\s*(\d+(?:\.\d+)?)',  # ₱10.99
                r'(\d+(?:\.\d+)?)\s*PHP',  # 10.99 PHP
                r'Peso',  # Peso
                r'Philippine\s*Peso',  # Philippine Peso
            ],
            'TWD': [
                r'NT\$\s*(\d+(?:\.\d+)?)',  # NT$10.99
                r'(\d+(?:\.\d+)?)\s*TWD',  # 10.99 TWD
                r'Taiwan\s*Dollar',  # Taiwan Dollar
            ],
            'AED': [
                r'(\d+(?:\.\d+)?)\s*AED',  # 10.99 AED
                r'Dirham',  # Dirham
                r'UAE\s*Dirham',  # UAE Dirham
            ],
            'SAR': [
                r'(\d+(?:\.\d+)?)\s*SAR',  # 10.99 SAR
                r'Saudi\s*Riyal',  # Saudi Riyal
            ],
            'KWD': [
                r'(\d+(?:\.\d+)?)\s*KWD',  # 10.99 KWD
                r'Kuwaiti\s*Dinar',  # Kuwaiti Dinar
            ],
            'BHD': [
                r'(\d+(?:\.\d+)?)\s*BHD',  # 10.99 BHD
                r'Bahraini\s*Dinar',  # Bahraini Dinar
            ],
            'OMR': [
                r'(\d+(?:\.\d+)?)\s*OMR',  # 10.99 OMR
                r'Omani\s*Rial',  # Omani Rial
            ],
            'JOD': [
                r'(\d+(?:\.\d+)?)\s*JOD',  # 10.99 JOD
                r'Jordanian\s*Dinar',  # Jordanian Dinar
            ],
            'TRY': [
                r'(\d+(?:\.\d+)?)\s*TRY',  # 10.99 TRY
                r'Turkish\s*Lira',  # Turkish Lira
            ],
            'RUB': [
                r'(\d+(?:\.\d+)?)\s*RUB',  # 10.99 RUB
                r'Russian\s*Ruble',  # Russian Ruble
            ],
            'UAH': [
                r'(\d+(?:\.\d+)?)\s*UAH',  # 10.99 UAH
                r'Ukrainian\s*Hryvnia',  # Ukrainian Hryvnia
            ],
            'PLN': [
                r'(\d+(?:\.\d+)?)\s*PLN',  # 10.99 PLN
                r'Polish\s*Zloty',  # Polish Zloty
            ],
            'CZK': [
                r'(\d+(?:\.\d+)?)\s*CZK',  # 10.99 CZK
                r'Czech\s*Koruna',  # Czech Koruna
            ],
            'HUF': [
                r'(\d+(?:\.\d+)?)\s*HUF',  # 10.99 HUF
                r'Hungarian\s*Forint',  # Hungarian Forint
            ],
            'SEK': [
                r'(\d+(?:\.\d+)?)\s*SEK',  # 10.99 SEK
                r'Swedish\s*Krona',  # Swedish Krona
            ],
            'NOK': [
                r'(\d+(?:\.\d+)?)\s*NOK',  # 10.99 NOK
                r'Norwegian\s*Krone',  # Norwegian Krone
            ],
            'DKK': [
                r'(\d+(?:\.\d+)?)\s*DKK',  # 10.99 DKK
                r'Danish\s*Krone',  # Danish Krone
            ],
            'MXN': [
                r'(\d+(?:\.\d+)?)\s*MXN',  # 10.99 MXN
                r'Mexican\s*Peso',  # Mexican Peso
            ],
            'BRL': [
                r'R\$\s*(\d+(?:\.\d+)?)',  # R$10.99
                r'(\d+(?:\.\d+)?)\s*BRL',  # 10.99 BRL
                r'Brazilian\s*Real',  # Brazilian Real
            ],
            'ARS': [
                r'(\d+(?:\.\d+)?)\s*ARS',  # 10.99 ARS
                r'Argentine\s*Peso',  # Argentine Peso
            ],
            'CLP': [
                r'(\d+(?:\.\d+)?)\s*CLP',  # 10.99 CLP
                r'Chilean\s*Peso',  # Chilean Peso
            ],
            'COP': [
                r'(\d+(?:\.\d+)?)\s*COP',  # 10.99 COP
                r'Colombian\s*Peso',  # Colombian Peso
            ],
            'PEN': [
                r'(\d+(?:\.\d+)?)\s*PEN',  # 10.99 PEN
                r'Peruvian\s*Sol',  # Peruvian Sol
            ],
            'ZAR': [
                r'R\s*(\d+(?:\.\d+)?)',  # R10.99
                r'(\d+(?:\.\d+)?)\s*ZAR',  # 10.99 ZAR
                r'South\s*African\s*Rand',  # South African Rand
            ],
            'EGP': [
                r'(\d+(?:\.\d+)?)\s*EGP',  # 10.99 EGP
                r'Egyptian\s*Pound',  # Egyptian Pound
            ],
            'NGN': [
                r'(\d+(?:\.\d+)?)\s*NGN',  # 10.99 NGN
                r'Nigerian\s*Naira',  # Nigerian Naira
            ],
            'KES': [
                r'(\d+(?:\.\d+)?)\s*KES',  # 10.99 KES
                r'Kenyan\s*Shilling',  # Kenyan Shilling
            ],
            'MAD': [
                r'(\d+(?:\.\d+)?)\s*MAD',  # 10.99 MAD
                r'Moroccan\s*Dirham',  # Moroccan Dirham
            ],
            'TND': [
                r'(\d+(?:\.\d+)?)\s*TND',  # 10.99 TND
                r'Tunisian\s*Dinar',  # Tunisian Dinar
            ],
        }
        
        # Comprehensive country-based currency mapping for AliExpress
        self.country_currency_map = {
            # Asia
            'china': 'CNY', 'chinese': 'CNY',
            'japan': 'JPY', 'japanese': 'JPY',
            'korea': 'KRW', 'korean': 'KRW', 'south korea': 'KRW',
            'india': 'INR', 'indian': 'INR',
            'thailand': 'THB', 'thai': 'THB',
            'vietnam': 'VND', 'vietnamese': 'VND',
            'indonesia': 'IDR', 'indonesian': 'IDR',
            'philippines': 'PHP', 'philippine': 'PHP',
            'malaysia': 'MYR', 'malaysian': 'MYR',
            'singapore': 'SGD', 'singaporean': 'SGD',
            'hong kong': 'HKD', 'taiwan': 'TWD',
            'pakistan': 'PKR', 'pakistani': 'PKR',
            'bangladesh': 'BDT', 'bangladeshi': 'BDT',
            'sri lanka': 'LKR', 'nepal': 'NPR', 'nepalese': 'NPR',
            'myanmar': 'MMK', 'cambodia': 'KHR', 'cambodian': 'KHR',
            'laos': 'LAK', 'laotian': 'LAK', 'brunei': 'BND', 'macau': 'MOP',
            'mongolia': 'MNT', 'mongolian': 'MNT',
            'kazakhstan': 'KZT', 'uzbekistan': 'UZS',
            'kyrgyzstan': 'KGS', 'tajikistan': 'TJS',
            'afghanistan': 'AFN', 'afghan': 'AFN',
            
            # Middle East
            'uae': 'AED', 'united arab emirates': 'AED',
            'saudi arabia': 'SAR', 'saudi': 'SAR',
            'kuwait': 'KWD', 'kuwaiti': 'KWD',
            'bahrain': 'BHD', 'bahraini': 'BHD',
            'oman': 'OMR', 'omani': 'OMR',
            'jordan': 'JOD', 'jordanian': 'JOD',
            'lebanon': 'LBP', 'lebanese': 'LBP',
            'israel': 'ILS', 'israeli': 'ILS',
            'turkey': 'TRY', 'turkish': 'TRY',
            'iran': 'IRR', 'iranian': 'IRR',
            'iraq': 'IQD', 'iraqi': 'IQD',
            'syria': 'SYP', 'syrian': 'SYP',
            'yemen': 'YER', 'yemeni': 'YER',
            
            # Europe
            'europe': 'EUR', 'european': 'EUR',
            'germany': 'EUR', 'german': 'EUR',
            'france': 'EUR', 'french': 'EUR',
            'italy': 'EUR', 'italian': 'EUR',
            'spain': 'EUR', 'spanish': 'EUR',
            'netherlands': 'EUR', 'dutch': 'EUR',
            'belgium': 'EUR', 'belgian': 'EUR',
            'austria': 'EUR', 'austrian': 'EUR',
            'portugal': 'EUR', 'portuguese': 'EUR',
            'finland': 'EUR', 'finnish': 'EUR',
            'ireland': 'EUR', 'irish': 'EUR',
            'greece': 'EUR', 'greek': 'EUR',
            'united kingdom': 'GBP', 'britain': 'GBP', 'british': 'GBP',
            'switzerland': 'CHF', 'swiss': 'CHF',
            'sweden': 'SEK', 'swedish': 'SEK',
            'norway': 'NOK', 'norwegian': 'NOK',
            'denmark': 'DKK', 'danish': 'DKK',
            'poland': 'PLN', 'polish': 'PLN',
            'czech republic': 'CZK', 'czech': 'CZK',
            'hungary': 'HUF', 'hungarian': 'HUF',
            'russia': 'RUB', 'russian': 'RUB',
            'ukraine': 'UAH', 'ukrainian': 'UAH',
            
            # Americas
            'usa': 'USD', 'united states': 'USD', 'america': 'USD', 'american': 'USD',
            'canada': 'CAD', 'canadian': 'CAD',
            'mexico': 'MXN', 'mexican': 'MXN',
            'brazil': 'BRL', 'brazilian': 'BRL',
            'argentina': 'ARS', 'argentine': 'ARS',
            'chile': 'CLP', 'chilean': 'CLP',
            'colombia': 'COP', 'colombian': 'COP',
            'peru': 'PEN', 'peruvian': 'PEN',
            
            # Africa
            'south africa': 'ZAR', 'south african': 'ZAR',
            'egypt': 'EGP', 'egyptian': 'EGP',
            'nigeria': 'NGN', 'nigerian': 'NGN',
            'kenya': 'KES', 'kenyan': 'KES',
            'morocco': 'MAD', 'moroccan': 'MAD',
            'tunisia': 'TND', 'tunisian': 'TND',
            
            # Oceania
            'australia': 'AUD', 'australian': 'AUD',
            'new zealand': 'NZD', 'new zealand': 'NZD',
        }
    
    def detect_currency_from_price(self, price_text: str) -> Optional[str]:
        """
        Detect currency from price text
        
        Args:
            price_text: Text containing price information
            
        Returns:
            Currency code or None if not detected
        """
        if not price_text:
            return None
        
        price_text = price_text.strip().upper()
        
        # Check each currency pattern
        for currency, patterns in self.currency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, price_text, re.IGNORECASE):
                    return currency
        
        return None
    
    def detect_currency_from_country(self, country_text: str) -> Optional[str]:
        """
        Detect currency from country information
        
        Args:
            country_text: Text containing country information
            
        Returns:
            Currency code or None if not detected
        """
        if not country_text:
            return None
        
        country_text = country_text.lower().strip()
        
        # Check country mapping
        for country, currency in self.country_currency_map.items():
            if country in country_text:
                return currency
        
        return None
    
    def detect_currency_from_product(self, product_data: Dict[str, Any]) -> Optional[str]:
        """
        Detect currency from product data
        
        Args:
            product_data: Product information dictionary
            
        Returns:
            Currency code or None if not detected
        """
        # Check price fields
        price_fields = [
            'sale_price', 'original_price', 'price', 'cost',
            'sale_price_currency', 'original_price_currency'
        ]
        
        for field in price_fields:
            if field in product_data and product_data[field]:
                currency = self.detect_currency_from_price(str(product_data[field]))
                if currency:
                    return currency
        
        # Check title and description
        text_fields = ['product_title', 'title', 'description', 'product_description']
        for field in text_fields:
            if field in product_data and product_data[field]:
                currency = self.detect_currency_from_price(str(product_data[field]))
                if currency:
                    return currency
        
        # Check shop information
        shop_fields = ['shop_title', 'shop_name', 'shop_country', 'country']
        for field in shop_fields:
            if field in product_data and product_data[field]:
                currency = self.detect_currency_from_country(str(product_data[field]))
                if currency:
                    return currency
        
        return None
    
    def extract_price_from_text(self, text: str) -> Optional[float]:
        """
        Extract numeric price from text
        
        Args:
            text: Text containing price
            
        Returns:
            Price as float or None if not found
        """
        if not text:
            return None
        
        # Pattern to match numbers with optional decimal places
        price_pattern = r'(\d+(?:\.\d{2})?)'
        matches = re.findall(price_pattern, text)
        
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                return None
        
        return None
    
    def get_currency_info(self, currency_code: str) -> Dict[str, str]:
        """
        Get currency information
        
        Args:
            currency_code: Currency code (e.g., 'USD')
            
        Returns:
            Dictionary with currency information
        """
        currency_info = {
            # Major currencies
            'USD': {'name': 'US Dollar', 'symbol': '$', 'flag': '🇺🇸'},
            'EUR': {'name': 'Euro', 'symbol': '€', 'flag': '🇪🇺'},
            'GBP': {'name': 'British Pound', 'symbol': '£', 'flag': '🇬🇧'},
            'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'flag': '🇯🇵'},
            'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'flag': '🇨🇳'},
            'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'flag': '🇰🇷'},
            'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'flag': '🇮🇳'},
            'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'flag': '🇦🇺'},
            'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'flag': '🇨🇦'},
            'SGD': {'name': 'Singapore Dollar', 'symbol': 'S$', 'flag': '🇸🇬'},
            'HKD': {'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'flag': '🇭🇰'},
            'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'flag': '🇳🇿'},
            'CHF': {'name': 'Swiss Franc', 'symbol': 'CHF', 'flag': '🇨🇭'},
            'ILS': {'name': 'Israeli Shekel', 'symbol': '₪', 'flag': '🇮🇱'},
            
            # Asian currencies
            'MYR': {'name': 'Malaysian Ringgit', 'symbol': 'RM', 'flag': '🇲🇾'},
            'THB': {'name': 'Thai Baht', 'symbol': '฿', 'flag': '🇹🇭'},
            'VND': {'name': 'Vietnamese Dong', 'symbol': '₫', 'flag': '🇻🇳'},
            'IDR': {'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'flag': '🇮🇩'},
            'PHP': {'name': 'Philippine Peso', 'symbol': '₱', 'flag': '🇵🇭'},
            'TWD': {'name': 'Taiwan Dollar', 'symbol': 'NT$', 'flag': '🇹🇼'},
            'PKR': {'name': 'Pakistani Rupee', 'symbol': 'PKR', 'flag': '🇵🇰'},
            'BDT': {'name': 'Bangladeshi Taka', 'symbol': 'BDT', 'flag': '🇧🇩'},
            'LKR': {'name': 'Sri Lankan Rupee', 'symbol': 'LKR', 'flag': '🇱🇰'},
            'NPR': {'name': 'Nepalese Rupee', 'symbol': 'NPR', 'flag': '🇳🇵'},
            'MMK': {'name': 'Myanmar Kyat', 'symbol': 'MMK', 'flag': '🇲🇲'},
            'KHR': {'name': 'Cambodian Riel', 'symbol': 'KHR', 'flag': '🇰🇭'},
            'LAK': {'name': 'Lao Kip', 'symbol': 'LAK', 'flag': '🇱🇦'},
            'BND': {'name': 'Brunei Dollar', 'symbol': 'BND', 'flag': '🇧🇳'},
            'MOP': {'name': 'Macanese Pataca', 'symbol': 'MOP', 'flag': '🇲🇴'},
            'MNT': {'name': 'Mongolian Tugrik', 'symbol': 'MNT', 'flag': '🇲🇳'},
            'KZT': {'name': 'Kazakhstani Tenge', 'symbol': 'KZT', 'flag': '🇰🇿'},
            'UZS': {'name': 'Uzbekistani Som', 'symbol': 'UZS', 'flag': '🇺🇿'},
            'KGS': {'name': 'Kyrgyzstani Som', 'symbol': 'KGS', 'flag': '🇰🇬'},
            'TJS': {'name': 'Tajikistani Somoni', 'symbol': 'TJS', 'flag': '🇹🇯'},
            'AFN': {'name': 'Afghan Afghani', 'symbol': 'AFN', 'flag': '🇦🇫'},
            
            # Middle East currencies
            'AED': {'name': 'UAE Dirham', 'symbol': 'AED', 'flag': '🇦🇪'},
            'SAR': {'name': 'Saudi Riyal', 'symbol': 'SAR', 'flag': '🇸🇦'},
            'KWD': {'name': 'Kuwaiti Dinar', 'symbol': 'KWD', 'flag': '🇰🇼'},
            'BHD': {'name': 'Bahraini Dinar', 'symbol': 'BHD', 'flag': '🇧🇭'},
            'OMR': {'name': 'Omani Rial', 'symbol': 'OMR', 'flag': '🇴🇲'},
            'JOD': {'name': 'Jordanian Dinar', 'symbol': 'JOD', 'flag': '🇯🇴'},
            'LBP': {'name': 'Lebanese Pound', 'symbol': 'LBP', 'flag': '🇱🇧'},
            'TRY': {'name': 'Turkish Lira', 'symbol': 'TRY', 'flag': '🇹🇷'},
            'IRR': {'name': 'Iranian Rial', 'symbol': 'IRR', 'flag': '🇮🇷'},
            'IQD': {'name': 'Iraqi Dinar', 'symbol': 'IQD', 'flag': '🇮🇶'},
            'SYP': {'name': 'Syrian Pound', 'symbol': 'SYP', 'flag': '🇸🇾'},
            'YER': {'name': 'Yemeni Rial', 'symbol': 'YER', 'flag': '🇾🇪'},
            
            # European currencies
            'SEK': {'name': 'Swedish Krona', 'symbol': 'SEK', 'flag': '🇸🇪'},
            'NOK': {'name': 'Norwegian Krone', 'symbol': 'NOK', 'flag': '🇳🇴'},
            'DKK': {'name': 'Danish Krone', 'symbol': 'DKK', 'flag': '🇩🇰'},
            'PLN': {'name': 'Polish Zloty', 'symbol': 'PLN', 'flag': '🇵🇱'},
            'CZK': {'name': 'Czech Koruna', 'symbol': 'CZK', 'flag': '🇨🇿'},
            'HUF': {'name': 'Hungarian Forint', 'symbol': 'HUF', 'flag': '🇭🇺'},
            'RUB': {'name': 'Russian Ruble', 'symbol': 'RUB', 'flag': '🇷🇺'},
            'UAH': {'name': 'Ukrainian Hryvnia', 'symbol': 'UAH', 'flag': '🇺🇦'},
            
            # American currencies
            'MXN': {'name': 'Mexican Peso', 'symbol': 'MXN', 'flag': '🇲🇽'},
            'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'flag': '🇧🇷'},
            'ARS': {'name': 'Argentine Peso', 'symbol': 'ARS', 'flag': '🇦🇷'},
            'CLP': {'name': 'Chilean Peso', 'symbol': 'CLP', 'flag': '🇨🇱'},
            'COP': {'name': 'Colombian Peso', 'symbol': 'COP', 'flag': '🇨🇴'},
            'PEN': {'name': 'Peruvian Sol', 'symbol': 'PEN', 'flag': '🇵🇪'},
            
            # African currencies
            'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'flag': '🇿🇦'},
            'EGP': {'name': 'Egyptian Pound', 'symbol': 'EGP', 'flag': '🇪🇬'},
            'NGN': {'name': 'Nigerian Naira', 'symbol': 'NGN', 'flag': '🇳🇬'},
            'KES': {'name': 'Kenyan Shilling', 'symbol': 'KES', 'flag': '🇰🇪'},
            'MAD': {'name': 'Moroccan Dirham', 'symbol': 'MAD', 'flag': '🇲🇦'},
            'TND': {'name': 'Tunisian Dinar', 'symbol': 'TND', 'flag': '🇹🇳'},
        }
        
        return currency_info.get(currency_code.upper(), {
            'name': currency_code,
            'symbol': currency_code,
            'flag': '🏳️'
        })

    def detect_currency_from_text(self, text: str) -> Optional[str]:
        """
        Detect currency from text (combines price and country detection)
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected currency code or None
        """
        if not text:
            return None
        
        # First try price detection
        detected_currency = self.detect_currency_from_price(text)
        if detected_currency:
            return detected_currency
        
        # Then try country detection
        detected_currency = self.detect_currency_from_country(text)
        if detected_currency:
            return detected_currency
        
        return None

# Create global currency detector instance
currency_detector = CurrencyDetector()
