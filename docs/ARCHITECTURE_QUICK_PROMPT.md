# Quick System Architecture Diagram Prompt

## Copy-Paste Ready Prompt 🚀

```text
Create a System Architecture Diagram for "Hourz" - a local helper marketplace platform.

TECHNOLOGY STACK:
- Mobile: Flutter (Dart) with Riverpod state management
- Backend: FastAPI (Python 3.11) with SQLModel ORM
- Database: PostgreSQL with PostGIS (geospatial data)
- Real-time: WebSocket for chat
- Auth: JWT (access + refresh tokens)
- DevOps: Docker, Jenkins CI/CD, SonarQube

MAIN COMPONENTS:

1. CLIENT LAYER (Flutter Mobile Apps)
   - iOS/Android/Web apps
   - Features: User profiles, Gig browsing, Real-time chat, File uploads, Payments, Reviews

2. API LAYER (FastAPI Server - Port 8000)
   Endpoints:
   - /api/auth/* - Two-step registration & JWT authentication
   - /api/users/* - User profile management
   - /api/gigs/* - Job posting and matching
   - /api/files/* - File upload/serving (profile images, gig images)
   - /api/chat/* - Chat messages
   - /api/transactions/* - Payment processing
   - /api/reviews/* - Rating system
   - /api/buddies/* - User connections
   - /ws/* - WebSocket for real-time chat

3. DATABASE (PostgreSQL + PostGIS)
   Tables: user, address (with GPS), gig, chat, message, transaction, review, buddylist, uploadedfile

4. FILE STORAGE
   - Local storage with Docker volumes
   - Categories: profile/, gig/, general/
   - Static file serving endpoint

5. REAL-TIME COMMUNICATION
   - WebSocket connections
   - Chat room management
   - Message broadcasting

6. CI/CD PIPELINE (Jenkins)
   - Automated testing with pytest
   - SonarQube code quality
   - Docker containerization
   - Automated deployment

KEY FLOWS TO SHOW:

1. User Registration:
   Mobile → POST /api/auth/register → Create user → Return JWT → POST /api/auth/profile-setup → Complete profile

2. Gig Matching:
   Seeker posts gig → Stored with GPS → Helpers browse (location-filtered) → Helper accepts → WebSocket chat opens → Payment transaction

3. File Upload:
   Mobile → POST /api/files/upload/profile → Validate → Save to uploads/ → Create DB record → Return URL → Display image

4. Real-time Chat:
   Users connect WebSocket → Send messages → Broadcast to participants → Persist to DB

DIAGRAM STYLE:
- Modern cloud architecture style
- Clear layers: Client → API → Database → External
- Show HTTP/HTTPS and WebSocket protocols
- Color coding: Blue=Client, Green=Backend, Orange=Database, Purple=WebSocket, Red=Security
- Include icons for Flutter, FastAPI, PostgreSQL, Docker
- Show both sync (REST) and async (WebSocket) communication

Generate a professional architecture diagram suitable for technical documentation and presentations.
```

---

## Alternative: Generate Mermaid Diagram Code

```text
Create a Mermaid diagram code for the Hourz system architecture with these components:

1. Flutter Mobile App (client)
2. FastAPI Backend (api-server)
3. PostgreSQL Database (db)
4. File Storage (storage)
5. WebSocket Server (ws)
6. Jenkins CI/CD (cicd)

Show these connections:
- Mobile ↔ API (HTTP/HTTPS)
- Mobile ↔ WebSocket (WS)
- API ↔ Database (SQL)
- API ↔ File Storage (File I/O)
- CI/CD → API (Deploy)

Include key endpoints:
- /api/auth (Authentication)
- /api/gigs (Gig Management)
- /api/files (File Upload/Serve)
- /ws (WebSocket Chat)

Use graph TD (top-down) or graph LR (left-right) layout.
```

---

## 🎯 Expected Output

The AI should generate diagrams showing:

✅ **Layer Architecture**
```
┌─────────────────────────┐
│   Flutter Mobile App    │  (iOS, Android, Web)
└───────────┬─────────────┘
            │ HTTP/HTTPS
            │ WebSocket
┌───────────▼─────────────┐
│   FastAPI Backend       │  (Port 8000)
│   - REST API            │
│   - WebSocket Server    │
│   - JWT Auth            │
│   - File Management     │
└───────────┬─────────────┘
            │
    ┌───────┴────────┐
    │                │
┌───▼──────┐  ┌─────▼─────┐
│PostgreSQL│  │   File    │
│+ PostGIS │  │  Storage  │
└──────────┘  └───────────┘
```

✅ **Key Features Highlighted**
- Two-step user registration
- Geolocation-based gig matching
- Real-time chat system
- File upload/serving
- Transaction management

✅ **Security Boundaries**
- JWT authentication points
- CORS configuration
- Password hashing
- Token refresh mechanism

---

## 💡 Usage Tips

1. **For ChatGPT/Claude**: Copy the main prompt and ask for specific format
2. **For Mermaid**: Ask for "mermaid diagram code" specifically
3. **For Visual**: Request SVG or PNG export instructions
4. **For Details**: Follow up with "zoom in on [component]" for deeper dives

---

## 📚 What's Next

After getting your diagram:
1. Save to `/docs/architecture/` folder
2. Add to README.md
3. Update for infrastructure changes
4. Share with team for onboarding

