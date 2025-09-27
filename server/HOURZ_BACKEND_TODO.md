# Hourz Backend Development Todo List

## Phase 1: Core Foundation & MVP

### 1. Database Schema & Models ✅ (In Progress)
- [ ] **User Model Updates**
  - [x] Remove unused UserTypeEnum 
  - [ ] Add location fields (fixed_location as PostGIS Point)
  - [ ] Add is_available boolean for Helper status
  - [ ] Add profile fields: name, photo_url, contact_info
  - [ ] Add reputation_score field
  - [ ] Remove marketplace-specific fields (items, reviews, etc.)

- [ ] **New Core Models**
  - [ ] Create Gig/Request model (title, description, duration, budget, location, status)
  - [ ] Create GigStatus enum (PENDING, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED)
  - [ ] Create ChatRoom model (gig_id, participants)
  - [ ] Create Message model (room_id, sender_id, content, timestamp, image_url)
  - [ ] Create BuddyList/Favorites model (user_id, buddy_id)
  - [ ] Create Review model (gig_id, reviewer_id, reviewee_id, rating, comment)
  - [ ] Create Transaction model (gig_id, amount, status, service_fee)

- [ ] **Remove Marketplace Models**
  - [ ] Remove Item, Category, ItemImage models
  - [ ] Remove marketplace-specific relationships
  - [ ] Clean up unused enums (ItemStatus, ItemCondition)

### 2. Database Migrations
- [ ] Create Alembic migration to drop marketplace tables
- [ ] Create migration for new Hourz schema
- [ ] Add PostGIS extension setup
- [ ] Test migrations up/down

### 3. Authentication & User Management
- [x] JWT authentication (already implemented)
- [ ] Update user registration for dual-role (Helper/Seeker)
- [ ] Add location setting endpoints
- [ ] Add availability toggle endpoint
- [ ] Update user profile endpoints

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

### 6. Real-time Chat System
- [ ] **WebSocket Setup**
  - [ ] Install websockets dependencies (fastapi websockets)
  - [ ] Create WebSocket connection manager
  - [ ] Implement room-based chat routing
  - [ ] Add connection authentication (JWT in WebSocket)

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

### 11. Testing & Quality
- [ ] **Unit Tests**
  - [ ] Update existing auth tests
  - [ ] Add gig CRUD tests
  - [ ] Add geospatial query tests
  - [ ] Add WebSocket chat tests

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

### 14. Infrastructure & Deployment
- [ ] Update Docker Compose for new dependencies
- [ ] Add PostGIS to Docker setup
- [ ] Configure WebSocket support in deployment
- [ ] Environment variable management

### 15. Security & Validation
- [ ] Add input validation for all new endpoints
- [ ] Implement rate limiting
- [ ] Add CORS configuration for Flutter app
- [ ] Security review of file upload handling

## Immediate Next Steps (Priority Order)
1. ✅ Clean up old marketplace models and enums
2. 🔄 Update User model for Helper/Seeker functionality  
3. ⏳ Create new Gig and Chat models
4. ⏳ Set up PostGIS and spatial queries
5. ⏳ Implement core gig CRUD APIs
6. ⏳ Set up WebSocket chat system

## Notes
- **PostGIS Setup**: Need to ensure PostGIS extension is available in Docker
- **WebSocket Authentication**: Plan JWT token validation for WebSocket connections
- **File Storage**: Start with local file storage, plan for cloud storage later
- **Testing Strategy**: Update test database to include PostGIS extension
- **Performance**: Consider caching strategies for frequently accessed data

---
**Legend:** ✅ Done | 🔄 In Progress | ⏳ Planned | ❌ Blocked