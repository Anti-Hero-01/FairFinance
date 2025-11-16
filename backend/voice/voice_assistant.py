"""
Multilingual voice transparency assistant
Supports English, Hindi, and Marathi
"""

import base64
import io
import json
from typing import Dict, Any, Optional
import speech_recognition as sr
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None
from backend.config.settings import settings
from backend.services.ml_service import ml_service
from backend.services.explanation_service import explanation_service

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language_map = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'mr': 'mr-IN'
        }
    
    def transcribe_audio(self, audio_data: str, language: str = 'en') -> str:
        """Transcribe audio to text"""
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            wav_io = None
            
            # If pydub is available, try to convert audio formats
            if PYDUB_AVAILABLE and AudioSegment:
                try:
                    # Convert audio to WAV format (speech_recognition requires WAV)
                    audio_segment = None
                    error_messages = []
                    
                    # Try different formats
                    formats_to_try = ["webm", "ogg", "mp3", "wav", "m4a"]
                    for fmt in formats_to_try:
                        try:
                            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)
                            break
                        except Exception as e:
                            error_messages.append(f"{fmt}: {str(e)}")
                            continue
                    
                    # If all format attempts fail, try raw PCM
                    if audio_segment is None:
                        try:
                            audio_segment = AudioSegment.from_raw(io.BytesIO(audio_bytes), sample_width=2, frame_rate=16000, channels=1)
                        except Exception:
                            pass
                    
                    # Convert to WAV format with proper settings
                    if audio_segment:
                        wav_io = io.BytesIO()
                        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                        audio_segment.export(wav_io, format="wav")
                        wav_io.seek(0)
                except Exception as e:
                    # If conversion fails, try using raw bytes as WAV
                    pass
            
            # If conversion didn't work, try using raw bytes directly
            if wav_io is None:
                wav_io = io.BytesIO(audio_bytes)
            
            # Use speech recognition
            with sr.AudioFile(wav_io) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Recognize speech
            lang_code = self.language_map.get(language, 'en-US')
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            return text
        except sr.UnknownValueError:
            return "Could not understand audio. Please speak clearly."
        except sr.RequestError as e:
            return f"Error with speech recognition service: {e}"
        except Exception as e:
            # Return a more user-friendly error message
            error_msg = str(e)
            if "could not be read" in error_msg.lower() or "pcm" in error_msg.lower() or "ffmpeg" in error_msg.lower():
                return "Error processing audio: Audio format not supported. Please ensure ffmpeg is installed or try recording in WAV format."
            return f"Error processing audio: {error_msg}"
    
    def interpret_query(self, query: str, application_id: Optional[int] = None) -> Dict[str, Any]:
        """Interpret user query and determine intent"""
        query_lower = query.lower()
        
        # Intent detection
        if any(word in query_lower for word in ['why', 'reason', 'explain', 'how', 'what']):
            intent = 'explanation'
        elif any(word in query_lower for word in ['improve', 'better', 'suggest', 'advice']):
            intent = 'improvement'
        elif any(word in query_lower for word in ['status', 'decision', 'approved', 'denied']):
            intent = 'status'
        else:
            intent = 'general'
        
        return {
            'intent': intent,
            'query': query,
            'application_id': application_id
        }
    
    def generate_response(self, interpreted_query: Dict[str, Any], 
                         explanation_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate response based on interpreted query"""
        intent = interpreted_query['intent']
        query = interpreted_query['query']
        
        templates = explanation_service.templates.get('voice_responses', {})
        
        if intent == 'explanation':
            if explanation_data:
                top_features = explanation_data.get('top_features', {})
                top_pos = top_features.get('top_positive', [])
                top_neg = top_features.get('top_negative', [])
                
                if top_pos:
                    features = ", ".join([f.get('feature', '') for f in top_pos[:3]])
                    return f"The main factors in your loan decision were: {features}."
                elif top_neg:
                    features = ", ".join([f.get('feature', '') for f in top_neg[:3]])
                    return f"Your application was affected by: {features}."
            
            return "Your loan decision was based on your financial profile including credit score, income, and debt-to-income ratio."
        
        elif intent == 'improvement':
            return "To improve your loan eligibility, consider increasing your credit score, reducing your debt-to-income ratio, and maintaining a stable employment history."
        
        elif intent == 'status':
            return "You can check your loan application status in your dashboard."
        
        else:
            return "I can help you understand your loan decision, suggest improvements, or check your application status. What would you like to know?"
    
    def process_voice_query(self, audio_data: str, language: str, 
                           application_id: Optional[int] = None,
                           explanation_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process complete voice query"""
        # Transcribe
        transcribed_text = self.transcribe_audio(audio_data, language)
        
        # Interpret
        interpreted_query = self.interpret_query(transcribed_text, application_id)
        
        # Generate response
        response_text = self.generate_response(interpreted_query, explanation_data)
        
        return {
            'interpreted_query': interpreted_query['query'],
            'response_text': response_text,
            'explanation_data': explanation_data
        }

# Global voice assistant
voice_assistant = VoiceAssistant()

