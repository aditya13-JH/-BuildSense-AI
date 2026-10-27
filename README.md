<img width="2870" height="1520" alt="image" src="https://github.com/user-attachments/assets/f89b4b15-1517-4ea8-bf53-81dc9a2d98fa" />



# 🏗️ BuildSense AI – Construction Intelligence Platform

A full-stack web application that uses **Google Gemini AI** to assist construction professionals with safety analysis, crack detection, property valuation, and project planning.

---

## 🧰 Tech Stack

| Layer     | Technology                     |
|-----------|-------------------------------|
| Frontend  | React 18 + Vite + Vanilla CSS |
| Backend   | Python FastAPI                |
| AI        | Google Gemini 1.5 Flash       |
| Database  | None (stateless)              |

---

## 📁 Project Structure

```
BuildSense-AI/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx          ← Navigation sidebar
│   │   │   ├── Dashboard.jsx        ← Home/overview page
│   │   │   ├── SafetyAnalysis.jsx   ← Upload & analyze site images
│   │   │   ├── CrackDetection.jsx   ← Detect cracks in structures
│   │   │   ├── PropertyValuation.jsx← Estimate property value
│   │   │   ├── ProjectPlanner.jsx   ← Generate project schedules
│   │   │   └── AIAssistant.jsx      ← Chat with AI assistant
│   │   ├── App.jsx                  ← Main app with routing
│   │   ├── App.css                  ← All styles (orange/white/gray theme)
│   │   └── main.jsx                 ← React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py                      ← All FastAPI endpoints
│   ├── requirements.txt
│   └── .env.example                 ← Copy this to .env and add your API key
└── README.md
```

---

## 🚀 Setup & Running Locally

### Prerequisites
- **Python 3.9+** (for the backend)
- **Node.js 18+** and **npm** (for the frontend) — [Download Node.js](https://nodejs.org/)

---

### Step 1 — Backend Setup

```bash
# 1. Navigate to the backend folder
cd BuildSense-AI/backend

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create your .env file from the example
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux

# 4. Open .env and add your Gemini API key:
#    GEMINI_API_KEY=your_actual_key_here
#    Get a free key at: https://aistudio.google.com/

# 5. Start the backend server
uvicorn main:app --reload
```

Backend will run at: **http://localhost:8000**  
API docs available at: **http://localhost:8000/docs**

---

### Step 2 — Frontend Setup

Open a **new terminal window**:

```bash
# 1. Navigate to the frontend folder
cd BuildSense-AI/frontend

# 2. Install Node.js dependencies
npm install

# 3. Start the development server
npm run dev
```

Frontend will run at: **http://localhost:5173**

---

## ✨ Features

| Feature              | Needs API Key? | Description                                              |
|----------------------|:--------------:|----------------------------------------------------------|
| 🦺 Safety Analysis   | ✅ Yes          | Upload a site photo → Gemini identifies safety hazards   |
| 🔍 Crack Detection   | ✅ Yes          | Upload a wall/concrete image → Gemini assesses cracks    |
| 💰 Property Valuation| ❌ No           | Fill a form → Instant estimate in Indian Rupees (₹)     |
| 📋 Project Planner   | ❌ No           | Enter project details → Get a phased schedule table      |
| 🤖 AI Assistant      | ✅ Yes          | Ask any construction question in a chat interface        |

---

## 🔑 Getting a Gemini API Key (Free)

1. Go to [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Copy the key and paste it into `backend/.env` as:
   ```
   GEMINI_API_KEY=paste_your_key_here
   ```

> ⚠️ **Security:** Never share your `.env` file. The API key is only used by the backend and is never sent to the browser.

---

## 🔗 API Endpoints

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/health`             | Check server status      |
| POST   | `/api/safety/analyze`     | Analyze site image       |
| POST   | `/api/cracks/analyze`     | Detect cracks in image   |
| POST   | `/api/valuation/estimate` | Calculate property value |
| POST   | `/api/planning/generate`  | Generate project schedule|
| POST   | `/api/assistant/chat`     | Chat with AI assistant   |

---

## 🎨 Design

- **Color scheme:** Orange (`#f97316`), White, Dark Gray (`#1a1a2e`)
- **Font:** Inter (Google Fonts)
- **Layout:** Fixed sidebar + scrollable main content
- **Responsive:** Works on desktop and tablet screens
