from typing import List, Dict, Any
from app.helpers.mongo import get_courses
import logging

logger = logging.getLogger(__name__)

class CourseService:
    def __init__(self):
        self.course_data = ""
        self.courses_json = []
        self.loaded = False
    
    def load_course_data(self) -> bool:
        """Load course data from MongoDB and format for LLM."""
        try:
            # Get all courses from MongoDB using your existing helper
            self.courses_json = get_courses(limit=200)
            
            if not self.courses_json:
                logger.warning("No course data found in database")
                return False
            
            # Format courses for LLM consumption
            self.course_data = self._format_courses_for_llm(self.courses_json)
            self.loaded = True
            
            logger.info(f"Loaded {len(self.courses_json)} courses from MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"Error loading course data from MongoDB: {e}")
            self.loaded = False
            return False
    
    def _format_courses_for_llm(self, courses: List[Dict[str, Any]]) -> str:
        """Format course data for LLM consumption."""
        course_list = []
        
        for course in courses:  # Limit to avoid token limits
            # Use your existing MongoDB course structure
            course_code = course.get("COURSE", "")
            title = course.get("TITLE", "")
            instructor = course.get("INSTRUCTOR", "")
            delivery_mode = course.get("INSTRUCTION_METHOD", "")
            credits = course.get("CREDITS", "")
            days = course.get("DAYS", "")
            times = course.get("TIMES", "")
            crn = course.get("CRN", "")

            schedule = f"{days} {times}".strip()
            
            course_str = (
                f"Course {course_code}, titled {title}. "
                f"It is taught by {instructor} and is a {delivery_mode} course worth {credits} credits. "
                f"The schedule is {schedule} with CRN {crn}."
            )
            course_list.append(course_str)
        
        return "\n---\n".join(course_list)
    
    def get_course_data(self) -> str:
        """Get the formatted course data string."""
        return self.course_data
    
    def get_courses_json(self) -> List[Dict[str, Any]]:
        """Get the raw course data as JSON."""
        return self.courses_json
    
    def is_data_loaded(self) -> bool:
        """Check if course data is loaded."""
        return self.loaded

# Global instance
course_service = CourseService()

