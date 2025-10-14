"""
Integration tests for Quote routes.

These tests use a real MongoDB connection (no mocking) and test the
pre-implemented quote endpoints including initial denormalization.

NOTE: These tests do NOT test propagation of product updates to quotes.
That is the candidate's challenge to implement.
"""


async def test_create_quote_with_denormalization(client):
    """
    Test POST /quotes creates a quote with denormalized product data.

    This tests the initial denormalization that happens when creating a quote.
    It verifies that product data is correctly embedded into the quote.
    """
    # Create a product first
    product_data = {
        "name": "Premium Mulch",
        "description": "High quality mulch",
        "price": 35.50,
        "unit": "yard",
        "supplier_name": "Green Supplies",
        "category": "Mulch",
        "sku": "MUL-001"
    }
    product_response = await client.post("/products/", json=product_data)
    product_id = product_response.json()["_id"]

    # Create a quote referencing the product
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "project_name": "Test Project",
        "status": "draft",
        "line_items": [
            {
                "product_id": product_id,
                "quantity": 10.0
            }
        ]
    }

    response = await client.post("/quotes/", json=quote_data)

    assert response.status_code == 201
    data = response.json()

    # Verify basic quote fields
    assert data["customer_name"] == "Test Customer"
    assert data["customer_email"] == "test@example.com"
    assert data["project_name"] == "Test Project"
    assert data["status"] == "draft"

    # Verify denormalized product data in line items
    assert len(data["line_items"]) == 1
    line_item = data["line_items"][0]

    assert line_item["product_id"] == product_id
    assert line_item["product_name"] == "Premium Mulch"  # Denormalized
    assert line_item["product_price"] == 35.50  # Denormalized
    assert line_item["product_unit"] == "yard"  # Denormalized
    assert line_item["quantity"] == 10.0

    # Verify calculated totals
    assert line_item["line_total"] == 355.00  # 10.0 * 35.50
    assert data["total_amount"] == 355.00

    # Verify database fields
    assert "_id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_create_quote_multiple_line_items(client):
    """Test creating a quote with multiple line items and correct total calculation."""
    # Create two products
    product1_data = {
        "name": "Mulch",
        "description": "Mulch product",
        "price": 20.00,
        "unit": "yard",
        "supplier_name": "Supplier A",
        "category": "Mulch",
        "sku": "MUL-001"
    }
    product1_response = await client.post("/products/", json=product1_data)
    product1_id = product1_response.json()["_id"]

    product2_data = {
        "name": "Stone",
        "description": "Stone product",
        "price": 50.00,
        "unit": "ton",
        "supplier_name": "Supplier B",
        "category": "Stone",
        "sku": "STN-001"
    }
    product2_response = await client.post("/products/", json=product2_data)
    product2_id = product2_response.json()["_id"]

    # Create quote with both products
    quote_data = {
        "customer_name": "Multi-Item Customer",
        "customer_email": "multi@example.com",
        "line_items": [
            {"product_id": product1_id, "quantity": 5.0},
            {"product_id": product2_id, "quantity": 3.0}
        ]
    }

    response = await client.post("/quotes/", json=quote_data)

    assert response.status_code == 201
    data = response.json()

    # Verify both line items
    assert len(data["line_items"]) == 2

    # First line item
    assert data["line_items"][0]["product_name"] == "Mulch"
    assert data["line_items"][0]["product_price"] == 20.00
    assert data["line_items"][0]["quantity"] == 5.0
    assert data["line_items"][0]["line_total"] == 100.00  # 5.0 * 20.00

    # Second line item
    assert data["line_items"][1]["product_name"] == "Stone"
    assert data["line_items"][1]["product_price"] == 50.00
    assert data["line_items"][1]["quantity"] == 3.0
    assert data["line_items"][1]["line_total"] == 150.00  # 3.0 * 50.00

    # Verify total
    assert data["total_amount"] == 250.00  # 100.00 + 150.00


async def test_create_quote_invalid_product_id(client):
    """Test POST /quotes returns 404 when product doesn't exist."""
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "line_items": [
            {
                "product_id": "507f1f77bcf86cd799439011",  # Valid format but doesn't exist
                "quantity": 10.0
            }
        ]
    }

    response = await client.post("/quotes/", json=quote_data)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_create_quote_invalid_product_id_format(client):
    """Test POST /quotes returns 400 for invalid ObjectId format."""
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "line_items": [
            {
                "product_id": "not-a-valid-id",
                "quantity": 10.0
            }
        ]
    }

    response = await client.post("/quotes/", json=quote_data)

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


async def test_create_quote_validation_error(client):
    """Test POST /quotes validates required fields."""
    # Missing required fields
    quote_data = {
        "customer_name": "Test Customer"
        # Missing: customer_email, line_items
    }

    response = await client.post("/quotes/", json=quote_data)

    assert response.status_code == 422  # Validation error


async def test_create_quote_requires_line_items(client):
    """Test POST /quotes requires at least one line item."""
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "line_items": []  # Empty - should fail
    }

    response = await client.post("/quotes/", json=quote_data)

    assert response.status_code == 422  # Validation error


async def test_create_quote_defaults_to_draft(client):
    """Test that quotes default to 'draft' status if not specified."""
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "Test",
        "price": 10.00,
        "unit": "yard",
        "supplier_name": "Supplier",
        "category": "Mulch",
        "sku": "TEST-001"
    }
    product_response = await client.post("/products/", json=product_data)
    product_id = product_response.json()["_id"]

    # Create quote without specifying status
    quote_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "line_items": [
            {"product_id": product_id, "quantity": 1.0}
        ]
        # Note: status not provided
    }

    response = await client.post("/quotes/", json=quote_data)

    assert response.status_code == 201
    assert response.json()["status"] == "draft"


async def test_list_quotes(client):
    """Test GET /quotes returns list of all quotes."""
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "Test",
        "price": 15.00,
        "unit": "yard",
        "supplier_name": "Supplier",
        "category": "Mulch",
        "sku": "TEST-001"
    }
    product_response = await client.post("/products/", json=product_data)
    product_id = product_response.json()["_id"]

    # Create two quotes
    quote1_data = {
        "customer_name": "Customer 1",
        "customer_email": "customer1@example.com",
        "line_items": [{"product_id": product_id, "quantity": 5.0}]
    }
    quote2_data = {
        "customer_name": "Customer 2",
        "customer_email": "customer2@example.com",
        "line_items": [{"product_id": product_id, "quantity": 10.0}]
    }

    await client.post("/quotes/", json=quote1_data)
    await client.post("/quotes/", json=quote2_data)

    # List all quotes
    response = await client.get("/quotes/")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["customer_name"] == "Customer 1"
    assert data[1]["customer_name"] == "Customer 2"


async def test_list_quotes_empty(client):
    """Test GET /quotes returns empty list when no quotes exist."""
    response = await client.get("/quotes/")

    assert response.status_code == 200
    assert response.json() == []


async def test_get_quote_by_id(client):
    """Test GET /quotes/{id} returns a specific quote."""
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "Test",
        "price": 25.00,
        "unit": "yard",
        "supplier_name": "Supplier",
        "category": "Mulch",
        "sku": "TEST-001"
    }
    product_response = await client.post("/products/", json=product_data)
    product_id = product_response.json()["_id"]

    # Create a quote
    quote_data = {
        "customer_name": "Specific Customer",
        "customer_email": "specific@example.com",
        "project_name": "Specific Project",
        "line_items": [{"product_id": product_id, "quantity": 7.0}]
    }
    create_response = await client.post("/quotes/", json=quote_data)
    quote_id = create_response.json()["_id"]

    # Get the quote by ID
    response = await client.get(f"/quotes/{quote_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["_id"] == quote_id
    assert data["customer_name"] == "Specific Customer"
    assert data["project_name"] == "Specific Project"


async def test_get_quote_not_found(client):
    """Test GET /quotes/{id} returns 404 for non-existent quote."""
    fake_id = "507f1f77bcf86cd799439011"

    response = await client.get(f"/quotes/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_get_quote_invalid_id_format(client):
    """Test GET /quotes/{id} returns 400 for invalid ObjectId format."""
    invalid_id = "not-a-valid-objectid"

    response = await client.get(f"/quotes/{invalid_id}")

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()
