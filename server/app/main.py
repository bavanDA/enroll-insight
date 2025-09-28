from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import courses,speech,advisor
from app.services import course_service
app = FastAPI(
    title="NJIT Gemini Course Advisor",
    description="Conversational advising for NJIT CS Undergrads."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("Loading and processing course schedule data from MongoDB...")
    success = course_service.load_course_data()
    if not success:
        print("Warning: Course data failed to load from MongoDB.")
    else:
        course_count = len(course_service.get_courses_json())
        print(f"Successfully loaded {course_count} courses from MongoDB.")


# Register routes
app.include_router(speech.router)
app.include_router(courses.router)
app.include_router(advisor.router)


