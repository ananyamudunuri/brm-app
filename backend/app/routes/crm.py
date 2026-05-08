# backend/app/routes/crm.py
"""
CRM Routes - Customer, Note, Affiliation Management
Matches the exact database schema provided
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import logging

from app.database import get_db
from app.models import Customer, CustomerNote, Affiliation, Contact, User
from app.schemas import (
    CustomerCreate, CustomerResponse, CustomerUpdate,
    NoteCreate, NoteResponse,
    AffiliationCreate, AffiliationResponse,
    ContactResponse
)
from ..auth import get_current_active_user, require_roles

router = APIRouter(prefix="/crm", tags=["CRM"])
logger = logging.getLogger(__name__)


# ==================== Customer Endpoints ====================

@router.get("/customers")
async def get_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by customer name, email, or industry"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all customers with pagination and filtering"""
    try:
        query = db.query(Customer)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.customer_name.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Customer.industry.ilike(search_term)
                )
            )
        
        # Apply status filter
        if status_filter:
            query = query.filter(Customer.status == status_filter)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Order by creation date
        query = query.order_by(Customer.created_at.desc())
        
        # Apply pagination
        customers = query.offset(skip).limit(limit).all()
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
        current_page = (skip // limit) + 1
        
        # Serialize response
        result = []
        for customer in customers:
            customer_dict = {
                "customer_id": str(customer.customer_id),
                "customer_name": customer.customer_name or "",
                "industry": customer.industry or "",
                "phone": customer.phone or "",
                "email": customer.email or "",
                "location": customer.location or "",
                "website": customer.website or "",
                "linkedin_url": customer.linkedin_url or "",
                "no_of_employees": customer.no_of_employees,
                "established_year": customer.established_year,
                "status": customer.status or "ACTIVE",
                "created_by": customer.created_by or "",
                "created_at": customer.created_at.isoformat() if customer.created_at else None,
                "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
                "version": customer.version or 1,
                "contacts": []
            }
            result.append(customer_dict)
        
        logger.info(f"User {current_user.email} retrieved {len(result)} customers (total: {total_count})")
        
        # Return paginated response with metadata
        return {
            "data": result,
            "pagination": {
                "total": total_count,
                "page": current_page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": current_page < total_pages,
                "has_previous": current_page > 1
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching customers: {str(e)}"
        )


@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific customer by ID"""
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get contacts for this customer
        contacts = db.query(Contact).filter(Contact.customer_id == customer_id).all()
        
        return {
            "customer_id": str(customer.customer_id),
            "customer_name": customer.customer_name or "",
            "industry": customer.industry or "",
            "phone": customer.phone or "",
            "email": customer.email or "",
            "location": customer.location or "",
            "website": customer.website or "",
            "linkedin_url": customer.linkedin_url or "",
            "no_of_employees": customer.no_of_employees,
            "established_year": customer.established_year,
            "status": customer.status or "ACTIVE",
            "created_by": customer.created_by or "",
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
            "version": customer.version or 1,
            "contacts": [
                {
                    "contact_id": str(contact.contact_id),
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "title": contact.title
                }
                for contact in contacts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching customer: {str(e)}"
        )


@router.post("/customers")
async def create_customer(
    customer: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new customer"""
    try:
        # Validate required field
        customer_name = customer.get("customer_name", "").strip()
        if not customer_name:
            raise HTTPException(status_code=400, detail="Customer name is required")
        
        # Check if customer name already exists
        existing = db.query(Customer).filter(Customer.customer_name == customer_name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Customer name already exists")
        
        # Create new customer
        db_customer = Customer(
            customer_name=customer_name,
            industry=customer.get("industry"),
            phone=customer.get("phone"),
            email=customer.get("email"),
            location=customer.get("location"),
            website=customer.get("website"),
            linkedin_url=customer.get("linkedin_url"),
            no_of_employees=customer.get("no_of_employees"),
            established_year=customer.get("established_year"),
            status=customer.get("status", "ACTIVE"),
            created_by=current_user.email,
            version=1
        )
        
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        
        logger.info(f"Customer created successfully: {db_customer.customer_name} (ID: {db_customer.customer_id})")
        
        return {
            "success": True,
            "message": "Customer created successfully",
            "customer": {
                "customer_id": str(db_customer.customer_id),
                "customer_name": db_customer.customer_name,
                "industry": db_customer.industry,
                "email": db_customer.email,
                "phone": db_customer.phone,
                "status": db_customer.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating customer: {str(e)}"
        )


@router.put("/customers/{customer_id}")
async def update_customer(
    customer_id: UUID,
    customer: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a customer"""
    try:
        db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Check if customer name is being changed and if it conflicts
        new_name = customer.get("customer_name")
        if new_name and new_name != db_customer.customer_name:
            existing = db.query(Customer).filter(Customer.customer_name == new_name).first()
            if existing:
                raise HTTPException(status_code=400, detail="Customer name already exists")
            db_customer.customer_name = new_name
        
        # Update fields only if provided
        if "industry" in customer:
            db_customer.industry = customer["industry"]
        if "phone" in customer:
            db_customer.phone = customer["phone"]
        if "email" in customer:
            db_customer.email = customer["email"]
        if "location" in customer:
            db_customer.location = customer["location"]
        if "website" in customer:
            db_customer.website = customer["website"]
        if "linkedin_url" in customer:
            db_customer.linkedin_url = customer["linkedin_url"]
        if "no_of_employees" in customer:
            db_customer.no_of_employees = customer["no_of_employees"]
        if "established_year" in customer:
            db_customer.established_year = customer["established_year"]
        if "status" in customer:
            db_customer.status = customer["status"]
        
        # Increment version for optimistic locking
        db_customer.version += 1
        
        db.commit()
        db.refresh(db_customer)
        
        return {
            "success": True,
            "message": "Customer updated successfully",
            "customer": {
                "customer_id": str(db_customer.customer_id),
                "customer_name": db_customer.customer_name,
                "industry": db_customer.industry,
                "email": db_customer.email,
                "phone": db_customer.phone,
                "status": db_customer.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating customer: {str(e)}"
        )


@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a customer (hard delete - cascade will remove affiliations and notes)"""
    try:
        db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer_name = db_customer.customer_name
        db.delete(db_customer)
        db.commit()
        
        logger.info(f"Customer deleted: {customer_name} (ID: {customer_id}) by {current_user.email}")
        
        return {"message": f"Customer '{customer_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting customer: {str(e)}"
        )


# ==================== Customer Notes Endpoints ====================

@router.get("/customers/{customer_id}/notes")
async def get_customer_notes(
    customer_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all notes for a specific customer"""
    try:
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        notes = db.query(CustomerNote).filter(
            CustomerNote.customer_id == customer_id
        ).order_by(CustomerNote.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for note in notes:
            note_dict = {
                "note_id": str(note.note_id),
                "note_text": note.note_text,
                "note_type": note.note_type,
                "created_by": note.created_by,
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "is_edited": note.is_edited,
                "edited_at": note.edited_at.isoformat() if note.edited_at else None,
                "edited_by": note.edited_by
            }
            result.append(note_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer notes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/customers/{customer_id}/notes")
async def create_customer_note(
    customer_id: UUID,
    note_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new note for a customer"""
    try:
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        note_text = note_data.get("note_text", "").strip()
        if not note_text:
            raise HTTPException(status_code=400, detail="Note text is required")
        
        db_note = CustomerNote(
            customer_id=customer_id,
            note_text=note_text,
            note_type=note_data.get("note_type", "GENERAL"),
            created_by=current_user.email
        )
        
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        
        return {
            "note_id": str(db_note.note_id),
            "note_text": db_note.note_text,
            "note_type": db_note.note_type,
            "created_by": db_note.created_by,
            "created_at": db_note.created_at.isoformat() if db_note.created_at else None,
            "message": "Note added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating note: {str(e)}"
        )


@router.put("/notes/{note_id}")
async def update_customer_note(
    note_id: UUID,
    note_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing note (creates edit trail)"""
    try:
        db_note = db.query(CustomerNote).filter(CustomerNote.note_id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Update note
        db_note.note_text = note_data.get("note_text", db_note.note_text)
        db_note.note_type = note_data.get("note_type", db_note.note_type)
        db_note.is_edited = True
        db_note.edited_at = datetime.utcnow()
        db_note.edited_by = current_user.email
        
        db.commit()
        db.refresh(db_note)
        
        return {
            "note_id": str(db_note.note_id),
            "note_text": db_note.note_text,
            "note_type": db_note.note_type,
            "is_edited": db_note.is_edited,
            "edited_at": db_note.edited_at.isoformat() if db_note.edited_at else None,
            "edited_by": db_note.edited_by,
            "message": "Note updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating note: {str(e)}"
        )


@router.delete("/notes/{note_id}")
async def delete_customer_note(
    note_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a note"""
    try:
        db_note = db.query(CustomerNote).filter(CustomerNote.note_id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        db.delete(db_note)
        db.commit()
        
        return {"message": "Note deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting note: {str(e)}"
        )


# ==================== Affiliations Endpoints ====================

@router.get("/affiliations")
async def get_affiliations(
    parent_customer_id: Optional[UUID] = Query(None, description="Filter by parent customer"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all affiliations"""
    try:
        query = db.query(Affiliation)
        
        if parent_customer_id:
            query = query.filter(Affiliation.parent_customer_id == parent_customer_id)
        
        # Also get inverse affiliations
        query = query.order_by(Affiliation.created_at.desc())
        affiliations = query.offset(skip).limit(limit).all()
        
        result = []
        for aff in affiliations:
            aff_dict = {
                "affiliation_id": str(aff.affiliation_id),
                "parent_customer_id": str(aff.parent_customer_id),
                "affiliate_customer_id": str(aff.affiliate_customer_id),
                "relationship_type": aff.relationship_type,
                "notes": aff.notes,
                "status": aff.status,
                "created_by": aff.created_by,
                "created_at": aff.created_at.isoformat() if aff.created_at else None,
                "updated_at": aff.updated_at.isoformat() if aff.updated_at else None
            }
            result.append(aff_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching affiliations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching affiliations: {str(e)}"
        )


@router.post("/affiliations")
async def create_affiliation(
    affiliation: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new affiliation between customers"""
    try:
        parent_id = affiliation.get("parent_customer_id")
        affiliate_id = affiliation.get("affiliate_customer_id")
        
        if not parent_id or not affiliate_id:
            raise HTTPException(status_code=400, detail="Both parent and affiliate customer IDs are required")
        
        if parent_id == affiliate_id:
            raise HTTPException(status_code=400, detail="Cannot create self affiliation")
        
        # Verify both customers exist
        parent = db.query(Customer).filter(Customer.customer_id == parent_id).first()
        affiliate = db.query(Customer).filter(Customer.customer_id == affiliate_id).first()
        
        if not parent or not affiliate:
            raise HTTPException(status_code=404, detail="One or both customers not found")
        
        # Check if affiliation already exists
        existing = db.query(Affiliation).filter(
            Affiliation.parent_customer_id == parent_id,
            Affiliation.affiliate_customer_id == affiliate_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Affiliation already exists")
        
        db_affiliation = Affiliation(
            parent_customer_id=parent_id,
            affiliate_customer_id=affiliate_id,
            relationship_type=affiliation.get("relationship_type", "AFFILIATE"),
            notes=affiliation.get("notes"),
            status=affiliation.get("status", "ACTIVE"),
            created_by=current_user.email
        )
        
        db.add(db_affiliation)
        db.commit()
        db.refresh(db_affiliation)
        
        return {
            "affiliation_id": str(db_affiliation.affiliation_id),
            "message": "Affiliation created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating affiliation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating affiliation: {str(e)}"
        )


@router.delete("/affiliations/{affiliation_id}")
async def delete_affiliation(
    affiliation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an affiliation"""
    try:
        db_affiliation = db.query(Affiliation).filter(Affiliation.affiliation_id == affiliation_id).first()
        if not db_affiliation:
            raise HTTPException(status_code=404, detail="Affiliation not found")
        
        db.delete(db_affiliation)
        db.commit()
        
        return {"message": "Affiliation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting affiliation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting affiliation: {str(e)}"
        )


# ==================== Dashboard Endpoint ====================

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        total_customers = db.query(Customer).count()
        active_customers = db.query(Customer).filter(Customer.status == "ACTIVE").count()
        total_contacts = db.query(Contact).count()
        total_notes = db.query(CustomerNote).count()
        total_affiliations = db.query(Affiliation).filter(Affiliation.status == "ACTIVE").count()
        
        recent_customers = db.query(Customer).order_by(Customer.created_at.desc()).limit(5).all()
        recent_notes = db.query(CustomerNote).order_by(CustomerNote.created_at.desc()).limit(5).all()
        
        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "total_contacts": total_contacts,
            "total_notes": total_notes,
            "total_affiliations": total_affiliations,
            "recent_customers": [
                {
                    "customer_id": str(c.customer_id),
                    "customer_name": c.customer_name or "",
                    "email": c.email or "",
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in recent_customers
            ],
            "recent_notes": [
                {
                    "note_id": str(n.note_id),
                    "note_text": n.note_text[:100] + "..." if len(n.note_text) > 100 else n.note_text,
                    "note_type": n.note_type,
                    "created_at": n.created_at.isoformat() if n.created_at else None
                }
                for n in recent_notes
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )


# ==================== Admin Endpoints ====================

@router.get("/admin/users")
async def get_admin_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search by email or username"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        # Check if user is admin
        user_roles = (current_user.roles or "").split(",")
        user_roles = [role.strip() for role in user_roles]
        
        if "admin" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Admin access required. Your roles: {user_roles}"
            )
        
        query = db.query(User)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.username.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )
        
        # Order by creation date
        query = query.order_by(User.created_at.desc())
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        result = []
        for user in users:
            user_dict = {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name or "",
                "roles": user.roles or "user",
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            result.append(user_dict)
        
        logger.info(f"Admin {current_user.email} retrieved {len(result)} users")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


# ==================== Contacts Endpoints ====================

@router.get("/contacts")
async def get_contacts(
    customer_id: Optional[UUID] = Query(None, description="Filter by customer ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get contacts for a customer"""
    try:
        query = db.query(Contact)
        
        if customer_id:
            # Verify customer exists
            customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            query = query.filter(Contact.customer_id == customer_id)
        
        contacts = query.order_by(Contact.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for contact in contacts:
            contact_dict = {
                "contact_id": str(contact.contact_id),
                "customer_id": str(contact.customer_id),
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "title": contact.title or "",
                "department": contact.department or "",
                "email": contact.email or "",
                "phone": contact.phone or "",
                "mobile": contact.mobile or "",
                "fax": contact.fax or "",
                "address_line1": contact.address_line1 or "",
                "address_line2": contact.address_line2 or "",
                "city": contact.city or "",
                "state": contact.state or "",
                "postal_code": contact.postal_code or "",
                "country": contact.country or "",
                "notes": contact.notes or "",
                "is_primary": contact.is_primary or False,
                "status": contact.status or "ACTIVE",
                "created_by": contact.created_by or "",
                "created_at": contact.created_at.isoformat() if contact.created_at else None,
                "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
            }
            result.append(contact_dict)
        
        logger.info(f"User {current_user.email} retrieved {len(result)} contacts")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching contacts: {str(e)}"
        )