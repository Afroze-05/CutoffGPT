# 🎓 CollegePath AI

> **Agentic AI system for Maharashtra Engineering College Admissions**  
> Built with FastAPI · Groq (LLaMA 3.3) · Python · Vanilla JS

---

## 📌 What It Does

CollegePath AI is a multi-agent AI counselor that helps students find the right engineering college. It works like a real admission counselor:

| Feature | Description |
|---|---|
| 🤖 **AI Counselor Chat** | Conversational agent collects preferences naturally |
| 📄 **Marksheet Analysis** | Upload CET scorecard / Diploma PDF — AI extracts marks |
| 🎯 **Smart Recommendations** | Dream / Target / Safe college classification |
| ⚖️ **College Comparison** | Side-by-side AI-powered comparison |
| 🗺️ **Interactive Map** | Visualize colleges on Maharashtra map |
| 🧭 **Branch Guidance** | Interest quiz → AI recommends best branch |
| 📊 **Admin Dashboard** | Upload cutoff PDFs, manage colleges, view data |

---

## 🏗️ Architecture

```
CollegePath AI
├── main.py                    # FastAPI app entry point
├── backend/
│   ├── agents/
│   │   ├── recommendation_agent.py   # Dream/Target/Safe classifier
│   │   ├── conversation_agent.py     # Preference collection via chat
│   │   ├── branch_agent.py           # Branch guidance AI
│   │   └── comparison_agent.py       # College comparison AI
│   ├── api/
│   │   ├── student.py               # Student endpoints
│   │   ├── admin.py                 # Admin endpoints
│   │   └── branch.py                # Branch guidance endpoints
│   ├── services/
│   │   ├── groq_service.py          # Groq LLM wrapper
│   │   ├── pdf_service.py           # PDF extraction (pdfplumber + AI)
│   │   └── seed_data.py             # Sample Maharashtra college data
│   ├── models/
│   │   ├── college.py               # College, Branch, CutoffRecord
│   │   └── session.py               # StudentSession
│   └── core/
│       ├── config.py                # Settings (pydantic)
│       └── database.py              # Async SQLAlchemy
└── frontend/
    ├── templates/
    │   ├── index.html               # Student interface
    │   └── admin.html               # Admin dashboard
    └── static/
        ├── css/main.css
        └── js/app.js / admin.js
```

---

## 🚀 Quick Start

### 1. Get a Free Groq API Key
Go to [console.groq.com](https://console.groq.com) → Create account → Create API Key (free)

### 2. Setup & Run

**Option A: Quick start script**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Manual**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
python main.py
```

### 3. Open in browser
- **Student App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **Admin Panel**: http://localhost:8000/admin

### 4. Seed Sample Data (First Run!)
Go to Admin Panel → Click **"Seed Sample Data"** to load 10 Maharashtra colleges + cutoff data.

---

## 🔧 Configuration (`.env`)

```env
GROQ_API_KEY=your_groq_api_key_here   # Required!
GROQ_MODEL=llama-3.3-70b-versatile    # Groq model to use
PORT=8000
DEBUG=true
MAX_UPLOAD_SIZE_MB=20
```

---

## 📡 Key API Endpoints

### Student Flow
```
POST /api/student/session/new          → Create session
POST /api/student/upload-marksheet     → Upload PDF marksheet
POST /api/student/manual-profile       → Enter marks manually
POST /api/student/chat                 → Chat with AI counselor
POST /api/student/recommendations      → Get college recommendations
POST /api/student/compare              → Compare colleges
```

### Branch Guidance
```
GET  /api/branch/questions             → Get quiz questions
POST /api/branch/recommend             → Get AI branch recommendation
POST /api/branch/chat                  → Chat about branches
```

### Admin
```
POST /api/admin/seed                   → Seed sample data
POST /api/admin/upload-cutoff-pdf      → Upload cutoff PDF
GET  /api/admin/stats                  → Dashboard stats
GET  /api/admin/colleges               → List colleges
GET  /api/admin/cutoffs                → List cutoff records
```

---

## 🤖 How the Agents Work

### 1. PDF Extraction Agent
Uses `pdfplumber` to extract text from PDFs, then sends chunks to Groq to extract structured cutoff data (college name, branch, category, percentile).

### 2. Conversation Agent
Multi-turn chat agent that collects student preferences (branches, city, budget, hostel, etc.) naturally through conversation. Embeds `<extracted_data>` JSON in responses to track state.

### 3. Recommendation Agent
Queries the cutoff database → Scores each college-branch pair based on:
- Percentile delta from cutoff
- City/budget/hostel preference match
Then uses Groq to classify as Dream/Target/Safe with personalized reasoning.

### 4. Branch Guidance Agent
Takes interest quiz answers → Groq generates personalized branch recommendations with match %, career paths, scope, and salary ranges.

### 5. Comparison Agent
Fetches college + cutoff data → Builds comparison table → Groq generates AI verdict identifying best college for the specific student.

---

## 📊 Sample Colleges Included

| College | City | Type | NAAC |
|---|---|---|---|
| COEP (College of Engineering Pune) | Pune | Government | A++ |
| PICT Pune | Pune | Private | A |
| VIT Pune | Pune | Private | A+ |
| PCCOE | Pune | Private | A |
| MIT COE | Pune | Private | A+ |
| WCE Sangli | Sangli | Government | A |
| GCOE Pune | Pune | Government | A |
| DY Patil Akurdi | Pune | Private | A |
| SPPU IT | Pune | Government | A++ |
| GCEA Aurangabad | Aurangabad | Government | B++ |

---

## 🎓 Viva Preparation Points

1. **Why FastAPI?** — Async support, automatic Swagger docs, Pydantic validation, high performance
2. **Why Groq?** — Free API, fastest LLM inference (300+ tokens/sec), LLaMA 3.3 quality
3. **What makes it "agentic"?** — Multiple specialized agents collaborate, each with a specific role and decision-making capability
4. **How is cutoff data used?** — Stored in SQLite, queried by category/exam type, delta from student score determines tier
5. **Why SQLite?** — Simple deployment, no DB server needed, async support via aiosqlite
6. **How does PDF extraction work?** — pdfplumber extracts text → Groq AI parses structure → stored as CutoffRecord objects

---

## 📝 Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI + Uvicorn |
| LLM | Groq API (LLaMA 3.3 70B) |
| Database | SQLite + SQLAlchemy (async) |
| PDF Processing | pdfplumber |
| Frontend | Vanilla HTML/CSS/JS |
| Maps | Leaflet.js + OpenStreetMap |
| Validation | Pydantic v2 |
| Logging | Loguru |

---

## 🛠️ Troubleshooting

**ModuleNotFoundError**: Run `pip install -r requirements.txt` in your venv

**Groq API error**: Check your `GROQ_API_KEY` in `.env`

**No recommendations**: Go to Admin → Seed Sample Data first

**Map not showing**: Check internet connection (Leaflet loads from CDN)

---

*Made for Final Year Engineering Project Demo — CollegePath AI v1.0*
