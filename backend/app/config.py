# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/brm_db")
    
    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # App Settings
    APP_NAME = os.getenv("APP_NAME", "CRM Application")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS = ["*"]
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Security
    BCRYPT_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    
    # GCP Settings
    GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "PROJECT-A")
    GCP_REGION = os.getenv("GCP_REGION", "us-central1")
    USE_SECRET_MANAGER = os.getenv("USE_SECRET_MANAGER", "False").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Backward compatibility (lowercase properties)
    @property
    def app_name(self):
        return self.APP_NAME
    
    @property
    def database_url(self):
        return self.DATABASE_URL
    
    @property
    def debug(self):
        return self.DEBUG
    
    @property
    def environment(self):
        return self.ENVIRONMENT
    
    @property
    def allowed_origins(self):
        return self.ALLOWED_ORIGINS
    
    @property
    def allowed_hosts(self):
        return self.ALLOWED_HOSTS

settings = Settings()


def validate_settings():
    """Validate critical settings"""
    if settings.ENVIRONMENT == "production":
        if not settings.JWT_SECRET_KEY or settings.JWT_SECRET_KEY == "your-secret-key-change-this-in-production":
            raise ValueError("JWT_SECRET_KEY must be set in production!")
        
        if settings.DATABASE_URL is None:
            raise ValueError("DATABASE_URL must be set in production!")


# Run validation on import
if settings.ENVIRONMENT == "production":
    validate_settings()