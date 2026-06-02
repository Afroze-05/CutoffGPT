"""
CollegePath AI — PDF & OCR Extraction Service
Handles both admin cutoff PDFs and student marksheets.
"""
import re
import json
from pathlib import Path
from typing import Optional
import pdfplumber
from loguru import logger
from backend.services.groq_service import get_groq_service


class PDFExtractionService:
    """Extracts structured data from PDFs using pdfplumber + Groq AI."""

    def __init__(self):
        self.groq = get_groq_service()

    # ─── CUTOFF PDF ──────────────────────────────────────────────────────────

    async def extract_cutoff_pdf(self, pdf_path: str) -> list[dict]:
        """
        Extract cutoff records from admin-uploaded CAP/CET cutoff PDFs.
        Returns list of structured cutoff dicts.
        """
        raw_text = self._extract_text(pdf_path)
        if not raw_text:
            raise ValueError("Could not extract text from PDF")

        # Chunk the text so it fits in context
        chunks = self._chunk_text(raw_text, max_chars=6000)
        all_records = []

        for i, chunk in enumerate(chunks):
            logger.info(f"Processing cutoff chunk {i+1}/{len(chunks)}")
            records = await self._parse_cutoff_chunk(chunk)
            all_records.extend(records)

        logger.info(f"Extracted {len(all_records)} cutoff records from {pdf_path}")
        return all_records

    async def _parse_cutoff_chunk(self, text: str) -> list[dict]:
        system = """You are an expert at extracting college admission cutoff data from Maharashtra CAP/CET PDF documents.
Extract ALL cutoff records from the given text.
Return ONLY a valid JSON array of objects. Each object must have these keys:
- college_name (string)
- branch_name (string)
- exam_type (string: "CET" or "CAP" or "JEE" or "Diploma")
- year (integer, e.g. 2023)
- round_no (integer, e.g. 1, 2, 3)
- category (string: "OPEN", "OBC", "SC", "ST", "NT1", "NT2", "NT3", "EWS", "SEBC", "TFWS")
- gender (string: "ALL", "MALE", "FEMALE")
- cutoff_percentile (float or null)
- cutoff_rank (integer or null)
- cutoff_marks (float or null)
- seats (integer or null)
If a field is not present, use null.
Return [] if no records found."""

        try:
            resp = await self.groq.chat(
                messages=[{"role": "user", "content": f"Extract cutoff records from this text:\n\n{text}"}],
                system_prompt=system,
                temperature=0.1,
                max_tokens=4096,
                json_mode=False,
            )
            # Find JSON array in response
            match = re.search(r'\[.*\]', resp, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.warning(f"Cutoff chunk parsing error: {e}")
        return []

    # ─── MARKSHEET ───────────────────────────────────────────────────────────

    async def extract_marksheet(self, pdf_path: str) -> dict:
        """
        Extract student data from uploaded marksheet/scorecard.
        Returns structured student profile dict.
        """
        raw_text = self._extract_text(pdf_path)
        if not raw_text:
            raise ValueError("Could not extract text from marksheet")

        return await self._parse_marksheet(raw_text[:5000])

    async def _parse_marksheet(self, text: str) -> dict:
        system = """You are an expert at reading Indian engineering entrance exam scorecards and diploma marksheets.
Extract student information and return ONLY a valid JSON object with these keys:
- student_name (string or null)
- exam_type (string: "CET", "JEE", "Diploma", "HSC" — pick the most appropriate)
- percentage (float or null — overall percentage if available)
- percentile (float or null — percentile score if CET/JEE)
- rank (integer or null — CET/JEE rank)
- category (string: "OPEN", "OBC", "SC", "ST", "NT1", "NT2", "NT3", "EWS", "SEBC" or null)
- year (integer or null — year of exam)
- subjects (object or null — subject-wise marks if diploma/HSC)
Return a JSON object only, no explanation."""

        try:
            resp = await self.groq.chat(
                messages=[{"role": "user", "content": f"Extract student data from this marksheet:\n\n{text}"}],
                system_prompt=system,
                temperature=0.1,
                max_tokens=1024,
                json_mode=False,
            )
            match = re.search(r'\{.*\}', resp, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.warning(f"Marksheet parsing error: {e}")

        return {
            "student_name": None,
            "exam_type": "CET",
            "percentage": None,
            "percentile": None,
            "rank": None,
            "category": None,
            "year": None,
            "subjects": None,
        }

    # ─── UTILITIES ───────────────────────────────────────────────────────────

    def _extract_text(self, pdf_path: str) -> str:
        """Extract raw text from PDF using pdfplumber."""
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    # Also try table extraction
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                row_text = " | ".join(str(cell or "") for cell in row)
                                text_parts.append(row_text)
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF text extraction failed for {pdf_path}: {e}")
            return ""

    def _chunk_text(self, text: str, max_chars: int = 6000) -> list[str]:
        """Split large text into processable chunks."""
        lines = text.split("\n")
        chunks, current, current_len = [], [], 0
        for line in lines:
            if current_len + len(line) > max_chars and current:
                chunks.append("\n".join(current))
                current, current_len = [], 0
            current.append(line)
            current_len += len(line)
        if current:
            chunks.append("\n".join(current))
        return chunks


_pdf_service: Optional[PDFExtractionService] = None


def get_pdf_service() -> PDFExtractionService:
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFExtractionService()
    return _pdf_service
