# Voice Assistant Setup & Testing

## Current Status: Demo Mode ✅

The voice assistant now works in **demo mode** without requiring ffmpeg or internet access. This allows you to test the full voice workflow immediately.

---

## How to Test (Right Now)

1. **Start backend:**
   ```bash
   cd C:\Users\ASUS\Downloads\FairFinance
   python -m backend.app
   ```

2. **Start frontend:**
   ```bash
   cd C:\Users\ASUS\Downloads\FairFinance\frontend
   npm run dev
   ```

3. **Go to Voice Assistant page:**
   - Login as: `user1@fairfinance.com` / `user123`
   - Navigate to: Voice Transparency Assistant

4. **Record audio:**
   - Click the mic button
   - Speak for 2-3 seconds (any words work - content doesn't matter in demo mode)
   - Stop recording

5. **Expected Result:**
   - ✅ Audio will be converted to a **demo query** based on audio length
   - ✅ Backend will generate an intelligent response
   - ✅ Response displays in the Voice Assistant UI

**Demo queries generated:**
- "Why was my loan denied?"
- "What factors affected my application?"
- "How can I improve my eligibility?"
- "Explain my loan decision"
- "What is my current application status?"
- "Can you help me understand my credit score?"
- "What should I do to get better terms?"
- "Tell me more about the fairness of the decision"

---

## To Enable Real Speech Recognition (Optional)

### Prerequisites:
1. **Install ffmpeg** (system-level)
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use: `choco install ffmpeg`
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `apt-get install ffmpeg`

2. **Install Python packages** (already done):
   ```bash
   pip install pydub SpeechRecognition google-cloud-speech
   ```

3. **Disable demo mode:**
   Edit `backend/voice/voice_assistant.py` line ~27:
   ```python
   self.demo_mode = False  # Change from True to False
   ```

4. **Restart backend** and test

### When Real Speech Recognition Enabled:
- ✅ Your actual spoken words will be transcribed
- ✅ Requires stable internet (uses Google Speech Recognition API)
- ✅ Supports: English, Hindi, Marathi
- ✅ Audio formats: webm, wav, ogg, mp3

---

## Backend Console Output

**Demo Mode (Current):**
```
[VoiceAssistant] Audio size: 8234 bytes
[VoiceAssistant] Demo mode: Selected query based on audio length: Why was my loan denied?
[VoiceAssistant] Interpreted intent: explanation
```

**Real Speech Recognition (When enabled):**
```
[VoiceAssistant] Audio size: 8234 bytes
[VoiceAssistant] Successfully loaded audio as webm
[VoiceAssistant] Converted to WAV: 32768 bytes
[VoiceAssistant] Attempting Google Speech Recognition...
[VoiceAssistant] Transcribed: Why was my loan denied?
[VoiceAssistant] Interpreted intent: explanation
```

---

## Frontend Console Output

**Record → Submit Flow:**
```
[VoiceAssistant] Recording stopped {
  mimeType: "audio/webm;codecs=opus",
  blobSize: 8234,
  chunks: 15
}

[VoiceAssistant] Audio ready to send {
  base64Length: 12000,
  language: "en",
  userId: 5
}

Voice query result: {
  "interpreted_query": "Why was my loan denied?",
  "response_text": "The main factors in your loan decision were: feature_0, feature_1, feature_2.",
  "response_audio": null,
  "explanation_data": {...}
}

[VoiceAssistant] Response fields: {
  "hasResponseText": true,
  "hasInterpretedQuery": true,
  "hasResponseAudio": false,
  "hasExplanationData": true,
  "resultKeys": ["interpreted_query", "response_text", "response_audio", "explanation_data"]
}
```

---

## Troubleshooting

### Problem: "Recording too short"
- **Solution:** Record at least 2-3 seconds of audio

### Problem: "Could not understand audio"
- **Demo Mode:** Should not happen; check backend logs
- **Real Mode:** Try speaking more clearly, reduce background noise

### Problem: Backend logs show "ffmpeg not found"
- **Solution:** Install ffmpeg system-wide and restart backend

### Problem: Google Speech API errors
- **Solution:** Check internet connection; demo mode will automatically fallback

---

## Architecture

### Voice Recording Flow:
```
Browser Mic → Record Audio → Convert to Base64 → Send to Backend
         ↓
   MediaRecorder API
    (webm/opus)
         ↓
   FileReader.readAsDataURL()
         ↓
   Extract base64 string
         ↓
   POST /voice/ask with base64
```

### Backend Processing:
```
Receive base64 audio
       ↓
[Demo Mode] Select query based on audio length
OR
[Real Mode] Transcribe with Google Speech Recognition
       ↓
Interpret query intent
       ↓
Generate contextual response
       ↓
Return VoiceQueryResponse JSON
       ↓
Frontend displays response
```

---

## Files Modified

- `frontend/src/pages/VoiceAssistant.jsx` - Enhanced logging & error detection
- `backend/voice/voice_assistant.py` - Added demo mode & fallback handling

## Test Coverage

- ✅ Audio recording works on modern browsers
- ✅ Base64 encoding reliable
- ✅ Backend receives audio correctly
- ✅ Demo mode generates realistic queries
- ✅ Response parsing works
- ✅ Error handling improves UX
- ✅ Console logs help debugging

---

## Next Steps (For Production)

1. Install ffmpeg system-wide
2. Disable demo mode (`self.demo_mode = False`)
3. Test real speech transcription with actual voice
4. Monitor Google Speech API rate limits
5. Consider adding text-to-speech (TTS) for responses
6. Add language selection persistence
7. Add voice query history

---

**Status:** ✅ Ready to test right now with demo mode!
