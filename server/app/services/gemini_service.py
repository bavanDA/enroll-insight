import time
from fastapi import HTTPException
from google import genai
from google.genai import types
from app.config import Config

class GeminiService:
    def __init__(self):
        self.client = genai.Client() if not Config.GEMINI_API_KEY else genai.Client(api_key=Config.GEMINI_API_KEY)
    
    async def call_with_retry(
        self, 
        prompt: str, 
        system_instruction: str, 
        max_retries: int = None,
        model: str = None
    ) -> str:
        """Handles the Gemini API call with exponential backoff for robustness."""
        max_retries = max_retries or Config.GEMINI_MAX_RETRIES
        model = model or Config.GEMINI_MODEL
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(system_instruction=system_instruction),
                )
                return response.candidates[0].content.parts[0].text.strip()
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Gemini API call failed (attempt {attempt + 1}). Retrying in {wait_time}s. Error: {e}")
                    time.sleep(wait_time)
                else:
                    raise HTTPException(status_code=500, detail=f"Gemini API call failed after {max_retries} attempts: {e}")
        raise HTTPException(status_code=500, detail="Unknown error during Gemini API call.")
    
    async def validate_answer(self, field: str, question: str, answer: str, retries: int) -> str:
        """Uses Gemini to validate the user's answer and generate the next prompt."""
        system_instruction = (
            "You are an NJIT academic advisor. Your task is to confirm the student's answer. "
            "Your responses must be extremely short, clear, and highly conversational for text-to-speech. Do not use markdown characters or bullet points. "
            "Rules:\n"
            "- If the answer is valid/meaningful → Respond with a polite, *one-sentence* confirmation, e.g., 'Got it. Moving to the next question.'\n"
            "- If invalid/irrelevant and retries < 2 → Start your response with 'REPEAT:' and politely say they didn't answer correctly, then clearly repeat the question.\n"
            "- If invalid again (retries == 2) → Start your response with 'SKIP:' and say 'I'll skip this for now and move on.'\n"
            "Do not include any other text besides the required output."
        )

        user_prompt = f"""
        Question: {question}
        Field: {field}
        Student Answer: {answer if answer else "[no response]"}
        Retry Count: {retries}
        """
        
        return await self.call_with_retry(user_prompt, system_instruction)