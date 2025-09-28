import json
from typing import Dict
from app.models.student import StudentState, AdvisorResponse
from app.services.gemini_service import GeminiService
from app.services.course_service import course_service
from app.services.conversation_service import ConversationService
from app.helpers.data_processing import extract_course_from_text
from app.config import Config, ADVISOR_QUESTIONS, CS_PLAN_OF_STUDY

class AdvisorService:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.conversation_service = ConversationService()
        self.retry_tracker: Dict[str, Dict[str, int]] = {}
    
    def _ensure_retry_tracker(self, session_id: str):
        """Ensure retry tracker exists for session."""
        if session_id not in self.retry_tracker:
            self.retry_tracker[session_id] = {}
    
    async def generate_next_course_recommendation(self, state: StudentState) -> str:
        """Generate the next course recommendation based on conversation history and preferences"""
        
        # Build context from conversation history
        conversation_context = self.conversation_service.get_conversation_context(state)
        
        # Build preferences context
        preferences_context = self.conversation_service.get_preferences_context(state)
        
        # Build excluded courses context - be more explicit
        excluded_courses = ", ".join(state.recommended_courses) if state.recommended_courses else "None"
        
        # Create a more explicit system instruction to avoid repetition
        system_instruction = (
            "You are a conversational NJIT Computer Science academic advisor. The student wants ANOTHER course recommendation. "
            f"CRITICAL: You have already recommended these courses: {excluded_courses}. "
            "DO NOT recommend any of these courses again. Find a DIFFERENT course that fits their profile. "
            "For a freshman CS student, good options include: MATH 111 (Calculus I), ENGL 101 (English Composition), "
            "PHYS 111 (Physics I), or other first-year requirements from the curriculum. "
            "Be conversational, mention the specific course details including CRN, and ask if they want more options. "
            "Keep response to 2-3 sentences maximum."
        )
        
        user_prompt = (
            f"CURRICULUM GUIDE:\n{CS_PLAN_OF_STUDY}\n\n"
            f"STUDENT PROFILE:\nMajor: {state.major}, Year: {state.year}, "
            f"Time Preference: {state.time_preference}, Career Goals: {state.career_goals}\n\n"
            f"CONVERSATION HISTORY:\n{conversation_context}\n\n"
            f"USER PREFERENCES:\n{preferences_context}\n\n"
            f"COURSES ALREADY RECOMMENDED (MUST NOT REPEAT): {excluded_courses}\n\n"
            f"RECOMMENDATION COUNT: {state.current_recommendation_count}\n\n"
            f"AVAILABLE COURSES (pick a DIFFERENT course than already recommended):\n{course_service.get_course_data()}"
        )
        
        return await self.gemini_service.call_with_retry(user_prompt, system_instruction)

    async def handle_user_feedback(self, state: StudentState, user_response: str) -> str:
        """Handle user feedback and generate appropriate response"""
        
        # Update conversation history
        self.conversation_service.update_conversation_history(state, "user", user_response)
        
        # Extract preferences from user response
        self.conversation_service.extract_user_preferences(user_response, state)
        
        # Check if user wants to end conversation
        if self.conversation_service.should_end_conversation(user_response):
            state.conversation_phase = "concluded"
            return "Thank you for the great conversation! Feel free to come back anytime if you need more course recommendations. Good luck with your studies!"
        
        # Check if user wants a new recommendation
        if self.conversation_service.wants_new_recommendation(user_response):
            return await self.generate_next_course_recommendation(state)
        
        # Generate contextual response based on their feedback
        system_instruction = (
            "You are a conversational NJIT academic advisor. The student just gave you feedback about a course recommendation. "
            "Respond naturally to their comment, acknowledge their feedback, and then smoothly transition to asking "
            "if they'd like another recommendation or have specific questions. "
            "Keep your response conversational, engaging, and under 2 sentences for text-to-speech clarity. "
            "Always end with a question to keep the conversation going."
        )
        
        conversation_context = self.conversation_service.get_conversation_context(state, 5)
        
        user_prompt = (
            f"Student just said: '{user_response}'\n\n"
            f"Recent conversation context:\n{conversation_context}\n\n"
            f"Student profile: {state.year} {state.major} student interested in {state.career_goals}"
        )
        
        return await self.gemini_service.call_with_retry(user_prompt, system_instruction)

    async def process_next_step(self, state: StudentState) -> AdvisorResponse:
        """Main method to process the next conversation step."""
        
        # Ensure course data is loaded
        if not course_service.is_data_loaded():
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Course schedule data not available.")

        # Ensure retry tracker exists for this session
        self._ensure_retry_tracker(state.session_id)

        # Handle concluded conversations
        if state.conversation_phase == "concluded":
            return AdvisorResponse(
                next_step="complete", 
                response_text="Our conversation has ended. Would you like to start a new session?"
            )

        # Handle continuous recommendations phase
        if state.conversation_phase == "continuous_recommendations":
            if state.last_user_query:
                # Check if user wants a new recommendation explicitly
                wants_new_rec = self.conversation_service.wants_new_recommendation(state.last_user_query)
                
                if wants_new_rec:
                    # Generate new recommendation
                    state.current_recommendation_count += 1
                    advisor_response = await self.generate_next_course_recommendation(state)
                    
                    # Extract and track the new course recommendation
                    course_found = extract_course_from_text(advisor_response)
                    
                    if course_found and course_found not in state.recommended_courses:
                        state.recommended_courses.append(course_found)
                        print(f"Added new course to recommended list: {course_found}")
                    
                else:
                    # Handle general feedback/questions
                    advisor_response = await self.handle_user_feedback(state, state.last_user_query)
                
                self.conversation_service.update_conversation_history(state, "user", state.last_user_query)
                self.conversation_service.update_conversation_history(state, "advisor", advisor_response)
                
                return AdvisorResponse(
                    next_step="continuous_conversation", 
                    response_text=advisor_response,
                    conversation_context={
                        "phase": state.conversation_phase,
                        "recommendation_count": state.current_recommendation_count,
                        "recommended_courses": state.recommended_courses,
                        "history_length": len(state.conversation_history)
                    }
                )

        # Handle initial questions logic (Steps 1-3)
        for idx, q in enumerate(ADVISOR_QUESTIONS):
            field = q["field"]
            question_text = q["question"]
            user_answer = getattr(state, field)
            retries = self.retry_tracker[state.session_id].get(field, 0)
            
            if user_answer is None:
                return AdvisorResponse(next_step=field, response_text=question_text)

            if retries == 0 and user_answer is not None:
                continue
            
            if retries > Config.RETRY_LIMIT and user_answer is not None:
                continue
            
            if user_answer is not None and retries <= Config.RETRY_LIMIT:
                advisor_reply = await self.gemini_service.validate_answer(field, question_text, user_answer, retries)
                
                if advisor_reply.upper().startswith("REPEAT:"):
                    self.retry_tracker[state.session_id][field] = retries + 1
                    return AdvisorResponse(next_step=field, response_text=advisor_reply.replace("REPEAT:", "").strip())
                
                elif advisor_reply.upper().startswith("SKIP:"):
                    self.retry_tracker[state.session_id][field] = Config.RETRY_LIMIT + 1
                    next_field = ADVISOR_QUESTIONS[idx + 1]['field'] if idx + 1 < len(ADVISOR_QUESTIONS) else 'follow_up_response'
                    return AdvisorResponse(next_step=next_field, response_text=advisor_reply.replace("SKIP:", "").strip())
                
                else:
                    self.retry_tracker[state.session_id][field] = 0
                    next_field = ADVISOR_QUESTIONS[idx + 1]['field'] if idx + 1 < len(ADVISOR_QUESTIONS) else 'follow_up_response'
                    
                    if next_field == 'follow_up_response':
                        confirmation_message = advisor_reply.strip()
                        
                        system_instruction_step5 = (
                            "You are an expert, friendly, and encouraging NJIT advisor. The student has answered the three initial questions. "
                            "Acknowledge the last answer briefly, then smoothly transition into asking three distinct, personalized follow-up questions to prepare for the final recommendation. "
                            "Your response must be highly conversational and clear for text-to-speech. Your entire response must be under 3 short sentences. Do not use markdown characters, lists, or symbols in your response. Do not give any recommendations yet."
                        )
                        user_prompt_step5 = (
                            f"Acknowledge this confirmation first: '{confirmation_message}'\n\n"
                            f"Student Profile:\nMajor: {state.major}, Year: {state.year}, "
                            f"Time Preference: {state.time_preference}, Career Goals: {state.career_goals}\n\n"
                            f"Course Data:\n{course_service.get_course_data()}"
                        )
                        advisor_text_step5 = await self.gemini_service.call_with_retry(user_prompt_step5, system_instruction_step5)
                        return AdvisorResponse(next_step="follow_up_response", response_text=advisor_text_step5)
                    
                    return AdvisorResponse(next_step=next_field, response_text=advisor_reply.strip())
                
        # Step 5: Ask Follow-up Questions
        if state.follow_up_response is None:
            system_instruction = (
                "You are an expert, friendly, and encouraging NJIT advisor. The student has finished the initial questions. "
                "You must now ask three distinct, personalized follow-up questions to prepare for the final recommendation. "
                "Your response must be highly conversational and clear for text-to-speech. Your entire response must be under 3 short sentences. Do not use markdown characters, lists, or symbols in your response. Do not give any recommendations yet."
            )
            user_prompt = (
                f"Profile:\nMajor: {state.major}, Year: {state.year}, "
                f"Time Preference: {state.time_preference}, Career Goals: {state.career_goals}\n\n"
                f"Course Data:\n{course_service.get_course_data()}"
            )

            print(course_service.get_course_data())
            advisor_text = await self.gemini_service.call_with_retry(user_prompt, system_instruction)
            return AdvisorResponse(next_step="follow_up_response", response_text=advisor_text)

        # Step 6: First recommendation and transition to continuous mode
        if state.final_choice is None and state.conversation_phase == "initial_questions":
            # Generate first recommendation
            system_instruction = (
                "You are an NJIT Computer Science Academic Advisor. Based on all collected info, "
                "provide the single best-fit course recommendation. Be highly conversational and accessible for text-to-speech. "
                "Quote the course details directly from the provided schedule data. "
                "Do not use greetings or re-introductions. Start directly with the recommendation. "
                "End by asking if they'd like more recommendations or have questions about this course. "
                "Keep your response to exactly 3 concise sentences maximum."
            )
            recommendation_prompt = (
                f"CURRICULUM GUIDE:\n{CS_PLAN_OF_STUDY}\n\n"
                f"STUDENT PROFILE:\nMajor: {state.major}, Year: {state.year}, "
                f"Time Preference: {state.time_preference}, Career Goals: {state.career_goals}\n"
                f"Follow-up Answers:\n{state.follow_up_response}\n\n"
                f"AVAILABLE COURSES:\n{course_service.get_course_data()}"
            )
            advisor_text = await self.gemini_service.call_with_retry(recommendation_prompt, system_instruction)
            
            # Extract course name from recommendation and add to recommended courses
            course_found = extract_course_from_text(advisor_text)
            
            if course_found and course_found not in state.recommended_courses:
                state.recommended_courses.append(course_found)
                print(f"Added course to recommended list: {course_found}")
            
            # Transition to continuous recommendations phase
            state.conversation_phase = "continuous_recommendations"
            state.recommendation_text = advisor_text
            state.current_recommendation_count = 1
            
            # Add to conversation history
            self.conversation_service.update_conversation_history(state, "advisor", advisor_text)
            
            return AdvisorResponse(
                next_step="first_recommendation_given", 
                response_text=advisor_text,
                conversation_context={
                    "phase": state.conversation_phase,
                    "recommendation_count": state.current_recommendation_count
                }
            )
        
        # Default: Continue conversation
        return AdvisorResponse(
            next_step="continuous_conversation", 
            response_text="I'm here to help you with more course recommendations! What would you like to know?",
            conversation_context={
                "phase": state.conversation_phase,
                "recommendation_count": state.current_recommendation_count
            }
        )

