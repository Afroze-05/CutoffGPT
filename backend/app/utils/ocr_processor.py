import io
import os
import base64
import requests
from PIL import Image
import numpy as np
import pytesseract
from ..config.config import settings

class OCRProcessor:
    def __init__(self):
        self.reader = None
        self.rapid_ocr = None
        self.rapid_ocr_checked = False
        # Try to find tesseract executable on Windows if not in PATH
        if os.name == 'nt':
            tess_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Users\API\AppData\Local\Tesseract-OCR\tesseract.exe',
                r'D:\Program Files\Tesseract-OCR\tesseract.exe'
            ]
            for path in tess_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def _get_reader(self):
        if self.reader is None:
            try:
                import easyocr
                # Disable GPU if causing issues in some environments
                self.reader = easyocr.Reader(['en'], gpu=False)
                print("EasyOCR initialized successfully (CPU mode).")
            except Exception as e:
                print(f"Error initializing EasyOCR: {e}")
        return self.reader

    def _get_rapid_ocr(self):
        if self.rapid_ocr is None and not self.rapid_ocr_checked:
            self.rapid_ocr_checked = True
            try:
                from rapidocr_onnxruntime import RapidOCR
                self.rapid_ocr = RapidOCR()
                print("RapidOCR initialized successfully.")
            except Exception as e:
                print(f"Error initializing RapidOCR: {e}")
        return self.rapid_ocr

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        text = ""
        try:
            print("OCR started")
            image = Image.open(io.BytesIO(image_bytes))
            text = self._extract_from_pil_image(image)

            print(f"OCR text length: {len(text)}")
            if not text.strip():
                print("WARNING: OCR extracted NO text.")
            return text
        except Exception as e:
            print(f"OCR CRITICAL FAILURE: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def extract_text(self, file_bytes: bytes, filename: str = "") -> str:
        print("OCR pipeline started")
        if file_bytes.startswith(b"%PDF") or filename.lower().endswith(".pdf"):
            print("OCR detected PDF input")
            return self._extract_text_from_pdf(file_bytes)
        print("OCR detected image input")
        return self.extract_text_from_image(file_bytes)

    def _extract_from_pil_image(self, image: Image.Image) -> str:
        text = ""
        image_np = np.array(image.convert("RGB"))

        # Primary OCR: EasyOCR
        print("Attempting EasyOCR...")
        reader = self._get_reader()
        if reader:
            try:
                results = reader.readtext(image_np)
                text = " ".join([res[1] for res in results]).strip()
                print(f"EasyOCR output length: {len(text)}")
            except Exception as e:
                print(f"EasyOCR failed on image: {e}")

        # Fallback OCR: Tesseract
        if not text.strip():
            print("EasyOCR empty/failure; attempting RapidOCR fallback...")
            try:
                rapid = self._get_rapid_ocr()
                if rapid:
                    # rapidocr accepts ndarray image
                    result, _ = rapid(image_np)
                    if result:
                        text = " ".join([line[1] for line in result]).strip()
                    print(f"RapidOCR output length: {len(text)}")
            except Exception as e:
                print(f"RapidOCR failed on image: {e}")
                text = ""

        # Final fallback OCR: Tesseract
        if not text.strip():
            print("RapidOCR empty/failure; attempting Tesseract fallback...")
            try:
                text = pytesseract.image_to_string(image).strip()
                print(f"Tesseract output length: {len(text)}")
            except Exception as e:
                print(f"Tesseract failed on image: {e}")
                text = ""

        # Cloud fallback OCR: Groq vision (no local OCR runtime needed)
        if not text.strip():
            print("Tesseract empty/failure; attempting Groq Vision OCR fallback...")
            try:
                image_bytes = io.BytesIO()
                image.save(image_bytes, format="PNG")
                text = self._extract_with_groq_vision(image_bytes.getvalue())
                print(f"Groq Vision OCR output length: {len(text)}")
            except Exception as e:
                print(f"Groq Vision OCR fallback failed: {e}")
                text = ""
        return text

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        text_parts = []
        try:
            import pypdf
            print("Trying embedded PDF text extraction...")
            pdf = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf.pages:
                extracted = (page.extract_text() or "").strip()
                if extracted:
                    text_parts.append(extracted)
            text = "\n".join(text_parts).strip()
            print(f"Embedded PDF text length: {len(text)}")
        except Exception as e:
            print(f"Embedded PDF text extraction failed: {e}")
            text = ""

        if len(text) >= 50:
            return text

        # Scanned PDF OCR fallback (best-effort)
        print("PDF appears scanned/empty text, trying page-image OCR...")
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
            ocr_pages = []
            for idx in range(len(pdf)):
                page = pdf[idx]
                pil_image = page.render(scale=2.0).to_pil()
                page_text = self._extract_from_pil_image(pil_image)
                if page_text.strip():
                    ocr_pages.append(page_text.strip())
            scanned_text = "\n".join(ocr_pages).strip()
            print(f"Scanned PDF OCR text length: {len(scanned_text)}")
            return scanned_text
        except Exception as e:
            print(f"Scanned PDF OCR fallback failed: {e}")
            return text

    def _extract_with_groq_vision(self, image_bytes: bytes) -> str:
        if not settings.GROQ_API_KEY:
            print("Groq API key not configured; skipping Groq Vision OCR.")
            return ""

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are an OCR engine. Extract all visible text from this marksheet image. "
                                "Return only plain text from the document, preserving numbers and line breaks. "
                                "Do not explain, summarize, or add commentary. "
                                "If no document text is readable, return an empty string."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                        },
                    ],
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if resp.status_code != 200:
            print(f"Groq Vision OCR HTTP error: {resp.status_code} {resp.text[:300]}")
            return ""
        data = resp.json()
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

ocr_processor = None

def get_ocr_processor():
    global ocr_processor
    if ocr_processor is None:
        ocr_processor = OCRProcessor()
    return ocr_processor
