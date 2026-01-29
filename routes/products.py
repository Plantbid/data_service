"""
Product routes for the landscape supply platform.

These endpoints manage product CRUD operations.
The PATCH endpoint includes a TODO for implementing propagation to quotes.
"""
from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from database.mongodb import get_database
from models.product import Product, ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate) -> Product:
    """
    Create a new product.

    Args:
        product_data: Product creation data

    Returns:
        The created product with generated ID and timestamps
    """
    db = get_database()
    products_collection = db["products"]

    # Convert to dict and add timestamps
    product_dict = product_data.model_dump()
    product_dict["created_at"] = datetime.now(timezone.utc)
    product_dict["updated_at"] = datetime.now(timezone.utc)

    # Insert into database
    result = await products_collection.insert_one(product_dict)

    # Fetch and return the created product
    created_product = await products_collection.find_one({"_id": result.inserted_id})
    if not created_product:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created product"
        )

    # Convert ObjectId to string for response
    created_product["_id"] = str(created_product["_id"])
    return Product(**created_product)


@router.get("/", response_model=List[Product])
async def list_products() -> List[Product]:
    """
    List all products.

    Returns:
        List of all products in the database
    """
    db = get_database()
    products_collection = db["products"]

    products = []
    async for product_doc in products_collection.find():
        product_doc["_id"] = str(product_doc["_id"])
        products.append(Product(**product_doc))

    return products


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str) -> Product:
    """
    Get a specific product by ID.

    Args:
        product_id: The product ID

    Returns:
        The requested product

    Raises:
        HTTPException: If product not found or invalid ID format
    """
    db = get_database()
    products_collection = db["products"]

    # Validate ObjectId format
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )

    # Find product
    product_doc = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not product_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )

    product_doc["_id"] = str(product_doc["_id"])
    return Product(**product_doc)


@router.patch("/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate) -> Product:
    """
    Update a product and propagate changes to quotes.

    TODO: Implement propagation logic to update denormalized data in quotes.

    Args:
        product_id: The product ID to update
        product_update: Fields to update (partial update supported)

    Returns:
        The updated product

    Raises:
        HTTPException: If product not found or invalid ID format
    """
    db = get_database()
    products_collection = db["products"]

    # Validate ObjectId format
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )

    # Check if product exists
    existing_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )

    # Build update document (only include fields that were provided)
    update_data = product_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Always update the updated_at timestamp
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Update the product
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )

    # Fetch the updated product
    updated_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated product"
        )

    # TODO: IMPLEMENT PROPAGATION LOGIC HERE
    # When a product is updated, all quotes that reference this product
    # need to have their denormalized data updated.
    #
    # Consider:
    # - How to find all affected quotes?
    # - How to update denormalized fields (product_name, product_price, product_unit)?
    # - How to recalculate line_total and total_amount?
    # - How to ensure reliability and consistency?
    # - Scalability: there could be a million quotes related to this product.

    updated_product["_id"] = str(updated_product["_id"])
    return Product(**updated_product)
