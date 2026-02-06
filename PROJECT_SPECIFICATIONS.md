# Digital Archaeology — Project Specifications

### 1) Project summary
**Digital Archaeology** is a local-first Streamlit application for ingesting university notices (PDFs/images), extracting text (direct PDF text extraction + OCR fallback), enriching the document with summarization + classification, indexing embeddings in FAISS, and providing:
- **Semantic search** over notices
- **RAG-style Q&A** using a local Ollama-hosted LLM (Mistral)
- **Dashboard** for system stats + logs
- **Web crawler** to download notices into a watched folder

### 2) Target environment
- **OS**: Arch Linux (project includes `setup_arch.sh` for pacman installs)
- **Python**: venv-based (created at `digital-archaeology/venv`)
- **UI runtime**: Streamlit (served on port **8501**)

### 3) Key features (functional requirements)
#### 3.1 Ingestion
- Upload multiple files from the sidebar:
  - Supported types: **PDF**, **PNG**, **JPG/JPEG**
- Save uploaded files into `data/raw/`.
- Trigger a processing run that:
  - Extracts text
  - Summarizes + classifies
  - Writes metadata JSON
  - Indexes embeddings into FAISS

#### 3.2 Text extraction (OCR / parsing)
Implemented in `src/ocr.py` (`OCREngine`):
- **PDF**:
  - Try `PyMuPDF` (`page.get_text()`)
  - If extracted text is too short, fallback to **OCR**:
    - Render page to image (`get_pixmap(dpi=300)`)
    - Run `pytesseract.image_to_string(...)`
- **Images**: OCR via `pytesseract.image_to_string(...)`
- Text is normalized with `src/utils.py:clean_text()` (whitespace cleanup).

#### 3.3 Enrichment (summarization + classification)
Implemented in `src/processor.py` (`DocumentProcessor`) and `src/summarizer.py` (`DocumentSummarizer`) and `src/classifier.py` (`NoticeClassifier`):

- **Summarization backends** (selected via `config/config.yaml:summarization.method`):
  - `"mistral"`: calls Ollama generate API (default URL `http://localhost:11434/api/generate`)
  - `"extract"`: extractive LSA summarization via `sumy` (uses NLTK punkt)
  - (Code supports `"bart"` / `"t5-*"`, via transformers pipeline, but YAML defaults to `"mistral"`.)
- **Classification**: keyword-based multi-label classification into categories:
  - `Examination`, `Scholarship`, `Transport`, `Academic`, `Administrative`, `Events`
  - If none matched: `General`

#### 3.4 Indexing & retrieval (semantic search)
Implemented in:
- `src/embeddings.py` (`EmbeddingGenerator`): SentenceTransformers embeddings (default model `all-MiniLM-L6-v2`)
- `src/indexer.py` (`FaissIndexer`): FAISS IndexFlatL2 (default dimension **384**)
- `src/processor.py` (`DocumentProcessor._index_document`): hybrid indexing
- `src/search.py` (`SearchEngine.search`): retrieval + optional metadata filters

**Hybrid indexing strategy**
- **Summary vector**: one vector per document built from:
  - document summary + categories + filename
  - saved as metadata `type="summary"`, `id="<filename>_summary"`, `content_snippet=<summary>`
- **Chunk vectors**: multiple vectors per document from chunked content:
  - chunking is simple paragraph accumulation up to ~500 chars
  - metadata `type="chunk"`, `id="<filename>_chunk_<n>"`, `content_snippet=<chunk>`

**Storage**
- FAISS index file: `data/index/faiss_index.bin`
- Metadata (pickled): `data/index/metadata.pkl`
- Per-document enriched metadata JSON: `data/metadata/<filename>.json`

**Query flow**
- Embed query → FAISS search → return top-k metadata records (summary/chunks).
- Optional category filtering happens after retrieval in `SearchEngine.search`.

#### 3.5 Q&A (RAG) with Mistral via Ollama
Implemented in:
- `src/qa_engine.py` (`MistralQAEngine`)
- `app.py` (“Ask AI” tab)

Flow:
- User asks a question
- App retrieves top documents from semantic search
- Q&A engine builds a context string and calls Ollama (`/api/generate`)
- Returns:
  - `answer` (LLM response)
  - `sources` (top filenames)
  - `confidence` (high/medium/low/error)

#### 3.6 Monitoring (watch folder auto-ingestion)
Implemented in `src/monitor.py` using `watchdog`:
- Watches `config.directories.watch` (default `data/watch/`)
- On file creation (pdf/jpg/jpeg/png):
  - debounce for `monitoring.debounce_seconds`
  - calls `DocumentProcessor.process_file(...)`

#### 3.7 Web crawler (scraper)
Implemented in `src/scraper.py` (`NoticesCrawler`):
- BFS crawling from `config.scraping.target_urls`
- Domain-restricted to `config.scraping.base_url` domain
- Downloads files matching extensions into `config.directories.watch`
- Writes:
  - downloaded binary file
  - sidecar metadata: `<file>.<ext>.meta.json`
  - download history: `data/watch/download_history.txt`

### 4) Configuration (config/config.yaml)
Key configuration areas:
- **directories**:
  - `raw`, `processed`, `index`, `watch`, `metadata`, `logs`
- **monitoring**:
  - enabled, debounce, extensions
- **summarization**:
  - method (`mistral` / `extract`), sentences, model_url, model_name
- **scraping**:
  - base_url, target_urls, download_limit, rate_limit, retry_count, timeout, max_depth
- **search**:
  - model_name, top_k

### 5) Data contracts (metadata schema)
Per-file JSON written to `data/metadata/<filename>.json` (example keys):
- `filename` (string)
- `path` (string)
- `type` (string: `"pdf"` / `"image"`)
- `content` (string, cleaned full text)
- `page_count` (int)
- `summary` (string)
- `categories` (list[string])
- `ingest_date` (ISO-8601 string)
- `file_size` (int, bytes)
- `processed` (bool)

FAISS metadata entries stored in `data/index/metadata.pkl` are derived from this, but may omit `content` (deleted before indexing) and add:
- `type`: `"summary"` or `"chunk"`
- `id`: unique ID string
- `content_snippet`: summary or chunk snippet

### 6) External dependencies (runtime)
Python packages (see `requirements.txt`):
- `streamlit`, `sentence-transformers`, `faiss-cpu`, `pymupdf`, `pytesseract`, `Pillow`, `numpy`, `pandas`
- Phase 2: `watchdog`, `beautifulsoup4`, `requests`, `sumy`, `nltk`, `lxml`, `pyyaml`

System packages installed by `setup_arch.sh`:
- `tesseract`, `tesseract-data-eng`, `poppler`, `python`, `python-pip`, `base-devel`

Local services:
- **Ollama** running locally with the **Mistral** model pulled (for summarization/Q&A when method is `"mistral"`).

### 7) How to run
- Setup:
  - `./setup_arch.sh`
- Run app:
  - `./run.sh`
- Streamlit will start on:
  - `http://localhost:8501`

### 8) Known implementation constraints / notes
- **FAISS score semantics**: `FaissIndexer.search()` returns L2 distances; lower means “closer/more similar”. Any UI that converts it to a percentage should treat it carefully.
- **Filtering depends on exact category names**: the filter values must match classifier output strings exactly (e.g. `"Examination"` vs `"Exam"`).

