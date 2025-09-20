# AI Agent Instructions - CHAYENITY Project

This file provides comprehensive guidance for AI agents working on the CHAYENITY project. Read this file to understand the complete context and requirements.

## Project Context & Vision

CHAYENITY is evolving from a Thai travel application into a **Local Community Marketplace** platform. The project combines travel functionality with community-based commerce features.

### Current Status
- **Backend**: FastAPI-based server with user authentication and travel features
- **Target Evolution**: Local marketplace for buying, selling, and exchanging services between neighbors
- **Geographic Focus**: Initially Thailand-focused, with Hat Yai area for location-based features

## Technology Stack

### Backend (Current Implementation)
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with asyncpg driver + PostGIS extension for geospatial queries
- **ORM**: SQLAlchemy 2.0 with async support
- **Data Modeling**: SQLModel for database models
- **Authentication**: JWT tokens (dual token system: refresh/access)
- **Migration**: Alembic
- **Testing**: Pytest with async support
- **Code Quality**: Black (formatting), Ruff (linting)
- **Dependency Management**: Poetry

### Frontend (Planned Implementation)
- **Framework**: Flutter/Dart
- **State Management**: Provider or Riverpod
- **Backend Services**: Firebase (Auth, Firestore, Storage, FCM, Realtime Database)
- **Local Storage**: SharedPreferences, SQLite (sqflite)
- **Location Services**: geolocator package, Google Maps API
- **Image Handling**: image_picker, cached_network_image
- **Payment**: Mock Stripe integration

## Database Schema Overview

### Core Entities

#### User Management
```sql
User:
- id (UUID, primary key)
- email (unique, indexed)
- hashed_password
- full_name
- profile_image_url
- contact_info (phone/LINE ID)
- address_text, latitude, longitude
- is_verified, reputation_score
- created_at
```

#### Marketplace Core
```sql
Category:
- id (UUID, primary key)
- name (unique, indexed)

Item:
- id (UUID, primary key)
- title, description, price
- condition (NEW, USED_LIKE_NEW, USED_GOOD, USED_FAIR)
- status (AVAILABLE, RESERVED, SOLD)
- latitude, longitude
- category_id, owner_id
- created_at, updated_at

ItemImage:
- id (UUID, primary key)
- image_url
- item_id (foreign key)
```

#### Social Features
```sql
Review:
- id (UUID, primary key)
- rating (1-5), comment
- reviewer_id, reviewee_id, item_id
- created_at

Favorite:
- user_id, item_id (composite primary key)

WantedItem:
- id (UUID, primary key)
- user_id, title, description
- category_id, max_price
- created_at, updated_at
```

#### Communication
```sql
Conversation:
- id (UUID, primary key)
- item_id, user1_id, user2_id
- created_at, updated_at

Message:
- id (UUID, primary key)
- content, image_url
- is_read, is_unsent, timestamp
- conversation_id, sender_id
```

#### System Features
```sql
Notification:
- id (UUID, primary key)
- user_id, title, message
- type (NEW_MESSAGE, ITEM_INTEREST, PRICE_CHANGE, etc.)
- is_read, metadata (JSONB)
- created_at

Report:
- id (UUID, primary key)
- reporter_id, reported_user_id
- reason (SPAM, INAPPROPRIATE, SCAM, etc.)
- description, created_at

Transaction:
- id (UUID, primary key)
- item_id, buyer_id, seller_id
- amount, currency, status
- created_at, updated_at, completed_at
```

### Important Database Considerations
- Use PostGIS extension for geospatial queries
- Create GIST index for location-based searches:
  ```sql
  CREATE INDEX idx_item_location ON item USING GIST (
      ST_MakePoint(longitude, latitude)::geography
  );
  ```
- Separate API layer from models (don't send SQLModel directly to frontend)

## Core Features to Implement

### 1. User Registration & Verification
- Firebase Auth integration
- Location-based verification
- User profiles with contact info and address
- ID verification system (simulated)

### 2. Item Listing Management
- Add items with image upload (camera/gallery)
- Category system for items
- Price, condition, and detailed descriptions
- Item status management (available/reserved/sold)
- Edit and delete listings

### 3. Advanced Search & Filtering
- Keyword search
- Filter by category, price range, distance
- Sort by price, date posted, distance
- Map-based search interface
- Save favorite searches

### 4. In-app Messaging System
- Chat between buyers and sellers
- Image sharing in chat
- Message read status
- Price negotiation through chat
- Chat history management

### 5. Rating & Review System
- 1-5 star ratings after transactions
- Review both buyers and sellers
- Review history and reputation scores
- Report inappropriate users
- User safety features

### 6. Push Notifications
- New message alerts
- Item interest notifications
- New items in favorite categories
- Price change alerts for watched items

### 7. Saved Items & Wishlist
- Save interesting items
- Create wanted item lists
- Track item price changes
- Share wishlists

### 8. Transaction History & Offline Support
- Purchase and sale history
- Transaction statistics
- Offline data access for saved items
- Data sync when back online

## Development Commands

### Backend Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
.venv\Scripts\activate.bat  # Windows
source .venv/bin/activate   # Linux/Mac

# Database operations
./alembic/init_db.sh                                    # Initialize
alembic revision --autogenerate -m "description"       # Create migration
alembic upgrade head                                    # Apply migrations

# Run application
fastapi dev     # Development
fastapi run     # Production

# Testing and quality
pytest                  # Run tests
pytest --cov=app       # With coverage
black .                # Format code
ruff check .           # Lint code
ruff check . --fix     # Fix linting issues
```

### Project Structure
```
app/
├── main.py          # Application entry point
├── api.py           # API router aggregation
├── models.py        # SQLModel database models
├── security.py      # Authentication utilities
├── database/        # Database session management
├── configs/         # Application configuration
├── routes/          # API endpoints by resource
├── crud/            # Database operations (CRUD)
├── schemas/         # Pydantic request/response models
├── tests/           # Test suite
└── utils/           # Utility functions
```

## Authentication System
- **Dual Token System**: Refresh tokens (long-lived) + Access tokens (short-lived)
- **Multiple Login Methods**: Email, phone number, or citizen ID
- **PIN Security**: Additional PIN-based authentication layer
- **JWT Implementation**: Using python-jose with bcrypt for password hashing

## Security Considerations
- Image validation before upload
- Hide sensitive personal information
- User reporting and blocking system
- Safety notifications for transactions
- Secure payment integration (mock Stripe)

## Mock Data Requirements
- Item categories with icons
- Sample items (name, price, images, descriptions)
- Sample users and reviews
- Hat Yai area location coordinates
- Report types (spam, inappropriate, etc.)

## Frontend Development Sessions (Planned)
1. **Project Setup & Dart Basics** - Flutter structure, splash screen, onboarding
2. **Authentication & Basic Widgets** - Firebase Auth, profile setup, navigation
3. **Layout & Advanced Widgets** - Item lists, detail pages, forms, responsive design
4. **State Management** - Provider/Riverpod, CRUD operations, form validation
5. **API Integration & Navigation** - Firebase integration, search, filtering
6. **Storage & Notifications** - Firebase Storage, FCM, local storage, chat system
7. **Final Features** - Reviews, transaction history, security features, optimization

## API Design Principles
- Use Pydantic schemas for request/response validation
- Don't expose SQLModel directly to frontend
- Implement proper error handling and status codes
- Use dependency injection for database sessions
- Follow FastAPI best practices for async operations

## Performance Optimization
- Use PostGIS for efficient geospatial queries
- Implement proper database indexing
- Consider Redis for caching frequently accessed data
- Optimize image storage and delivery
- Implement pagination for large data sets

## Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- Mock external services (Firebase, payment systems)
- Test authentication flows thoroughly
- Include geolocation-based test scenarios

This instruction file should be referenced whenever working on any aspect of the CHAYENITY project to ensure consistency and understanding of the project's scope and requirements.