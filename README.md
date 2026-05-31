# 🎓 CollegePath AI

**AI-powered college admission counselor for engineering students in Maharashtra.**

CollegePath AI helps students choose the right college based on marks, rank, category, branch preference, budget, and more — using a RAG-powered chatbot, smart recommendation engine, interactive map, and OCR marksheet analysis.

---

## 📸 Features

| Feature | Description |
|---|---|
| 🔍 College Finder | AI recommendations split into Dream / Target / Safe |
| 📋 Marksheet OCR | Upload marksheet image → auto-extract percentage & category |
| 📄 PDF Cutoffs | Admin uploads CAP round PDFs → auto-extracted into DB |
| 💬 AI Chatbot | RAG-powered chatbot answers from real uploaded cutoff data |
| ⚖️ Comparison | Side-by-side comparison table for multiple colleges |
| 🗺️ Map View | Leaflet.js interactive map with college locations |
| 🧭 Branch Guide | Interest quiz → AI recommends your ideal engineering branch |

---

## 🗂️ Folder Structure

```
collegepath-ai/
│
├── backend/
│   ├── main.py              ← FastAPI server, all API endpoints
│   ├── database.py          ← SQLite setup and connection helper
│   ├── pdf_processor.py     ← PDF text extraction + cutoff parsing
│   ├── ocr_reader.py        ← EasyOCR/pytesseract marksheet reading
│   ├── recommendation.py    ← Dream/Target/Safe recommendation engine
│   ├── rag.py               ← Pinecone RAG + Gemini/Groq chatbot
│   ├── sample_data.py       ← 15+ realistic Maharashtra college records
│   ├── requirements.txt     ← Python dependencies
│   └── .env.example         ← API key template
│
├── frontend/
│   ├── index.html           ← Single-page app structure
│   ├── style.css            ← Dark theme, glassmorphism, animations
│   └── script.js            ← All UI logic, API calls, map, chat
│
├── uploads/                 ← Uploaded PDFs and marksheets stored here
├── data/                    ← SQLite database stored here
└── README.md
```

---

## ⚙️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                    │
│  index.html + style.css + script.js                     │
│  Leaflet.js map │ Form UI │ Chat UI │ Upload UI         │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (fetch API)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│                                                         │
│  POST /upload-cutoff  → pdf_processor.py → SQLite       │
│                                          → Pinecone     │
│                                                         │
│  POST /upload-marksheet → ocr_reader.py                 │
│                                                         │
│  POST /recommend      → recommendation.py ← SQLite      │
│                                                         │
│  POST /chat           → rag.py → Pinecone (retrieve)    │
│                               → Gemini/Groq (generate)  │
│                                                         │
│  GET  /compare        → SQLite query                    │
│  POST /branch-guidance → rule-based scoring             │
└─────────────────────────────────────────────────────────┘
         │                    │                  │
         ▼                    ▼                  ▼
    SQLite DB           Pinecone VDB       Gemini/Groq API
  (college data)     (embeddings+RAG)     (LLM answers)
```

### How RAG Works (Simple Explanation)

```
INDEXING (when admin uploads PDF):
  PDF → extract text → split into chunks → embed with Gemini
  → store vectors in Pinecone

QUERYING (when student asks chatbot):
  Student question → embed → search Pinecone for similar chunks
  → send top 5 chunks + question to LLM → get grounded answer
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js not required (pure HTML/CSS/JS frontend)

### Step 1: Clone & Install Backend

```bash
# Go to backend folder
cd collegepath-ai/backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up API Keys

```bash
# Copy the example env file
cp .env.example .env

# Open .env and fill in your keys:
# PINECONE_API_KEY  → https://www.pinecone.io (free tier)
# GEMINI_API_KEY    → https://aistudio.google.com (free tier)
# GROQ_API_KEY      → https://console.groq.com (free tier, optional)
```

> **Note:** The app works in demo mode without API keys — it uses sample data and returns hardcoded answers. Add keys for full AI functionality.

### Step 3: Run the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
✅ Database initialized successfully
INFO: Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Run the Frontend

No build step needed! Just open the HTML file:

```bash
# Option A: Double-click frontend/index.html in your file explorer

# Option B: Use Python's built-in server (recommended to avoid CORS issues)
cd frontend
python -m http.server 3000
# Then open http://localhost:3000
```

### Step 5: Test It

1. Open `http://localhost:3000` in your browser
2. Fill in the preference form (name, percentage, category, branch)
3. Click **"Find My Colleges"** — you'll see Dream/Target/Safe recommendations
4. Try the AI chatbot: *"Which college can I get at 92% in OPEN category?"*
5. Use the Branch Guidance quiz
6. Click any college card to see it on the map

---

## 🗄️ Database Schema

```sql
CREATE TABLE colleges (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name               TEXT NOT NULL,
    branch             TEXT NOT NULL,
    category           TEXT NOT NULL,        -- OPEN, OBC, SC, ST, EWS
    cutoff_percentile  REAL,                 -- e.g. 92.5
    cutoff_rank        INTEGER,              -- e.g. 1200
    fees               INTEGER,             -- Annual fees in INR
    city               TEXT,
    type               TEXT,                -- government / private
    placements_avg     INTEGER,             -- Average LPA
    naac_grade         TEXT,                -- A++, A+, A, B++...
    hostel_available   INTEGER,             -- 1 = yes, 0 = no
    latitude           REAL,
    longitude          REAL,
    UNIQUE(name, branch, category)
);
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload-cutoff` | Upload cutoff PDF (form-data, field: `file`) |
| POST | `/upload-marksheet` | Upload student marksheet (form-data, field: `file`) |
| POST | `/recommend` | Get college recommendations (JSON body) |
| POST | `/chat` | AI chatbot message (JSON body) |
| POST | `/branch-guidance` | Branch recommendation quiz (JSON body) |
| GET | `/compare?names=A,B,C` | Compare colleges by name |
| GET | `/all-colleges` | List all colleges in DB |

### Example: /recommend request body
```json
{
  "student_name": "Rahul Sharma",
  "percentage": 92.5,
  "rank": 1400,
  "category": "OPEN",
  "preferred_branch": "Computer Engineering",
  "preferred_city": "Pune",
  "budget": 150000,
  "hostel_needed": true,
  "govt_preferred": false,
  "placement_priority": true
}
```

---

## 📦 Sample Data

The app comes with 15+ realistic college records in `backend/sample_data.py`, including:

- COEP Pune (Government, cutoff ~99%)
- VJTI Mumbai (Government, cutoff ~98.5%)
- PICT Pune (Private, cutoff ~97.8%)
- VIT Pune (Private, cutoff ~93.5%)
- PCCOE Pune (Private, cutoff ~92.5%)
- Symbiosis IT (Private, cutoff ~94%)
- MIT COE Pune, DY Patil, Walchand, and more

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| CORS error in browser | Make sure backend is running on port 8000 |
| OCR not working | Install `easyocr`: `pip install easyocr` |
| Map not loading | Check internet connection (OpenStreetMap tiles) |
| Chat returns generic answer | Add `GEMINI_API_KEY` or `GROQ_API_KEY` to `.env` |
| PDF extraction returns 0 records | App falls back to sample data automatically |

---

## 🧪 Running Without API Keys (Demo Mode)

Everything works in demo mode:
- **Recommendations** use sample college data from `sample_data.py`
- **OCR** returns demo student data
- **Chatbot** returns a helpful fallback message
- **Map** shows pre-loaded Pune college markers

---

## 📋 Presentation Checklist

- [ ] Backend running on port 8000
- [ ] Frontend open in browser
- [ ] Demo the preference form → show Dream/Target/Safe cards
- [ ] Demo the chatbot with sample questions
- [ ] Demo the branch guidance quiz
- [ ] Show map with college markers
- [ ] Show comparison table
- [ ] Explain RAG architecture diagram above

---

*Built with FastAPI · SQLite · Pinecone · Gemini AI · Leaflet.js*