"""
Script to create test users for all roles
Run this to populate the database with test accounts
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.models.database import SessionLocal, User, init_db
import bcrypt

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly"""
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')

def create_test_users():
    """Create test users for all roles"""
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    # Test users data
    test_users = [
        # Regular Users (5)
        {"email": "user1@fairfinance.com", "password": "user123", "full_name": "Harsh", "role": "user"},
        {"email": "user2@fairfinance.com", "password": "user123", "full_name": "Jane Smith", "role": "user"},
        {"email": "user3@fairfinance.com", "password": "user123", "full_name": "Bob Johnson", "role": "user"},
        {"email": "user4@fairfinance.com", "password": "user123", "full_name": "Alice Williams", "role": "user"},
        {"email": "user5@fairfinance.com", "password": "user123", "full_name": "Charlie Brown", "role": "user"},
        
        # Admin Users (5)
        {"email": "admin1@fairfinance.com", "password": "admin123", "full_name": "Rajat", "role": "admin"},
        {"email": "admin2@fairfinance.com", "password": "admin123", "full_name": "Admin Two", "role": "admin"},
        {"email": "admin3@fairfinance.com", "password": "admin123", "full_name": "Admin Three", "role": "admin"},
        {"email": "admin4@fairfinance.com", "password": "admin123", "full_name": "Admin Four", "role": "admin"},
        {"email": "admin5@fairfinance.com", "password": "admin123", "full_name": "Admin Five", "role": "admin"},
        
        # Auditor Users (5)
        {"email": "auditor1@fairfinance.com", "password": "auditor123", "full_name": "Jitesh", "role": "auditor"},
        {"email": "auditor2@fairfinance.com", "password": "auditor123", "full_name": "Auditor Two", "role": "auditor"},
        {"email": "auditor3@fairfinance.com", "password": "auditor123", "full_name": "Auditor Three", "role": "auditor"},
        {"email": "auditor4@fairfinance.com", "password": "auditor123", "full_name": "Auditor Four", "role": "auditor"},
        {"email": "auditor5@fairfinance.com", "password": "auditor123", "full_name": "Auditor Five", "role": "auditor"},
    ]
    
    created_count = 0
    skipped_count = 0
    
    print("Creating test users...")
    print("=" * 60)
    
    for user_data in test_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if existing_user:
            print(f"[SKIP] {user_data['email']} (already exists)")
            skipped_count += 1
            continue
        
        # Create new user
        hashed_password = get_password_hash(user_data["password"])
        user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            role=user_data["role"],
            is_active=True
        )
        
        db.add(user)
        created_count += 1
        print(f"[OK] Created: {user_data['email']} ({user_data['role']})")
    
    db.commit()
    db.close()
    
    print("=" * 60)
    print(f"\n[SUCCESS] Created {created_count} users")
    print(f"[SKIP] Skipped {skipped_count} existing users")
    print("\n" + "=" * 60)
    print("TEST USER CREDENTIALS")
    print("=" * 60)
    
    # Print credentials organized by role
    roles = ["user", "admin", "auditor"]
    for role in roles:
        print(f"\n[{role.upper()} ROLE]:")
        print("-" * 60)
        role_users = [u for u in test_users if u["role"] == role]
        for i, user in enumerate(role_users, 1):
            print(f"  {i}. Email: {user['email']}")
            print(f"     Password: {user['password']}")
            print(f"     Name: {user['full_name']}")
            print()
    
    print("=" * 60)
    print("\n[INFO] You can now login with any of these credentials!")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")

if __name__ == "__main__":
    create_test_users()

