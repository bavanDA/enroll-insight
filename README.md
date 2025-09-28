# 📚 Accessible Voice-Based Course Advisor

A voice-navigated chatbot that helps students — especially from the disability community — find and register for required university courses quickly, easily, and entirely through speech.

## 💡 Inspiration

Course registration is often overwhelming, visually demanding, and difficult to navigate, especially for students with visual, motor, or learning disabilities. We wanted to create a tool that empowers these student by making the process fully accessible through conversational voice interactions.

## 🧠 What It Does

Enroll Insight is an accessibility focused application that utilizes speech to text and text to speech technologies alongside an AI assistant to make course registration/schedule creation at NJIT more inclusive.

- Accepts voice input from the user
- Asks follow-up questions about academic year, time preferences, and career goals
- Recommends personalized courses
- Responds via voice using text-to-speech
- Avoids recommending the same course more than once
- Keeps context using session tracking

## 🛠️ How We Built It

- **Frontend**: React + Tailwind CSS
- **Speech Processing**: Azure Cognitive Speech Services (STT + TTS)
- **Backend**: FastAPI + Python
- **AI Chat Layer**: Gemini AI (Google GenAI)
- **Database**: MongoDB for storing synced NJIT course data
- **Course Sync**: Custom API client that fetches latest courses from NJIT and syncs them to MongoDB

## 🚧 Challenges We Faced

- Gemini was inconsistent: ignored instructions and often repeated recommendations
- Prompt tuning required many iterations
- We had to build a recommendation tracker to prevent duplicates

## 🏆 Accomplishments

- Built a full accessibility-focused tool in **under 24 hours**
- Created real-time voice-first UX
- Improved accessibility and inclusion for a real use case

## 🎓 What we learned

We learned how to use multiple new technologies during the course of this project. 

- how to utilize Microsoft Azure's speech resources to integrate text to speech/speech to text into the project
- how to tailor prompts for Google Gemini in order to get the most accurate results
- how to create a backend using FastAPI and Python and a frontend using React

## 🔮 What’s Next

- Improve UI/UX based on feedback from disabled students
- Add support for other majors (currently only supports Computer Science)
- Integrate authentication for personalized recommendations
- Add support for other GenAI APIs like Copilot, ChatGPT, Claude, and Grok
- Add features such as calendar syncing and waitlist alerts

## 📅 Date

September 28, 2025
