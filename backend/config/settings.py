"""
Application settings and configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FairFinance API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "fairfinance"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "fairfinance"
    
    # Encryption
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-change-this"
    
    # ML Models
    MODEL_PATH: str = str(BASE_DIR / "ml/model.pkl")
    PREPROCESSOR_PATH: str = str(BASE_DIR / "ml/preprocessor.pkl")
    ETHICAL_TWIN_PATH: str = str(BASE_DIR / "ml/ethical_twin.pkl")
    SHAP_EXPLAINER_PATH: str = str(BASE_DIR / "ml/shap_explainer.pkl")
    FEATURE_NAMES_PATH: str = str(BASE_DIR / "ml/feature_names.pkl")
    
    # Config Files
    EXPLANATION_TEMPLATES_PATH: str = str(BASE_DIR / "configs/explanation_templates.json")
    CONSENT_CONFIG_PATH: str = str(BASE_DIR / "configs/consent_config.json")
    BIAS_GROUPS_CONFIG_PATH: str = str(BASE_DIR / "configs/bias_groups_config.json")
    
    # Voice Assistant
    OPENAI_API_KEY: Optional[str] = None
    VOICE_LANGUAGES: list = ["en", "hi", "mr"]  # English, Hindi, Marathi
    
    # CORS
    # Include localhost and 127.0.0.1 variants used by dev servers
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = True

settings = Settings()

