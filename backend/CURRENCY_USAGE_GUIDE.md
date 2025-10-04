# راهنمای استفاده از سیستم تبدیل ارز

## ✅ سیستم آماده است!

سیستم تبدیل ارز با موفقیت راه‌اندازی شده و آماده استفاده است.

## 🎯 ویژگی‌های پیاده‌سازی شده

- ✅ جدول `currency_rate` در دیتابیس MySQL ایجاد شد
- ✅ نرخ‌های پیش‌فرض (USD, EUR, ILS) اضافه شدند
- ✅ API endpoints برای مدیریت نرخ‌ها
- ✅ سرویس تبدیل قیمت
- ✅ تست کامل سیستم

## 📊 نرخ‌های فعلی

| از | به | نرخ |
|----|----|-----|
| USD | EUR | 0.85 |
| USD | ILS | 3.65 |
| EUR | USD | 1.18 |
| EUR | ILS | 4.30 |
| ILS | USD | 0.27 |
| ILS | EUR | 0.23 |

## 🔧 بروزرسانی نرخ‌ها

### روش 1: از طریق API

```bash
# بروزرسانی نرخ USD به EUR
curl -X POST "http://localhost:8000/api/currency-rates/rates" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "USD",
    "to_currency": "EUR", 
    "rate": 0.87
  }'
```

### روش 2: از طریق دیتابیس

```sql
-- بروزرسانی نرخ USD به EUR
UPDATE currency_rate 
SET rate = 0.87, updated_at = NOW() 
WHERE from_currency = 'USD' AND to_currency = 'EUR';
```

### روش 3: بروزرسانی گروهی

```bash
curl -X POST "http://localhost:8000/api/currency-rates/rates/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {"from_currency": "USD", "to_currency": "EUR", "rate": 0.87},
    {"from_currency": "USD", "to_currency": "ILS", "rate": 3.70},
    {"from_currency": "EUR", "to_currency": "USD", "rate": 1.15}
  ]'
```

## 💱 تبدیل قیمت

### تبدیل منفرد

```python
from services.currency_converter import currency_converter

# تبدیل 100 USD به EUR
converted_price = currency_converter.convert_price(100.0, 'USD', 'EUR')
print(f"$100 USD = €{converted_price} EUR")
```

### از طریق API

```bash
curl -X POST "http://localhost:8000/api/currency-converter/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 100.0,
    "from_currency": "USD",
    "to_currency": "EUR"
  }'
```

## 📋 API Endpoints موجود

### مدیریت نرخ‌ها
- `GET /api/currency-rates/rates` - دریافت تمام نرخ‌ها
- `GET /api/currency-rates/rates/{from}/{to}` - دریافت نرخ خاص
- `POST /api/currency-rates/rates` - تنظیم/بروزرسانی نرخ
- `POST /api/currency-rates/rates/bulk` - بروزرسانی چندین نرخ
- `DELETE /api/currency-rates/rates/{from}/{to}` - حذف نرخ

### تبدیل قیمت
- `POST /api/currency-converter/convert` - تبدیل قیمت منفرد
- `POST /api/currency-converter/convert/bulk` - تبدیل چندین قیمت
- `GET /api/currency-converter/rate/{from}/{to}` - دریافت نرخ تبدیل

## 🔄 استفاده در Frontend

برای استفاده در frontend، می‌توانید از API endpoints استفاده کنید:

```javascript
// تبدیل قیمت محصول
const convertPrice = async (price, fromCurrency, toCurrency) => {
  const response = await fetch('/api/currency-converter/convert', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      price: price,
      from_currency: fromCurrency,
      to_currency: toCurrency
    })
  });
  
  const result = await response.json();
  return result.converted_price;
};

// مثال استفاده
const convertedPrice = await convertPrice(100, 'USD', 'EUR');
console.log(`$100 USD = €${convertedPrice} EUR`);
```

## 📅 بروزرسانی روزانه

برای بروزرسانی روزانه نرخ‌ها:

1. **نرخ‌های جدید را از منابع معتبر دریافت کنید**
2. **از API bulk update استفاده کنید**
3. **یا مستقیماً در دیتابیس بروزرسانی کنید**

## 🛠️ عیب‌یابی

### اگر نرخ تبدیل پیدا نشد:
```bash
# بررسی نرخ‌های موجود
curl "http://localhost:8000/api/currency-rates/rates"

# راه‌اندازی مجدد نرخ‌های پیش‌فرض
curl -X POST "http://localhost:8000/api/currency-converter/initialize-default-rates"
```

### اگر خطای دیتابیس دریافت کردید:
```bash
# اجرای اسکریپت بررسی ساختار
cd backend
python check_database_structure.py
```

## 🎉 خلاصه

سیستم تبدیل ارز کاملاً آماده است و شامل:

- ✅ جدول `currency_rate` در MySQL
- ✅ 6 نرخ تبدیل پیش‌فرض
- ✅ API endpoints کامل
- ✅ سرویس تبدیل قیمت
- ✅ تست‌های موفق

حالا می‌توانید از این سیستم برای تبدیل قیمت محصولات به واحدهای پولی مختلف استفاده کنید!
