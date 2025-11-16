"""
Server startup script with proper path handling
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import and run
from backend.app import app
import uvicorn

if __name__ == "__main__":
    print("Starting FairFinance API...")
    print("API will be available at: http://localhost:8000")
    print("API Docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

