# backend/app/models.py
"""
Database models for CRM Application
Matches the exact database schema provided
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, JSON, CheckConstraint, UniqueConstraint, BigInteger
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    roles = Column(Text, default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Note: No relationships to Customer because Customer.created_by is a string, not a foreign key
    # Relationships will be handled at the query level
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class TokenRevocation(Base):
    __tablename__ = "token_revocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_jti = Column(String(36), unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    reason = Column(String(255))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<TokenRevocation(id={self.id}, token_jti={self.token_jti})>"


class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(255))
    phone = Column(String(500))
    email = Column(String(255))
    location = Column(Text)
    website = Column(String(255))
    linkedin_url = Column(String(255))
    no_of_employees = Column(Integer)
    established_year = Column(Integer)
    status = Column(String(20), nullable=False, default='ACTIVE')
    created_by = Column(String(255))  # This stores email, not a foreign key
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(Integer, default=1)
    
    # Note: No direct relationship to User because created_by is a string
    # Contacts relationship - one customer has many contacts
    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    notes = relationship("CustomerNote", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name={self.customer_name})>"


class Contact(Base):
    __tablename__ = "contacts"
    
    contact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(100))
    department = Column(String(100))
    
    # Contact Details
    email = Column(String(255))
    phone = Column(String(50))
    mobile = Column(String(50))
    fax = Column(String(50))
    
    # Address Information
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Additional Information
    notes = Column(Text)
    is_primary = Column(Boolean, default=False)
    
    # Status & Tracking
    status = Column(String(20), default='ACTIVE')
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="contacts")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Contact(id={self.contact_id}, name={self.full_name})>"


class CustomerNote(Base):
    __tablename__ = "customer_notes"
    
    note_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    note_text = Column(Text, nullable=False)
    note_type = Column(String(50), default='GENERAL')
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True))
    edited_by = Column(String(255))
    
    # Relationships
    customer = relationship("Customer", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id={self.note_id}, type={self.note_type})>"


class Affiliation(Base):
    __tablename__ = "affiliations"
    
    affiliation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    affiliate_customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(50), default='AFFILIATE')
    notes = Column(Text)
    status = Column(String(20), default='ACTIVE')
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent_customer = relationship("Customer", foreign_keys=[parent_customer_id])
    affiliate_customer = relationship("Customer", foreign_keys=[affiliate_customer_id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint('parent_customer_id != affiliate_customer_id', name='no_self_affiliation'),
        UniqueConstraint('parent_customer_id', 'affiliate_customer_id', 'relationship_type', name='unique_affiliation'),
    )
    
    def __repr__(self):
        return f"<Affiliation(id={self.affiliation_id}, type={self.relationship_type})>"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(20), nullable=False)
    old_data = Column(JSON)
    new_data = Column(JSON)
    changed_by = Column(String(255), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    def __repr__(self):
        return f"<AuditLog(id={self.log_id}, table={self.table_name}, action={self.action})>"