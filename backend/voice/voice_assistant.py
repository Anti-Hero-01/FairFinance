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
        # Enable test/demo mode (set to False when real speech recognition is available)
        self.demo_mode = True
    
    def get_demo_query(self, audio_data: str) -> str:
        """Generate a demo query based on audio length (for testing without ffmpeg)"""
        try:
            audio_bytes = base64.b64decode(audio_data)
            audio_len = len(audio_bytes)
            
            # Demo mode: generate queries based on audio length
            # This allows testing without speech recognition setup
            demo_queries = [
                "Why was my loan denied?",
                "What factors affected my application?",
                "How can I improve my eligibility?",
                "Explain my loan decision",
                "What is my current application status?",
                "Can you help me understand my credit score?",
                "What should I do to get better terms?",
                "Tell me more about the fairness of the decision"
            ]
            
            # Use audio length to pick a demo query
            query_idx = (audio_len % len(demo_queries))
            selected_query = demo_queries[query_idx]
            print(f"[VoiceAssistant] Demo mode: Selected query based on audio length: {selected_query}")
            return selected_query
        except Exception as e:
            print(f"[VoiceAssistant] Demo mode error: {e}")
            return "Tell me about my loan decision"
    
    def transcribe_audio(self, audio_data: str, language: str = 'en') -> str:
        """Transcribe audio to text with fallback to demo mode"""
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            print(f"[VoiceAssistant] Audio size: {len(audio_bytes)} bytes")
            
            # Check if pydub is available
            if not PYDUB_AVAILABLE:
                print("[VoiceAssistant] pydub not installed, switching to demo mode")
                print("[VoiceAssistant] To enable real speech recognition: pip install pydub && install ffmpeg")
                if self.demo_mode:
                    return self.get_demo_query(audio_data)
                else:
                    return "Error: pydub not installed. Please install ffmpeg and pydub for real speech recognition."
            
            wav_io = None
            
            # Try to convert audio formats using pydub
            try:
                audio_segment = None
                error_messages = []
                
                # Try different formats
                formats_to_try = ["webm", "ogg", "mp3", "wav", "m4a"]
                for fmt in formats_to_try:
                    try:
                        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)
                        print(f"[VoiceAssistant] Successfully loaded audio as {fmt}")
                        break
                    except Exception as e:
                        error_messages.append(f"{fmt}: {str(e)}")
                        continue
                
                # If all format attempts fail, try raw PCM
                if audio_segment is None:
                    try:
                        audio_segment = AudioSegment.from_raw(io.BytesIO(audio_bytes), sample_width=2, frame_rate=16000, channels=1)
                        print("[VoiceAssistant] Successfully loaded audio as raw PCM")
                    except Exception as e:
                        print(f"[VoiceAssistant] Failed to load as raw PCM: {e}")
                
                # Convert to WAV format with proper settings
                if audio_segment:
                    wav_io = io.BytesIO()
                    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                    audio_segment.export(wav_io, format="wav")
                    wav_io.seek(0)
                    print(f"[VoiceAssistant] Converted to WAV: {wav_io.getbuffer().nbytes} bytes")
                else:
                    print("[VoiceAssistant] Could not convert audio format, trying demo mode")
                    if self.demo_mode:
                        return self.get_demo_query(audio_data)
                    
            except Exception as e:
                print(f"[VoiceAssistant] Audio conversion error: {e}")
                # Fallback to demo mode if conversion fails
                if self.demo_mode:
                    print("[VoiceAssistant] Switching to demo mode due to conversion error")
                    return self.get_demo_query(audio_data)
            
            # If conversion didn't work, try using raw bytes directly
            if wav_io is None:
                wav_io = io.BytesIO(audio_bytes)
                print("[VoiceAssistant] Using raw audio bytes as WAV")
            
            # Try Google Speech Recognition
            try:
                print("[VoiceAssistant] Attempting Google Speech Recognition...")
                with sr.AudioFile(wav_io) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)
                
                # Recognize speech
                lang_code = self.language_map.get(language, 'en-US')
                text = self.recognizer.recognize_google(audio, language=lang_code)
                print(f"[VoiceAssistant] Transcribed: {text}")
                return text
            
            except sr.UnknownValueError:
                print("[VoiceAssistant] Google API could not understand audio")
                if self.demo_mode:
                    print("[VoiceAssistant] Switching to demo mode")
                    return self.get_demo_query(audio_data)
                return "Could not understand audio. Please speak clearly."
            except sr.RequestError as e:
                print(f"[VoiceAssistant] Google API error: {e}")
                if self.demo_mode:
                    print("[VoiceAssistant] Google API unavailable, switching to demo mode")
                    return self.get_demo_query(audio_data)
                # If Google API fails (offline/error), return generic message
                return f"Error with speech recognition service. Please check internet connection."
        
        except Exception as e:
            # Return a more user-friendly error message
            print(f"[VoiceAssistant] Transcription error: {e}")
            if self.demo_mode:
                print("[VoiceAssistant] Critical error, switching to demo mode")
                return self.get_demo_query(audio_data)
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

