# backend/app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import logging

from app.database import get_db
from app.models import User, TokenRevocation
from app.config import settings
from app.utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)
security = HTTPBearer()


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    from jose import jwt
    to_encode = data.copy()
    # Use uppercase attribute names from config
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": str(uuid.uuid4())
    })
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    from jose import jwt
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    from jose import JWTError, jwt
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "type"]}
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


@router.post("/login")
async def login(
    response: Response,
    login_data: dict,
    db: Session = Depends(get_db)
):
    """Login user and return JWT tokens"""
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Create tokens
    access_token = create_access_token({"user_id": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(user.id)
    
    # Set refresh token as cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth/refresh"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Get new access token using refresh token"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new tokens
        new_access_token = create_access_token({"user_id": str(user.id), "email": user.email})
        new_refresh_token = create_refresh_token(user.id)
        
        # Update refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/api/auth/refresh"
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Verify current token"""
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "valid": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "roles": user.roles.split(",") if user.roles else []
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user"""
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        token_jti = payload.get("jti")
        
        # Revoke the token
        if token_jti:
            revocation = TokenRevocation(
                token_jti=token_jti,
                user_id=payload.get("user_id"),
                expires_at=datetime.fromtimestamp(payload.get("exp"))
            )
            db.add(revocation)
            db.commit()
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
    
    # Clear refresh token cookie
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    
    return {"message": "Logged out successfully"}