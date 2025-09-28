# Prompting Guide for NJIT CS Advisor (Gemini)

This document explains how prompting works in the NJIT CS Advisor
project.

------------------------------------------------------------------------

## 1. Project Scope & Curriculum Source

-   This project helps **undergraduate Computer Science students**
    only.\
-   Recommendations are based on the **official NJIT BS in Computer
    Science curriculum**:\
    👉
    https://catalog.njit.edu/undergraduate/computing-sciences/computer-science/bs/
-   Gemini is guided by this curriculum to suggest appropriate
    semester-based courses.

------------------------------------------------------------------------

## 2. Gathering Student Information

We ask students three core questions:

``` json
{"field": "year", "question": "What Student Year are you in? (e.g., Freshman, Junior)"},
{"field": "time_preference", "question": "What is your preferred time for classes? (e.g., Morning, Evening, Online)"},
{"field": "career_goals", "question": "What are your primary Career Goals? (e.g., Software Engineer, Cybersecurity, Data Science)"}
```

This forms the **student profile**.

------------------------------------------------------------------------

## 3. Recommendations (Avoiding Duplicates)

During testing, Gemini sometimes **repeated courses**.\
To fix this, we track recommended courses and pass them into the prompt:

    You are a conversational NJIT Computer Science academic advisor. 
    The student wants ANOTHER course recommendation. 
    CRITICAL: You have already recommended these courses: {excluded_courses}.

We then embed the student profile with available course data:

    CURRICULUM GUIDE: {CS_PLAN_OF_STUDY}

    STUDENT PROFILE:
    Year: {state.year}
    Time Preference: {state.time_preference}
    Career Goals: {state.career_goals}

    COURSES ALREADY RECOMMENDED: {excluded_courses}

    AVAILABLE COURSES:
    {course_service.get_course_data()}

Gemini then suggests a **new, non-duplicate course** that matches the
student's needs.

------------------------------------------------------------------------

##  Prompting Workflow

1.  Collect student info
2.  Embed student profile with NJIT curriculum and Courses
3.  Recommend **non-duplicate** courses
