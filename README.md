
# 🧩 Simple Modular FastAPI Backend

A **minimal, module-based FastAPI backend** with:

* Feature-first structure (`modules/*`)
* JWT authentication
* PostgreSQL + PostGIS (Docker only)
* Backend runs locally inside a virtual environment

---

## ⚙️ Requirements

* **Python 3.10+**
* **Docker & Docker Compose**

---

## 🚀 First-Time Setup (Windows)

### 1️⃣ Clone the repository

```powershell
git clone <repo-url>
cd backend
```

---

### 2️⃣ Allow PowerShell to activate venv (one-time per terminal)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

### 3️⃣ Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

You should now see:

```
(.venv)
```

---

### 4️⃣ Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🐳 Start Database (PostGIS)

```powershell
docker compose up -d
```

PostgreSQL + PostGIS will be available on:

```
localhost:5432
```

---

## ▶️ Run the Backend (ALWAYS inside venv)

```powershell
uvicorn app.main:app --reload
```

---

## 📚 API Documentation

* Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc → [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔐 Authentication (JWT)

* JWT logic is in `app/core/security.py`
* Protect routes using:

```python
Depends(get_current_user)
```

Clients must send:

```
Authorization: Bearer <token>
```

---

## ⚠️ Important Rules

### ✅ Always run inside the virtual environment

If `(venv)` is not visible in the terminal, the app **will not work correctly**.

To re-enter venv anytime:

```powershell
.\.venv\Scripts\Activate.ps1
```


## 🧩 Creating a New Module

1. Create a new folder:

```
app/modules/<module_name>/
```

2. Add these files:

```
router.py
service.py
repository.py
models.py
schemas.py
```

3. Register the router in `app/main.py`:

```python
from app.modules.<module_name>.router import router as module_router
app.include_router(module_router, prefix="/<module_name>")
```

---

## 🧠 Environment Variables

All required values are defined in `.env`:

```env
ENVIRONMENT=local

SECRET_KEY=supersecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_DB=app
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---

## 🧪 Common Commands

### Activate venv

```powershell
.\.venv\Scripts\Activate.ps1
```

### Start DB

```powershell
docker compose up -d
```

### Run backend

```powershell
uvicorn app.main:app --reload
```

### Stop DB

```powershell
docker compose down
```

---

## 🎯 Philosophy

* Keep infrastructure minimal
* Keep modules isolated
* Add complexity only when needed
* Optimize for speed and clarity

---