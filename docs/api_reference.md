# FairFinance API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "user"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Predictions

#### Make Prediction
```http
POST /predict
Authorization: Bearer <token>
Content-Type: application/json

{
  "application_data": {
    "age": 35,
    "income": 50000,
    "credit_score": 720,
    "loan_amount": 100000,
    "employment_years": 5,
    "debt_to_income": 0.3,
    "credit_history_length": 10,
    "number_of_accounts": 3,
    "defaults": 0,
    "gender": "male",
    "region": "urban",
    "age_group": "26-40"
  }
}

Response:
{
  "approved": true,
  "probability": 0.85,
  "application_id": 1,
  "explanation_summary": "Your loan was approved...",
  "top_features": {...}
}
```

#### Get Applications
```http
GET /predict/applications
Authorization: Bearer <token>
```

#### Get Application
```http
GET /predict/applications/{application_id}
Authorization: Bearer <token>
```

### Explanations

#### Get Explanation
```http
GET /explain/{application_id}
Authorization: Bearer <token>

Response:
{
  "application_id": 1,
  "prediction": true,
  "probability": 0.85,
  "top_positive_features": [...],
  "top_negative_features": [...],
  "shap_values": {...},
  "ethical_twin_explanation": {...},
  "explanation_text": "..."
}
```

#### Explain Profile
```http
POST /explain/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1
}
```

### Consent

#### Get Consent Dashboard
```http
GET /consent/dashboard
Authorization: Bearer <token>
```

#### Update Consent
```http
POST /consent/update
Authorization: Bearer <token>
Content-Type: application/json

{
  "data_category": "income",
  "consent_given": true
}
```

### Voice

#### Process Voice Query
```http
POST /voice/ask
Authorization: Bearer <token>
Content-Type: application/json

{
  "audio_data": "base64_encoded_audio",
  "language": "en",
  "application_id": 1,
  "user_id": 1
}
```

### Governance

#### Get Decision Log
```http
GET /governance/decision-log/{user_id}
Authorization: Bearer <token>
```

#### Get Fairness Report
```http
GET /governance/fairness-report
Authorization: Bearer <token>
```

#### Admin Override
```http
POST /governance/admin/override
Authorization: Bearer <token>
Content-Type: application/json

{
  "application_id": 1,
  "new_decision": true,
  "reason": "Manual review approved"
}
```

#### Get Audit Trail
```http
GET /governance/audit-trail?limit=100
Authorization: Bearer <token>
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

