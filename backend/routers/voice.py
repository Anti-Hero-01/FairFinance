"""
Voice assistant routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models.database import get_db, User, LoanApplication
from backend.schemas.voice import VoiceQueryRequest, VoiceQueryResponse
from backend.services.auth import get_current_active_user
from backend.services.permissions import Permission, require_any_permission
from backend.voice.voice_assistant import voice_assistant
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/ask", response_model=VoiceQueryResponse)
def process_voice_query(
    request: VoiceQueryRequest,
    current_user: User = Depends(require_any_permission([
        Permission.VOICE_ASSISTANT_FULL,
        Permission.VOICE_ASSISTANT_LIMITED
    ])),
    db: Session = Depends(get_db)
):
    """Process voice query (Full for User/Admin, Limited for Auditor)"""
    # Get explanation data if application_id provided
    explanation_data = None
    if request.application_id:
        application = db.query(LoanApplication).filter(
            LoanApplication.id == request.application_id,
            LoanApplication.user_id == current_user.id
        ).first()
        
        if application:
            explanation_data = application.explanation
    
    # Process voice query
    result = voice_assistant.process_voice_query(
        request.audio_data,
        request.language,
        request.application_id,
        explanation_data
    )
    
    return VoiceQueryResponse(
        interpreted_query=result['interpreted_query'],
        response_text=result['response_text'],
        response_audio=None,  # Could add TTS here
        explanation_data=result.get('explanation_data')
    )

