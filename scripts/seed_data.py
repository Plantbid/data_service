"""
Seed script to populate initial product data for testing.

Usage:
    python scripts/seed_data.py
"""
import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path to import from project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from motor.motor_asyncio import AsyncIOMotorClient


SAMPLE_PRODUCTS = [
    {
        "name": "Premium Hardwood Mulch",
        "description": "Dark brown hardwood mulch, finely shredded",
        "price": 35.50,
        "unit": "yard",
        "supplier_name": "Green Valley Supplies",
        "category": "Mulch",
        "sku": "MUL-HW-001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Red Cedar Mulch",
        "description": "Natural red cedar mulch with pleasant aroma",
        "price": 42.00,
        "unit": "yard",
        "supplier_name": "Green Valley Supplies",
        "category": "Mulch",
        "sku": "MUL-RC-002",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "River Rock 1-3 inch",
        "description": "Smooth river rock, mixed earth tones",
        "price": 65.00,
        "unit": "ton",
        "supplier_name": "Mountain Stone Co",
        "category": "Stone",
        "sku": "STN-RR-001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Pea Gravel",
        "description": "Small rounded gravel, ideal for pathways",
        "price": 48.50,
        "unit": "ton",
        "supplier_name": "Mountain Stone Co",
        "category": "Stone",
        "sku": "STN-PG-002",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Premium Topsoil",
        "description": "Rich, screened topsoil perfect for gardens",
        "price": 28.00,
        "unit": "yard",
        "supplier_name": "Earth Materials Inc",
        "category": "Soil",
        "sku": "SOL-TS-001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Compost Blend",
        "description": "Organic compost blend, nutrient-rich",
        "price": 32.50,
        "unit": "yard",
        "supplier_name": "Earth Materials Inc",
        "category": "Soil",
        "sku": "SOL-CB-002",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Playground Mulch",
        "description": "Safety-certified playground mulch",
        "price": 38.00,
        "unit": "yard",
        "supplier_name": "SafePlay Materials",
        "category": "Mulch",
        "sku": "MUL-PG-003",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Crushed Granite",
        "description": "Gray crushed granite, 3/4 inch",
        "price": 52.00,
        "unit": "ton",
        "supplier_name": "Mountain Stone Co",
        "category": "Stone",
        "sku": "STN-CG-003",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Garden Soil Mix",
        "description": "Balanced soil mix for raised beds",
        "price": 35.00,
        "unit": "yard",
        "supplier_name": "Earth Materials Inc",
        "category": "Soil",
        "sku": "SOL-GM-003",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Black Dyed Mulch",
        "description": "Deep black dyed hardwood mulch",
        "price": 39.50,
        "unit": "yard",
        "supplier_name": "Green Valley Supplies",
        "category": "Mulch",
        "sku": "MUL-BK-004",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]


async def seed_database():
    """Seed the database with sample products."""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "landscape_supply")

    print(f"Connecting to MongoDB at {mongodb_url}")
    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]

    try:
        # Test connection
        await client.admin.command('ping')
        print(f"Connected to database: {db_name}")

        # Clear existing products
        products_collection = db["products"]
        deleted = await products_collection.delete_many({})
        print(f"Cleared {deleted.deleted_count} existing products")

        # Insert sample products
        result = await products_collection.insert_many(SAMPLE_PRODUCTS)
        print(f"Inserted {len(result.inserted_ids)} products")

        # Display inserted products
        print("\nInserted products:")
        async for product in products_collection.find():
            print(f"  - {product['name']} (${product['price']}/{product['unit']}) - SKU: {product['sku']}")

        print("\n✅ Database seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
