import { useState, useRef, useEffect } from 'react'
import Sidebar from '../components/ui/Sidebar'
import Card from '../components/ui/Card'
import PageTitle from '../components/ui/PageTitle'
import Button from '../components/ui/Button'
import VoiceWave from '../components/ui/VoiceWave'
import { voiceService } from '../services/voiceService'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { Mic, MicOff, Globe, Volume2, VolumeX } from 'lucide-react'

const VoiceAssistant = () => {
  const { user, logout } = useAuth()
  const [recording, setRecording] = useState(false)
  const [language, setLanguage] = useState('en')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [audioPlaying, setAudioPlaying] = useState(false)
  const [error, setError] = useState(null)
  
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioRef = useRef(null)

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'mr', name: 'Marathi' }
  ]

  useEffect(() => {
    return () => {
      // Cleanup: stop recording if component unmounts
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      setError(null)
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      })
      
      // Try to use WAV format first, fallback to WebM
      let mimeType = 'audio/webm;codecs=opus'
      const options = [
        'audio/wav',
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus'
      ]
      
      // Find supported format
      for (const option of options) {
        if (MediaRecorder.isTypeSupported(option)) {
          mimeType = option
          break
        }
      }
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        // Use the actual mimeType that was selected, not hard-coded 'audio/webm'
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType })
        console.debug('[VoiceAssistant] Recording stopped', {
          mimeType: mimeType,
          blobSize: audioBlob.size,
          chunks: audioChunksRef.current.length
        })
        
        // Wait 200ms to ensure all data is flushed to blob
        await new Promise(resolve => setTimeout(resolve, 200))
        
        await processAudio(audioBlob)
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setRecording(true)
      toast.success('Recording started')
    } catch (error) {
      console.error('Error accessing microphone:', error)
      setError('Failed to access microphone. Please check permissions.')
      toast.error('Failed to access microphone')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
      setRecording(false)
      toast.success('Recording stopped')
    }
  }

  const processAudio = async (audioBlob) => {
    setLoading(true)
    setResponse(null)
    
    try {
      // Convert blob to base64
      const reader = new FileReader()
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1] // Remove data:audio/webm;base64, prefix
        
        // Validate audio: check minimum length to ensure we have real audio data
        if (!base64Audio || base64Audio.length < 5000) {
          const errorMsg = 'Recording too short. Please record at least 1-2 seconds of audio.'
          console.warn('[VoiceAssistant] Audio validation failed:', {
            base64Length: base64Audio?.length || 0,
            minRequired: 5000
          })
          setError(errorMsg)
          setLoading(false)
          toast.error(errorMsg)
          return
        }
        
        console.debug('[VoiceAssistant] Audio ready to send', {
          base64Length: base64Audio.length,
          language: language,
          userId: user?.id
        })
        
        try {
          const result = await voiceService.processQuery(
            base64Audio,
            language,
            null,
            user?.id
          )
          
          console.log('Voice query result:', JSON.stringify(result, null, 2))
          
          if (result) {
            console.debug('[VoiceAssistant] Response fields:', {
              hasResponseText: !!result.response_text,
              hasInterpretedQuery: !!result.interpreted_query,
              hasResponseAudio: !!result.response_audio,
              hasExplanationData: !!result.explanation_data,
              resultKeys: Object.keys(result)
            })
            
            // Check if transcription failed
            if (result.interpreted_query?.includes('Could not understand audio') || 
                result.interpreted_query?.includes('Error processing audio') ||
                result.interpreted_query?.includes('Error with speech recognition')) {
              console.warn('[VoiceAssistant] Audio transcription failed:', result.interpreted_query)
              setError(`Transcription failed: ${result.interpreted_query}. Try speaking more clearly or check backend logs.`)
              toast.error('Audio transcription failed. Check console for details.')
              setLoading(false)
              return
            }
            
            setResponse(result)
            
            // If TTS audio is available, play it
            if (result.response_audio) {
              console.debug('[VoiceAssistant] Playing TTS audio')
              playAudio(result.response_audio)
            }
            
            // Show success message if we got a response
            if (result.response_text) {
              toast.success('Voice query processed successfully')
            } else {
              console.warn('[VoiceAssistant] No response_text in result')
            }
          } else {
            setError('No response received from voice assistant')
            toast.error('No response received from voice assistant')
          }
        } catch (error) {
          console.error('Error processing voice query:', error)
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to process voice query'
          setError(errorMessage)
          toast.error(errorMessage)
        } finally {
          setLoading(false)
        }
      }
      reader.onerror = () => {
        setError('Failed to read audio file')
        toast.error('Failed to read audio file')
        setLoading(false)
      }
      reader.readAsDataURL(audioBlob)
    } catch (error) {
      console.error('Error processing audio:', error)
      setError('Failed to process audio')
      toast.error('Failed to process audio')
      setLoading(false)
    }
  }

  const playAudio = (audioData) => {
    try {
      // If audioData is base64, convert it
      const audioBlob = base64ToBlob(audioData, 'audio/mpeg')
      const audioUrl = URL.createObjectURL(audioBlob)
      
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.src = ''
      }
      
      const audio = new Audio(audioUrl)
      audioRef.current = audio
      
      audio.onplay = () => setAudioPlaying(true)
      audio.onended = () => {
        setAudioPlaying(false)
        URL.revokeObjectURL(audioUrl)
      }
      audio.onerror = () => {
        setAudioPlaying(false)
        toast.error('Failed to play audio response')
      }
      
      audio.play()
    } catch (error) {
      console.error('Error playing audio:', error)
      toast.error('Failed to play audio response')
    }
  }

  const base64ToBlob = (base64, mimeType) => {
    const byteCharacters = atob(base64)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    return new Blob([byteArray], { type: mimeType })
  }

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setAudioPlaying(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onLogout={logout} />
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <PageTitle
            title="Voice Transparency Assistant"
            subtitle="Ask questions about your loan decisions in your preferred language"
            icon={Mic}
          />

          {/* Language Selection */}
          <Card className="mb-6">
            <label className="block text-sm font-semibold text-navy-900 mb-4">
              Select Language
            </label>
            <div className="flex flex-wrap gap-3">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                    language === lang.code
                      ? 'bg-primary-500 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Globe className="w-4 h-4" />
                  {lang.name}
                </button>
              ))}
            </div>
          </Card>

          {/* Recording Interface */}
          <Card className="mb-6">
            <div className="flex flex-col items-center justify-center py-12">
              {!recording ? (
                <button
                  onClick={startRecording}
                  className="flex items-center justify-center w-32 h-32 rounded-full bg-primary-500 hover:bg-primary-600 text-white shadow-xl hover:shadow-2xl transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-primary-300"
                  disabled={loading}
                >
                  <Mic className="w-16 h-16" />
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="flex items-center justify-center w-32 h-32 rounded-full bg-red-500 hover:bg-red-600 text-white shadow-xl hover:shadow-2xl transition-all duration-200 transform hover:scale-105 animate-pulse focus:outline-none focus:ring-4 focus:ring-red-300"
                >
                  <MicOff className="w-16 h-16" />
                </button>
              )}
              
              <p className="mt-6 text-lg font-medium text-gray-700">
                {recording ? 'Recording... Click to stop' : loading ? 'Processing your query...' : 'Click to start recording'}
              </p>
              
              {(recording || loading) && (
                <div className="mt-6 w-full max-w-md">
                  <VoiceWave isActive={recording || loading} />
                </div>
              )}
            </div>
          </Card>

          {/* Error Display */}
          {error && (
            <Card className="mb-6 border-l-4 border-red-500 bg-red-50">
              <div className="flex items-start gap-3">
                <div className="text-red-500 mt-0.5">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-red-800 mb-1">Error</h3>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </Card>
          )}

          {/* Loading State */}
          {loading && (
            <Card className="mb-6">
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mr-3"></div>
                <span className="text-gray-700 font-medium">Processing your query...</span>
              </div>
            </Card>
          )}

          {/* Response Display */}
          {response && (
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-navy-900">Response</h2>
                {response.response_audio && (
                  <button
                    onClick={audioPlaying ? stopAudio : () => playAudio(response.response_audio)}
                    className="p-2 rounded-lg bg-primary-100 hover:bg-primary-200 text-primary-600 transition-colors"
                  >
                    {audioPlaying ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                  </button>
                )}
              </div>
              
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Your question:</strong>
                </p>
                <p className="text-blue-900 font-medium">{response.interpreted_query || 'Processing...'}</p>
              </div>
              
              <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Answer:</strong>
                </p>
                <p className="text-gray-900">{response.response_text || 'No response available'}</p>
              </div>

              {response.explanation_data && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm font-semibold text-gray-900 mb-2">Additional Details:</p>
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(response.explanation_data, null, 2)}
                  </pre>
                </div>
              )}
            </Card>
          )}

          {/* Instructions */}
          <Card className="mt-6">
            <h3 className="text-lg font-semibold text-navy-900 mb-4">How to use</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Select your preferred language (English, Hindi, or Marathi)</li>
              <li>Click the microphone button to start recording</li>
              <li>Ask questions about your loan decision, such as:
                <ul className="list-disc list-inside ml-6 mt-2 space-y-1 text-gray-600">
                  <li>"Why was my loan denied?"</li>
                  <li>"What factors affected my application?"</li>
                  <li>"How can I improve my eligibility?"</li>
                  <li>"Explain my loan decision"</li>
                </ul>
              </li>
              <li>Click again to stop recording and get your answer</li>
              <li>Listen to the audio response if available</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default VoiceAssistant
