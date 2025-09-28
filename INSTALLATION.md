
# ⚙️ Installation Guide



This guide walks you through setting up the **Accessible Voice-Based Course Advisor** project locally on your machine.

---

## 🖥️ Backend Setup (FastAPI + Speech + Gemini + MongoDB)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/enroll-insight.git
cd enroll-insight/server
```

### 2. Create and Activate a Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg (required for Azure Speech)

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# macOS (with Homebrew)
brew install ffmpeg
```

### 5. Create the `.env` File

Create a `.env` file in the `server/` directory with the following content:

```
MONGO_URI=mongodb://localhost:27017
DB_NAME=enroll_insight
GEMINI_API_KEY=your_gemini_api_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_REGION=your_azure_region
```

### 6. Run the Backend

```bash
uvicorn app.main:app --port 8000
```

The API will be running at: [http://localhost:8000](http://localhost:8000)

---

## 🌐 Frontend Setup (React + Tailwind)

### 1. Navigate to the Client Directory

```bash
cd ../client
```

### 2. Install Node.js Dependencies

```bash
npm install
```

### 3. Run the Frontend

```bash
npm run dev
```

Frontend will be served at: [http://localhost:5173](http://localhost:5173)
