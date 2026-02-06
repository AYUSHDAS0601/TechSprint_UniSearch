import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any
from .utils import setup_logging, clean_text
import io

logger = setup_logging("OCR_Module")

# Explicitly set Tesseract path for Arch Linux default
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

class OCREngine:
    def __init__(self):
        logger.info("Initializing OCR Engine (Tesseract + PyMuPDF)...")

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Extracts text from a given file (PDF or Image).
        Returns a dictionary with metadata and extracted text.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {}

        logger.info(f"Processing file: {file_path.name}")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                return self._process_pdf(file_path)
            elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                return self._process_image(file_path)
            else:
                logger.warning(f"Unsupported file format: {file_path.suffix}")
                return {}
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            return {}

    def _process_image(self, image_path: Path) -> Dict[str, Any]:
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            clean_content = clean_text(text)
            
            return {
                "filename": image_path.name,
                "path": str(image_path),
                "type": "image",
                "content": clean_content,
                "page_count": 1
            }
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            raise e

    def _process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        doc = fitz.open(pdf_path)
        full_text = []

        for page_num, page in enumerate(doc):
            # First try extracting text directly (for digital PDFs)
            text = page.get_text()
            
            # If little to no text found, try OCR on the page image (scanned PDF)
            if len(text.strip()) < 10: 
                logger.info(f"Page {page_num + 1} of {pdf_path.name} appears scanned. Using OCR...")
                pix = page.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                text = pytesseract.image_to_string(image)
            
            full_text.append(text)

        doc.close()
        
        combined_text = "\n".join(full_text)
        clean_content = clean_text(combined_text)

        return {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "type": "pdf",
            "content": clean_content,
            "page_count": len(full_text)
        }
