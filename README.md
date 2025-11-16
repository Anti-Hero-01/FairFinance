# FairFinance - Ethical AI for Transparent Banking

**GHCI Hackathon Round 2 Submission**

FairFinance is a comprehensive ethical AI system for transparent banking that demonstrates fairness, explainability, and compliance in loan decision-making.

## 🎯 Project Overview

FairFinance provides:
- **Transparent Loan Decisions** with SHAP explainability
- **Fairness Monitoring** using Fairlearn/AIF360 metrics
- **Privacy-First Consent Management** with granular data controls
- **Multilingual Voice Assistant** (English, Hindi, Marathi)
- **Governance Dashboard** for auditors and compliance officers
- **Ethical Twin** interpretable surrogate model for human-readable explanations

## 📁 Project Structure

```
FairFinance/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main application
│   ├── routers/            # API routes
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── explainability/     # Explanation services
│   ├── audit/              # Audit logging
│   ├── voice/              # Voice assistant
│   └── config/             # Configuration
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # Reusable components
│   │   ├── services/       # API services
│   │   ├── hooks/          # React hooks
│   │   └── context/        # Context providers
│   └── public/             # Static assets
│
├── ml/                     # ML pipeline
│   ├── preprocessing.py   # Data preprocessing
│   ├── synthetic_data.py  # Bias injection
│   ├── train.py           # Model training
│   ├── fairness_pipeline.py # Fairness metrics
│   ├── shap_utils.py      # SHAP explainability
│   ├── ethical_twin.py    # Interpretable surrogate
│   └── model.pkl          # Trained model (generated)
│
├── data/                   # Data files
│   └── credit_dataset.csv.xls
│
├── configs/                # Configuration files
│   ├── explanation_templates.json
│   ├── consent_config.json
│   └── bias_groups_config.json
│
├── docs/                   # Documentation
│   ├── api_reference.md
│   └── fairness_report.md
│
└── docker-compose.yml      # Docker setup
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional)
- PostgreSQL 15+ (if not using Docker)
- MongoDB 7+ (if not using Docker)

### Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd FairFinance
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Train ML models:**
   ```bash
   docker-compose exec backend python -m ml.train
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   SECRET_KEY=your-secret-key
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=fairfinance
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB=fairfinance
   ENCRYPTION_KEY=your-32-byte-encryption-key
   ```

5. **Initialize database:**
   ```bash
   python -c "from models.database import init_db; init_db()"
   ```

6. **Run the backend:**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

#### ML Pipeline Setup

1. **Navigate to project root:**
   ```bash
   cd ..
   ```

2. **Train models:**
   ```bash
   python -m ml.train
   ```

   This will:
   - Preprocess the credit dataset
   - Add synthetic bias using `bias_groups_config.json`
   - Train Logistic Regression and XGBoost models
   - Train Ethical Twin surrogate model
   - Generate SHAP explainer
   - Compute fairness metrics
   - Save models to `ml/` directory

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env` file:**
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Run the frontend:**
   ```bash
   npm run dev
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000

## 📚 Usage Guide

### 1. Training ML Models

Train all models from scratch:

```bash
python -m ml.train
```

This generates:
- `ml/model.pkl` - Best trained model
- `ml/logistic_regression.pkl` - Logistic Regression model
- `ml/xgboost.pkl` - XGBoost model
- `ml/ethical_twin.pkl` - Ethical Twin surrogate
- `ml/preprocessor.pkl` - Data preprocessor
- `ml/shap_explainer.pkl` - SHAP explainer
- `ml/feature_names.pkl` - Feature names
- `docs/fairness_report.md` - Fairness analysis report

### 2. Making Loan Predictions

1. **Register/Login** at http://localhost:3000
2. **Navigate to "Apply for Loan"**
3. **Fill in the application form:**
   - Age, Income, Credit Score
   - Loan Amount, Employment Years
   - Debt-to-Income Ratio
   - Credit History, Accounts, Defaults
   - Optional: Gender, Region, Age Group
4. **Submit** to get instant prediction with explanation

### 3. Viewing Explanations

1. **After submission**, you'll be redirected to the explanation dashboard
2. **View SHAP feature contributions** in interactive charts
3. **See Ethical Twin decision rules** for human-readable explanations
4. **Understand top positive/negative factors** affecting your decision

### 4. Using Voice Assistant

1. **Navigate to "Voice Assistant"**
2. **Select language** (English, Hindi, or Marathi)
3. **Click microphone** to start recording
4. **Ask questions** like:
   - "Why was my loan denied?"
   - "What factors affected my application?"
   - "How can I improve my eligibility?"
5. **Get instant explanations** in your preferred language

### 5. Managing Consent

1. **Navigate to "Consent Dashboard"**
2. **Review data categories:**
   - Income data
   - Credit history
   - Transactions
   - Location
   - Demographics
3. **Toggle consent** for each category
4. **View required permissions** for each feature

### 6. Profile Explanation

1. **Navigate to "My Profile"**
2. **View your risk category** (Low/Medium/High)
3. **See top influencing factors** across all applications
4. **Get improvement suggestions** to increase eligibility

### 7. Governance Dashboard (Admin/Auditor)

1. **Navigate to "Governance"** (requires admin/auditor role)
2. **View fairness metrics:**
   - Demographic Parity Difference
   - Equal Opportunity Difference
   - Disparate Impact Ratio
3. **Check for violations** against thresholds
4. **Review decision logs** with immutable audit trail
5. **Generate fairness reports**

## 🔐 Security Features

- **JWT Authentication** with role-based access control
- **AES-256 Field-Level Encryption** for protected attributes
- **Consent Management** with granular permissions
- **Immutable Audit Logs** in MongoDB
- **Admin Override** with full audit trail

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Predictions
- `POST /predict` - Make loan prediction
- `GET /predict/applications` - Get user applications
- `GET /predict/applications/{id}` - Get specific application

### Explanations
- `GET /explain/{application_id}` - Get SHAP explanation
- `POST /explain/profile` - Get profile explanation

### Consent
- `GET /consent/dashboard` - Get consent dashboard
- `POST /consent/update` - Update consent
- `GET /consent/alerts` - Get consent alerts

### Voice
- `POST /voice/ask` - Process voice query

### Governance
- `GET /governance/decision-log/{user_id}` - Get decision log
- `GET /governance/fairness-report` - Get fairness report
- `POST /governance/admin/override` - Admin override decision
- `GET /governance/audit-trail` - Get audit trail

## 🧪 Testing

### Test ML Pipeline

```bash
python -m ml.preprocessing
python -m ml.synthetic_data
python -m ml.fairness_pipeline
```

### Test Backend

```bash
cd backend
pytest  # If tests are added
```

### Test Frontend

```bash
cd frontend
npm test  # If tests are added
```

## 📖 Configuration Files

### `configs/bias_groups_config.json`
Defines protected attributes and fairness thresholds:
- Protected attributes: gender, region, age_group
- Metrics: demographic_parity, equal_opportunity, disparate_impact
- Thresholds for each metric

### `configs/consent_config.json`
Defines data categories and consent requirements:
- Data categories with descriptions
- Required permissions for each feature
- Default consent settings
- Alert messages

### `configs/explanation_templates.json`
Templates for generating human-readable explanations:
- Loan approval/denial messages
- Profile explanations
- Improvement suggestions
- Voice responses

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up --build

# Execute commands in containers
docker-compose exec backend python -m ml.train
docker-compose exec backend python -c "from models.database import init_db; init_db()"
```

## 🔧 Troubleshooting

### Backend Issues

1. **Database connection errors:**
   - Ensure PostgreSQL is running
   - Check connection credentials in `.env`

2. **Model loading errors:**
   - Run `python -m ml.train` to generate models
   - Check model paths in `backend/config/settings.py`

3. **Import errors:**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Frontend Issues

1. **API connection errors:**
   - Check `VITE_API_URL` in `.env`
   - Ensure backend is running on port 8000

2. **Build errors:**
   - Clear node_modules: `rm -rf node_modules && npm install`

### ML Pipeline Issues

1. **Dataset not found:**
   - Ensure `data/credit_dataset.csv.xls` exists
   - The pipeline will create synthetic data if file is missing

2. **SHAP errors:**
   - Install SHAP: `pip install shap`
   - Some models may not support TreeExplainer

## 📝 Development

### Adding New Features

1. **Backend:**
   - Add routes in `backend/routers/`
   - Add schemas in `backend/schemas/`
   - Add services in `backend/services/`

2. **Frontend:**
   - Add pages in `frontend/src/pages/`
   - Add components in `frontend/src/components/`
   - Add services in `frontend/src/services/`

3. **ML:**
   - Add preprocessing steps in `ml/preprocessing.py`
   - Add fairness metrics in `ml/fairness_pipeline.py`

## 🎓 GHCI Hackathon Requirements

This project fulfills all Round 2 requirements:

✅ **Technology Stack**: FastAPI, React, PostgreSQL, MongoDB, XGBoost, SHAP
✅ **System Architecture**: Microservices with clear separation
✅ **Data Model**: SQLAlchemy models + MongoDB for logs
✅ **AI/ML Components**: ML pipeline, SHAP, Ethical Twin, Fairness metrics
✅ **Security**: JWT, AES encryption, Consent management
✅ **Scalability**: Docker, async FastAPI, caching ready

## 📄 License

This project is created for GHCI Hackathon Round 2.

## 👥 Team

Built as a full engineering team inside a single AI:
- Senior Backend Engineer
- ML Engineer
- Fullstack Developer
- Architect
- Compliance Officer
- UX Designer

## 🙏 Acknowledgments

- UCI Credit Dataset
- SHAP library for explainability
- Fairlearn/AIF360 for fairness metrics
- FastAPI and React communities

---

**For questions or issues, please refer to the API documentation at `/docs` or check the codebase.**

