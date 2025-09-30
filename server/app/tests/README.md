# Test Directory Organization

This directory contains different types of tests organized by purpose and scope.

## 📁 Directory Structure

### `app/tests/` - Main Test Suite
- **Unit Tests**: Individual component testing
  - `test_security.py` - Authentication & security tests
  - `test_basic_models.py` - Database model tests
  - `test_models/` - Specific model tests
    - `test_user.py` - User model tests
    - `test_gig.py` - Gig model tests

### `app/tests/test_auth/` - Authentication Tests
- `test_auth.py` - Authentication flow tests
- `test_register.py` - User registration tests

### `app/tests/integration/` - Integration Tests
- `test_buddy_endpoints.py` - **✅ Buddy system API tests (COMPLETE)**
- `test_gig_system.py` - **✅ Gig system API tests (COMPLETE)**
- `test_chat_apis.py` - **✅ Chat system API tests (COMPLETE)**
- `test_user_profile_system.py` - **✅ User profile API tests (COMPLETE)**
- `test_profile_apis.py` - Profile management API tests
- `test_end_to_end_gig_flow.py` - **✅ End-to-end gig workflows (COMPLETE)**
- `test_chat_room_functionality.py` - **✅ Chat room functionality tests (COMPLETE)**
- `test_file_upload_integration.py` - **✅ File upload integration tests (COMPLETE)**

### `app/tests/test_websocket/` - WebSocket Tests
- `test_chat.py` - **✅ Real-time chat WebSocket tests (COMPLETE)**

### `app/tests/dev/` - Development Utilities
- `test_joins.py` - SQLModel join syntax testing
- `test_sqlmodel_columns.py` - SQLAlchemy column access testing

## 🚀 Running Tests

### Run All Tests
```bash
poetry run pytest app/tests/
```

### Run Specific Test Categories
```bash
# Unit tests
poetry run pytest app/tests/test_*.py app/tests/test_models/

# Integration tests (live server tests)
poetry run pytest app/tests/integration/

# Authentication tests
poetry run pytest app/tests/test_auth/

# WebSocket tests
poetry run pytest app/tests/test_websocket/
```

### Run Individual Test Files
```bash
# Run buddy system tests
poetry run python app/tests/integration/test_buddy_endpoints.py

# Run gig system tests  
poetry run python app/tests/integration/test_gig_system.py

# Run chat API tests
poetry run python app/tests/integration/test_chat_apis.py
```

## ✅ Test Status

### **COMPLETE & TESTED** 🎉
- **Buddy System** - All 6 endpoints working with full CRUD operations
- **Gig System** - All 9 endpoints working with geospatial queries
- **Chat System** - All REST APIs and WebSocket communication
- **User Authentication** - Registration, login, JWT tokens
- **User Profiles** - Profile management and location services

### **In Development** 🔧
- **Reviews & Ratings** - Not yet implemented
- **Payment/Transactions** - Mock system pending
- **Image Upload** - File handling system pending

## 📋 Notes

- Integration tests require a running FastAPI server (`poetry run python -m app.main`)
- Some tests create test users and data in the database
- WebSocket tests require proper WebSocket connection handling
- Dev utilities are for debugging SQLModel/SQLAlchemy issues during development