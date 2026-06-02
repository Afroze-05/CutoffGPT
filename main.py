"""
CollegePath AI — Main FastAPI Application
Agentic AI system for Maharashtra engineering college admissions
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from loguru import logger

from backend.core.config import get_settings
from backend.core.database import init_db
from backend.api.student import router as student_router
from backend.api.admin import router as admin_router
from backend.api.branch import router as branch_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("🚀 CollegePath AI starting up...")
    await init_db()
    logger.info("✅ Database initialized")
    logger.info(f"🤖 Groq model: {settings.groq_model}")
    yield
    logger.info("👋 CollegePath AI shutting down")


app = FastAPI(
    title="CollegePath AI",
    description="Agentic AI for Maharashtra Engineering College Admissions",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(student_router)
app.include_router(admin_router)
app.include_router(branch_router)

# Serve static frontend
static_dir = Path("frontend/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates_dir = Path("frontend/templates")


@app.get("/", include_in_schema=False)
async def serve_index():
    index = templates_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "CollegePath AI API running. Visit /docs for API documentation."}


@app.get("/admin", include_in_schema=False)
async def serve_admin():
    admin = templates_dir / "admin.html"
    if admin.exists():
        return FileResponse(str(admin))
    return {"message": "Admin panel"}


@app.get("/health")
async def health():
    return {"status": "healthy", "app": settings.app_name, "model": settings.groq_model}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
