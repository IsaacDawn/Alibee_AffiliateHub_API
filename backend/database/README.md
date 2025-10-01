# Database Configuration - Alibee Affiliate

## 📋 Overview

This directory contains all database-related components for the Alibee Affiliate application.

## 🗂️ Files

- `connection.py` - Database connection management with connection pooling
- `migrations.py` - Database migration system for schema management
- `__init__.py` - Package initialization

## 🏗️ Database Schema

### Main Tables

#### `saved_products`
Stores user's saved products with affiliate links.

```sql
CREATE TABLE saved_products (
    product_id VARCHAR(255) NOT NULL PRIMARY KEY,
    product_title TEXT,
    promotion_link TEXT,
    product_category VARCHAR(255),
    custom_title TEXT,
    has_video BOOLEAN DEFAULT FALSE,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_saved_at (saved_at),
    INDEX idx_category (product_category),
    INDEX idx_updated_at (updated_at)
);
```

#### `search_logs` (Optional)
Tracks search queries for analytics.

```sql
CREATE TABLE search_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query VARCHAR(500),
    results_count INT DEFAULT 0,
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_query (query),
    INDEX idx_timestamp (search_timestamp)
);
```

#### `system_stats` (Optional)
Stores system statistics and metrics.

```sql
CREATE TABLE system_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_name VARCHAR(100) NOT NULL UNIQUE,
    stat_value VARCHAR(500),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stat_name (stat_name)
);
```

## 🔧 Setup

### 1. Environment Configuration

Create a `.env` file with your database credentials:

```env
# Database Configuration
DB_HOST=your_database_host
DB_PORT=3306
DB_NAME=alibee_affiliate
DB_USER=your_username
DB_PASSWORD=your_password
```

### 2. Run Database Setup

```bash
cd backend
python setup_database.py
```

### 3. Manual Migration (if needed)

```python
from database.migrations import migration
migration.run_migrations()
```

## 🚀 Features

### Connection Pooling
- Automatic connection pool management
- Fallback to direct connections if pool fails
- Configurable pool size (default: 5 connections)

### Migration System
- Automatic database creation
- Table creation with proper indexes
- Constraint management
- Schema versioning

### Error Handling
- Comprehensive error logging
- Graceful fallbacks
- Connection retry logic

## 📊 API Endpoints

### Database Management
- `GET /api/database/info` - Get database information
- `POST /api/database/migrate` - Run migrations
- `POST /api/database/constraints` - Add constraints
- `GET /api/database/stats` - Get detailed statistics

### Health Check
- `GET /api/health` - Check database connectivity

## 🔍 Monitoring

### Health Check Response
```json
{
    "status": "healthy",
    "database": {
        "status": "healthy",
        "message": "Database connected - 15 saved products"
    },
    "aliexpress_api": {
        "status": "configured",
        "configured": true
    }
}
```

### Database Stats Response
```json
{
    "success": true,
    "basic_stats": {
        "savedProducts": 15,
        "totalProducts": 0
    },
    "database_info": {
        "database_name": "alibee_affiliate",
        "mysql_version": "8.0.35",
        "tables": ["saved_products", "search_logs", "system_stats"],
        "saved_products_count": 15,
        "status": "connected"
    }
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check database credentials in `.env`
   - Verify database server is running
   - Check network connectivity

2. **Migration Failed**
   - Ensure database user has CREATE privileges
   - Check for existing conflicting tables
   - Review error logs

3. **Pool Initialization Failed**
   - System will fallback to direct connections
   - Check MySQL connector version
   - Verify pool configuration

### Logs
All database operations are logged with appropriate levels:
- INFO: Normal operations
- ERROR: Connection and query failures
- DEBUG: Detailed operation traces

## 🔒 Security

- Use environment variables for credentials
- Connection pooling prevents connection exhaustion
- Prepared statements prevent SQL injection
- Proper error handling prevents information leakage

## 📈 Performance

- Connection pooling reduces connection overhead
- Indexes on frequently queried columns
- Efficient pagination for large datasets
- Optimized queries with proper WHERE clauses
