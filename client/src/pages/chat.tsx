import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface StudentState {
  session_id: string;
  major?: string;
  year?: string;
  time_preference?: string;
  career_goals?: string;
  follow_up_response?: string;
  final_choice?: string;
  last_user_query?: string;
  recommendation_text?: string;
  conversation_history: { role: string; message: string; timestamp: string }[];
  recommended_courses: string[];
  user_preferences: Record<string, any>;
  conversation_phase: string;
  last_recommendation_feedback?: string;
  current_recommendation_count: number;
}

interface AdvisorResponse {
  next_step: string;
  response_text: string;
  conversation_context?: Record<string, any>;
}

interface Message {
  role: 'user' | 'advisor';
  text: string;
  timestamp: string;
  audioUrl?: string;
}

const Chat: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId] = useState(uuidv4());
  const [currentField, setCurrentField] = useState<string>('year');
  const [state, setState] = useState<StudentState>({
    session_id: sessionId,
    major: 'Computer Science',
    conversation_history: [],
    recommended_courses: [],
    user_preferences: {},
    conversation_phase: 'initial_questions',
    current_recommendation_count: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Speech features - Fixed implementation
  const [isRecording, setIsRecording] = useState(false);
  const [speechLoading, setSpeechLoading] = useState<string | null>(null);
  const [playingAudio, setPlayingAudio] = useState<string | null>(null);
  const [autoPlaySpeech, setAutoPlaySpeech] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // Initialize conversation
  useEffect(() => {
    initializeChat();
  }, []);

  // Cleanup audio resources
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const initializeChat = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/advise/next_step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          major: 'Computer Science',
          conversation_history: [],
          recommended_courses: [],
          user_preferences: {},
          conversation_phase: 'initial_questions',
          current_recommendation_count: 0,
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: AdvisorResponse = await response.json();
      const advisorMessage: Message = {
        role: 'advisor',
        text: data.response_text,
        timestamp: new Date().toISOString()
      };

      setMessages([advisorMessage]);
      setCurrentField(data.next_step);
      setError(null);

      // Auto-play initial message if enabled
      if (autoPlaySpeech) {
        await playTextToSpeech(data.response_text, 0);
      }
    } catch (err) {
      console.error('Error initializing chat:', err);
      setError('Failed to initialize chat. Please try again.');
      setMessages([{
        role: 'advisor',
        text: 'Hello! I\'m your NJIT Course Advisor. What year are you in? (e.g., Freshman, Sophomore, Junior, Senior)',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Fixed recording implementation
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      });
      
      streamRef.current = stream;
      chunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm;codecs=opus' });
        await handleRecordingComplete(audioBlob);
        
        // Cleanup
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setError(null);
      
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setSpeechLoading('transcribing');
    }
  };

  // Handle completed recording
  const handleRecordingComplete = async (audioBlob: Blob) => {
    try {
      setSpeechLoading('transcribing');

      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');

      const response = await fetch('http://localhost:8000/speech/speech-to-text', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to transcribe audio');
      }

      const data = await response.json();
      setInput(data.transcript);
      setSpeechLoading(null);
      
      // Automatically send the transcribed message
      if (data.transcript && data.transcript.trim()) {
        setTimeout(() => {
          sendMessageWithText(data.transcript);
        }, 100);
      }
      
    } catch (err) {
      console.error('Error transcribing audio:', err);
      setError('Failed to transcribe audio. Please try again.');
      setSpeechLoading(null);
    }
  };

  // Convert text to speech and play
  const playTextToSpeech = async (text: string, messageIndex: number) => {
    try {
      setSpeechLoading(`tts-${messageIndex}`);
      setPlayingAudio(`message-${messageIndex}`);

      const formData = new FormData();
      formData.append('text', text);

      const response = await fetch('http://localhost:8000/speech/text-to-speech', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to generate speech');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // Update message with audio URL
      setMessages(prev => prev.map((msg, idx) => 
        idx === messageIndex ? { ...msg, audioUrl } : msg
      ));

      // Play audio
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.onended = () => {
          setPlayingAudio(null);
          URL.revokeObjectURL(audioUrl);
        };
        await audioRef.current.play();
      }

      setSpeechLoading(null);
    } catch (err) {
      console.error('Error generating speech:', err);
      setError('Failed to generate speech. Please try again.');
      setSpeechLoading(null);
      setPlayingAudio(null);
    }
  };

  // Stop playing audio
  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setPlayingAudio(null);
  };

  // Send message with custom text (for transcribed audio)
  const sendMessageWithText = async (messageText: string) => {
    if (!messageText.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      text: messageText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    // Update the appropriate field based on current step
    let updatedState = { ...state };
    
    if (currentField === 'year') {
      updatedState.year = messageText;
    } else if (currentField === 'time_preference') {
      updatedState.time_preference = messageText;
    } else if (currentField === 'career_goals') {
      updatedState.career_goals = messageText;
    } else if (currentField === 'follow_up_response') {
      updatedState.follow_up_response = messageText;
    } else {
      updatedState.last_user_query = messageText;
    }

    // Update conversation history
    const conversationHistoryEntry = {
      role: 'user',
      message: messageText,
      timestamp: new Date().toISOString()
    };

    updatedState.conversation_history = [
      ...state.conversation_history,
      conversationHistoryEntry
    ];

    setInput('');

    try {
      const response = await fetch('http://localhost:8000/advise/next_step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedState)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: AdvisorResponse = await response.json();
      const advisorMessage: Message = {
        role: 'advisor',
        text: data.response_text,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, advisorMessage]);

      // Add advisor response to conversation history
      const advisorHistoryEntry = {
        role: 'advisor',
        message: data.response_text,
        timestamp: new Date().toISOString()
      };

      const finalUpdatedState = {
        ...updatedState,
        conversation_history: [
          ...updatedState.conversation_history,
          advisorHistoryEntry
        ]
      };

      setState(finalUpdatedState);
      setCurrentField(data.next_step);

      // Update conversation context if provided
            if (data.conversation_context) {
              const ctx = data.conversation_context;
              setState(prev => ({
                ...prev,
                conversation_phase: ctx.phase ?? prev.conversation_phase,
                current_recommendation_count: ctx.recommendation_count ?? prev.current_recommendation_count,
                recommended_courses: ctx.recommended_courses ?? prev.recommended_courses
              }));
            }

      // Auto-play advisor response if enabled
      if (autoPlaySpeech) {
        const messageIndex = messages.length + 1; // +1 because we just added the advisor message
        setTimeout(() => playTextToSpeech(data.response_text, messageIndex), 500);
      }

    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message. Please try again.');
      
      const errorMessage: Message = {
        role: 'advisor',
        text: 'Sorry, I encountered an error. Please try again or rephrase your message.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Regular send message (for typed input)
  const sendMessage = async () => {
    await sendMessageWithText(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading && !isRecording) {
      sendMessage();
    }
  };

  const resetChat = () => {
    setMessages([]);
    setState({
      session_id: uuidv4(),
      major: 'Computer Science',
      conversation_history: [],
      recommended_courses: [],
      user_preferences: {},
      conversation_phase: 'initial_questions',
      current_recommendation_count: 0,
    });
    setCurrentField('year');
    setError(null);
    stopAudio();
    
    // Stop any ongoing recording
    if (isRecording && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
    
    initializeChat();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold text-center text-blue-800">🎓 NJIT Course Advisor</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setAutoPlaySpeech(!autoPlaySpeech)}
            className={`px-4 py-2 rounded transition-colors ${
              autoPlaySpeech 
                ? 'bg-green-500 hover:bg-green-600 text-white' 
                : 'bg-gray-300 hover:bg-gray-400 text-gray-700'
            }`}
            title="Auto-play advisor responses"
          >
            🔊 {autoPlaySpeech ? 'ON' : 'OFF'}
          </button>
          <button
            onClick={resetChat}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded transition-colors"
          >
            Reset Chat
          </button>
        </div>
      </div>

      {/* Status Display */}
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
        <div className="text-sm text-blue-700">
          <strong>Session:</strong> {sessionId.slice(0, 8)}... |{' '}
          <strong>Phase:</strong> {state.conversation_phase.replace('_', ' ')} |{' '}
          <strong>Recommendations:</strong> {state.current_recommendation_count} |{' '}
          <strong>Auto-play:</strong> {autoPlaySpeech ? 'Enabled' : 'Disabled'}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Chat Messages */}
      <div className="border rounded-lg p-4 h-[500px] overflow-y-auto bg-gray-50 mb-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            {loading ? 'Initializing chat...' : 'No messages yet'}
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`my-3 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
              <div className={`inline-block max-w-[80%] px-4 py-3 rounded-lg ${
                msg.role === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white border border-gray-300 text-gray-800'
              }`}>
                <div className="whitespace-pre-wrap">{msg.text}</div>
                
                {/* Audio controls for advisor messages */}
                {msg.role === 'advisor' && (
                  <div className="flex items-center gap-2 mt-2">
                    {speechLoading === `tts-${index}` ? (
                      <div className="flex items-center text-xs text-gray-500">
                        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-gray-500 mr-1"></div>
                        Generating speech...
                      </div>
                    ) : playingAudio === `message-${index}` ? (
                      <button
                        onClick={stopAudio}
                        className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded"
                      >
                        ⏹️ Stop
                      </button>
                    ) : (
                      <button
                        onClick={() => playTextToSpeech(msg.text, index)}
                        className="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded"
                        disabled={!!speechLoading}
                      >
                        🔊 Play
                      </button>
                    )}
                  </div>
                )}
                
                <div className={`text-xs mt-1 ${
                  msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="text-left my-3">
            <div className="inline-block bg-white border border-gray-300 text-gray-800 px-4 py-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span>Advisor is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area with Speech Controls */}
      <div className="flex gap-3 items-end">
        <div className="flex-1">
          <input
            type="text"
            className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={
              speechLoading === 'transcribing' ? 'Transcribing your speech...' :
              currentField === 'year' ? 'What year are you in? (e.g., Freshman, Senior)' :
              currentField === 'time_preference' ? 'What\'s your preferred time? (e.g., Morning, Evening)' :
              currentField === 'career_goals' ? 'What are your career goals? (e.g., Software Engineer)' :
              currentField === 'follow_up_response' ? 'Tell me more about your preferences...' :
              'Type your message here...'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading || isRecording || speechLoading === 'transcribing'}
          />
        </div>
        
        {/* Voice Recording Button */}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={loading || speechLoading === 'transcribing'}
          className={`px-4 py-3 rounded-lg font-medium transition-colors min-w-[60px] ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
              : 'bg-green-500 hover:bg-green-600 text-white'
          } disabled:bg-gray-400`}
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
        >
          {isRecording ? '⏹️' : '🎤'}
        </button>

        {/* Send Button */}
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim() || isRecording}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>...</span>
            </div>
          ) : (
            'Send'
          )}
        </button>
      </div>

      {/* Recording Status */}
      {isRecording && (
        <div className="mt-2 text-center">
          <div className="inline-flex items-center gap-2 bg-red-100 border border-red-300 text-red-700 px-3 py-1 rounded-lg">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm">Recording... Click stop when finished</span>
          </div>
        </div>
      )}

      {/* Speech Loading Status */}
      {speechLoading === 'transcribing' && (
        <div className="mt-2 text-center">
          <div className="inline-flex items-center gap-2 bg-blue-100 border border-blue-300 text-blue-700 px-3 py-1 rounded-lg">
            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-500"></div>
            <span className="text-sm">Converting speech to text...</span>
          </div>
        </div>
      )}

      {/* Hidden audio element for playing TTS */}
      <audio ref={audioRef} hidden />

      {/* Debug Info */}
      <details className="mt-4 text-xs">
        <summary className="cursor-pointer text-gray-500">Debug Info</summary>
        <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
          {JSON.stringify({ 
            ...state, 
            speechFeatures: { 
              isRecording, 
              speechLoading, 
              playingAudio, 
              autoPlaySpeech,
              mediaRecorderState: mediaRecorderRef.current?.state || 'inactive',
              streamActive: streamRef.current?.active || false
            } 
          }, null, 2)}
        </pre>
      </details>
    </div>
  );
};

export default Chat;