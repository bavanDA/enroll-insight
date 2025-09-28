# 📚 Accessible Voice-Based Course Advisor

A voice-navigated chatbot that helps students — especially from the disability community — find and register for required university courses quickly, easily, and entirely through speech.

## 💡 Inspiration

We discovered that visually impaired and neurodiverse students often face major challenges navigating complex course registration systems. This project aims to break down that barrier using natural, accessible voice interaction.

## 🧠 What It Does

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

## 🔮 What’s Next

- Improve UI/UX based on feedback from disabled students  
- Add support for other majors (currently only supports Computer Science)  
- Integrate authentication for personalized recommendations  
- Add support for other GenAI APIs like Copilot, ChatGPT, Claude, and Grok  


## 🔧 Built With

- [x] React  
- [x] Tailwind CSS  
- [x] FastAPI  
- [x] Python  
- [x] Azure Cognitive Speech Services  
- [x] Gemini AI  
- [x] MongoDB  

## 📅 Date

September 28, 2025
