# backend/seed_data.py
#!/usr/bin/env python
"""
Seed database with initial data for CRM application
PostgreSQL only - Database: brm_db
"""

import sys
import os
from datetime import datetime
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["ENVIRONMENT"] = "development"

from app.database import init_database, get_db_session
from app.models import User, Customer, Contact, CustomerNote, Affiliation
from app.utils.security import get_password_hash
from sqlalchemy import text


# Sample Customers (matching your exact schema)
SAMPLE_CUSTOMERS = [
    {
        "customer_name": "TechCorp Solutions",
        "email": "contact@techcorp.com",
        "phone": "+1-555-0101",
        "industry": "Technology",
        "location": "123 Tech Street, San Francisco, CA 94105",
        "website": "https://techcorp.com",
        "linkedin_url": "https://linkedin.com/company/techcorp",
        "no_of_employees": 250,
        "established_year": 2015,
        "status": "ACTIVE"
    },
    {
        "customer_name": "Global Innovations",
        "email": "info@globalinnovations.com",
        "phone": "+1-555-0102",
        "industry": "Manufacturing",
        "location": "456 Industry Road, Chicago, IL 60601",
        "website": "https://globalinnovations.com",
        "linkedin_url": "https://linkedin.com/company/globalinnovations",
        "no_of_employees": 500,
        "established_year": 2008,
        "status": "ACTIVE"
    },
    {
        "customer_name": "Smart Systems Ltd",
        "email": "sales@smartsystems.com",
        "phone": "+1-555-0103",
        "industry": "Software",
        "location": "789 Digital Avenue, Austin, TX 78701",
        "website": "https://smartsystems.com",
        "linkedin_url": "https://linkedin.com/company/smartsystems",
        "no_of_employees": 120,
        "established_year": 2018,
        "status": "ACTIVE"
    },
    {
        "customer_name": "Premier Consulting Group",
        "email": "hello@premierconsulting.com",
        "phone": "+1-555-0104",
        "industry": "Consulting",
        "location": "321 Business Park, New York, NY 10001",
        "website": "https://premierconsulting.com",
        "linkedin_url": "https://linkedin.com/company/premierconsulting",
        "no_of_employees": 80,
        "established_year": 2012,
        "status": "ACTIVE"
    },
    {
        "customer_name": "DataFlow Analytics",
        "email": "info@dataflow.com",
        "phone": "+1-555-0105",
        "industry": "Analytics",
        "location": "555 Data Drive, Seattle, WA 98101",
        "website": "https://dataflow.com",
        "linkedin_url": "https://linkedin.com/company/dataflow",
        "no_of_employees": 45,
        "established_year": 2020,
        "status": "INACTIVE"
    }
]

# Sample Contacts
SAMPLE_CONTACTS = [
    {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@techcorp.com",
        "phone": "+1-555-1001",
        "mobile": "+1-555-2001",
        "title": "CEO",
        "department": "Executive",
        "is_primary": True,
        "notes": "Primary contact, decision maker"
    },
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@techcorp.com",
        "phone": "+1-555-1002",
        "title": "CTO",
        "department": "Technology",
        "is_primary": False,
        "notes": "Technical decision maker"
    },
    {
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael.brown@globalinnovations.com",
        "phone": "+1-555-1003",
        "mobile": "+1-555-2003",
        "title": "Director of Sales",
        "department": "Sales",
        "is_primary": True,
        "notes": "Sales director"
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily.davis@smartsystems.com",
        "phone": "+1-555-1004",
        "title": "Product Manager",
        "department": "Product",
        "is_primary": True,
        "notes": "Product manager"
    },
    {
        "first_name": "David",
        "last_name": "Wilson",
        "email": "david.wilson@premierconsulting.com",
        "phone": "+1-555-1005",
        "mobile": "+1-555-2005",
        "title": "Managing Partner",
        "department": "Executive",
        "is_primary": True,
        "notes": "Managing partner"
    }
]

# Sample Notes
SAMPLE_NOTES = [
    {
        "note_text": "Had a great introductory meeting. Discussed potential collaboration opportunities.",
        "note_type": "MEETING"
    },
    {
        "note_text": "Conducted product demo. Client showed strong interest in enterprise features.",
        "note_type": "CALL"
    },
    {
        "note_text": "Need to follow up on pricing discussion and send proposal by end of week.",
        "note_type": "FOLLOW_UP"
    },
    {
        "note_text": "Gathered technical requirements. Need to schedule another call with engineering team.",
        "note_type": "IMPORTANT"
    },
    {
        "note_text": "Discussed contract terms. Client requested adjustments to payment schedule.",
        "note_type": "MEETING"
    }
]

# Sample Affiliations
SAMPLE_AFFILIATIONS = [
    {
        "relationship_type": "PARTNER",
        "notes": "Strategic technology partner"
    },
    {
        "relationship_type": "VENDOR",
        "notes": "Primary software vendor"
    },
    {
        "relationship_type": "SUBSIDIARY",
        "notes": "Wholly owned subsidiary"
    }
]


def seed_database():
    """Seed the database with initial data"""
    print("🌱 Starting database seeding...")
    print("📦 Database: PostgreSQL (brm_db)")
    
    try:
        # Initialize database tables (skip admin creation)
        print("📦 Creating database tables...")
        init_database(skip_admin=True)
        
        # Now get a session
        print("📦 Getting database session...")
        db = get_db_session()
        
        # Check if data already exists
        user_count = db.query(User).count()
        if user_count > 0:
            print(f"⚠️  Database already has {user_count} users. Use --force to override.")
            db.close()
            return
        
        # Create users
        print("📝 Creating users...")
        admin = User(
            email="admin@example.com",
            username="admin",
            password_hash=get_password_hash("Admin123!"),
            full_name="System Administrator",
            roles="admin",
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        
        regular_user = User(
            email="user@example.com",
            username="user",
            password_hash=get_password_hash("User123!"),
            full_name="Regular User",
            roles="user",
            is_active=True,
            is_verified=True
        )
        db.add(regular_user)
        db.commit()
        print("✅ Created 2 users")
        
        # Create customers
        print("📝 Creating customers...")
        customers = []
        for data in SAMPLE_CUSTOMERS:
            customer = Customer(
                **data,
                created_by=admin.email
            )
            db.add(customer)
            customers.append(customer)
        db.commit()
        print(f"✅ Created {len(customers)} customers")
        
        # Create contacts
        print("📝 Creating contacts...")
        contacts = []
        for i, data in enumerate(SAMPLE_CONTACTS):
            contact = Contact(
                **data,
                customer_id=customers[i % len(customers)].customer_id,
                created_by=admin.email
            )
            db.add(contact)
            contacts.append(contact)
        db.commit()
        print(f"✅ Created {len(contacts)} contacts")
        
        # Create notes
        print("📝 Creating notes...")
        for i, data in enumerate(SAMPLE_NOTES):
            customer = customers[i % len(customers)]
            note = CustomerNote(
                **data,
                customer_id=customer.customer_id,
                created_by=admin.email
            )
            db.add(note)
        db.commit()
        print(f"✅ Created {len(SAMPLE_NOTES)} notes")
        
        # Create affiliations
        print("📝 Creating affiliations...")
        for i, data in enumerate(SAMPLE_AFFILIATIONS):
            if i + 1 < len(customers):
                affiliation = Affiliation(
                    parent_customer_id=customers[i].customer_id,
                    affiliate_customer_id=customers[i + 1].customer_id,
                    **data,
                    created_by=admin.email
                )
                db.add(affiliation)
        db.commit()
        print(f"✅ Created {len(SAMPLE_AFFILIATIONS)} affiliations")
        
        # Summary
        print("\n" + "="*50)
        print("🎉 DATABASE SEEDING COMPLETED!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"   Users: {db.query(User).count()}")
        print(f"   Customers: {db.query(Customer).count()}")
        print(f"   Contacts: {db.query(Contact).count()}")
        print(f"   Notes: {db.query(CustomerNote).count()}")
        print(f"   Affiliations: {db.query(Affiliation).count()}")
        
        print("\n🔑 Login Credentials:")
        print("   Admin: admin@example.com / Admin123!")
        print("   User: user@example.com / User123!")
        
        print("\n📧 Sample Customers:")
        for customer in db.query(Customer).limit(5):
            print(f"   - {customer.customer_name} ({customer.email})")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def force_seed():
    """Force seed - clear existing data first"""
    print("⚠️  WARNING: This will clear ALL existing data in the database!")
    response = input("Type 'YES' to continue: ")
    
    if response != "YES":
        print("❌ Seeding cancelled.")
        return
    
    try:
        # Initialize database
        print("📦 Initializing database...")
        init_database(skip_admin=True)
        
        print("📦 Getting database session...")
        db = get_db_session()
        
        # Delete all data in reverse order of dependencies
        print("🗑️  Clearing all existing data...")
        db.execute(text("TRUNCATE TABLE affiliations CASCADE"))
        db.execute(text("TRUNCATE TABLE customer_notes CASCADE"))
        db.execute(text("TRUNCATE TABLE contacts CASCADE"))
        db.execute(text("TRUNCATE TABLE customers CASCADE"))
        db.execute(text("TRUNCATE TABLE users CASCADE"))
        db.commit()
        print("✅ Existing data cleared")
        
        db.close()
        
        # Now seed fresh data
        seed_database()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    if "--force" in sys.argv:
        force_seed()
    else:
        seed_database()