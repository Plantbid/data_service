"""
MongoDB connection setup for the landscape supply platform.

This module provides async MongoDB connection management using Motor.
"""
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from settings import settings


class MongoDB:
    """MongoDB connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongodb() -> None:
    """
    Establish connection to MongoDB.
    Called on application startup.
    """
    mongodb_url = settings.MONGODB_URL
    db_name = settings.MONGODB_DB_NAME

    if not mongodb_url or not db_name:
        raise ValueError("MONGODB_URL and MONGODB_DB_NAME must be configured in settings")

    print(f"Connecting to MongoDB at {mongodb_url}, database: {db_name}")

    mongodb.client = AsyncIOMotorClient(mongodb_url)
    mongodb.database = mongodb.client[db_name]

    # Test the connection
    try:
        await mongodb.client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb_connection() -> None:
    """
    Close MongoDB connection.
    Called on application shutdown.
    """
    if mongodb.client:
        mongodb.client.close()
        print("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database instance.

    Returns:
        AsyncIOMotorDatabase: The database instance

    Raises:
        RuntimeError: If database connection is not established
    """
    if mongodb.database is None:
        raise RuntimeError(
            "Database connection not established. "
            "Make sure to call connect_to_mongodb() on startup."
        )
    return mongodb.database
