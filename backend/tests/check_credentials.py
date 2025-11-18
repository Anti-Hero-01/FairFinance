from backend.models.database import SessionLocal, User, init_db
from fastapi.testclient import TestClient
from backend.app import app


def main():
    print("Starting app TestClient (runs startup lifecycle)...")
    client = TestClient(app)

    # Wait a moment for lifespan startup to complete
    print("Initializing DB and listing users after app startup...")
    # Also explicitly call create_test_users to ensure test accounts exist (diagnostic)
    try:
        from backend import create_test_users
        print("Explicitly invoking create_test_users for diagnosis...")
        create_test_users.create_test_users()
    except Exception as e:
        print("create_test_users invocation error:", e)
    init_db()
    db = SessionLocal()
    users = db.query(User).all()
    for u in users:
        print(f"User id={u.id}, email={u.email}, role={u.role}, active={u.is_active}, hashed_len={len(u.hashed_password) if u.hashed_password else 0}")
    db.close()
    email = "user1@fairfinance.com"
    password = "user123"
    print(f"Attempting login for {email}...")
    r = client.post("/auth/login", json={"email": email, "password": password})
    print("Status code:", r.status_code)
    try:
        print("Response:", r.json())
    except Exception:
        print("Non-JSON response:", r.text)

if __name__ == '__main__':
    main()
