"""
CollegePath AI — Admin API Router
"""
import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from backend.core.database import get_db
from backend.core.config import get_settings
from backend.models.college import College, Branch, CutoffRecord, AdminUpload
from backend.services.pdf_service import get_pdf_service
from backend.services.seed_data import SEED_COLLEGES, SEED_BRANCHES, SEED_CUTOFFS
from backend.api.schemas import APIResponse, AdminUploadResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])
settings = get_settings()
pdf_service = get_pdf_service()


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get admin dashboard statistics."""
    college_count = await db.scalar(select(func.count()).select_from(College))
    branch_count = await db.scalar(select(func.count()).select_from(Branch))
    cutoff_count = await db.scalar(select(func.count()).select_from(CutoffRecord))
    upload_count = await db.scalar(select(func.count()).select_from(AdminUpload))

    return APIResponse(data={
        "colleges": college_count,
        "branches": branch_count,
        "cutoff_records": cutoff_count,
        "uploads": upload_count,
    })


# ─── SEED DATA ───────────────────────────────────────────────────────────────

@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """Seed the database with sample Maharashtra college data."""
    colleges_added = 0
    branches_added = 0
    cutoffs_added = 0

    # Seed colleges
    for col_data in SEED_COLLEGES:
        existing = await db.scalar(
            select(College).where(College.name == col_data["name"])
        )
        if not existing:
            college = College(**col_data)
            db.add(college)
            colleges_added += 1

    await db.flush()

    # Seed branches
    for branch_data in SEED_BRANCHES:
        existing = await db.scalar(
            select(Branch).where(Branch.name == branch_data["name"])
        )
        if not existing:
            branch = Branch(**branch_data)
            db.add(branch)
            branches_added += 1

    await db.flush()

    # Seed cutoffs
    for cutoff_data in SEED_CUTOFFS:
        # Find college_id
        college = await db.scalar(
            select(College).where(
                College.short_name.ilike(f"%{cutoff_data['college_name'].split()[0]}%")
            )
        )
        cutoff = CutoffRecord(
            college_id=college.id if college else None,
            **cutoff_data
        )
        db.add(cutoff)
        cutoffs_added += 1

    await db.flush()

    logger.info(f"Seeded: {colleges_added} colleges, {branches_added} branches, {cutoffs_added} cutoffs")

    return APIResponse(
        message="Database seeded successfully",
        data={
            "colleges_added": colleges_added,
            "branches_added": branches_added,
            "cutoffs_added": cutoffs_added,
        }
    )


# ─── CUTOFF PDF UPLOAD ────────────────────────────────────────────────────────

@router.post("/upload-cutoff-pdf")
async def upload_cutoff_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    exam_type: str = Form("CET"),
    year: int = Form(2023),
    db: AsyncSession = Depends(get_db),
):
    """Upload and process a cutoff PDF."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.max_upload_size_mb}MB")

    # Save file
    file_path = Path(settings.upload_dir) / f"cutoff_{exam_type}_{year}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    # Create upload record
    upload = AdminUpload(
        filename=file.filename,
        file_path=str(file_path),
        file_type="cutoff_pdf",
        status="processing",
    )
    db.add(upload)
    await db.flush()
    upload_id = upload.id

    # Process in background
    background_tasks.add_task(
        _process_cutoff_pdf_bg,
        upload_id=upload_id,
        file_path=str(file_path),
        exam_type=exam_type,
        year=year,
    )

    return AdminUploadResponse(
        upload_id=upload_id,
        filename=file.filename,
        status="processing",
        message="File uploaded. Processing in background — check status endpoint.",
    )


async def _process_cutoff_pdf_bg(upload_id: int, file_path: str, exam_type: str, year: int):
    """Background task to process cutoff PDF."""
    from backend.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            records = await pdf_service.extract_cutoff_pdf(file_path)

            for record in records:
                record["exam_type"] = exam_type
                record["year"] = record.get("year") or year
                record["source_file"] = file_path

                # Find matching college
                college = await db.scalar(
                    select(College).where(
                        College.name.ilike(f"%{record.get('college_name', '')[:20]}%")
                    )
                )

                cutoff = CutoffRecord(
                    college_id=college.id if college else None,
                    college_name=record.get("college_name", "Unknown"),
                    branch_name=record.get("branch_name", "Unknown"),
                    exam_type=record.get("exam_type", exam_type),
                    year=record.get("year", year),
                    round_no=record.get("round_no", 1),
                    category=record.get("category", "OPEN"),
                    gender=record.get("gender", "ALL"),
                    cutoff_percentile=record.get("cutoff_percentile"),
                    cutoff_rank=record.get("cutoff_rank"),
                    cutoff_marks=record.get("cutoff_marks"),
                    seats=record.get("seats"),
                    source_file=file_path,
                )
                db.add(cutoff)

            # Update upload record
            upload = await db.get(AdminUpload, upload_id)
            if upload:
                upload.status = "done"
                upload.records_extracted = len(records)
                upload.processed_at = datetime.utcnow()

            await db.commit()
            logger.info(f"Upload {upload_id} processed: {len(records)} records")

        except Exception as e:
            logger.error(f"Background processing failed for upload {upload_id}: {e}")
            async with AsyncSessionLocal() as db2:
                upload = await db2.get(AdminUpload, upload_id)
                if upload:
                    upload.status = "failed"
                    upload.error_message = str(e)
                await db2.commit()


@router.get("/uploads")
async def list_uploads(db: AsyncSession = Depends(get_db)):
    """List all admin uploads."""
    result = await db.execute(
        select(AdminUpload).order_by(AdminUpload.created_at.desc()).limit(50)
    )
    uploads = result.scalars().all()
    return APIResponse(data=[
        {
            "id": u.id,
            "filename": u.filename,
            "file_type": u.file_type,
            "status": u.status,
            "records_extracted": u.records_extracted,
            "error_message": u.error_message,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in uploads
    ])


# ─── COLLEGES ────────────────────────────────────────────────────────────────

@router.get("/colleges")
async def list_colleges(db: AsyncSession = Depends(get_db)):
    """List all colleges."""
    result = await db.execute(select(College).order_by(College.name))
    colleges = result.scalars().all()
    return APIResponse(data=[
        {
            "id": c.id,
            "name": c.name,
            "short_name": c.short_name,
            "city": c.city,
            "college_type": c.college_type,
            "naac_grade": c.naac_grade,
            "annual_fees": c.annual_fees,
            "avg_placement_lpa": c.avg_placement_lpa,
            "hostel_available": c.hostel_available,
            "latitude": c.latitude,
            "longitude": c.longitude,
        }
        for c in colleges
    ])


@router.get("/cutoffs")
async def list_cutoffs(
    college_name: str = None,
    exam_type: str = None,
    year: int = None,
    db: AsyncSession = Depends(get_db),
):
    """List cutoff records with optional filters."""
    query = select(CutoffRecord)
    if college_name:
        query = query.where(CutoffRecord.college_name.ilike(f"%{college_name}%"))
    if exam_type:
        query = query.where(CutoffRecord.exam_type == exam_type)
    if year:
        query = query.where(CutoffRecord.year == year)

    result = await db.execute(query.limit(200))
    records = result.scalars().all()

    return APIResponse(data=[
        {
            "id": r.id,
            "college_name": r.college_name,
            "branch_name": r.branch_name,
            "exam_type": r.exam_type,
            "year": r.year,
            "round_no": r.round_no,
            "category": r.category,
            "cutoff_percentile": r.cutoff_percentile,
            "cutoff_rank": r.cutoff_rank,
            "seats": r.seats,
        }
        for r in records
    ])
