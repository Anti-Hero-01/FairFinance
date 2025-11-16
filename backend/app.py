"""
FairFinance FastAPI Application
Main entry point for the backend API
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.settings import settings
from backend.models.database import init_db
from backend.routers import auth, predictions, explanations, consent, governance, voice

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    print("Starting FairFinance API...")
    init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down FairFinance API...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Ethical AI for Transparent Banking - GHCI Hackathon Round 2",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(explanations.router)
app.include_router(consent.router)
app.include_router(governance.router)
app.include_router(voice.router)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "FairFinance API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

