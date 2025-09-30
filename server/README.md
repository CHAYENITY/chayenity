# ✨ Hourz Backend - Local Helper Marketplace ✨

Hourz is a local helper marketplace connecting Seekers who need help with Helpers who provide hourly services. Built with FastAPI, PostGIS, and real-time WebSocket chat.

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

### Start PostgreSQL with PostGIS using Docker Compose

```bash
# In the root directory (chayenity/)
docker-compose up -d
```

This starts a PostgreSQL database with PostGIS extension for geospatial functionality.

### 🛢 Initialize Database 🛢

```bash
poetry run python scripts/init_db_directly.py
```

This creates all Hourz tables directly using SQLModel:

- User (dual Helper/Seeker roles)
- Gig (location-based tasks)  
- ChatRoom & Message (real-time chat)
- BuddyList (trusted connections)
- Review & Transaction (feedback and payments)

### 🔍 Verify Database Setup

Check that all tables were created:

```bash
docker exec -it chayenity-pg psql -U admin -d chayenity -c "\dt"
```

---

### ⚙️ Alternative: Alembic Migrations (if needed) ⚙️

If you prefer using Alembic migrations:

```bash
alembic revision --autogenerate -m "Initial Hourz schema"
alembic upgrade head
```

## 🚀 Run the Application 🚀

### 🧪 Development Mode

```bash
poetry run fastapi dev app/main.py
```

### 🚀 Production Mode

```bash
poetry run fastapi run app/main.py
```

The API will be available at:

- **API**: <http://localhost:8000>
- **Interactive Docs**: <http://localhost:8000/docs>
- **Alternative Docs**: <http://localhost:8000/redoc>

---

## 🧹 Code Formatting 🧹

```bash
poetry run black .
```

---

## 🧪 Testing 🧪

Run all tests:

```bash
poetry run pytest
```

Run specific test file:

```bash
poetry run pytest app/tests/test_basic_models.py -v
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

## 📚 Documentation 📚

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [PostGIS](https://postgis.net/)
- [Alembic](https://alembic.sqlalchemy.org/)
