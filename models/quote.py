"""
Quote data models for the landscape supply platform.

Quotes represent customer requests for materials with embedded (denormalized) product data.
This denormalization allows for fast reads without joins, but requires propagation when products change.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuoteLineItem(BaseModel):
    """
    A single line item in a quote with denormalized product data.

    This embeds product information at the time the quote was created.
    When the source product changes, these denormalized fields should be updated.
    """

    product_id: str = Field(..., description="Reference to the product ID")
    product_name: str = Field(..., description="Product name (denormalized)")
    product_price: float = Field(..., description="Product price at quote time (denormalized)")
    product_unit: str = Field(..., description="Product unit (denormalized)")
    quantity: float = Field(..., description="Quantity requested", gt=0)
    line_total: float = Field(..., description="Total for this line (quantity * price)")


class QuoteBase(BaseModel):
    """Base quote fields."""

    customer_name: str = Field(..., description="Customer name", min_length=1)
    customer_email: str = Field(..., description="Customer email")
    project_name: Optional[str] = Field(None, description="Optional project name")
    status: str = Field(
        default="draft",
        description="Quote status (draft, sent, accepted, rejected)",
    )


class QuoteCreate(QuoteBase):
    """Schema for creating a new quote."""

    line_items: List[QuoteLineItem] = Field(
        ..., description="Line items in the quote", min_length=1
    )


class Quote(QuoteBase):
    """
    Complete quote model with database fields.

    Quotes contain denormalized product data in line_items for performance.
    """

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    line_items: List[QuoteLineItem] = Field(..., description="Line items in the quote")
    total_amount: float = Field(..., description="Total quote amount")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "customer_name": "Green Landscapes LLC",
                "customer_email": "contact@greenlandscapes.com",
                "project_name": "Riverside Park Renovation",
                "status": "draft",
                "line_items": [
                    {
                        "product_id": "507f1f77bcf86cd799439011",
                        "product_name": "Premium Hardwood Mulch",
                        "product_price": 35.50,
                        "product_unit": "yard",
                        "quantity": 10.0,
                        "line_total": 355.00,
                    }
                ],
                "total_amount": 355.00,
                "created_at": "2024-01-15T14:30:00Z",
                "updated_at": "2024-01-15T14:30:00Z",
            }
        }
    )
