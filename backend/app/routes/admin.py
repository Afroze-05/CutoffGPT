from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..models.models import Cutoff, College, Document
from ..utils.pdf_processor import extract_text_from_pdf
from ..rag.vector_store import vector_store_manager
from ..config.config import settings
import os
import shutil

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/upload-cutoff")
async def upload_cutoff(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOADS_DIR, f"cutoff_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        text = extract_text_from_pdf(file_path)
        # Store in vector DB
        vector_store_manager.add_documents([text], [{"source": file.filename, "type": "cutoff"}])
        
        # Record in DB
        # For now, using a mock admin user_id=1
        new_doc = Document(
            user_id=1,
            filename=file.filename,
            file_path=file_path,
            doc_type="cutoff"
        )
        db.add(new_doc)
        db.commit()
        
        return {"message": "Cutoff PDF uploaded and processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
def get_admin_documents(db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.doc_type == "cutoff").all()

@router.post("/add-college")
def add_college(name: str, location: str, db: Session = Depends(get_db)):
    college = College(name=name, location=location)
    db.add(college)
    db.commit()
    return {"message": "College added successfully"}
