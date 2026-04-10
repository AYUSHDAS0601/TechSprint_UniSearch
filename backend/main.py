"""
FastAPI backend for Digital Archaeology.
Exposes search, Q&A, ingestion, analytics, and dynamic web crawling endpoints.
"""

import sys
import os
import logging
import time
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any

import yaml
import requests as http_requests
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

# ─── Path bootstrap ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from src.search import SearchEngine
from src.qa_engine import MistralQAEngine

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("API")

# ─── Config ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    cfg_path = BASE_DIR / "config" / "config.yaml"
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f) or {}
    dirs = dict(cfg.get("directories") or {})
    for k, v in list(dirs.items()):
        if isinstance(v, str):
            p = Path(v)
            if not p.is_absolute():
                dirs[k] = str((BASE_DIR / p).resolve())
    cfg["directories"] = dirs
    return cfg

CONFIG = load_config()

# ─── Directories ──────────────────────────────────────────────────────────────
DATA_DIR   = BASE_DIR / "data"
RAW_DIR    = DATA_DIR / "raw"
WATCH_DIR  = DATA_DIR / "watch"
LOG_DIR    = BASE_DIR / "logs"

for d in [RAW_DIR, WATCH_DIR, LOG_DIR, DATA_DIR / "metadata", DATA_DIR / "index", DATA_DIR / "crawled_pages"]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Engines (lazy-init to avoid blocking startup) ────────────────────────────
_search_engine: Optional[SearchEngine] = None
_qa_engine: Optional[MistralQAEngine] = None
_engine_lock = threading.Lock()

def get_search_engine() -> SearchEngine:
    global _search_engine
    if _search_engine is None:
        with _engine_lock:
            if _search_engine is None:
                logger.info("Initialising SearchEngine...")
                _search_engine = SearchEngine(DATA_DIR, config=CONFIG)
    return _search_engine

def get_qa_engine() -> MistralQAEngine:
    global _qa_engine
    if _qa_engine is None:
        summa = CONFIG.get("summarization", {})
        _qa_engine = MistralQAEngine(
            model_url=summa.get("model_url", "http://127.0.0.1:11434/api/generate"),
            model_name=summa.get("model_name", "mistral"),
            timeout=summa.get("timeout", 120),
        )
    return _qa_engine

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Digital Archaeology API",
    version="4.0.0",
    description="Semantic document search and AI Q&A for university archives.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic models ──────────────────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str
    categories: Optional[List[str]] = []
    k: Optional[int] = 5

class QARequest(BaseModel):
    question: str
    k: Optional[int] = 5

class CrawlRequest(BaseModel):
    urls: List[str]              # One or more seed URLs
    max_pages: Optional[int] = 25
    max_depth: Optional[int] = 2
    same_domain_only: Optional[bool] = True
    index_immediately: Optional[bool] = True  # Auto-index scraped pages

# ─── In-memory crawl status ───────────────────────────────────────────────────
_crawl_status: Dict[str, Any] = {
    "running": False,
    "pages_scraped": 0,
    "files_downloaded": 0,
    "indexed": 0,
    "errors": [],
    "log": [],
    "started_at": None,
    "finished_at": None,
}

def _crawl_log(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    _crawl_status["log"].append(entry)
    _crawl_status["log"] = _crawl_status["log"][-100:]  # keep last 100
    logger.info(msg)

# ─── Background crawl task ────────────────────────────────────────────────────
def _run_crawl_job(req: CrawlRequest):
    global _crawl_status
    _crawl_status.update({
        "running": True,
        "pages_scraped": 0,
        "files_downloaded": 0,
        "indexed": 0,
        "errors": [],
        "log": [],
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "finished_at": None,
    })

    try:
        from src.scraper import WebCrawler
        from src.embeddings import EmbeddingGenerator
        from src.indexer import FaissIndexer
        from src.classifier import NoticeClassifier
        from src.utils import clean_text

        embedder = EmbeddingGenerator(CONFIG["search"].get("model_name", "all-MiniLM-L6-v2"))
        indexer = FaissIndexer(DATA_DIR / "index")
        classifier = NoticeClassifier()

        def on_page_saved(page_data: dict):
            """Index each scraped page immediately."""
            if not req.index_immediately:
                return
            full_text = page_data.get("full_text", "").strip()
            if not full_text or len(full_text) < 100:
                return

            title = page_data.get("title", "Scraped Page")
            categories = classifier.classify(full_text)

            # Build a rich indexable string
            indexable = (
                f"{title}\n"
                f"{' '.join(h['text'] for h in page_data.get('headings', []))}\n"
                f"{' '.join(page_data.get('keywords', []))}\n"
                f"{full_text[:2000]}"
            )
            cleaned = clean_text(indexable)

            # Create metadata record
            meta = {
                "filename": title[:120],
                "source_url": page_data.get("source_url", ""),
                "domain": page_data.get("domain", ""),
                "type": "web_page",
                "categories": categories,
                "summary": " ".join(page_data.get("paragraphs", [""])[:2])[:500],
                "content_snippet": full_text[:400],
                "headings": [h["text"] for h in page_data.get("headings", [])],
                "keywords": page_data.get("keywords", []),
                "dates_found": page_data.get("dates_found", []),
                "ingest_date": page_data.get("scraped_at", ""),
                "file_size": len(full_text.encode()),
                "processed": True,
            }

            # Chunk and index
            chunks = [cleaned[i:i+500] for i in range(0, min(len(cleaned), 3000), 400)]
            if not chunks:
                return

            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:
                    continue
                emb = embedder.generate(chunk)
                if len(emb.shape) == 1:
                    emb = emb.reshape(1, -1)
                chunk_meta = meta.copy()
                chunk_meta["type"] = "web_chunk"
                chunk_meta["id"] = f"{page_data['source_url']}_chunk_{i}"
                chunk_meta["content_snippet"] = chunk[:400]
                indexer.add_single_document(emb[0], chunk_meta)
                _crawl_status["indexed"] += 1

            _crawl_log(f"Indexed: {title[:60]!r} (+{len(chunks)} chunks)")

        _crawl_log(f"Starting crawl of {req.urls}")
        crawler = WebCrawler(
            download_dir=WATCH_DIR,
            data_dir=DATA_DIR,
            rate_limit=1.2,
            timeout=12,
            retry_count=2,
            same_domain_only=req.same_domain_only,
        )

        result = crawler.crawl(
            start_urls=req.urls,
            max_pages=req.max_pages,
            max_depth=req.max_depth,
            download_files=True,
            on_page_saved=on_page_saved,
        )

        _crawl_status["pages_scraped"] = result["pages_scraped"]
        _crawl_status["files_downloaded"] = result["files_downloaded"]

        # Also ingest any downloaded PDFs/images
        if result["files_downloaded"] > 0:
            _crawl_log("Processing downloaded binary files...")
            try:
                engine = get_search_engine()
                new_files = engine.ingest_new_files()
                _crawl_log(f"Indexed {len(new_files)} binary files.")
            except Exception as e:
                _crawl_status["errors"].append(f"Binary ingest error: {e}")

        # Reload the search engine's indexer so new data is immediately searchable
        try:
            engine = get_search_engine()
            engine.indexer._load_or_create_index()
            _crawl_log("Search index refreshed.")
        except Exception as e:
            _crawl_status["errors"].append(f"Index refresh error: {e}")

        _crawl_log(f"Done. pages={result['pages_scraped']}, files={result['files_downloaded']}, indexed={_crawl_status['indexed']}")

    except Exception as e:
        _crawl_status["errors"].append(str(e))
        _crawl_log(f"FATAL: {e}")
        logger.exception("Crawl job failed")
    finally:
        _crawl_status["running"] = False
        _crawl_status["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Digital Archaeology API", "version": "4.0.0", "status": "online"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}

@app.get("/api/stats")
async def get_stats():
    try:
        engine = get_search_engine()
        total_vectors = engine.indexer.index.ntotal if engine.indexer.index else 0
        total_docs = len(list(RAW_DIR.glob("*"))) + len(list(WATCH_DIR.glob("*")))
    except Exception:
        total_vectors = 0
        total_docs = 0

    # Check Ollama
    summa = CONFIG.get("summarization", {})
    model_name = summa.get("model_name", "mistral")
    ollama_ok = False
    try:
        base = summa.get("model_url", "http://127.0.0.1:11434/api/generate")
        base = base.split("/api/")[0]
        resp = http_requests.get(f"{base}/api/tags", timeout=2)
        tags = resp.json().get("models", [])
        ollama_ok = any(m.get("name") == model_name for m in tags)
    except Exception:
        pass

    return {
        "total_documents": total_docs,
        "total_vectors": total_vectors,
        "llm_model": model_name,
        "llm_available": ollama_ok,
        "status": "online",
    }

@app.post("/api/search")
async def search(req: SearchRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        engine = get_search_engine()
        filters = {"categories": req.categories} if req.categories else None
        results = engine.search(req.query, k=req.k or 5, filters=filters)

        # Normalise score field so frontend gets 0..1 similarity (not L2 distance)
        for r in results:
            raw = r.get("score", 0)
            # L2 distance → bounded similarity: sim = 1 / (1 + dist)
            r["score"] = float(1.0 / (1.0 + raw))

        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.exception("Search failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qa")
async def ask_question(req: QARequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        engine = get_search_engine()
        search_results = engine.search(req.question, k=req.k or 5)
        context_docs = [
            {
                "filename": r.get("filename", "Unknown"),
                "text": r.get("content_snippet", "") or r.get("summary", ""),
                "summary": r.get("summary", ""),
                "source_url": r.get("source_url", ""),
            }
            for r in search_results
        ]

        if not context_docs:
            return {"answer": "No relevant documents found in the archive for your question.", "sources": []}

        qa = get_qa_engine()
        result = qa.answer_question(req.question, context_docs)

        # Include source URLs if available
        sources_with_url = []
        for r in search_results[:3]:
            fn = r.get("filename", "Unknown")
            url = r.get("source_url", "")
            sources_with_url.append({"name": fn, "url": url})

        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "sources_detail": sources_with_url,
            "confidence": result.get("confidence", "medium"),
        }
    except Exception as e:
        logger.exception("Q&A failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
async def ingest_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    try:
        saved = []
        for uf in files:
            dest = RAW_DIR / uf.filename
            content = await uf.read()
            dest.write_bytes(content)
            saved.append(uf.filename)
            logger.info(f"Saved upload: {uf.filename} ({len(content)/1024:.1f} KB)")

        engine = get_search_engine()
        new_indexed = engine.ingest_new_files()
        return {
            "message": f"Processed {len(saved)} file(s).",
            "saved_files": saved,
            "indexed": len(new_indexed),
        }
    except Exception as e:
        logger.exception("Ingest failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crawl/start")
async def start_crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Start a background crawl job.
    Accepts one or more URLs, crawls each page, extracts text,
    and indexes into FAISS for immediate searchability.
    """
    if _crawl_status["running"]:
        raise HTTPException(status_code=409, detail="A crawl is already running. Wait for it to finish.")

    if not req.urls:
        raise HTTPException(status_code=400, detail="Provide at least one URL to crawl.")

    # Validate URLs
    valid_urls = []
    for u in req.urls:
        u = u.strip()
        if not u.startswith(("http://", "https://")):
            u = "https://" + u
        valid_urls.append(u)
    req.urls = valid_urls

    background_tasks.add_task(_run_crawl_job, req)
    return {
        "message": "Crawl started in background.",
        "urls": req.urls,
        "max_pages": req.max_pages,
    }

@app.get("/api/crawl/status")
async def crawl_status():
    """Return current crawl job status (poll this for live progress)."""
    return dict(_crawl_status)

@app.post("/api/crawl/stop")
async def stop_crawl():
    """Signal the crawl to stop (best-effort)."""
    _crawl_status["running"] = False
    return {"message": "Stop signal sent."}

@app.get("/api/logs")
async def get_logs(lines: int = Query(30, ge=1, le=200)):
    log_file = LOG_DIR / "app.log"
    if not log_file.exists():
        return {"logs": ["No log file found."]}
    all_lines = log_file.read_text(errors="replace").splitlines()
    return {"logs": all_lines[-lines:]}

# Backward-compatible scrape endpoint
@app.post("/api/scrape")
async def run_scrape_legacy(background_tasks: BackgroundTasks):
    """Legacy endpoint: crawl config URLs."""
    cfg_urls = CONFIG.get("scraping", {}).get("target_urls", [])
    if not cfg_urls:
        raise HTTPException(status_code=400, detail="No target_urls in config.yaml")
    req = CrawlRequest(urls=cfg_urls, max_pages=CONFIG["scraping"].get("download_limit", 20))
    background_tasks.add_task(_run_crawl_job, req)
    return {"message": f"Crawl started for {len(cfg_urls)} configured URL(s)."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
