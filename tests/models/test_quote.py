"""
Tests for Quote Pydantic models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from models.quote import QuoteLineItem, QuoteBase, QuoteCreate, Quote


def test_quote_line_item_valid():
    """Test that QuoteLineItem accepts valid data."""
    line_item_data = {
        "product_id": "507f1f77bcf86cd799439011",
        "product_name": "Premium Mulch",
        "product_price": 35.50,
        "product_unit": "yard",
        "quantity": 10.0,
        "line_total": 355.00
    }
    line_item = QuoteLineItem(**line_item_data)
    assert line_item.product_id == "507f1f77bcf86cd799439011"
    assert line_item.quantity == 10.0
    assert line_item.line_total == 355.00


def test_quote_line_item_requires_positive_quantity():
    """Test that QuoteLineItem rejects zero or negative quantities."""
    line_item_data = {
        "product_id": "507f1f77bcf86cd799439011",
        "product_name": "Premium Mulch",
        "product_price": 35.50,
        "product_unit": "yard",
        "quantity": 0.0,  # Invalid: must be > 0
        "line_total": 0.0
    }
    with pytest.raises(ValidationError):
        QuoteLineItem(**line_item_data)


def test_quote_create_valid():
    """Test that QuoteCreate accepts valid data."""
    line_item = QuoteLineItem(
        product_id="507f1f77bcf86cd799439011",
        product_name="Premium Mulch",
        product_price=35.50,
        product_unit="yard",
        quantity=10.0,
        line_total=355.00
    )
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "project_name": "Test Project",
        "status": "draft",
        "line_items": [line_item]
    }
    quote = QuoteCreate(**quote_data)
    assert quote.customer_name == "Test Customer"
    assert quote.customer_email == "test@example.com"
    assert len(quote.line_items) == 1
    assert quote.status == "draft"


def test_quote_create_requires_at_least_one_line_item():
    """Test that QuoteCreate requires at least one line item."""
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "line_items": []  # Invalid: must have at least 1 item
    }
    with pytest.raises(ValidationError):
        QuoteCreate(**quote_data)


def test_quote_create_defaults_to_draft_status():
    """Test that QuoteCreate defaults status to 'draft'."""
    line_item = QuoteLineItem(
        product_id="507f1f77bcf86cd799439011",
        product_name="Premium Mulch",
        product_price=35.50,
        product_unit="yard",
        quantity=10.0,
        line_total=355.00
    )
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "line_items": [line_item]
        # Note: status not provided
    }
    quote = QuoteCreate(**quote_data)
    assert quote.status == "draft"


def test_quote_model_with_id_and_timestamps():
    """Test that Quote model includes MongoDB _id and timestamps."""
    line_item = QuoteLineItem(
        product_id="507f1f77bcf86cd799439011",
        product_name="Premium Mulch",
        product_price=35.50,
        product_unit="yard",
        quantity=10.0,
        line_total=355.00
    )
    quote_data = {
        "_id": "507f1f77bcf86cd799439012",
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "project_name": "Test Project",
        "status": "draft",
        "line_items": [line_item],
        "total_amount": 355.00,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    quote = Quote(**quote_data)
    assert quote.id == "507f1f77bcf86cd799439012"
    assert quote.customer_name == "Test Customer"
    assert quote.total_amount == 355.00
    assert isinstance(quote.created_at, datetime)
    assert isinstance(quote.updated_at, datetime)


def test_quote_denormalized_structure():
    """Test that Quote properly embeds denormalized product data in line items."""
    line_item = QuoteLineItem(
        product_id="507f1f77bcf86cd799439011",
        product_name="Premium Mulch",  # Denormalized
        product_price=35.50,            # Denormalized
        product_unit="yard",            # Denormalized
        quantity=10.0,
        line_total=355.00
    )

    # Verify the line item has denormalized product fields
    assert line_item.product_name == "Premium Mulch"
    assert line_item.product_price == 35.50
    assert line_item.product_unit == "yard"

    # These are the fields that will need to be updated when products change
    assert hasattr(line_item, 'product_name')
    assert hasattr(line_item, 'product_price')
    assert hasattr(line_item, 'product_unit')
