# backend/app/__init__.py
"""
BRM Application Package
"""

# Import database functions
from app.database import (
    get_db,
    get_db_session,
    init_database,
    cleanup_database,
    check_database_health,
    Base
)

# Import models (this will register them with Base)
from app import models

__all__ = [
    "Base",
    "get_db",
    "get_db_session", 
    "init_database",
    "cleanup_database",
    "check_database_health"
]