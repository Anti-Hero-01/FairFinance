import sys
from fastapi.testclient import TestClient
from backend.app import app

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


errors = []

print("Starting integration runner...")

# Register accounts
for email, name, role in [
    ("user1@example.com", "User One", "user"),
    ("auditor1@example.com", "Auditor One", "auditor"),
    ("admin1@example.com", "Admin One", "admin"),
]:
    r = register_user(email, name, role)
    print(f"Register {email}: {r.status_code}")
    # It's fine if the user already exists from previous runs (status 400 with duplicate email)
    if r.status_code not in (200, 400):
        errors.append(f"Register failed for {email}: {r.status_code} {r.text}")

# Login user
r = login_user("user1@example.com")
if r.status_code != 200:
    errors.append(f"Login failed for user1: {r.status_code} {r.text}")
    print(errors[-1])
    sys.exit(2)
user_token = r.json().get("access_token")
print("User token obtained")

# Get current user info to extract user id for later checks
me = client.get("/auth/me", headers=auth_header(user_token))
if me.status_code == 200:
    current_user_id = me.json().get("id")
else:
    current_user_id = 1

# Ensure required consents are enabled for a clean initial run
for cat in ("income", "credit_history"):
    client.post("/consent/update", json={"data_category": cat, "consent_given": True}, headers=auth_header(user_token))

# Make a prediction
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
pr = client.post("/predict", json={"application_data": application}, headers=auth_header(user_token))
print(f"Predict status: {pr.status_code}")
if pr.status_code != 200:
    errors.append(f"Predict failed: {pr.status_code} {pr.text}")
else:
    print("Predict response:", pr.json())
    app_id = pr.json().get("application_id")

# List applications
la = client.get("/predict/applications", headers=auth_header(user_token))
print(f"List apps status: {la.status_code}")
if la.status_code != 200:
    errors.append(f"List apps failed: {la.status_code} {la.text}")
else:
    print(f"Applications count: {len(la.json())}")

# Revoke consent for income
rev = client.post("/consent/update", json={"data_category": "income", "consent_given": False}, headers=auth_header(user_token))
print(f"Revoke consent status: {rev.status_code}")
if rev.status_code != 200:
    errors.append(f"Revoke consent failed: {rev.status_code} {rev.text}")

# Predict again -> should be forbidden
pr2 = client.post("/predict", json={"application_data": application}, headers=auth_header(user_token))
print(f"Predict after revoke: {pr2.status_code}")
if pr2.status_code != 403:
    errors.append(f"Predict after revoke expected 403, got {pr2.status_code}")

# Admin and auditor checks
r_admin_login = login_user("admin1@example.com")
if r_admin_login.status_code != 200:
    errors.append("Admin login failed")
    print(r_admin_login.text)
    sys.exit(3)
admin_token = r_admin_login.json().get("access_token")

r_aud_login = login_user("auditor1@example.com")
if r_aud_login.status_code != 200:
    errors.append("Auditor login failed")
    print(r_aud_login.text)
    sys.exit(4)
auditor_token = r_aud_login.json().get("access_token")

# Admin retrain
rt = client.post("/governance/retrain", headers=auth_header(admin_token))
print(f"Retrain: {rt.status_code}")
if rt.status_code != 200:
    errors.append(f"Retrain failed: {rt.status_code} {rt.text}")

# Auditor fairness report (likely insufficient data)
fair = client.get("/governance/fairness-report", headers=auth_header(auditor_token))
print(f"Fairness report status: {fair.status_code}")
if fair.status_code not in (200, 400):
    errors.append(f"Fairness endpoint unexpected status: {fair.status_code}")

# Admin export logs
exp = client.get("/governance/export-logs", headers=auth_header(admin_token))
print(f"Export logs status: {exp.status_code}")
if exp.status_code != 200:
    errors.append(f"Export logs failed: {exp.status_code} {exp.text}")

# Decision logs for the created user
logs = client.get(f"/governance/decision-log/{current_user_id}", headers=auth_header(admin_token))
print(f"Decision logs status: {logs.status_code}")
if logs.status_code != 200:
    errors.append(f"Decision logs failed: {logs.status_code} {logs.text}")
else:
    print(f"Decision logs count: {len(logs.json())}")

if errors:
    print("Integration runner detected errors:")
    for e in errors:
        print(" -", e)
    sys.exit(5)

print("Integration runner completed successfully")
sys.exit(0)
