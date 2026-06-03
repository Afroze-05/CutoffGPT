from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database.session import engine, Base
from .routes import auth, admin, student, chat, colleges
from .config.config import settings
import logging
from sqlalchemy import inspect, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables and initialize components
try:
    logger.info("Starting database initialization...")
    Base.metadata.create_all(bind=engine)
    # Lightweight runtime migration for existing databases.
    inspector = inspect(engine)
    if "student_profiles" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("student_profiles")}
        if "raw_ocr_text" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE student_profiles ADD COLUMN raw_ocr_text VARCHAR"))
            logger.info("Applied migration: student_profiles.raw_ocr_text")
    print("Database Connected")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    print(f"CRITICAL: Database initialization failed: {e}")

try:
    from .utils.ocr_processor import get_ocr_processor
    get_ocr_processor()
    print("OCR Initialized")
except Exception as e:
    logger.error(f"OCR initialization failed: {e}")
    print(f"CRITICAL: OCR initialization failed: {e}")

try:
    from .rag.vector_store import vector_store_manager
    print("ChromaDB Initialized")
except Exception as e:
    logger.error(f"ChromaDB initialization failed: {e}")
    print(f"CRITICAL: ChromaDB initialization failed: {e}")

try:
    from .llm.groq_client import get_groq_llm
    get_groq_llm()
    print("Groq Initialized")
except Exception as e:
    logger.error(f"Groq initialization failed: {e}")
    print(f"CRITICAL: Groq initialization failed: {e}")

app = FastAPI(
    title="CollegePath AI API",
    description="Full-stack AI platform for college recommendations",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "message": str(exc)},
    )

# Include routes
try:
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(student.router)
    app.include_router(chat.router)
    app.include_router(colleges.router)
    print("Routes Registered")
except Exception as e:
    logger.error(f"Route registration failed: {e}")
    print(f"CRITICAL: Route registration failed: {e}")

@app.on_event("startup")
async def startup_event():
    print("Backend Started")

@app.get("/")
def read_root():
    return {"message": "Welcome to CollegePath AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
