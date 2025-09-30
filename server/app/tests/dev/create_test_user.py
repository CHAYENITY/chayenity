#!/usr/bin/env python
"""
Create a test user for testing the chat APIs
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.database.session import engine
from app.models import User
from app.security import get_password_hash
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession


async def create_test_user():
    """Create a test user for API testing"""
    
    # Test user data
    test_email = "chattest@example.com"  # Use different email for chat testing
    test_password = "testpass123"
    test_full_name = "Chat Test User"
    
    print(f"Creating test user: {test_email}")
    
    # Create async session
    from app.database.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        # Check if user already exists
        stmt = select(User).where(User.email == test_email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            print(f"✅ Test user {test_email} already exists!")
            return
        
        # Create new test user
        password_hash = get_password_hash(test_password)
        
        test_user = User(
            id=uuid4(),
            email=test_email,
            hashed_password=password_hash,
            full_name=test_full_name,
            contact_info="123-456-7890",
            address_text="123 Test Street, Test City",
            is_verified=True,
            reputation_score=5.0,
            created_at=datetime.now(),  # Remove timezone
            updated_at=datetime.now()   # Remove timezone
        )
        
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        
        print(f"✅ Test user created successfully!")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Full Name: {test_full_name}")
        print(f"   ID: {test_user.id}")


if __name__ == "__main__":
    asyncio.run(create_test_user())