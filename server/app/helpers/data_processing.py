from typing import Optional, Dict, Any, List

def extract_course_from_text(text: str) -> Optional[str]:
    """Extract course code from recommendation text."""
    import re
    course_patterns = [
        r'Course ([A-Z]+\s*\d+)',  # "Course CS100"
        r'([A-Z]+\s*\d+),',        # "CS100,"
        r'([A-Z]+\s*\d+)\s+titled', # "CS100 titled"
        r'recommend\s+([A-Z]+\s*\d+)', # "recommend CS100"
    ]
    
    for pattern in course_patterns:
        course_match = re.search(pattern, text, re.IGNORECASE)
        if course_match:
            return course_match.group(1).replace(' ', '')  # Remove spaces like "CS 100" -> "CS100"
    
    return None

def format_course_for_display(course: Dict[str, Any]) -> str:
    """Format a single course for display purposes."""
    course_code = course.get("course_code", course.get("Course", ""))
    title = course.get("title", course.get("Title", ""))
    instructor = course.get("instructor", course.get("Instructor", ""))
    credits = course.get("credits", course.get("Credits", ""))
    days = course.get("days", course.get("Days", ""))
    times = course.get("times", course.get("Times", ""))
    crn = course.get("crn", course.get("CRN", ""))
    delivery_mode = course.get("delivery_mode", course.get("Delivery Mode", ""))
    
    schedule = f"{days} {times}".strip()
    
    return (
        f"{course_code}: {title}\n"
        f"Instructor: {instructor}\n"
        f"Schedule: {schedule}\n"
        f"Credits: {credits} | Mode: {delivery_mode} | CRN: {crn}"
    )

def validate_course_data(course: Dict[str, Any]) -> bool:
    """Validate that a course record has required fields."""
    required_fields = ["course_code", "title"]
    
    # Check for either new format or legacy format
    for field in required_fields:
        if field not in course and field.title() not in course and field.upper() not in course:
            return False
    
    return True

def normalize_course_data(course: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize course data to consistent format."""
    normalized = {}
    
    # Map common field variations to standard names
    field_mappings = {
        "course_code": ["Course", "course", "COURSE"],
        "title": ["Title", "TITLE"],
        "instructor": ["Instructor", "INSTRUCTOR"],
        "section": ["Section", "SECTION"],
        "crn": ["CRN"],
        "days": ["Days", "DAYS"],
        "times": ["Times", "TIMES"],
        "delivery_mode": ["Delivery Mode", "DELIVERY_MODE", "delivery_mode"],
        "credits": ["Credits", "CREDITS"],
        "status": ["Status", "STATUS"],
        "comments": ["Comments", "COMMENTS"]
    }
    
    for standard_field, variations in field_mappings.items():
        for variation in variations:
            if variation in course:
                normalized[standard_field] = course[variation]
                break
        # If not found in variations, use original key if it exists
        if standard_field not in normalized and standard_field in course:
            normalized[standard_field] = course[standard_field]
    
    return normalized