# ✨ Hourz Backend - Local Helper Marketplace ✨

Hourz is a local helper marketplace connecting Seekers who need help with Helpers who provide hourly services. Built with FastAPI, PostGIS, and real-time WebSocket chat.

## 🚀 Quick Start

1. **Install dependencies**: `poetry install`
2. **Start database**: `docker-compose up -d`
3. **Setup database**: 
   ```bash
   docker exec -it chayenity-pg psql -U admin -d postgres -c "CREATE DATABASE hourz;"
   docker exec -it chayenity-pg psql -U admin -d hourz -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   ```
4. **Run migrations**: `.venv\Scripts\python.exe -m alembic upgrade head`
5. **Start server**: `poetry run fastapi dev app/main.py`
6. **Access API**: <http://localhost:8000/docs>

---

## 🛠️ Project setup 🛠️

### Install Python 3.11

- `Linux`

```bash
brew install python@3.11
```

- `Windows`

```bash
winget install Python.Python.3.11
```

[Python download](https://www.python.org/downloads/)

---

### (Optional) Install pipx

- `Linux`

```bash
brew install pipx
pipx ensurepath
```

- `Windows`

```bash
python -m pip install --upgrade pipx
pipx ensurepath
```

[Pipx download](https://pipx.pypa.io/stable/installation/)

---

## ⚙️ Install Poetry ⚙️

```bash
pipx install poetry
```

[Poetry download](https://python-poetry.org/docs/)

### 🔨 Configure Poetry to create virtual environment in project 🔨

```bash
poetry config virtualenvs.in-project true
```

### 🔧 ! If you encounter issues because you are not using Python 3.11 as your main version, create and set the virtual environment 🔧

- `Linux`

```bash
poetry env use python3.11
```

- `Windows`

```bash
py -3.11 -c "import sys; print(sys.executable)"
```

```bash
poetry env use [full path\Python\Python311\python.exe]
```

---

## ⬇️ Install dependencies ⬇️

```bash
cd server
poetry install
```

### 🔧 Setting Up Virtual Environment in VS Code 🔧

```bash
poetry env info --path
```

`Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)

`Python: Select Interpreter`

`Enter interpreter path...`

---

### Active Environments

```bash
.venv\Scripts\activate.bat
```

---

## � Database Setup 🐳

### 1. Start PostgreSQL with PostGIS using Docker Compose

```bash
# In the root directory (chayenity/)
docker-compose up -d
```

This starts a PostgreSQL database with PostGIS extension for geospatial functionality.

### 2. Create Database and Enable PostGIS

```bash
# Create the hourz database
docker exec -it chayenity-pg psql -U admin -d postgres -c "CREATE DATABASE hourz;"

# Enable PostGIS extension
docker exec -it chayenity-pg psql -U admin -d hourz -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 3. Run Database Migrations

```bash
# Activate virtual environment
.venv\Scripts\activate.bat

# Apply database migrations
.venv\Scripts\python.exe -m alembic upgrade head
```

This creates all Hourz tables using Alembic migrations:

- User (dual Helper/Seeker roles with geospatial locations)
- Gig (location-based tasks with PostGIS point data)  
- ChatRoom & Message (real-time chat system)
- BuddyList (trusted helper connections)
- Review & Transaction (feedback and payment tracking)
- UploadedFile (file management system)

### 🔍 Verify Database Setup

Check that all tables were created:

```bash
docker exec -it chayenity-pg psql -U admin -d hourz -c "\dt"
```

Check migration status:

```bash
.venv\Scripts\python.exe -m alembic current
```

---

## 🗃️ Database Migration Management 🗃️

### Check Migration Status

```bash
# See current migration version
.venv\Scripts\python.exe -m alembic current

# See migration history
.venv\Scripts\python.exe -m alembic history --verbose
```

### Creating New Migrations

When you modify models in `app/models.py`:

```bash
# Generate new migration automatically
.venv\Scripts\python.exe -m alembic revision --autogenerate -m "Add new field to User model"

# Apply the new migration
.venv\Scripts\python.exe -m alembic upgrade head
```

### Migration Management

```bash
# Upgrade to latest migration
.venv\Scripts\python.exe -m alembic upgrade head

# Upgrade to specific migration
.venv\Scripts\python.exe -m alembic upgrade 001_initial_schema

# Rollback to previous migration
.venv\Scripts\python.exe -m alembic downgrade -1

# Reset to empty database
.venv\Scripts\python.exe -m alembic downgrade base
```

### 🚨 Important Notes

- Always review auto-generated migrations before applying
- Migration files are stored in `alembic/versions/`
- The database name is `hourz` (not `chayenity`)
- PostGIS extension is required for geospatial features

---

## 🚀 Run the Application 🚀

### 🧪 Development Mode

```bash
# Activate virtual environment (if not already active)
.venv\Scripts\activate.bat

# Start development server
poetry run fastapi dev app/main.py
# OR using Python directly
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 🚀 Production Mode

```bash
# Activate virtual environment
.venv\Scripts\activate.bat

# Start production server
poetry run fastapi run app/main.py
# OR using Python directly
.venv\Scripts\python.exe -m uvicorn app.main:app
```

The API will be available at:

- **API**: <http://localhost:8000>
- **Interactive Docs**: <http://localhost:8000/docs>
- **Alternative Docs**: <http://localhost:8000/redoc>

### 📖 API Documentation

Comprehensive API documentation is available:

- `API_DOCUMENTATION.md` - Complete API reference with all endpoints, schemas, and examples
- `API_QUICK_REFERENCE.md` - Quick lookup for developers
- `FRONTEND_INTEGRATION_GUIDE.md` - TypeScript/React integration examples

---

## 🧹 Code Formatting 🧹

```bash
# Activate virtual environment
.venv\Scripts\activate.bat

# Format code with Black
poetry run black .

# Check formatting without making changes
poetry run black --check .

# Format specific files
poetry run black app/models.py app/main.py
```

# Format code with Black
poetry run black .

# Check formatting without making changes
poetry run black --check .

# Format specific files
poetry run black app/models.py app/main.py
```

---

## 🧪 Testing 🧪

```bash
# Activate virtual environment
.venv\Scripts\activate.bat

# Run all tests
poetry run pytest
# OR using Python directly
.venv\Scripts\python.exe -m pytest

# Run specific test file
poetry run pytest app/tests/test_basic_models.py -v

# Run tests with coverage
poetry run pytest --cov=app
```

---

## 📡 WebSocket Chat 📡

The application includes real-time chat functionality:

- JWT-authenticated WebSocket connections
- Room-based messaging tied to gigs
- Message persistence to database

Connect to WebSocket at: `ws://localhost:8000/ws/chat/{room_id}?token=your_jwt_token`

---

## 🗺️ PostGIS Features 🗺️

Location-based functionality using PostGIS:

- Store user and gig locations as geographic points
- Distance-based gig discovery
- Geospatial indexing for performance

---

## �️ Troubleshooting 🛠️

### Common Issues

**Database Connection Issues:**
```bash
# Check if PostgreSQL container is running
docker ps

# Restart the database container
docker-compose down && docker-compose up -d

# Check database exists
docker exec -it chayenity-pg psql -U admin -d postgres -c "\l"
```

**Migration Issues:**
```bash
# Check current migration status
.venv\Scripts\python.exe -m alembic current

# Reset migrations if needed
.venv\Scripts\python.exe -m alembic downgrade base
.venv\Scripts\python.exe -m alembic upgrade head

# Generate new migration if models changed
.venv\Scripts\python.exe -m alembic revision --autogenerate -m "Your change description"
```

**Virtual Environment Issues:**
```bash
# Recreate virtual environment
poetry env remove python
poetry install

# Check Python version
.venv\Scripts\python.exe --version  # Should be 3.11
```

**Port Conflicts:**
```bash
# Check what's running on port 8000
netstat -ano | findstr :8000

# Kill process if needed (replace PID)
taskkill /F /PID <process_id>
```

---

## �📚 Documentation 📚

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [PostGIS](https://postgis.net/)
- [Alembic](https://alembic.sqlalchemy.org/)
