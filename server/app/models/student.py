from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class StudentState(BaseModel):
    session_id: str
    # Major and Year Type are fixed to CS Undergrad, but kept for state tracking if needed
    major: str = "Computer Science" 
    year: Optional[str] = None
    time_preference: Optional[str] = None
    career_goals: Optional[str] = None
    follow_up_response: Optional[str] = None
    final_choice: Optional[str] = None
    last_user_query: Optional[str] = None 
    recommendation_text: Optional[str] = None 
    
    # Enhanced conversation tracking
    conversation_history: List[Dict[str, str]] = []
    recommended_courses: List[str] = []  # Track already recommended courses
    user_preferences: Dict[str, Any] = {}  # Track user likes/dislikes
    conversation_phase: str = "initial_questions"  # initial_questions, continuous_recommendations, concluded
    last_recommendation_feedback: Optional[str] = None
    current_recommendation_count: int = 0

class AdvisorResponse(BaseModel):
    next_step: str
    response_text: str
    conversation_context: Optional[Dict[str, Any]] = {}  # Additional context for frontend
