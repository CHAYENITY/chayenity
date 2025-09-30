#!/usr/bin/env python
"""
Direct database initialization script.
This creates all tables directly using SQLModel.create_all()
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import SQLModel
from app.database.session import engine
from app.models import *  # Import all models


async def init_db():
    """Initialize database by creating all tables"""
    print("Creating all tables...")
    
    async with engine.begin() as conn:
        # Drop all tables first for a clean slate
        await conn.run_sync(SQLModel.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("✅ Database initialization complete!")
    print("All Hourz tables have been created.")


if __name__ == "__main__":
    asyncio.run(init_db())