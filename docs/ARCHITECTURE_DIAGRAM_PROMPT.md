# System Architecture Diagram Generation Prompt

Use this prompt with AI diagram generation tools (like Mermaid, PlantUML, or visual diagram generators):

---

## 📋 Prompt for AI Diagram Generator

```
Create a comprehensive System Architecture Diagram for "Hourz" - a local helper marketplace platform connecting Seekers who need help with Helpers who provide hourly services.

### System Overview:
Hourz is a full-stack mobile application with backend API, real-time communication, and geospatial features.

### Technology Stack:

**Frontend/Mobile:**
- Flutter (Dart) mobile application
- Cross-platform (iOS, Android, Web, Desktop)
- State Management: flutter_riverpod
- HTTP Client: Dio
- Routing: go_router
- Environment: flutter_dotenv

**Backend:**
- FastAPI (Python 3.11) REST API
- SQLModel ORM with SQLAlchemy
- PostgreSQL database with PostGIS extension (geospatial data)
- WebSocket support for real-time chat
- JWT authentication (access + refresh tokens)
- Poetry for dependency management

**DevOps & Infrastructure:**
- Docker containers for deployment
- Jenkins CI/CD pipeline
- SonarQube for code quality analysis
- pnpm for project-wide package management
- Git workflow with feature branches

### Core Components to Include:

#### 1. Client Layer (Mobile Apps)
- Flutter Mobile Application
  - iOS App
  - Android App
  - Web App (optional)
- Features:
  - User registration/authentication
  - Profile management
  - Gig browsing and creation
  - Real-time chat
  - File upload (profile images, gig images)
  - Geolocation services
  - Payment transactions
  - Review/rating system
  - Buddy list management

#### 2. API Gateway & Backend Services
- FastAPI Application Server (Port 8000)
- API Endpoints:
  - `/api/auth/*` - Authentication & authorization
  - `/api/users/*` - User profile management
  - `/api/gigs/*` - Gig CRUD operations
  - `/api/files/*` - File upload/serving system
  - `/api/chat/*` - Chat message operations
  - `/api/transactions/*` - Payment transactions
  - `/api/reviews/*` - Review/rating system
  - `/api/buddies/*` - Buddy list management
  - `/ws/*` - WebSocket connections for real-time chat

#### 3. Authentication & Security
- Two-step registration flow:
  - Step 1: Email + password registration
  - Step 2: Complete profile setup
- JWT Token System:
  - Access tokens (short-lived)
  - Refresh tokens (long-lived)
  - Token rotation with JTI tracking
- Password hashing (bcrypt)
- CORS middleware

#### 4. Database Layer
- PostgreSQL with PostGIS extension
- Main Tables:
  - `user` - User accounts with profile data
  - `address` - User addresses with GPS coordinates (POINT geometry)
  - `gig` - Service requests/offers
  - `chat` - Chat conversations
  - `chatparticipant` - Chat participants
  - `message` - Chat messages
  - `transaction` - Payment records
  - `review` - User reviews/ratings
  - `buddylist` - User connections
  - `uploadedfile` - File metadata
- Database Features:
  - Geospatial indexing (PostGIS)
  - UUID primary keys
  - Relationships with foreign keys
  - Timestamps (created_at, updated_at)

#### 5. File Storage System
- Local container storage with persistent Docker volumes
- Categorized uploads:
  - `uploads/profile/` - User profile images
  - `uploads/gig/` - Gig-related images
  - `uploads/general/` - General purpose files
- Static file serving endpoint: `/api/files/serve/{category}/{filename}`
- File upload validation (type, size)
- Metadata tracking in database

#### 6. Real-time Communication
- WebSocket connections for chat
- Message types: text, image, system
- Real-time message delivery
- Chat room management
- Online status tracking

#### 7. External Integrations & Services
- Geolocation services (GPS coordinates)
- Payment gateway (future integration)
- Push notifications (future integration)
- Email service (future integration)

#### 8. CI/CD Pipeline
- Jenkins Pipeline:
  - Code checkout from GitHub
  - Python virtual environment setup
  - Poetry dependency installation
  - PostgreSQL test database container
  - pytest test execution with coverage
  - SonarQube code quality analysis
  - Docker image build
  - Container deployment (commented/optional)
  - Docker registry push (commented/optional)

#### 9. Monitoring & Health Checks
- `/health` endpoint for service health
- Database connectivity checks
- Logging system
- Error tracking

### Data Flow Examples to Visualize:

**User Registration Flow:**
1. Mobile app → POST `/api/auth/register` (email, password)
2. Backend validates → Creates user with is_profile_complete=false
3. Returns user data + JWT tokens
4. Mobile app → PUT `/api/auth/profile-setup` (complete profile)
5. Backend updates user → Sets is_profile_complete=true
6. User can now access full platform

**Gig Creation & Matching Flow:**
1. Seeker creates gig → POST `/api/gigs` (title, description, location, hourly_rate)
2. Backend stores gig with geospatial data
3. Helpers browse gigs → GET `/api/gigs` (with location-based filtering)
4. Helper accepts gig → PUT `/api/gigs/{id}/accept`
5. Real-time chat established via WebSocket
6. Transaction created after completion

**File Upload Flow:**
1. User uploads profile image → POST `/api/files/upload/profile`
2. Backend validates file type and size
3. Generates UUID filename
4. Saves to `uploads/profile/` directory
5. Creates UploadedFile database record
6. Returns file URL: `/api/files/serve/profile/{uuid}.jpg`
7. Mobile app displays image from URL

**Real-time Chat Flow:**
1. Users connect to WebSocket → WS `/ws/{chat_id}`
2. Backend manages connections in memory
3. User sends message → Backend broadcasts to participants
4. Message persisted to database
5. Offline messages delivered on reconnection

### Diagram Requirements:

**Visual Elements to Include:**
- Clear separation of layers (Client, API, Database, External)
- Arrows showing data flow direction
- Protocol labels (HTTP/HTTPS, WebSocket, TCP/IP)
- Port numbers where relevant
- Security boundaries (authentication points)
- Data storage locations (database, file system)
- Asynchronous communication paths (WebSocket)
- Third-party integrations (labeled as external)

**Color Coding Suggestions:**
- Blue: Client/Frontend components
- Green: Backend API services
- Orange: Database and storage
- Purple: Real-time communication (WebSocket)
- Red: Security/authentication components
- Gray: External services and infrastructure

**Diagram Style:**
- Use modern cloud architecture style
- Include icons for technologies (Flutter, FastAPI, PostgreSQL, Docker)
- Show both synchronous (REST API) and asynchronous (WebSocket) communication
- Indicate data persistence points
- Show CI/CD pipeline as separate flow
- Use grouping/containers for logical separation

**Additional Context:**
- System supports both Helper and Seeker roles (single user table)
- Designed for horizontal scalability
- File serving can be migrated to CDN later
- Database uses geospatial queries for location-based matching
- Two-step registration improves UX and data quality
- JWT tokens support secure authentication with refresh mechanism

Generate a professional, clear, and comprehensive architecture diagram that would be suitable for:
1. Developer onboarding documentation
2. Technical presentations
3. System design discussions
4. Infrastructure planning
```

---

## 🎨 Recommended AI Tools for Generation:

### Option 1: Mermaid Diagram
Ask the AI to generate a Mermaid diagram code that you can render using:
- GitHub README (native support)
- mermaid.live
- VS Code extensions

### Option 2: PlantUML
Generate PlantUML code for more detailed diagrams with:
- plantuml.com
- VS Code PlantUML extensions

### Option 3: Visual Diagram Services
Use with AI diagram generators like:
- Excalidraw (with AI)
- draw.io (with AI plugins)
- Lucidchart (AI features)
- Whimsical (AI whiteboard)

### Option 4: Text-based Description
Ask for a detailed textual description that you can use to manually create diagrams in:
- Figma
- Sketch
- Adobe XD

---

## 📝 Example Follow-up Prompts:

**For more detail:**
```
"Can you zoom in on the authentication flow and show the JWT token lifecycle in detail?"
```

**For specific components:**
```
"Create a detailed diagram focusing only on the real-time chat WebSocket architecture"
```

**For deployment view:**
```
"Show the Docker container architecture and how services communicate in the deployed environment"
```

**For data model:**
```
"Create an Entity-Relationship Diagram (ERD) for the database schema with all relationships"
```

---

## 🚀 Quick Start:

1. Copy the main prompt above
2. Paste into your preferred AI tool (ChatGPT, Claude, etc.)
3. Request specific diagram format (Mermaid, PlantUML, etc.)
4. Refine with follow-up questions
5. Export and add to your documentation

---

## 📌 Notes:

- This architecture is based on the actual Hourz project implementation
- All components and flows are currently implemented or documented
- Feel free to adjust the prompt for specific focus areas
- The system is designed for scalability and future enhancements
