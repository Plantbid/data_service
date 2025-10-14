"""
Tests for Product Pydantic models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from models.product import ProductBase, ProductCreate, ProductUpdate, Product


def test_product_create_valid():
    """Test that ProductCreate accepts valid data."""
    product_data = {
        "name": "Test Mulch",
        "description": "A test product",
        "price": 25.50,
        "unit": "yard",
        "supplier_name": "Test Supplier",
        "category": "Mulch",
        "sku": "TEST-001"
    }
    product = ProductCreate(**product_data)
    assert product.name == "Test Mulch"
    assert product.price == 25.50
    assert product.sku == "TEST-001"


def test_product_create_requires_positive_price():
    """Test that ProductCreate rejects negative or zero prices."""
    product_data = {
        "name": "Test Mulch",
        "price": 0.0,  # Invalid: must be > 0
        "unit": "yard",
        "supplier_name": "Test Supplier",
        "category": "Mulch",
        "sku": "TEST-001"
    }
    with pytest.raises(ValidationError):
        ProductCreate(**product_data)


def test_product_create_requires_name():
    """Test that ProductCreate requires a name."""
    product_data = {
        "price": 25.50,
        "unit": "yard",
        "supplier_name": "Test Supplier",
        "category": "Mulch",
        "sku": "TEST-001"
    }
    with pytest.raises(ValidationError):
        ProductCreate(**product_data)


def test_product_update_all_fields_optional():
    """Test that ProductUpdate allows partial updates (all fields optional)."""
    # Only updating price
    update = ProductUpdate(price=30.00)
    assert update.price == 30.00
    assert update.name is None
    assert update.description is None

    # Only updating name
    update2 = ProductUpdate(name="New Name")
    assert update2.name == "New Name"
    assert update2.price is None


def test_product_model_with_id_and_timestamps():
    """Test that Product model includes MongoDB _id and timestamps."""
    product_data = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Test Mulch",
        "description": "A test product",
        "price": 25.50,
        "unit": "yard",
        "supplier_name": "Test Supplier",
        "category": "Mulch",
        "sku": "TEST-001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    product = Product(**product_data)
    assert product.id == "507f1f77bcf86cd799439011"
    assert product.name == "Test Mulch"
    assert isinstance(product.created_at, datetime)
    assert isinstance(product.updated_at, datetime)


def test_product_model_accepts_id_alias():
    """Test that Product model correctly aliases _id to id."""
    product_data = {
        "id": "507f1f77bcf86cd799439011",  # Using 'id' instead of '_id'
        "name": "Test Mulch",
        "price": 25.50,
        "unit": "yard",
        "supplier_name": "Test Supplier",
        "category": "Mulch",
        "sku": "TEST-001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    product = Product(**product_data)
    assert product.id == "507f1f77bcf86cd799439011"
