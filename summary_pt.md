# Digital Archaeology - Project Summary

## 🛠️ Technology Stack (What We Used)

### 1. Core Processing
- **OCR Engine**: `Tesseract-OCR` (System package)
  - *Wrapper*: `pytesseract`
  - *Reason*: Robust, open-source, runs offline.
- **PDF Handling**: `PyMuPDF` (aka `fitz`)
  - *Reason*: Significantly faster rendering than PyPDF2; handles hybrid PDF/Images well.
- **Language**: Python 3.12 (Arch Linux System Python)

### 2. Semantic Intelligence
- **Embeddings**: `sentence-transformers`
  - *Model*: `all-MiniLM-L6-v2`
  - *Reason*: Lightweight, incredibly fast on CPU, good semantic performance.
- **Vector Database**: `FAISS (CPU)`
  - *Reason*: Industry standard for vector similarity search, low overhead.
- **Summarization**: `sumy` (LSA/TextRank)
  - *Reason*: Completely offline extractive summarization. No need for heavy LLMs.
- **Classification**: Keyword-based Heuristics
  - *Reason*: Simple, deterministic, and fast for known categories (Exam, Bus, etc.).

### 3. Automation & System
- **Monitoring**: `watchdog`
  - *Reason*: Efficient file system event handling for auto-ingestion.
- **Scraping**: `requests` + `beautifulsoup4`
  - *Reason*: Standard stack for reliable HTML parsing.

### 4. User Interface
- **Framework**: `Streamlit`
  - *Reason*: Rapid prototyping, pure Python UI, great for data apps.

---

## 🚫 What We Did NOT Use (And Why)

- **PyPDF2 / pypdf**:
  - *Reason*: Slower and less reliable for text extraction from complex layouts compared to PyMuPDF.
- **Generative AI / LLMs (GPT-4, Llama, Gemini)**:
  - *Reason*: Project constraint was **offline capability**. Generative models require heavy local hardware or internet APIs. We used extraction (`sumy`) instead.
- **Complex Databases (PostgreSQL/MySQL)**:
  - *Reason*: Overkill for a prototype. We used file-based storage (`.json` metadata + `.bin` FAISS index) for portability.
- **Docker**:
  - *Reason*: Optimized for bare-metal Arch Linux performance using system packages (`pacman`).

---

## ✅ Accomplishments

### Phase 1: Core Pipeline
- Full Pipeline: Raw PDF → OCR → Embeddings → Searchable Index
- Technologies: Tesseract, PyMuPDF, Sentence Transformers, FAISS

### Phase 2: Automation
- Auto-Pilot: Drop files in `data/watch`, auto-indexed
- Web Scraper: Download notices from university websites
- Smart Metadata: Auto-categorization and extractive summaries

### Phase 3: AI Integration (Mistral)
- **Q&A Engine**: Ask natural language questions about notices
- **Enhanced Summarization**: Mistral-powered summaries (with TextRank fallback)
- **RAG Architecture**: Retrieval-Augmented Generation for accurate answers

**Example:**
- Query: "When is the exam registration deadline?"
- System: Searches relevant docs → Sends to Mistral → Returns answer with sources
