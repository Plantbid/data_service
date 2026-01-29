"""
Quote routes for the landscape supply platform.

These endpoints manage quote CRUD operations.
The POST endpoint demonstrates denormalization by embedding product data.
"""
from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from database.mongodb import get_database
from models.quote import Quote, QuoteCreate, QuoteLineItem

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("/", response_model=Quote, status_code=status.HTTP_201_CREATED)
async def create_quote(quote_data: QuoteCreate) -> Quote:
    """
    Create a new quote with denormalized product data.

    This endpoint demonstrates the denormalization pattern:
    - For each line item, look up the product by product_id
    - Embed product data (product_name, product_price, product_unit) into the quote
    - Calculate line_total (quantity × price) for each item
    - Calculate total_amount (sum of all line totals)

    Args:
        quote_data: Quote creation data with line items containing product_id and quantity

    Returns:
        The created quote with fully denormalized product data

    Raises:
        HTTPException: If any referenced product is not found
    """
    db = get_database()
    products_collection = db["products"]
    quotes_collection = db["quotes"]

    # Build the line items with denormalized product data
    denormalized_line_items = []
    total_amount = 0.0

    for item in quote_data.line_items:
        # Validate ObjectId format
        if not ObjectId.is_valid(item.product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid product ID format: {item.product_id}"
            )

        # Look up the product
        product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )

        # Calculate line total
        line_total = item.quantity * product["price"]

        # Create denormalized line item
        denormalized_item = QuoteLineItem(
            product_id=item.product_id,
            product_name=product["name"],
            product_price=product["price"],
            product_unit=product["unit"],
            quantity=item.quantity,
            line_total=line_total
        )
        denormalized_line_items.append(denormalized_item.model_dump())
        total_amount += line_total

    # Build the quote document
    quote_dict = quote_data.model_dump(exclude={"line_items"})
    quote_dict["line_items"] = denormalized_line_items
    quote_dict["total_amount"] = total_amount
    quote_dict["created_at"] = datetime.now(timezone.utc)
    quote_dict["updated_at"] = datetime.now(timezone.utc)

    # Insert into database
    result = await quotes_collection.insert_one(quote_dict)

    # Fetch and return the created quote
    created_quote = await quotes_collection.find_one({"_id": result.inserted_id})
    if not created_quote:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created quote"
        )

    # Convert ObjectId to string for response
    created_quote["_id"] = str(created_quote["_id"])
    return Quote(**created_quote)


@router.get("/", response_model=List[Quote])
async def list_quotes() -> List[Quote]:
    """
    List all quotes.

    Returns:
        List of all quotes in the database with their denormalized product data
    """
    db = get_database()
    quotes_collection = db["quotes"]

    quotes = []
    async for quote_doc in quotes_collection.find():
        quote_doc["_id"] = str(quote_doc["_id"])
        quotes.append(Quote(**quote_doc))

    return quotes


@router.get("/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str) -> Quote:
    """
    Get a specific quote by ID.

    Args:
        quote_id: The quote ID

    Returns:
        The requested quote with denormalized product data

    Raises:
        HTTPException: If quote not found or invalid ID format
    """
    db = get_database()
    quotes_collection = db["quotes"]

    # Validate ObjectId format
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid quote ID format"
        )

    # Find quote
    quote_doc = await quotes_collection.find_one({"_id": ObjectId(quote_id)})
    if not quote_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote {quote_id} not found"
        )

    quote_doc["_id"] = str(quote_doc["_id"])
    return Quote(**quote_doc)
