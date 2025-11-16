# Backend Setup & Running Guide

## Prerequisites Check

1. **Python 3.11+** installed
2. **Dependencies** installed (see Step 1 below)

## Step-by-Step Instructions

### Step 1: Install Dependencies

Open terminal in the project root and run:

```bash
cd backend
python -m pip install -r requirements.txt
```

**OR** install individually if you encounter issues:

```bash
python -m pip install fastapi uvicorn[standard] pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart sqlalchemy pymongo pandas numpy scikit-learn xgboost shap cryptography python-dotenv aiofiles httpx email-validator
```

### Step 2: Train ML Models (First Time Only)

From project root:

```bash
python ml/train.py
```

This will create:
- `ml/model.pkl` - Main model
- `ml/preprocessor.pkl` - Data preprocessor
- `ml/feature_names.pkl` - Feature names

### Step 3: Initialize Database (First Time Only)

From project root:

```bash
python -c "import sys; sys.path.insert(0, '.'); from backend.models.database import init_db; init_db(); print('Database initialized!')"
```

### Step 4: Create Test Users (Optional)

From project root:

```bash
python backend/create_test_users.py
```

### Step 5: Start Backend Server

**Option A: Using run_server.py (Recommended)**

From project root:

```bash
cd backend
python run_server.py
```

**Option B: Using batch file (Windows)**

Double-click `start_backend.bat` or run:

```bash
start_backend.bat
```

**Option C: Using uvicorn directly**

From project root:

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Option D: Using Python directly (if path issues)**

From project root:

```bash
python -m backend.run_server
```

### Step 6: Verify Backend is Running

Open your browser and check:

- **Health Check**: http://localhost:8000/health
  - Should return: `{"status": "healthy"}`

- **API Documentation**: http://localhost:8000/docs
  - Should show Swagger UI with all endpoints

- **Root Endpoint**: http://localhost:8000/
  - Should return API info

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Use `run_server.py` which handles path correctly:

```bash
cd backend
python run_server.py
```

### Issue: `ModuleNotFoundError: No module named 'email_validator'`

**Solution**: Install email-validator:

```bash
python -m pip install email-validator
```

### Issue: `ModuleNotFoundError: No module named 'bcrypt'`

**Solution**: Install bcrypt:

```bash
python -m pip install bcrypt
```

### Issue: Database connection errors

**Solution**: The backend uses SQLite by default (no setup needed). If you see database errors:

```bash
python -c "import sys; sys.path.insert(0, '.'); from backend.models.database import init_db; init_db()"
```

### Issue: Port 8000 already in use

**Solution**: Either:
1. Stop the process using port 8000
2. Change port in `run_server.py`:
   ```python
   uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
   ```

## Expected Output

When backend starts successfully, you should see:

```
Starting FairFinance API...
Database initialized
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Quick Start (All Steps)

```bash
# 1. Install dependencies
cd backend
python -m pip install -r requirements.txt
cd ..

# 2. Train models (first time)
python ml/train.py

# 3. Initialize database (first time)
python -c "import sys; sys.path.insert(0, '.'); from backend.models.database import init_db; init_db()"

# 4. Create test users (optional)
python backend/create_test_users.py

# 5. Start backend
cd backend
python run_server.py
```

## Backend Endpoints

Once running, access:

- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **Auth**: http://localhost:8000/auth/login
- **Predict**: http://localhost:8000/predict
- **Explain**: http://localhost:8000/explain/{id}
- **Consent**: http://localhost:8000/consent/dashboard
- **Governance**: http://localhost:8000/governance/fairness-report

## Notes

- Backend runs on **port 8000** by default
- **Auto-reload** is enabled (changes auto-refresh)
- Database file: `fairfinance.db` (SQLite)
- MongoDB uses in-memory storage if not available

---

**Backend is ready when you see "Uvicorn running on http://0.0.0.0:8000"** 🚀


