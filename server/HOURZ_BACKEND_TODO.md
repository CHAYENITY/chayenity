# Hourz Backend Development Todo List

## Phase 1: Core Foundation & MVP

### 1. Database Schema & Models ✅ (In Progress)
- [x] **User Model Updates**
  - [x] Remove unused UserTypeEnum 
  - [x] Add location fields (fixed_location as PostGIS Point)
  - [x] Add is_available boolean for Helper status
  - [x] Add profile fields: name, photo_url, contact_info
  - [x] Add reputation_score field
  - [x] Remove marketplace-specific fields (items, reviews, etc.)

- [x] **New Core Models**
  - [x] Create Gig/Request model (title, description, duration, budget, location, status)
  - [x] Create GigStatus enum (PENDING, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED)
  - [x] Create ChatRoom model (gig_id, participants)
  - [x] Create Message model (room_id, sender_id, content, timestamp, image_url)
  - [x] Create BuddyList/Favorites model (user_id, buddy_id)
  - [x] Create Review model (gig_id, reviewer_id, reviewee_id, rating, comment)
  - [x] Create Transaction model (gig_id, amount, status, service_fee)

- [x] **Remove Marketplace Models**
  - [x] Remove Item, Category, ItemImage models
  - [x] Remove marketplace-specific relationships
  - [x] Clean up unused enums (ItemStatus, ItemCondition)

### 2. Database Setup ✅
- [x] ✅ Direct database initialization with SQLModel.create_all()
- [x] ✅ PostGIS extension setup in Docker
- [x] ✅ All Hourz tables created successfully
- [ ] ⏳ Create clean Alembic migrations (optional for production)

### 3. Authentication & User Management ✅
- [x] ✅ JWT authentication (working and tested)
- [x] ✅ Update user registration for dual-role (Helper/Seeker)
- [x] ✅ Password security with bcrypt (tested)
- [ ] 🎯 Add location setting endpoints (NEXT PRIORITY)
- [ ] 🎯 Add availability toggle endpoint (NEXT PRIORITY)
- [ ] 🎯 Update user profile endpoints (NEXT PRIORITY)

### 4. Core API Endpoints - Gigs
- [ ] **Gig Management**
  - [ ] POST /api/gigs - Create new gig (Seeker)
  - [ ] GET /api/gigs - List nearby gigs (geospatial query)
  - [ ] GET /api/gigs/{id} - Get gig details
  - [ ] PUT /api/gigs/{id} - Update gig
  - [ ] DELETE /api/gigs/{id} - Cancel gig
  - [ ] POST /api/gigs/{id}/accept - Helper accepts gig
  - [ ] PUT /api/gigs/{id}/status - Update gig status

- [ ] **Geospatial Queries**
  - [ ] Implement PostGIS distance queries
  - [ ] Add radius-based gig search
  - [ ] Add map bounds-based search
  - [ ] Optimize with spatial indexes

### 5. User Location & Availability
- [ ] **Location APIs**
  - [ ] PUT /api/users/location - Set fixed location (Helper)
  - [ ] PUT /api/users/availability - Toggle is_available
  - [ ] GET /api/users/nearby - Find nearby helpers

## Phase 2: Communication & Advanced Features

### 6. Real-time Chat System ✅
- [x] ✅ **WebSocket Setup**
  - [x] ✅ Install websockets dependencies (fastapi websockets)
  - [x] ✅ Create WebSocket connection manager
  - [x] ✅ Implement room-based chat routing
  - [x] ✅ Add connection authentication (JWT in WebSocket)

- [ ] **Chat APIs**
  - [ ] GET /api/chat/rooms - List user's chat rooms
  - [ ] GET /api/chat/rooms/{id}/messages - Get message history
  - [ ] POST /api/chat/rooms/{id}/messages - Send message (fallback)
  - [ ] WebSocket events: join_room, send_message, receive_message

### 7. Buddy System
- [ ] **Favorites/Buddy APIs**
  - [ ] POST /api/buddies - Add user to buddy list
  - [ ] GET /api/buddies - Get buddy list
  - [ ] DELETE /api/buddies/{id} - Remove buddy
  - [ ] GET /api/buddies/available - Get available buddies

### 8. Image Management
- [ ] **File Upload System**
  - [ ] Set up file upload handling (mock S3/local storage)
  - [ ] POST /api/upload/profile - Upload profile image
  - [ ] POST /api/upload/gig - Upload gig images
  - [ ] Image URL generation and serving

## Phase 3: Reviews & Transactions

### 9. Review System
- [ ] **Review APIs**
  - [ ] POST /api/reviews - Create review after gig completion
  - [ ] GET /api/reviews/user/{id} - Get user reviews
  - [ ] PUT /api/users/{id}/reputation - Update reputation score
  - [ ] Review validation (only after completed gigs)

### 10. Mock Payment System
- [ ] **Transaction APIs**
  - [ ] POST /api/transactions/escrow - Create escrow (mock)
  - [ ] PUT /api/transactions/{id}/release - Release payment
  - [ ] GET /api/transactions/history - Transaction history
  - [ ] Service fee calculation logic

### 11. Testing & Quality ✅ (Foundation Complete)
- [x] ✅ **Unit Tests**
  - [x] ✅ Update existing auth tests
  - [x] ✅ Add comprehensive model tests
  - [x] ✅ Add password security tests
  - [x] ✅ Add PostGIS integration tests
  - [x] ✅ All 8 tests passing
  - [ ] 🎯 Add gig CRUD tests (after API implementation)
  - [ ] 🎯 Add WebSocket chat tests (after chat API)

- [ ] **Integration Tests**
  - [ ] End-to-end gig flow tests
  - [ ] Chat room functionality tests
  - [ ] File upload tests

## Phase 4: DevOps & Optimization

### 12. Database Optimization
- [ ] Add spatial indexes for location queries
- [ ] Add regular indexes on frequently queried fields
- [ ] Optimize chat message queries (pagination)
- [ ] Database performance testing

### 13. API Documentation
- [ ] Update OpenAPI/Swagger documentation
- [ ] Add API usage examples
- [ ] Document WebSocket events
- [ ] Create API testing guide

### 14. Infrastructure & Deployment ✅ (Core Complete)
- [x] ✅ Update Docker Compose for PostGIS
- [x] ✅ Add PostGIS to Docker setup
- [x] ✅ WebSocket infrastructure ready
- [x] ✅ Database initialization scripts
- [ ] 🎯 Production deployment configuration
- [ ] 🎯 Environment variable management

### 15. Security & Validation
- [ ] Add input validation for all new endpoints
- [ ] Implement rate limiting
- [ ] Add CORS configuration for Flutter app
- [ ] Security review of file upload handling

## ✅ COMPLETED FOUNDATION:
1. ✅ Clean up old marketplace models and enums
2. ✅ Update User model for Helper/Seeker functionality  
3. ✅ Create new Gig and Chat models
4. ✅ Set up PostGIS and spatial queries
5. ✅ Set up WebSocket chat system
6. ✅ Database initialization with all tables
7. ✅ Comprehensive test suite (8/8 passing)
8. ✅ Docker environment with PostGIS

## 🎯 IMMEDIATE NEXT PRIORITIES (Ready to Implement):
1. **🚀 Core Gig CRUD APIs** - Foundation for all gig functionality
2. **📍 Geospatial Search APIs** - Location-based gig discovery  
3. **👤 User Profile Management** - Location setting, availability toggle
4. **💬 Chat REST APIs** - Message history, room management
5. **🔄 Create Clean Alembic Migrations** - Production-ready migrations

## Notes
- **PostGIS Setup**: Need to ensure PostGIS extension is available in Docker
- **WebSocket Authentication**: Plan JWT token validation for WebSocket connections
- **File Storage**: Start with local file storage, plan for cloud storage later
- **Testing Strategy**: Update test database to include PostGIS extension
- **Performance**: Consider caching strategies for frequently accessed data

---
**Legend:** ✅ Done | 🔄 In Progress | ⏳ Planned | ❌ Blocked