"""
Tests for MongoDB connection setup.
"""
import pytest
from database.mongodb import get_database, mongodb


def test_get_database_raises_error_when_not_connected():
    """Test that get_database raises RuntimeError when database is not connected."""
    # Store original state
    original_database = mongodb.database

    # Set to None to simulate not connected
    mongodb.database = None

    with pytest.raises(RuntimeError, match="Database connection not established"):
        get_database()

    # Restore original state
    mongodb.database = original_database


def test_mongodb_singleton_exists():
    """Test that mongodb singleton object exists and has expected attributes."""
    assert hasattr(mongodb, 'client')
    assert hasattr(mongodb, 'database')
