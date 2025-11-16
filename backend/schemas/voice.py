"""
Voice assistant schemas
"""

from pydantic import BaseModel
from typing import Optional

class VoiceQueryRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: str = "en"  # en, hi, mr
    application_id: Optional[int] = None
    user_id: int

class VoiceQueryResponse(BaseModel):
    interpreted_query: str
    response_text: str
    response_audio: Optional[str] = None  # Base64 encoded response
    explanation_data: Optional[dict] = None

