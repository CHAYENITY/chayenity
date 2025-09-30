# Hourz: Local Helper App – AI Agent Requirement

---

## 1. General Information

- **Project Name:** Hourz
- **Core Concept:** A hyperlocal app that connects people who need hourly help (**Seeker**) with those available to help (**Helper**).
- **Tone & Vibe:** Chill, Friendly, Easy-to-Use, Hyperlocal
- **User Role:** Dual role (every user can be both Seeker and Helper in the same account)
- **Location System:**
  - **Helper:** Sets a **Fixed Location** and toggles `is_available`
  - **Seeker:** Pins current GPS location (auto or manual) when posting gigs
  - **Matching:** Geospatial queries within a defined distance
- **Repository:** Monorepo (Frontend, Backend, Infra together)
- **DevOps:** Docker Compose (dev/prod), Jenkins + SonarQube (CI/CD)
- **Payment:** Mock transaction (stubbed Stripe)

---

## 2. Technology Stack & Architecture

- **Frontend:**

  - Flutter (Dart)
  - Riverpod (State management)
  - Freezed (Immutable data classes)
  - Go Router, flutter_map (Map UI), geolocator (GPS pinning)
  - Dio (HTTP client)
  - JSON Annotation (JSON serialization/deserialization)
  - Lucide Icons (Icons)

- **Backend:**

  - FastAPI (Python)
  - WebSockets for real-time chat

- **Database:**

  - PostgreSQL
  - PostGIS extension for location queries

- **ORM & Migrations:** SQLAlchemy + Alembic
- **Authentication:** JWT (Email/Password)
- **Infrastructure:** Docker Compose
- **CI/CD:** Jenkins + SonarQube

**Repository Structure:**

```
/mobile  (Flutter)
/server   (FastAPI)
/infra     (Docker)
```

---

## 3. Core Features

### Phase 1: Minimum Viable Product (MVP)

- **User Authentication & Profile**

  - Register/Login with Email/Password (JWT)
  - Profile: name, photo, contact info
  - Dual-role available immediately

- **Location & Availability**

  - Users set a **Fixed Location** (PostGIS Point)
  - Helpers toggle `is_available` status

- **Gig/Request Posting**

  - Form: title, description, duration, budget
  - GPS auto-pin with draggable marker

- **Geospatial Search**
  - Home page: list of nearby gigs
  - Map view with gig pins

---

### Phase 2: Functionality & Communication

- **Job Acceptance Flow**

  - Helper accepts gig
  - Status updates: Pending → Accepted → In Progress → Completed/Cancelled

- **In-App Chat**

  - Auto chat room when gig is accepted
  - Real-time text + image messaging via WebSockets

- **Buddy System (Favorites)**

  - Add to Buddy/Favorite list
  - Quick access for repeat hires

- **Image Management**
  - Seeker: upload gig images
  - Helper: upload profile/gig images
  - Backend stores as URLs (mock cloud storage)

---

### Phase 3: Quality & Closure

- **Review System**

  - Rating (1–5 stars) + text review
  - Reputation score on profile

- **Mock Payment / Transaction**

  - Escrow simulation (Seeker → Helper)
  - Service charge deduction (display only)
  - Basic transaction history

- **CI/CD & Code Quality**
  - Jenkinsfile + pipelines
  - SonarQube integration (Quality Gate)
  - Final code refactoring & optimization

---

## 4. Design Principles

- **Aesthetics:** Chill & Friendly (Teal/Amber), Minimal design
- **Adaptive Design:** Responsive Flutter UI (mobile + tablet)
- **Clarity:** Job info, price, and distance must be clear and easy to read
