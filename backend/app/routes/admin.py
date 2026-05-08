# backend/app/routes/admin.py
"""
Admin Routes - User Management for administrators
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.models import User
from ..auth import get_current_active_user
from app.utils.security import get_password_hash, verify_password

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


# Schema for user operations
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    roles: str = "user"
    is_active: bool = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    roles: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    roles: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


def check_admin_access(current_user: User):
    """Check if current user has admin access"""
    user_roles = (current_user.roles or "").split(",")
    user_roles = [role.strip() for role in user_roles]
    if "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        check_admin_access(current_user)
        
        query = db.query(User)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.email.ilike(search_term)) |
                (User.username.ilike(search_term)) |
                (User.full_name.ilike(search_term))
            )
        
        # Order by creation date
        query = query.order_by(User.created_at.desc())
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        result = []
        for user in users:
            result.append({
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name or "",
                "roles": user.roles or "user",
                "is_active": user.is_active,
                "created_at": user.created_at
            })
        
        logger.info(f"Admin {current_user.email} retrieved {len(result)} users")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID (admin only)"""
    try:
        check_admin_access(current_user)
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name or "",
            "roles": user.roles or "user",
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    try:
        check_admin_access(current_user)
        
        # Check if user already exists
        existing = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="User with this email or username already exists")
        
        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            roles=user_data.roles,
            is_active=user_data.is_active,
            is_verified=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Admin {current_user.email} created user: {new_user.email}")
        
        return {
            "id": str(new_user.id),
            "email": new_user.email,
            "username": new_user.username,
            "full_name": new_user.full_name or "",
            "roles": new_user.roles or "user",
            "is_active": new_user.is_active,
            "created_at": new_user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)"""
    try:
        check_admin_access(current_user)
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't allow admin to remove their own admin role
        if user.id == current_user.id and user_data.roles and "admin" not in user_data.roles.split(","):
            raise HTTPException(status_code=400, detail="You cannot remove your own admin role")
        
        # Update fields
        if user_data.email:
            # Check if email is taken
            existing = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = user_data.email
        
        if user_data.username:
            # Check if username is taken
            existing = db.query(User).filter(User.username == user_data.username, User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = user_data.username
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.roles is not None:
            user.roles = user_data.roles
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        if user_data.password:
            user.password_hash = get_password_hash(user_data.password)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Admin {current_user.email} updated user: {user.email}")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name or "",
            "roles": user.roles or "user",
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    try:
        check_admin_access(current_user)
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't allow admin to delete themselves
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="You cannot delete your own account")
        
        db.delete(user)
        db.commit()
        
        logger.info(f"Admin {current_user.email} deleted user: {user.email}")
        
        return {"message": f"User {user.email} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))