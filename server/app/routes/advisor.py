from fastapi import APIRouter, HTTPException
from app.models.student import StudentState, AdvisorResponse
from app.services.advisor_service import AdvisorService

router = APIRouter(prefix="/advise", tags=["advisor"])
advisor_service = AdvisorService()

@router.post("/next_step", response_model=AdvisorResponse)
async def next_conversation_step(state: StudentState):
    """Main endpoint for advisor conversation flow."""
    return await advisor_service.process_next_step(state)

# Additional endpoints can be added here
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "NJIT Course Advisor"}

@router.post("/reset_session")
async def reset_session(session_id: str):
    """Reset a conversation session."""
    # Clear retry tracker for this session
    if hasattr(advisor_service, 'retry_tracker') and session_id in advisor_service.retry_tracker:
        del advisor_service.retry_tracker[session_id]
    return {"message": f"Session {session_id} has been reset"}