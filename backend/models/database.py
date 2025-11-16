"""
Database models and connection setup
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from backend.config.settings import settings
from pathlib import Path
import os

# Database connection - Use SQLite for easier setup, PostgreSQL for production
BASE_DIR = Path(__file__).resolve().parents[2]
if os.getenv("USE_SQLITE", "true").lower() == "true":
    DB_PATH = BASE_DIR / "fairfinance.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = relationship("LoanApplication", back_populates="user")

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    credit_score = Column(Integer, nullable=False)
    loan_amount = Column(Float, nullable=False)
    employment_years = Column(Integer, nullable=False)
    debt_to_income = Column(Float, nullable=False)
    credit_history_length = Column(Integer, nullable=False)
    number_of_accounts = Column(Integer, nullable=False)
    defaults = Column(Integer, nullable=False)
    
    # Protected attributes (encrypted)
    gender = Column(String, nullable=True)
    region = Column(String, nullable=True)
    age_group = Column(String, nullable=True)
    
    # Decision
    status = Column(String, default="pending")
    prediction = Column(Boolean, nullable=True)
    probability = Column(Float, nullable=True)
    decision_reason = Column(String, nullable=True)
    explanation = Column(JSON, nullable=True)
    
    # Admin override
    admin_override = Column(Boolean, default=False)
    override_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="applications")

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_category = Column(String, nullable=False)
    consent_given = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        {'extend_existing': True}
    )

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

