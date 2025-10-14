"""
Pytest configuration and fixtures for integration tests.
"""
import os
import pytest
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

# Import app and settings - ENVIRONMENT is controlled by .env file
from main import app
from database.mongodb import mongodb
from settings import settings


@pytest.fixture
async def client():
    """
    Create an async test client for each test.
    Manually handles MongoDB connection for testing.
    """
    # Create MongoDB connection manually in this loop
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = mongo_client[settings.MONGODB_DB_NAME]

    # Set the global mongodb instance for the app to use
    mongodb.client = mongo_client
    mongodb.database = db

    # Clean database before test
    await db["products"].delete_many({})
    await db["quotes"].delete_many({})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clean database after test
    await db["products"].delete_many({})
    await db["quotes"].delete_many({})

    # Close connection
    mongo_client.close()
    mongodb.client = None
    mongodb.database = None
