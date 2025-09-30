# ✨ Hourz Backend - Local Helper Marketplace ✨

Hourz is a local helper marketplace connecting Seekers who need help with Helpers who provide hourly services. Built with FastAPI, PostGIS, and real-time WebSocket chat.

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

## 🐳 Database Setup 🐳

### 1. Start PostgreSQL with Docker Compose

```bash
docker-compose up -d
```

### 2. Intial Database

- `Linux/MacOS`

```bash
./scripts/init_db.sh
```

- `Windows`

```bash
.\scripts\init_db.bat
```

---

## 🚀 Run the Application 🚀

### 🧪 Development Mode

```bash
# Start development server
poetry run fastapi dev
```

### 🚀 Production Mode

```bash
# Start production server
poetry run fastapi run
```

### 📖 API Documentation

Comprehensive API documentation is available:

- `API_DOCUMENTATION.md` - Complete API reference with all endpoints, schemas, and examples
- `API_QUICK_REFERENCE.md` - Quick lookup for developers
- `FRONTEND_INTEGRATION_GUIDE.md` - TypeScript/React integration examples

---

## 🧹 Code Formatting 🧹

```bash

# Format code with Black
poetry run black .

# Check formatting without making changes
poetry run black --check .
```

---

## 🧪 Testing 🧪

```bash
# Run all tests
poetry run pytest

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

## 📚 Documentation 📚

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [PostGIS](https://postgis.net/)
- [Alembic](https://alembic.sqlalchemy.org/)
