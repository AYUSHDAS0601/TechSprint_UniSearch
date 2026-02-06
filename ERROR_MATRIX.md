# Digital Archaeology — Error Matrix

### How to use this
Each row is a common failure mode with:
- **Symptoms**: what you see in the UI/terminal/logs
- **Likely cause**
- **Where to check**
- **Fix / workaround**

Log files:
- Streamlit + modules write to **`app.log`** by default (see `src/utils.py:setup_logging`).

---

### Error matrix (by subsystem)

| ID | Subsystem | Symptoms | Likely cause | Where to check | Fix / workaround | Severity |
|---:|---|---|---|---|---|---|
| E-SETUP-001 | Setup / Run | `Error: Virtual environment not found.` when running `./run.sh` | `venv/` not created | Terminal output | Run `./setup_arch.sh` to create venv + install deps | High |
| E-SETUP-002 | OCR | OCR always fails / empty text | `tesseract` not installed or not in PATH | `./run.sh` warning; `app.log` OCR logs | Install `tesseract tesseract-data-eng` (Arch: `sudo pacman -S tesseract tesseract-data-eng`) | High |
| E-OCR-001 | OCR | PDF ingestion returns no content | PDF is scanned; OCR failed; bad image render | `app.log` (OCR_Module) | Ensure `tesseract` works; try higher quality PDF; confirm file opens; re-run ingestion | High |
| E-OCR-002 | OCR | `fitz` / PyMuPDF import errors | `pymupdf` missing / broken install | Terminal / `app.log` | Reinstall deps inside venv: `pip install -r requirements.txt` | High |
| E-OCR-003 | OCR | Image files error on open | Corrupt image / unsupported encoding | `app.log` OCR errors | Re-export image (PNG/JPG), retry | Medium |
| E-EMB-001 | Embeddings | App hangs on first run / model download fails | SentenceTransformers model not cached and network blocked | Terminal / `app.log` (Embeddings_Module) | Run `./setup_arch.sh` (pre-download). If offline, pre-cache model beforehand | High |
| E-EMB-002 | Embeddings | `Failed to load model ...` | wrong model name in config | `config/config.yaml` and `app.log` | Set `search.model_name` to a valid SentenceTransformers model (default: `all-MiniLM-L6-v2`) | High |
| E-IDX-001 | Index | Search returns 0 results even after ingestion | index empty / ingestion never indexed | `data/index/metadata.pkl`, `app.log` (Indexer_Module) | Re-run ingestion; verify files exist in `data/raw/`; check processor errors | High |
| E-IDX-002 | Index | Index “resets” unexpectedly | `metadata.pkl`/`faiss_index.bin` corrupt → index recreated | `app.log` (`Failed to load index... creating new one`) | Restore from backup; otherwise re-ingest documents | Medium |
| E-PROC-001 | Processor | Metadata JSON not created | `data/metadata/` path missing/permission | `data/metadata/` and `app.log` (DocumentProcessor) | Ensure directories exist and are writable; rerun | Medium |
| E-SUM-001 | Summarizer | Summaries are very short / look like first 200 chars | summarizer backend failed → fallback | `app.log` (Summarizer) | Use `summarization.method: extract` for offline reliability; ensure NLTK data is available | Low |
| E-SUM-002 | Summarizer | NLTK download errors | first-time NLTK `punkt` download blocked | `app.log` (Summarizer) | Preinstall NLTK data (online once) or vendor it; switch to `mistral` summarization if available | Medium |
| E-LLM-001 | Ollama / Mistral | Q&A shows: `Error generating answer... ensure Ollama is running` | Ollama not running / wrong URL | `app.log` (QA_Engine); curl Ollama endpoint | Start Ollama; verify `summarization.model_url` is `http://localhost:11434/api/generate` | High |
| E-LLM-002 | Ollama / Mistral | Q&A is slow / times out | model cold start; machine too slow; timeout | `app.log` | Pull model ahead of time; increase timeout; reduce context size | Medium |
| E-QA-001 | Q&A integration | Answers are generic / context seems empty | app passes `text` but search metadata uses `content_snippet` / `summary` keys | `app.py` Q&A block; search results dict | Map retrieved fields correctly (use `summary` / `content_snippet`); re-test | Medium |
| E-SEARCH-001 | Search UI | Relevance % looks wrong / increases with worse matches | FAISS returns L2 distance (lower is better) but UI treats as “score” | `src/indexer.py`, `src/search.py`, UI card | Convert distance to similarity or display “distance” instead of percent | Low |
| E-SEARCH-002 | Search | Category filter removes everything | Filter values don’t match classifier categories | UI list vs `src/classifier.py` | Align UI options to: `Examination, Scholarship, Transport, Academic, Administrative, Events, General` | High |
| E-MON-001 | Monitor | Dropping a file into watch dir does nothing | monitor not running | separate monitor process | Run `python -m src.monitor` (or `src/monitor.py`) alongside app if desired | Medium |
| E-MON-002 | Monitor | Duplicate/partial processing | file still being copied when event fires | `src/monitor.py` debounce | Increase `monitoring.debounce_seconds` in config | Low |
| E-SCRAPE-001 | Scraper | Crawl downloads 0 files | selectors/pages not relevant; limit reached; domain restriction | `app.log` (Scraper) | Adjust `scraping.target_urls`, increase `max_depth`, verify site structure | Medium |
| E-SCRAPE-002 | Scraper | SSL / request warnings, fetch failures | `verify=False` + site blocks or timeouts | `app.log` | Increase timeout/retry; lower rate; try different seed URLs | Medium |
| E-UI-001 | UI | Styling looks “broken” after Streamlit update | Streamlit DOM/CSS selectors changed | visual regression | Prefer stable selectors; adjust CSS in `src/styles.py` | Low |

---

### Quick “first checks” checklist
- **Files exist** in `data/raw/` (uploads saved)
- **Metadata appears** in `data/metadata/`
- **Index exists** in `data/index/` (`faiss_index.bin`, `metadata.pkl`)
- **Ollama running** (if using Mistral features)
- **Category filter matches classifier strings** (see `src/classifier.py`)

