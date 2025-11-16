# FairFinance - Quick Start Guide

## ✅ Project Status

The FairFinance project is now **RUNNING**!

### 🚀 Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 📋 What's Running

1. **Backend Server** (FastAPI)
   - Running on port 8000
   - SQLite database initialized
   - MongoDB using in-memory storage (if MongoDB not available)
   - ML models loaded and ready

2. **Frontend Server** (React + Vite)
   - Running on port 3000
   - Hot reload enabled
   - Connected to backend API

### 🎯 Next Steps

1. **Open your browser** and go to: http://localhost:3000

2. **Register a new account** or login

3. **Try the features**:
   - Apply for a loan
   - View SHAP explanations
   - Use the voice assistant
   - Manage consent settings
   - View profile explanations

### 🔧 If Servers Don't Start

**Start Backend manually:**
```bash
cd backend
set PYTHONPATH=..
python app.py
```

**Start Frontend manually:**
```bash
cd frontend
npm run dev
```

Or use the batch files:
- `start_backend.bat`
- `start_frontend.bat`

### 📝 Default Test Account

You can register a new account through the UI, or create one via API:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User","role":"user"}'
```

### 🎓 Demo Flow

1. Register/Login → Dashboard
2. Apply for Loan → Get Prediction
3. View Explanation → See SHAP charts
4. Voice Assistant → Ask questions
5. Consent Dashboard → Manage permissions
6. Profile Explanation → See risk factors

### ⚠️ Notes

- Database uses SQLite (fairfinance.db) for easy setup
- MongoDB uses in-memory storage if not available
- ML models are pre-trained and ready
- All features are functional and ready for demo

---

**Happy Hacking! 🚀**


