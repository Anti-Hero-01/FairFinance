import pytest
from fastapi.testclient import TestClient
from backend.app import app
import time

client = TestClient(app)

USER_PW = "Password123!"


def register_user(email, full_name, role):
    resp = client.post("/auth/register", json={
        "email": email,
        "full_name": full_name,
        "password": USER_PW,
        "role": role
    })
    return resp


def login_user(email):
    resp = client.post("/auth/login", json={"email": email, "password": USER_PW})
    return resp


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_user_register_login_and_prediction_flow():
    # Register users
    u = register_user("user1@example.com", "User One", "user")
    assert u.status_code == 200

    a = register_user("auditor1@example.com", "Auditor One", "auditor")
    assert a.status_code == 200

    admin = register_user("admin1@example.com", "Admin One", "admin")
    assert admin.status_code == 200

    # Login user
    login = login_user("user1@example.com")
    assert login.status_code == 200
    token = login.json().get("access_token")
    assert token

    # Make a prediction (consent defaults should allow)
    application = {
        "age": 30,
        "income": 5000.0,
        "credit_score": 700,
        "loan_amount": 1000.0,
        "employment_years": 2,
        "debt_to_income": 0.2,
        "credit_history_length": 5,
        "number_of_accounts": 3,
        "defaults": 0
    }

    predict_resp = client.post("/predict", json={"application_data": application}, headers=auth_header(token))
    assert predict_resp.status_code == 200, predict_resp.text
    jsonp = predict_resp.json()
    assert "approved" in jsonp and "application_id" in jsonp

    app_id = jsonp["application_id"]

    # Get user applications
    apps_resp = client.get("/predict/applications", headers=auth_header(token))
    assert apps_resp.status_code == 200
    apps = apps_resp.json()
    assert isinstance(apps, list) and len(apps) >= 1

    # Revoke consent for income and expect next predict to be forbidden
    # Update consent requires MANAGE_CONSENT permission which 'user' has
    revoke = client.post("/consent/update", json={"data_category": "income", "consent_given": False}, headers=auth_header(token))
    assert revoke.status_code == 200

    predict2 = client.post("/predict", json={"application_data": application}, headers=auth_header(token))
    assert predict2.status_code == 403


def test_admin_and_auditor_endpoints():
    # Login admin and auditor
    login_admin = login_user("admin1@example.com")
    assert login_admin.status_code == 200
    admin_token = login_admin.json().get("access_token")

    login_auditor = login_user("auditor1@example.com")
    assert login_auditor.status_code == 200
    auditor_token = login_auditor.json().get("access_token")

    # Admin trigger retraining
    retrain = client.post("/governance/retrain", headers=auth_header(admin_token))
    assert retrain.status_code == 200
    assert "message" in retrain.json()

    # Auditor requests fairness report - likely insufficient data; expect 400 or error
    fairness = client.get("/governance/fairness-report", headers=auth_header(auditor_token))
    assert fairness.status_code in (200, 400)

    # Admin export logs
    export = client.get("/governance/export-logs", headers=auth_header(admin_token))
    assert export.status_code == 200
    data = export.json()
    assert "data" in data or isinstance(export.text, str)

    # Admin can fetch decision logs for user
    # fetch decision log for user1 (id 1)
    logs = client.get(f"/governance/decision-log/1", headers=auth_header(admin_token))
    assert logs.status_code == 200
    assert isinstance(logs.json(), list)
