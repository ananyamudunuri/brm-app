# backend/app/database.py
"""
Database configuration for PostgreSQL with UUID support
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Global engine and session factory
engine = None
SessionLocal = None


def get_database_url() -> str:
    """
    Get PostgreSQL database URL from settings
    Database: brm_db
    User: postgres
    Password: postgres
    """
    # Check both uppercase and lowercase versions
    if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
        url = settings.DATABASE_URL
    elif hasattr(settings, 'database_url') and settings.database_url:
        url = settings.database_url
    else:
        url = "postgresql://postgres:postgres@localhost:5432/brm_db"
    
    return url


def init_database(skip_admin: bool = False):
    """
    Initialize database connection and create tables
    
    Args:
        skip_admin: If True, skip creating default admin user
    """
    global engine, SessionLocal, Base
    
    try:
        database_url = get_database_url()
        
        # Get debug value (handle both uppercase and lowercase)
        debug_mode = getattr(settings, 'DEBUG', False) or getattr(settings, 'debug', False)
        
        logger.info(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        # Create engine with PostgreSQL optimizations
        engine = create_engine(
            database_url,
            echo=debug_mode,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600
        )
        
        # Create session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        # Enable UUID extension in PostgreSQL using text()
        with engine.connect() as conn:
            # Check if we can connect
            logger.info("Testing database connection...")
            conn.execute(text("SELECT 1"))
            
            # Create UUID extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            conn.commit()
            logger.info("✅ UUID extension enabled")
        
        # Import all models and create tables
        from app import models
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created/verified")
        
        # Create default admin user only if not skipping
        if not skip_admin:
            create_default_admin()
        
        logger.info("✅ Database initialization completed successfully")
        return engine
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        SessionLocal = None
        engine = None
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI endpoints
    """
    if SessionLocal is None:
        raise Exception("Database not initialized. Call init_database() first.")
    
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session for scripts
    Remember to close the session when done!
    """
    if SessionLocal is None:
        raise Exception("Database not initialized. Call init_database() first.")
    
    return SessionLocal()


def create_default_admin():
    """
    Create default admin user if no users exist
    """
    try:
        if SessionLocal is None:
            logger.warning("SessionLocal is None, skipping admin creation")
            return
        
        db = SessionLocal()
        
        from app.models import User
        from app.utils.security import get_password_hash
        
        # Check if users table exists
        inspector = inspect(engine)
        if not inspector.has_table("users"):
            logger.warning("Users table doesn't exist yet, skipping admin creation")
            db.close()
            return
        
        # Check if any users exist
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("Creating default admin user...")
            
            admin_user = User(
                email="admin@example.com",
                username="admin",
                password_hash=get_password_hash("Admin123!"),
                full_name="System Administrator",
                roles="admin",
                is_active=True,
                is_verified=True
            )
            
            db.add(admin_user)
            db.commit()
            
            logger.info("✅ Default admin user created: admin@example.com / Admin123!")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error creating default admin: {str(e)}")


def cleanup_database():
    """
    Cleanup database connections on shutdown
    """
    global engine
    if engine:
        engine.dispose()
        engine = None
        logger.info("✅ Database connections closed")


def check_database_health() -> dict:
    """
    Check database health and return status
    """
    try:
        if SessionLocal is None:
            return {"status": "unhealthy", "connected": False, "error": "Database not initialized"}
        
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "connected": True}
    except Exception as e:
        return {"status": "unhealthy", "connected": False, "error": str(e)}