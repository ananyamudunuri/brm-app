# backend/app/routes/contacts.py
"""
Contacts Routes - Contact management for customers
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.models import Contact, Customer, User
from app.schemas import ContactCreate, ContactResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/crm/contacts", tags=["Contacts"])
logger = logging.getLogger(__name__)


@router.get("")
@router.get("/")
async def get_contacts(
    customer_id: Optional[UUID] = Query(None, description="Filter by customer ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all contacts, optionally filtered by customer"""
    try:
        query = db.query(Contact)
        
        if customer_id:
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


@router.post("")
@router.post("/")
async def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new contact for a customer"""
    try:
        logger.info(f"POST request received to /api/crm/contacts")
        logger.info(f"Contact data: {contact.dict()}")
        
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.customer_id == contact.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # If this contact is marked as primary, unset other primary contacts for this customer
        if contact.is_primary:
            existing_primary = db.query(Contact).filter(
                Contact.customer_id == contact.customer_id,
                Contact.is_primary == True
            ).first()
            if existing_primary:
                existing_primary.is_primary = False
        
        db_contact = Contact(
            customer_id=contact.customer_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            title=contact.title,
            department=contact.department,
            email=contact.email,
            phone=contact.phone,
            mobile=contact.mobile,
            fax=contact.fax,
            address_line1=contact.address_line1,
            address_line2=contact.address_line2,
            city=contact.city,
            state=contact.state,
            postal_code=contact.postal_code,
            country=contact.country,
            notes=contact.notes,
            is_primary=contact.is_primary,
            status=contact.status or "ACTIVE",
            created_by=current_user.email
        )
        
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        
        logger.info(f"Created contact: {db_contact.first_name} {db_contact.last_name}")
        
        return {
            "contact_id": str(db_contact.contact_id),
            "customer_id": str(db_contact.customer_id),
            "first_name": db_contact.first_name,
            "last_name": db_contact.last_name,
            "title": db_contact.title or "",
            "department": db_contact.department or "",
            "email": db_contact.email or "",
            "phone": db_contact.phone or "",
            "mobile": db_contact.mobile or "",
            "fax": db_contact.fax or "",
            "address_line1": db_contact.address_line1 or "",
            "address_line2": db_contact.address_line2 or "",
            "city": db_contact.city or "",
            "state": db_contact.state or "",
            "postal_code": db_contact.postal_code or "",
            "country": db_contact.country or "",
            "notes": db_contact.notes or "",
            "is_primary": db_contact.is_primary or False,
            "status": db_contact.status or "ACTIVE",
            "created_by": db_contact.created_by or "",
            "created_at": db_contact.created_at.isoformat() if db_contact.created_at else None,
            "updated_at": db_contact.updated_at.isoformat() if db_contact.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating contact: {str(e)}"
        )


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify contacts router is working"""
    return {"message": "Contacts router is working", "status": "ok"}


@router.get("/{contact_id}")
async def get_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific contact by ID"""
    try:
        contact = db.query(Contact).filter(Contact.contact_id == contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching contact: {str(e)}"
        )


@router.put("/{contact_id}")
async def update_contact(
    contact_id: UUID,
    contact: ContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a contact"""
    try:
        db_contact = db.query(Contact).filter(Contact.contact_id == contact_id).first()
        if not db_contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        if contact.is_primary:
            existing_primary = db.query(Contact).filter(
                Contact.customer_id == db_contact.customer_id,
                Contact.contact_id != contact_id,
                Contact.is_primary == True
            ).first()
            if existing_primary:
                existing_primary.is_primary = False
        
        db_contact.first_name = contact.first_name
        db_contact.last_name = contact.last_name
        db_contact.title = contact.title
        db_contact.department = contact.department
        db_contact.email = contact.email
        db_contact.phone = contact.phone
        db_contact.mobile = contact.mobile
        db_contact.fax = contact.fax
        db_contact.address_line1 = contact.address_line1
        db_contact.address_line2 = contact.address_line2
        db_contact.city = contact.city
        db_contact.state = contact.state
        db_contact.postal_code = contact.postal_code
        db_contact.country = contact.country
        db_contact.notes = contact.notes
        db_contact.is_primary = contact.is_primary
        db_contact.status = contact.status
        
        db.commit()
        db.refresh(db_contact)
        
        logger.info(f"User {current_user.email} updated contact {contact_id}")
        
        return {
            "contact_id": str(db_contact.contact_id),
            "customer_id": str(db_contact.customer_id),
            "first_name": db_contact.first_name,
            "last_name": db_contact.last_name,
            "title": db_contact.title or "",
            "department": db_contact.department or "",
            "email": db_contact.email or "",
            "phone": db_contact.phone or "",
            "mobile": db_contact.mobile or "",
            "fax": db_contact.fax or "",
            "address_line1": db_contact.address_line1 or "",
            "address_line2": db_contact.address_line2 or "",
            "city": db_contact.city or "",
            "state": db_contact.state or "",
            "postal_code": db_contact.postal_code or "",
            "country": db_contact.country or "",
            "notes": db_contact.notes or "",
            "is_primary": db_contact.is_primary or False,
            "status": db_contact.status or "ACTIVE",
            "created_by": db_contact.created_by or "",
            "created_at": db_contact.created_at.isoformat() if db_contact.created_at else None,
            "updated_at": db_contact.updated_at.isoformat() if db_contact.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating contact: {str(e)}"
        )


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a contact"""
    try:
        db_contact = db.query(Contact).filter(Contact.contact_id == contact_id).first()
        if not db_contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        contact_name = f"{db_contact.first_name} {db_contact.last_name}"
        
        db.delete(db_contact)
        db.commit()
        
        logger.info(f"User {current_user.email} deleted contact: {contact_name}")
        return {"message": f"Contact '{contact_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting contact: {str(e)}"
        )


@router.get("/customer/{customer_id}/primary")
async def get_primary_contact(
    customer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the primary contact for a customer"""
    try:
        contact = db.query(Contact).filter(
            Contact.customer_id == customer_id,
            Contact.is_primary == True,
            Contact.status == "ACTIVE"
        ).first()
        
        if not contact:
            return {"message": "No primary contact found", "contact": None}
        
        return {
            "message": "Primary contact found",
            "contact": {
                "contact_id": str(contact.contact_id),
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
                "phone": contact.phone,
                "title": contact.title
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching primary contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching primary contact: {str(e)}"
        )