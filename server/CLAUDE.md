# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based backend server for CHAYENITY, a travel application focused on Thailand. The application uses PostgreSQL as its database with SQLAlchemy for ORM and SQLModel for data modeling. Authentication is implemented using JWT tokens with both refresh and access tokens.

## Key Technologies

- FastAPI (Python 3.11)
- PostgreSQL with asyncpg driver
- SQLAlchemy 2.0 with async support
- SQLModel for data modeling
- Pydantic for data validation
- JWT for authentication
- Poetry for dependency management
- Alembic for database migrations
- Pytest for testing

## Common Development Commands

### Setup and Installation
```bash
# Install dependencies
poetry install

# Activate virtual environment
.venv\Scripts\activate.bat  # Windows
# or
source .venv/bin/activate   # Linux/Mac

# Configure Poetry to create virtual environment in project
poetry config virtualenvs.in-project true
```

### Database Operations
```bash
# Initialize database
./alembic/init_db.sh

# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head
```

### Running the Application
```bash
# Development mode
fastapi dev

# Production mode
fastapi run
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app
```

### Code Quality
```bash
# Format code
black .

# Lint code
ruff check .

# Fix linting issues automatically
ruff check . --fix
```

## Code Architecture

### Project Structure
```
app/
├── main.py          # Application entry point and configuration
├── api.py           # API router aggregation
├── models.py        # Database models using SQLModel
├── security.py      # Authentication and security utilities
├── database/        # Database configuration and session management
├── configs/         # Application configuration
├── routes/          # API endpoints organized by resource
├── crud/            # Database operations (Create, Read, Update, Delete)
├── schemas/         # Pydantic models for request/response validation
├── tests/           # Test suite
└── utils/           # Utility functions
```

### Key Components

1. **Authentication System**:
   - Dual token system (refresh/access tokens)
   - Multiple login methods (email, phone, citizen ID)
   - PIN-based additional security layer

2. **Database Layer**:
   - Asynchronous database operations
   - SQLModel for data modeling
   - Alembic for migrations
   - CRUD operations separated in dedicated modules

3. **API Structure**:
   - Modular routing in `/routes/`
   - Dependency injection for database sessions
   - Automatic OpenAPI documentation generation

4. **Configuration**:
   - Environment-based configuration using Pydantic Settings
   - `.env` file for local development settings

### Data Models

The main entities are:
- `User`: Core user account with authentication (email, phone, citizen ID)
- `Province`: Thai province information with city tier classification
- `UserTravel`: User travel plans with date ranges

Enums include:
- `CityTierEnum`: MAIN or SECONDARY city classification
- `UserTypeEnum`: TOURIST or OPERATOR user types

## Development Workflow

1. Create feature branches from `main`
2. Implement changes with corresponding tests
3. Run code formatting and linting
4. Ensure all tests pass
5. Create pull requests for review