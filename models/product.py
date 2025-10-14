"""
Product data models for the landscape supply platform.

Products represent materials that can be purchased (e.g., mulch, stone, soil).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base product fields."""

    name: str = Field(..., description="Product name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., description="Price per unit", gt=0)
    unit: str = Field(..., description="Unit of measurement (e.g., 'yard', 'ton', 'bag')")
    supplier_name: str = Field(..., description="Name of the supplier")
    category: str = Field(..., description="Product category (e.g., 'Mulch', 'Stone', 'Soil')")
    sku: str = Field(..., description="Stock keeping unit / product code")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product. All fields are optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    supplier_name: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None


class Product(ProductBase):
    """
    Complete product model with database fields.

    This model includes the MongoDB _id field and audit timestamps.
    """

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Premium Hardwood Mulch",
                "description": "Dark brown hardwood mulch, finely shredded",
                "price": 35.50,
                "unit": "yard",
                "supplier_name": "Green Valley Supplies",
                "category": "Mulch",
                "sku": "MUL-HW-001",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }
    )
