import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 🔹 Course schedule
    SCHEDULE_FILE_PATH = "Course_Schedule.csv"

    # 🔹 Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash"

    # 🔹 Azure Speech API
    AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
    AZURE_SPEECH_ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")

    # 🔹 Retry settings
    RETRY_LIMIT = 2

    MONGO_URI =  os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME", "njit_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "courses")
    SOURCE_URL = (
        "https://generalssb-prod.ec.njit.edu/"
        "BannerExtensibility/internalPb/virtualDomains.stuRegCrseSchedSectionsExcel"
        "?MTM%3DdGVybQ%3D%3D=NDA%3DMjAyNTkw&MTg%3DYXR0cg%3D%3D=OTI%3D&NA%3D%3Dc3ViamVjdA%3D%3D=NTU%3DQ1M%3D"
        "&NTU%3DcHJvZl91Y2lk=NTg%3Dundefined&encoded=true"
    )
    
    # Retry Configuration
    RETRY_LIMIT = 2
    GEMINI_MAX_RETRIES = 3
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # API Request Configuration
    REQUEST_TIMEOUT = 30
    
    # Conversation Configuration
    MAX_CONVERSATION_HISTORY = 20
    MAX_RECENT_MESSAGES = 10

# CS Curriculum Constants
CS_PLAN_OF_STUDY = """
NJIT B.S. in Computer Science Official Catalog Details (120 credits minimum):
---
Plan of Study Grid:
First Year 1st Semester: CS 100 (Roadmap to Computing, 3), MATH 111 (Calculus I, 4), ENGL 101 (English Composition, 3), PHYS 111 (Physics I, 3), PHYS 111A (Physics I Lab, 1). Term Credits: 14.
First Year 2nd Semester: CS 113 (Introduction to Computer Science I, 3), MATH 112 (Calculus II, 4), ENGL 102 (Composition for Research, 3), PHYS 121 (Physics II, 3), PHYS 121A (Physics II Lab, 1). Term Credits: 14.
Second Year 1st Semester: CS 114 (Introduction to Computer Science II, 3), CS/IS/IT Elective 200 or above (3), MATH 333 (Probability and Statistics, 3), Science Elective (3), History and Humanities GER 200 level (3). Term Credits: 15.
Second Year 2nd Semester: CS 241 (Foundations of Computer Science I, 3), CS 280 (Programming Language Concepts, 3), IS 350 (Computers, Society and Ethics, 3), COM 312 or COM 313 (Oral Presentations or Technical Writing, 3), MATH 337 (Linear Algebra, 3), YWCC 207 (Computing & Effective Com, 1). Term Credits: 16.
Third Year 1st Semester: CS 288 (Intensive Programming in Linux, 3), CS 332 (Principles of Operating Systems, 3), Social Sciences GER (3), CS 301 (Introduction to Data Science, 3), CS 356 (Introduction to Computer Networks, 3). Term Credits: 15.
Third Year 2nd Semester: CS 331 (Database System Design & Mgmt, 3), YWCC 307 (Professional Dev in Computing, 1), CS Elective 300 or above (3), CS 341 (Foundations of Computer Science II, 3), CS 350 (Intro to Computer Systems, 3), CS 351 (Introduction to Cybersecurity, 3). Term Credits: 16.
Fourth Year 1st Semester: CS 435 (Advanced Data Structures and Algorithm Design, 3), CS 490 (Guided Design in Software Engineering, 3), History and Humanities GER 300+ level (3), CS Elective 300 or above (3), CS Elective 300 or above (3). Term Credits: 15.
Fourth Year 2nd Semester: CS 491 (Senior Project, 3), Humanities and Social Science Senior Seminar GER (3), CS Elective 300 or above (3), General Elective (3), CS/IS/IT Elective 200 or above (3). Term Credits: 15.
Total Credits: 120.
---
ELECTIVE REQUIREMENTS AND RESTRICTIONS:
1. CS/IS/IT Elective: Two 3-credit CS/IS/IT electives (200-level or above) are required.
2. General Elective: Any 3 credit course except a course that is already required for your program or any course covering prerequisite material for first semester courses in your program.
3. Courses that CANNOT count as electives: ENGL 099, PHYS 102, MATH 105, MATH 107, MATH 244, MATH 226, MATH 326, MATH 341, DS 340, IS 331.
4. CS/IS/IT 485 special topic courses: Students can only use up to 6 credits from CS/IS/IT 485 with at most 3 credits of IS/IT 485 as electives towards graduation.
---
MINIMUM GRADES:
- Students must earn a grade of B or better in CS 100.
- Students must earn a grade of C or better in all CS courses that serve as prerequisites in a sequence of courses.
---
ADVISING NOTES:
- A full-time credit load is 12 credits.
- First-year students are placed in a curriculum that positions them for success which may result in additional time needed to complete curriculum requirements.
"""

# Questions Configuration
ADVISOR_QUESTIONS = [
    {"field": "year", "question": "What Student Year are you in? (e.g., Freshman, Junior)"},
    {"field": "time_preference", "question": "What is your preferred time for classes? (e.g., Morning, Evening, Online)"},
    {"field": "career_goals", "question": "What are your primary Career Goals? (e.g., Software Engineer, Cybersecurity, Data Science)"},
]