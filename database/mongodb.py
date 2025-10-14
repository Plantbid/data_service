"""
MongoDB connection setup for the landscape supply platform.

This module provides async MongoDB connection management using Motor.
"""
import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


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
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "landscape_supply")

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
