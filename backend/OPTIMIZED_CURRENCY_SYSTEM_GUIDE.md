# راهنمای سیستم ارزی بهینه شده - Optimized Currency System Guide

## 🎯 سیستم بهینه شده آماده است!

سیستم تبدیل ارز حالا بهینه شده و فقط به **3 ارز اصلی** تبدیل می‌کند: USD، EUR، ILS

## 💡 رویکرد بهینه شده

### 🔄 جریان تبدیل ارز
```
هر ارزی → USD (ارز پایه) → ارز هدف (USD/EUR/ILS)
```

### 📊 نرخ‌های ضروری (10 نرخ)
| از | به | نرخ | توضیحات |
|----|----|-----|---------|
| CNY | USD | 0.14 | یوان چین به دلار |
| INR | USD | 0.012 | روپیه هند به دلار |
| MYR | USD | 0.21 | رینگیت مالزی به دلار |
| THB | USD | 0.027 | بات تایلند به دلار |
| VND | USD | 0.000041 | دانگ ویتنام به دلار |
| IDR | USD | 0.000065 | روپیه اندونزی به دلار |
| PHP | USD | 0.018 | پزو فیلیپین به دلار |
| SGD | USD | 0.74 | دلار سنگاپور به دلار |
| USD | EUR | 0.85 | دلار به یورو |
| USD | ILS | 3.65 | دلار به شکل |

## ✅ مزایای سیستم بهینه شده

1. **کاهش پیچیدگی**: از 40+ نرخ به 10 نرخ ضروری
2. **بهبود عملکرد**: تبدیل سریع‌تر با USD به عنوان ارز پایه
3. **سادگی نگهداری**: فقط 10 نرخ برای بروزرسانی
4. **دقت بالا**: تبدیل دقیق با ارز پایه
5. **مقیاس‌پذیری**: آسان برای اضافه کردن ارزهای جدید

## 🔧 نحوه کارکرد

### مثال 1: تبدیل یوان چین به یورو
```python
# قیمت: ¥1000
# مرحله 1: ¥1000 → $140 (1000 × 0.14)
# مرحله 2: $140 → €119 (140 × 0.85)
# نتیجه: ¥1000 = €119
```

### مثال 2: تبدیل روپیه هند به شکل
```python
# قیمت: ₹5000
# مرحله 1: ₹5000 → $60 (5000 × 0.012)
# مرحله 2: $60 → ₪219 (60 × 3.65)
# نتیجه: ₹5000 = ₪219
```

## 🛠️ API Endpoints

### تبدیل قیمت
```bash
# تبدیل منفرد
curl -X POST "http://localhost:8000/api/currency-converter/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 1000,
    "from_currency": "CNY",
    "to_currency": "EUR"
  }'

# پاسخ: {"converted_price": 119.0, "original_price": 1000.0, ...}
```

### تشخیص ارز
```bash
# تشخیص از متن قیمت
curl -X POST "http://localhost:8000/api/currency-detector/detect/price" \
  -H "Content-Type: application/json" \
  -d '"¥2999"'

# پاسخ: {"detected_currency": "CNY", "confidence": "medium", ...}
```

## 📱 استفاده در Frontend

### تشخیص و تبدیل خودکار
```javascript
const convertProductPrice = async (productData, targetCurrency) => {
  // 1. تشخیص ارز محصول
  const currencyResponse = await fetch('/api/currency-detector/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_data: productData })
  });
  
  const { detected_currency, extracted_price } = await currencyResponse.json();
  
  if (!detected_currency || !extracted_price) {
    return null;
  }
  
  // 2. تبدیل قیمت
  const conversionResponse = await fetch('/api/currency-converter/convert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      price: extracted_price,
      from_currency: detected_currency,
      to_currency: targetCurrency
    })
  });
  
  const { converted_price } = await conversionResponse.json();
  return converted_price;
};

// مثال استفاده
const product = {
  product_title: 'Chinese Smartphone ¥2999',
  sale_price: '¥2999'
};

const priceInUSD = await convertProductPrice(product, 'USD');
console.log(`Price in USD: $${priceInUSD}`); // $419.86
```

## 📅 بروزرسانی نرخ‌ها

### بروزرسانی دستی
```sql
-- بروزرسانی نرخ یوان چین
UPDATE currency_rate 
SET rate = 0.15, updated_at = NOW() 
WHERE from_currency = 'CNY' AND to_currency = 'USD';
```

### بروزرسانی از طریق API
```bash
curl -X POST "http://localhost:8000/api/currency-rates/rates" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "CNY",
    "to_currency": "USD",
    "rate": 0.15
  }'
```

## 🎯 مثال‌های کاربردی

### محصول چینی
```python
# محصول: گوشی چینی ¥2999
product = {
    'product_title': 'Chinese Smartphone ¥2999',
    'sale_price': '¥2999'
}

# تشخیص ارز: CNY
# تبدیل به USD: $419.86
# تبدیل به EUR: €356.88
# تبدیل به ILS: ₪1532.49
```

### محصول هندی
```python
# محصول: ادویه هندی ₹450
product = {
    'product_title': 'Indian Spices ₹450',
    'sale_price': '₹450'
}

# تشخیص ارز: INR
# تبدیل به USD: $5.40
# تبدیل به EUR: €4.59
# تبدیل به ILS: ₪19.71
```

### محصول مالزیایی
```python
# محصول: کیف مالزیایی RM89
product = {
    'product_title': 'Malaysian Handbag RM89',
    'sale_price': 'RM89'
}

# تشخیص ارز: MYR
# تبدیل به USD: $18.69
# تبدیل به EUR: €15.89
# تبدیل به ILS: ₪68.22
```

## 📊 آمار سیستم بهینه شده

- ✅ **10 نرخ ضروری** (به جای 40+)
- ✅ **3 ارز هدف** (USD، EUR، ILS)
- ✅ **8 ارز مبدا** (CNY، INR، MYR، THB، VND، IDR، PHP، SGD)
- ✅ **USD به عنوان ارز پایه**
- ✅ **تبدیل 2 مرحله‌ای** (مبدا → USD → هدف)
- ✅ **عملکرد بهتر** و **نگهداری آسان‌تر**

## 🚀 مزایای کلیدی

1. **سادگی**: فقط 3 ارز برای نمایش به کاربر
2. **کارایی**: تبدیل سریع با ارز پایه
3. **دقت**: تبدیل دقیق با نرخ‌های به‌روز
4. **انعطاف**: پشتیبانی از ارزهای مختلف کشورها
5. **مقیاس‌پذیری**: آسان برای اضافه کردن ارزهای جدید

## 🎉 خلاصه

سیستم ارزی بهینه شده شامل:

- ✅ **3 ارز اصلی** برای نمایش (USD، EUR، ILS)
- ✅ **تشخیص خودکار** ارز محصولات
- ✅ **تبدیل دقیق** با USD به عنوان ارز پایه
- ✅ **10 نرخ ضروری** برای نگهداری
- ✅ **API endpoints** کامل
- ✅ **عملکرد بهتر** و **سادگی بیشتر**

حالا سیستم شما می‌تواند قیمت محصولات از کشورهای مختلف را تشخیص دهد و فقط به 3 ارز اصلی تبدیل کند!
