import logging
import re
from pathlib import Path
from typing import List, Union

def setup_logging(name: str = "DigitalArchaeology", log_file: str = "app.log") -> logging.Logger:
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console Handler
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
        
        # File Handler
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
        
    return logger

logger = setup_logging()

def maintain_directories(base_path: Path):
    """Ensures necessary data directories exist."""
    dirs = [
        base_path / "data" / "raw",
        base_path / "data" / "processed",
        base_path / "data" / "index"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    logger.info("Directory structure verified.")

def clean_text(text: str) -> str:
    """Cleans and normalizes extracted text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove non-printable characters (optional, depending on need)
    # text = ''.join(c for c in text if c.isprintable())
    
    return text

def get_file_list(directory: Path, extensions: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]) -> List[Path]:
    """Returns a list of files with matching extensions in the directory."""
    files = []
    if not directory.exists():
        return files
    
    for ext in extensions:
        files.extend(list(directory.glob(f"*{ext}")))
        files.extend(list(directory.glob(f"*{ext.upper()}")))
        
    return files
