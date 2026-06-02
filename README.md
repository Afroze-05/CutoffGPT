# CollegePath AI 🎓🤖

CollegePath AI is a full-stack AI platform designed to help students (Diploma/CET/JEE) navigate the complex college admission process. By leveraging RAG (Retrieval-Augmented Generation) and Agentic AI, the platform provides personalized college recommendations based on historical cutoff data and student profiles.

## 🚀 Features

- **Admin Cutoff System**: Upload and process historical cutoff PDFs into a vector database.
- **AI-Powered Recommendations**: Personalized lists of Dream, Target, and Safe colleges.
- **Conversational Agent**: Interactive chatbot using LangChain and Gemini 1.5 Flash.
- **Marksheet OCR**: Extract student details (percentage, rank) directly from marksheet images.
- **Interactive Map**: View colleges on Leaflet maps with nearby facilities.
- **Comparison Engine**: Side-by-side comparison of fees, placements, and ratings.
- **Branch Guidance**: Interest-based guidance for selecting the right engineering branch.

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, Tailwind CSS, Lucide Icons, Leaflet.js, Framer Motion.
- **Backend**: FastAPI (Python), LangChain, Google Gemini API.
- **Database**: SQLite (SQLAlchemy) & ChromaDB (Vector Search).
- **Processing**: PyPDF, EasyOCR.

## 📁 Folder Structure

```text
collegepath-ai/
├── frontend/          # Next.js Application
├── backend/           # FastAPI Application
│   ├── app/           # Core Logic (Agents, RAG, Routes)
│   ├── uploads/       # PDF/Image uploads
│   └── chroma_db/     # Vector database
└── README.md
```

## ⚙️ Setup Guide

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
```
- Create a `.env` file based on `.env.example` and add your `GEMINI_API_KEY`.
- Seed the database:
```bash
python seed_data.py
```
- Run the server:
```bash
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🧠 Architecture Explanation

### How RAG Works
1. **Ingestion**: Admin uploads a PDF. Text is extracted using `PyPDF`, split into chunks by LangChain's `RecursiveCharacterTextSplitter`.
2. **Embedding**: Chunks are converted to vectors using Gemini's `embedding-001` model.
3. **Storage**: Vectors and metadata are stored in `ChromaDB`.
4. **Retrieval**: When a student asks a question, the query is embedded and similar chunks are retrieved from ChromaDB.

### Agentic AI Implementation
The system uses a LangChain `Tool Calling Agent`. It has access to tools for:
- `search_cutoffs`: Queries the vector database.
- `get_college_details`: Queries the SQL database for structured data.
- `recommend_branches`: Uses Gemini to analyze student interests.
The agent decides which tool to use based on the user's intent.

### Vector Search
Uses cosine similarity within ChromaDB to find the most relevant historical cutoff snippets for a given student rank and category.

## 📝 API Documentation
Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
