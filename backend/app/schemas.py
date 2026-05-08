# backend/app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


# Customer Schemas
class CustomerBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    no_of_employees: Optional[int] = None
    established_year: Optional[int] = None
    status: str = "ACTIVE"

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    no_of_employees: Optional[int] = None
    established_year: Optional[int] = None
    status: Optional[str] = None

class CustomerResponse(CustomerBase):
    customer_id: UUID
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = 1
    contacts: List['ContactResponse'] = []
    
    class Config:
        from_attributes = True


# Contact Schemas
class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    fax: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    is_primary: bool = False
    status: str = "ACTIVE"

class ContactCreate(ContactBase):
    customer_id: UUID

class ContactResponse(ContactBase):
    contact_id: UUID
    customer_id: UUID
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Note Schemas
class NoteBase(BaseModel):
    note_text: str = Field(..., min_length=1)
    note_type: str = "GENERAL"

class NoteCreate(NoteBase):
    customer_id: UUID

class NoteResponse(NoteBase):
    note_id: UUID
    customer_id: UUID
    created_by: str
    created_at: datetime
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    edited_by: Optional[str] = None
    
    class Config:
        from_attributes = True


# Affiliation Schemas
class AffiliationBase(BaseModel):
    relationship_type: str = "AFFILIATE"
    notes: Optional[str] = None
    status: str = "ACTIVE"

class AffiliationCreate(AffiliationBase):
    parent_customer_id: UUID
    affiliate_customer_id: UUID

class AffiliationResponse(AffiliationBase):
    affiliation_id: UUID
    parent_customer_id: UUID
    affiliate_customer_id: UUID
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    roles: str = "user"
    is_active: bool = True

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    roles: str
    is_active: bool
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardResponse(BaseModel):
    total_customers: int
    active_customers: int
    total_contacts: int
    total_notes: int
    total_affiliations: int
    recent_customers: List[dict]
    recent_notes: List[dict]


# Update forward references
CustomerResponse.model_rebuild()