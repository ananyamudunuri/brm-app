# backend/app/main.py
"""
FastAPI CRM Application with JWT Authentication
Complete CRM system with customers, contacts, notes, and affiliations
"""
# backend/app/main.py
#from app.config import settings
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import Optional

from app.config import settings
from app.database import init_database, get_db
from app.routes import auth, crm, contacts,admin
from app.utils.secrets import secret_manager
from sqlalchemy import text  # Add this import at the top

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    Handles database initialization and secret fetching
    """
    # Startup
    logger.info("🚀 Starting CRM API Server...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    try:
        # Initialize database connection - synchronous call
        init_database()
        logger.info("✅ Database connection established")
        
        # Pre-fetch critical secrets (if in production)
        if settings.environment == "production":
            await secret_manager.get_secret("jwt-secret")
            await secret_manager.get_secret("db-connection-string")
            logger.info("✅ Secrets loaded from Secret Manager")
        else:
            logger.info("ℹ️  Using local configuration for development")
            
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        # Don't crash the app, but log the error
        logger.warning("Continuing with limited functionality...")
    
    logger.info("✅ CRM API Server ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down CRM API Server...")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Complete CRM Application with JWT Authentication\n\n"
                "Features:\n"
                "- User authentication with JWT tokens\n"
                "- Customer management\n"
                "- Contact management\n"
                "- Notes management\n"
                "- Affiliation/partner management\n"
                "- Dashboard analytics",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and token management"
        },
        {
            "name": "CRM",
            "description": "Customer, contact, and note management"
        },
        {
            "name": "Contacts",
            "description": "Contact management for customers"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Trusted Host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Include routers
app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(crm.router, prefix="/api", tags=["CRM"])
app.include_router(contacts.router, prefix="/api", tags=["Contacts"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CRM API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "documentation": "/api/docs" if settings.debug else "Documentation not available in production",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth",
            "crm": "/api/crm",
            "contacts": "/api/crm/contacts"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    """
    health_status = {
        "status": "healthy",
        "service": "crm-api",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown"
        }
    }
    
    # Check database connection
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level="info",
        access_log=True
    )