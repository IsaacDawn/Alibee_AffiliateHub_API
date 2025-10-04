# سیستم تبدیل ارز - Currency Conversion System

این سیستم امکان تبدیل قیمت محصولات به واحدهای پولی مختلف را فراهم می‌کند.

## ویژگی‌ها

- ✅ مدیریت نرخ تبدیل ارز در دیتابیس
- ✅ تبدیل قیمت‌های منفرد و گروهی
- ✅ API endpoints برای مدیریت نرخ‌ها
- ✅ پشتیبانی از USD، EUR، ILS
- ✅ امکان بروزرسانی دستی نرخ‌ها

## راه‌اندازی

### 1. ایجاد جدول در دیتابیس

```bash
cd backend
python setup_currency_table.py
```

### 2. بروزرسانی نرخ‌های تبدیل

#### از طریق API:

```bash
# تنظیم نرخ تبدیل USD به EUR
curl -X POST "http://localhost:8000/api/currency-rates/rates" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "USD",
    "to_currency": "EUR", 
    "rate": 0.85
  }'

# بروزرسانی چندین نرخ به صورت همزمان
curl -X POST "http://localhost:8000/api/currency-rates/rates/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {"from_currency": "USD", "to_currency": "EUR", "rate": 0.85},
    {"from_currency": "USD", "to_currency": "ILS", "rate": 3.65},
    {"from_currency": "EUR", "to_currency": "USD", "rate": 1.18}
  ]'
```

#### از طریق دیتابیس:

```sql
-- بروزرسانی نرخ USD به EUR
UPDATE currency_rate 
SET rate = 0.85, updated_at = NOW() 
WHERE from_currency = 'USD' AND to_currency = 'EUR';

-- اضافه کردن نرخ جدید
INSERT INTO currency_rate (from_currency, to_currency, rate) 
VALUES ('USD', 'EUR', 0.85) 
ON DUPLICATE KEY UPDATE rate = VALUES(rate), updated_at = NOW();
```

## API Endpoints

### مدیریت نرخ‌های تبدیل

| Method | Endpoint | توضیحات |
|--------|----------|---------|
| GET | `/api/currency-rates/rates` | دریافت تمام نرخ‌ها |
| GET | `/api/currency-rates/rates/{from}/{to}` | دریافت نرخ خاص |
| POST | `/api/currency-rates/rates` | تنظیم/بروزرسانی نرخ |
| POST | `/api/currency-rates/rates/bulk` | بروزرسانی چندین نرخ |
| DELETE | `/api/currency-rates/rates/{from}/{to}` | حذف نرخ |

### تبدیل قیمت

| Method | Endpoint | توضیحات |
|--------|----------|---------|
| POST | `/api/currency-converter/convert` | تبدیل قیمت منفرد |
| POST | `/api/currency-converter/convert/bulk` | تبدیل چندین قیمت |
| GET | `/api/currency-converter/rate/{from}/{to}` | دریافت نرخ تبدیل |
| POST | `/api/currency-converter/initialize-default-rates` | راه‌اندازی نرخ‌های پیش‌فرض |

## مثال‌های استفاده

### تبدیل قیمت منفرد

```python
import requests

# تبدیل 100 USD به EUR
response = requests.post("http://localhost:8000/api/currency-converter/convert", json={
    "price": 100.0,
    "from_currency": "USD",
    "to_currency": "EUR"
})

result = response.json()
print(f"${result['original_price']} USD = {result['converted_price']} EUR")
# خروجی: $100.0 USD = 85.0 EUR
```

### تبدیل چندین قیمت

```python
# تبدیل چندین قیمت از USD به ILS
response = requests.post("http://localhost:8000/api/currency-converter/convert/bulk", json={
    "prices": [10.0, 25.0, 50.0, 100.0],
    "from_currency": "USD",
    "to_currency": "ILS"
})

result = response.json()
for conversion in result['conversions']:
    print(f"${conversion['original_price']} USD = ₪{conversion['converted_price']} ILS")
```

## ساختار جدول currency_rate

```sql
CREATE TABLE currency_rate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_currency VARCHAR(3) NOT NULL,      -- ارز مبدا (USD, EUR, ILS)
    to_currency VARCHAR(3) NOT NULL,        -- ارز مقصد
    rate DECIMAL(10, 6) NOT NULL,           -- نرخ تبدیل
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_currency_pair (from_currency, to_currency)
);
```

## نرخ‌های پیش‌فرض

| از | به | نرخ |
|----|----|-----|
| USD | EUR | 0.85 |
| USD | ILS | 3.65 |
| EUR | USD | 1.18 |
| EUR | ILS | 4.30 |
| ILS | USD | 0.27 |
| ILS | EUR | 0.23 |

## نکات مهم

1. **بروزرسانی روزانه**: نرخ‌های تبدیل را روزانه بروزرسانی کنید
2. **دقت**: نرخ‌ها با 6 رقم اعشار ذخیره می‌شوند
3. **یکتایی**: هر جفت ارز فقط یک نرخ دارد
4. **پشتیبانی**: سیستم از USD، EUR، ILS پشتیبانی می‌کند

## عیب‌یابی

### خطای "No exchange rate found"
- مطمئن شوید نرخ تبدیل در دیتابیس وجود دارد
- از endpoint `/api/currency-converter/initialize-default-rates` استفاده کنید

### خطای اتصال به دیتابیس
- تنظیمات دیتابیس در `config/settings.py` را بررسی کنید
- مطمئن شوید جدول `currency_rate` ایجاد شده است

## توسعه

برای اضافه کردن ارز جدید:

1. ارز جدید را به `frontend/src/hooks/useCurrency.ts` اضافه کنید
2. نرخ‌های تبدیل مربوطه را در دیتابیس تنظیم کنید
3. آیکون و نماد ارز را در frontend اضافه کنید
