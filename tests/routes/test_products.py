"""
Integration tests for Product routes.

These tests use a real MongoDB connection (no mocking) and test the
pre-implemented CRUD endpoints.
"""


async def test_create_product(client):
    """Test POST /products creates a new product."""
    product_data = {
        "name": "Test Mulch",
        "description": "A test product",
        "price": 25.50,
        "unit": "yard",
        "supplier_name": "Test Supplier",
        "category": "Mulch",
        "sku": "TEST-001"
    }

    response = await client.post("/products/", json=product_data)

    assert response.status_code == 201
    data = response.json()

    # Verify response contains all fields
    assert data["name"] == "Test Mulch"
    assert data["description"] == "A test product"
    assert data["price"] == 25.50
    assert data["unit"] == "yard"
    assert data["supplier_name"] == "Test Supplier"
    assert data["category"] == "Mulch"
    assert data["sku"] == "TEST-001"

    # Verify database fields are present
    assert "_id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_create_product_validation_error(client):
    """Test POST /products rejects invalid data."""
    # Missing required fields
    product_data = {
        "name": "Test Product"
        # Missing: price, unit, supplier_name, category, sku
    }

    response = await client.post("/products/", json=product_data)
    assert response.status_code == 422  # Validation error


async def test_list_products(client):
    """Test GET /products returns list of all products."""
    # Create test products
    products = [
        {
            "name": "Product 1",
            "description": "First product",
            "price": 10.00,
            "unit": "yard",
            "supplier_name": "Supplier A",
            "category": "Mulch",
            "sku": "SKU-001"
        },
        {
            "name": "Product 2",
            "description": "Second product",
            "price": 20.00,
            "unit": "ton",
            "supplier_name": "Supplier B",
            "category": "Stone",
            "sku": "SKU-002"
        }
    ]

    for product in products:
        await client.post("/products/", json=product)

    # List all products
    response = await client.get("/products/")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Product 1"
    assert data[1]["name"] == "Product 2"


async def test_list_products_empty(client):
    """Test GET /products returns empty list when no products exist."""
    response = await client.get("/products/")

    assert response.status_code == 200
    assert response.json() == []


async def test_get_product_by_id(client):
    """Test GET /products/{id} returns a specific product."""
    # Create a product
    product_data = {
        "name": "Specific Product",
        "description": "A specific test product",
        "price": 30.00,
        "unit": "bag",
        "supplier_name": "Test Supplier",
        "category": "Soil",
        "sku": "SPEC-001"
    }

    create_response = await client.post("/products/", json=product_data)
    product_id = create_response.json()["_id"]

    # Get the product by ID
    response = await client.get(f"/products/{product_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["_id"] == product_id
    assert data["name"] == "Specific Product"
    assert data["price"] == 30.00


async def test_get_product_not_found(client):
    """Test GET /products/{id} returns 404 for non-existent product."""
    # Use a valid ObjectId format that doesn't exist
    fake_id = "507f1f77bcf86cd799439011"

    response = await client.get(f"/products/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_get_product_invalid_id_format(client):
    """Test GET /products/{id} returns 400 for invalid ObjectId format."""
    invalid_id = "not-a-valid-objectid"

    response = await client.get(f"/products/{invalid_id}")

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


async def test_update_product(client):
    """Test PATCH /products/{id} updates product fields."""
    # Create a product
    product_data = {
        "name": "Original Name",
        "description": "Original description",
        "price": 40.00,
        "unit": "yard",
        "supplier_name": "Original Supplier",
        "category": "Mulch",
        "sku": "ORIG-001"
    }

    create_response = await client.post("/products/", json=product_data)
    product_id = create_response.json()["_id"]

    # Update the product
    update_data = {
        "name": "Updated Name",
        "price": 45.00
    }

    response = await client.patch(f"/products/{product_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()

    # Verify updated fields
    assert data["name"] == "Updated Name"
    assert data["price"] == 45.00

    # Verify unchanged fields
    assert data["description"] == "Original description"
    assert data["unit"] == "yard"
    assert data["supplier_name"] == "Original Supplier"


async def test_update_product_not_found(client):
    """Test PATCH /products/{id} returns 404 for non-existent product."""
    fake_id = "507f1f77bcf86cd799439011"
    update_data = {"price": 50.00}

    response = await client.patch(f"/products/{fake_id}", json=update_data)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_update_product_invalid_id_format(client):
    """Test PATCH /products/{id} returns 400 for invalid ObjectId format."""
    invalid_id = "not-a-valid-objectid"
    update_data = {"price": 50.00}

    response = await client.patch(f"/products/{invalid_id}", json=update_data)

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


async def test_update_product_no_fields(client):
    """Test PATCH /products/{id} returns 400 when no fields provided."""
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

    create_response = await client.post("/products/", json=product_data)
    product_id = create_response.json()["_id"]

    # Try to update with no fields
    response = await client.patch(f"/products/{product_id}", json={})

    assert response.status_code == 400
    assert "no fields" in response.json()["detail"].lower()


async def test_update_product_validation_error(client):
    """Test PATCH /products/{id} validates update data."""
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

    create_response = await client.post("/products/", json=product_data)
    product_id = create_response.json()["_id"]

    # Try to update with invalid price (must be > 0)
    update_data = {"price": -5.00}

    response = await client.patch(f"/products/{product_id}", json=update_data)

    assert response.status_code == 422  # Validation error
