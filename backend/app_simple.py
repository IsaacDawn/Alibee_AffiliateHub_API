from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Alibee Affiliator API",
    description="Simple AliExpress Affiliate API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Alibee Affiliator API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/stats")
def get_stats():
    return {
        "data": {
            "total_products": 0,
            "total_likes": 0,
            "total_custom_titles": 0
        }
    }

@app.get("/api/search")
def search_products(q: str = "all", page: int = 1, pageSize: int = 150, use_api: bool = True):
    # Return demo products
    demo_products = [
        {
            "id": "1005009503660629",
            "title": "Demo Product 1",
            "image": "https://via.placeholder.com/300x300",
            "price": 29.99,
            "originalPrice": 39.99,
            "currency": "USD",
            "rating": 4.5,
            "storeName": "Demo Store",
            "hasVideo": False,
            "discount": 25
        },
        {
            "id": "1005009503660630",
            "title": "Demo Product 2",
            "image": "https://via.placeholder.com/300x300",
            "price": 19.99,
            "originalPrice": 24.99,
            "currency": "USD",
            "rating": 4.2,
            "storeName": "Demo Store",
            "hasVideo": True,
            "discount": 20
        }
    ]
    
    return {
        "items": demo_products,
        "page": page,
        "pageSize": pageSize,
        "hasMore": False,
        "total": len(demo_products)
    }

@app.get("/api/product/{product_id}")
def get_product_by_id(product_id: str):
    demo_product = {
        "id": product_id,
        "title": f"Product {product_id}",
        "image": "https://via.placeholder.com/300x300",
        "price": 29.99,
        "originalPrice": 39.99,
        "currency": "USD",
        "rating": 4.5,
        "storeName": "Demo Store",
        "hasVideo": False,
        "discount": 25
    }
    
    return {
        "items": [demo_product],
        "page": 1,
        "pageSize": 1,
        "hasMore": False,
        "total": 1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
