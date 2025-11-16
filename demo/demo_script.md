# FairFinance Demo Script

## Demo Flow for GHCI Hackathon Round 2

### 1. Introduction (30 seconds)
- "Welcome to FairFinance - Ethical AI for Transparent Banking"
- "This system demonstrates fairness, explainability, and compliance in loan decision-making"
- "Built for GHCI Hackathon Round 2"

### 2. User Registration & Login (1 minute)
- Show registration page
- Create a new user account
- Login and navigate to dashboard
- **Highlight**: JWT authentication, role-based access

### 3. Loan Application (2 minutes)
- Navigate to "Apply for Loan"
- Fill in application form:
  - Age: 35
  - Income: ₹50,000/month
  - Credit Score: 720
  - Loan Amount: ₹100,000
  - Employment Years: 5
  - Debt-to-Income: 0.3
  - Credit History: 10 years
  - Accounts: 3
  - Defaults: 0
  - Gender: Male (optional)
  - Region: Urban (optional)
- Submit application
- **Highlight**: Real-time prediction with ML models

### 4. SHAP Explainability Dashboard (2 minutes)
- Show explanation dashboard
- Display SHAP feature contributions chart
- Explain top positive factors (credit_score, income, etc.)
- Explain top negative factors (if any)
- Show Ethical Twin decision rules
- **Highlight**: Transparent, interpretable AI decisions

### 5. Voice Assistant (1.5 minutes)
- Navigate to Voice Assistant
- Select language (English/Hindi/Marathi)
- Demonstrate voice query:
  - "Why was my loan approved?"
  - Show interpreted query and response
- **Highlight**: Multilingual transparency

### 6. Consent Dashboard (1.5 minutes)
- Navigate to Consent Dashboard
- Show data categories:
  - Income data
  - Credit history
  - Transactions
  - Location
  - Demographics
- Toggle consent for a category
- Show real-time alert
- **Highlight**: Granular privacy controls

### 7. Profile Explanation (1 minute)
- Navigate to "My Profile"
- Show risk category (Low/Medium/High)
- Display top influencing factors
- Show improvement suggestions
- **Highlight**: Personalized financial insights

### 8. Governance Dashboard (2 minutes)
- Login as admin/auditor
- Navigate to Governance Dashboard
- Show fairness metrics:
  - Demographic Parity Difference
  - Equal Opportunity Difference
  - Disparate Impact Ratio
- Display fairness violations (if any)
- Show decision log with immutable audit trail
- Demonstrate admin override with audit trail
- **Highlight**: Compliance and governance

### 9. Technical Highlights (1 minute)
- Show backend API documentation at `/docs`
- Highlight:
  - FastAPI async architecture
  - PostgreSQL + MongoDB dual database
  - AES-256 field-level encryption
  - SHAP explainability
  - Fairlearn fairness metrics
  - Ethical Twin surrogate model

### 10. Closing (30 seconds)
- Summarize key features:
  - Transparent AI decisions
  - Fairness monitoring
  - Privacy-first consent
  - Multilingual support
  - Governance and compliance
- "Thank you for watching FairFinance!"

## Total Demo Time: ~12 minutes

## Key Talking Points

1. **Ethical AI**: Every decision is explainable and fair
2. **Privacy**: Users control their data usage
3. **Transparency**: SHAP and Ethical Twin provide clear explanations
4. **Compliance**: Full audit trail and governance dashboard
5. **Accessibility**: Multilingual voice assistant
6. **Scalability**: Docker-ready, production-grade architecture

## Demo Tips

- Have test data ready
- Pre-train models before demo
- Use realistic loan application values
- Show both approved and denied cases
- Highlight the fairness violations if present
- Emphasize the explainability features

