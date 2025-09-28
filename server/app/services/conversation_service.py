
import time
from typing import Dict, Any
from app.models.student import StudentState
from app.config import Config

class ConversationService:
    
    @staticmethod
    def update_conversation_history(state: StudentState, role: str, message: str):
        """Add message to conversation history"""
        state.conversation_history.append({
            "role": role, 
            "message": message, 
            "timestamp": str(time.time())
        })
        # Keep only last N messages to manage context size
        if len(state.conversation_history) > Config.MAX_CONVERSATION_HISTORY:
            state.conversation_history = state.conversation_history[-Config.MAX_CONVERSATION_HISTORY:]

    @staticmethod
    def extract_user_preferences(user_response: str, state: StudentState):
        """Extract preferences from user responses (likes, dislikes, interests)"""
        user_response_lower = user_response.lower()
        
        # Simple keyword-based preference extraction
        if any(word in user_response_lower for word in ["like", "love", "enjoy", "interested", "prefer"]):
            positive_signals = state.user_preferences.get("positive_signals", [])
            positive_signals.append(user_response)
            state.user_preferences["positive_signals"] = positive_signals
        
        if any(word in user_response_lower for word in ["don't like", "dislike", "boring", "not interested", "avoid"]):
            negative_signals = state.user_preferences.get("negative_signals", [])
            negative_signals.append(user_response)
            state.user_preferences["negative_signals"] = negative_signals
        
        if any(word in user_response_lower for word in ["morning", "afternoon", "evening", "night", "online", "hybrid"]):
            state.user_preferences["time_preferences"] = user_response

    @staticmethod
    def get_conversation_context(state: StudentState, message_limit: int = None) -> str:
        """Build context from conversation history."""
        limit = message_limit or Config.MAX_RECENT_MESSAGES
        recent_messages = state.conversation_history[-limit:]
        return "\n".join([f"{msg['role']}: {msg['message']}" for msg in recent_messages])
    
    @staticmethod
    def get_preferences_context(state: StudentState) -> str:
        """Build preferences context string."""
        if not state.user_preferences:
            return ""
        import json
        return f"User Preferences: {json.dumps(state.user_preferences, indent=2)}"
    
    @staticmethod
    def should_end_conversation(user_response: str) -> bool:
        """Check if user wants to end conversation."""
        end_signals = ["done", "finish", "complete", "that's all", "no more", "goodbye", "bye", "exit"]
        return any(signal in user_response.lower() for signal in end_signals)
    
    @staticmethod
    def wants_new_recommendation(user_response: str) -> bool:
        """Check if user wants a new recommendation."""
        new_rec_signals = ["another", "next", "more", "different", "something else", "what else", "other options", "more recommendations"]
        return any(signal in user_response.lower() for signal in new_rec_signals)