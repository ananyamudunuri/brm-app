# backend/app/auth.py
"""
Authentication module for JWT token handling and user authentication
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.database import get_db
from app.models import User, TokenRevocation
from app.utils.security import decode_token
from app.config import settings

logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    """
    Custom JWT Bearer authentication class
    Extracts and validates JWT token from Authorization header
    """
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return credentials.credentials


async def get_current_user(
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    try:
        # Decode and validate token
        payload = decode_token(token, settings.JWT_SECRET_KEY)
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check if token is revoked
        token_jti = payload.get("jti")
        if token_jti:
            revoked = db.query(TokenRevocation).filter(
                TokenRevocation.token_jti == token_jti
            ).first()
            if revoked:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
        
        # Get user from database
        user_id = payload.get("user_id")
        user = db.query(User).filter(
            User.id == user_id, 
            User.is_active == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
        
    except ValueError as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (checks if user is active)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_roles(required_roles: List[str]):
    """
    Dependency factory for role-based access control
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        user_roles = current_user.roles.split(",") if current_user.roles else []
        user_roles = [role.strip() for role in user_roles]
        
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return current_user
    return role_checker


# Shortcut dependencies for common role requirements
require_admin = require_roles(["admin", "super_admin"])
require_manager = require_roles(["admin", "manager"])