import streamlit as st
import time
import yaml
from pathlib import Path
import requests

from src.search import SearchEngine
from src.styles import get_css, result_card_html
from src.qa_engine import MistralQAEngine

# Page Config
st.set_page_config(
    page_title="Digital Archaeology",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Modern CSS
st.markdown(get_css(), unsafe_allow_html=True)

# Initialize paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
LOG_DIR = BASE_DIR / "logs"

# Load Config
@st.cache_resource
def load_config():
    with open(BASE_DIR / "config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f) or {}
    # Convert configured directory paths to absolute paths
    dirs = dict(cfg.get("directories") or {})
    for k, v in list(dirs.items()):
        if isinstance(v, str) and v:
            p = Path(v)
            if not p.is_absolute():
                dirs[k] = str((BASE_DIR / p).resolve())
    cfg["directories"] = dirs
    return cfg

def ollama_base_url(model_url: str) -> str:
    if not model_url:
        return "http://127.0.0.1:11434"
    idx = model_url.find("/api/")
    return model_url[:idx] if idx != -1 else model_url.rstrip("/")

config = load_config()

# Initialize Session State Engines
if 'engine' not in st.session_state:
    with st.spinner("Initializing Semantic Search Engine..."):
        st.session_state.engine = SearchEngine(DATA_DIR, config=config)

if 'qa_engine' not in st.session_state:
    summa_cfg = config.get('summarization', {})
    st.session_state.qa_engine = MistralQAEngine(
        model_url=summa_cfg.get('model_url', "http://localhost:11434/api/generate"),
        model_name=summa_cfg.get('model_name', 'mistral'),
        timeout=summa_cfg.get('timeout', 120),
    )

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hello! I am your AI assistant. Ask me anything about the university policies, schedules, or notices.", "sources": []}
    ]

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8rem !important; margin-bottom: 0;">UNI<span style="font-weight:300;">SEARCH</span></h1>
        <p style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 500;">AI-POWERED ARCHIVE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ollama Diagnostics
    st.markdown("### 🤖 System Status")
    summa_cfg = config.get("summarization", {}) or {}
    model_url = summa_cfg.get("model_url", "http://127.0.0.1:11434/api/generate")
    model_name = summa_cfg.get("model_name", "mistral")
    base = ollama_base_url(model_url)

    try:
        tags = requests.get(f"{base}/api/tags", timeout=2).json()
        models = [m.get("name") for m in (tags.get("models") or [])]
        if model_name in models:
            st.success(f"Connected: `{model_name}`")
        else:
            st.warning(f"Model `{model_name}` not found. Run `ollama pull {model_name}`")
    except Exception as e:
        st.error("Cannot reach LLM backend. Ensure Ollama is running.")
    
    st.markdown("### 📤 Ingestion Portal")
    uploaded_files = st.file_uploader("Upload Documents (PDF, Images)", type=['pdf', 'png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process & Index", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            for i, uf in enumerate(uploaded_files):
                file_path = RAW_DIR / uf.name
                with open(file_path, "wb") as f:
                    f.write(uf.getbuffer())
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            with st.spinner("Processing documents into vector space..."):
                st.session_state.engine.ingest_new_files()
            st.success(f"Successfully processed {len(uploaded_files)} files!")

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: var(--text-secondary); font-size: 0.75rem;'>v4.0.0 Genesis Edition</p>", unsafe_allow_html=True)

# Main Application
tab_search, tab_qa, tab_dashboard, tab_scraper = st.tabs(["🔍 Semantic Search", "💬 Ask AI", "📊 Analytics", "🕷️ Web Crawler"])

# --- TAB 1: SEARCH ---
with tab_search:
    st.markdown("<h2>Information Retrieval</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-secondary); margin-bottom: 2rem;'>Instantly find relevant notices and documents from the university archives.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Search Query", placeholder="e.g., 'Exam Schedule for B.Tech CSE'", label_visibility="collapsed")
    with col2:
        category_filter = st.multiselect("Category", ["Examination", "Scholarship", "Events", "General", "Administrative"], default=[], label_visibility="collapsed")

    if query:
        with st.spinner("Searching vector space..."):
            start_time = time.time()
            filters = {'categories': category_filter} if category_filter else None
            results = st.session_state.engine.search(query, k=config['search']['top_k'], filters=filters)
            end_time = time.time()
            
        st.caption(f"⚡ Found **{len(results)}** results in **{end_time - start_time:.3f}s**")
        
        for res in results:
            categories = res.get('categories', ['General'])
            res_type = res.get('type', 'unknown')
            
            summary_text = res.get('summary', '') if res_type == 'summary' else f"...{res.get('content_snippet', '')}..."
            if not summary_text:
                summary_text = str(res.get('text', 'No preview available.'))[:250] + "..."

            html = result_card_html(
                title=res.get('filename', 'Unknown Document'),
                summary=summary_text,
                tags=categories,
                score=res.get('score', 0) * 100,
                size=res.get('file_size', 0)//1024,
                file_type=res_type.upper(),
                query=query
            )
            st.markdown(html, unsafe_allow_html=True)

# --- TAB 2: AI ASSISTANT ---
with tab_qa:
    st.markdown("<h2>AI Research Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-secondary); margin-bottom: 1rem;'>Ask questions related to university documents and get synthesized answers with sources.</p>", unsafe_allow_html=True)
    
    # Display Chat History
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"], avatar="✨" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("View Referenced Sources"):
                        for i, source in enumerate(msg["sources"], 1):
                            st.caption(f"**{i}.** {source}")
    
    # Input
    if prompt := st.chat_input("Ask about scholarship deadlines, exam delays..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
                
            with st.chat_message("assistant", avatar="✨"):
                response_placeholder = st.empty()
                response_placeholder.markdown("🔍 _Scanning documents..._")
                
                # Fetch relevant docs
                search_results = st.session_state.engine.search(prompt, k=5)
                context_docs = []
                for res in search_results:
                    context_docs.append({
                        'filename': res.get('filename', 'Unknown'),
                        'text': res.get('content_snippet', '') or res.get('summary', ''),
                        'summary': res.get('summary', '')
                    })
                
                if not context_docs:
                    reply = "I couldn't find any relevant university documents regarding that query."
                    response_placeholder.markdown(reply)
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                else:
                    response_placeholder.markdown("🧠 _Synthesizing response..._")
                    qa_result = st.session_state.qa_engine.answer_question(prompt, context_docs)
                    
                    answer = qa_result['answer']
                    sources = qa_result.get('sources', [])
                    
                    response_placeholder.markdown(answer)
                    if sources:
                        with st.expander("View Referenced Sources"):
                            for i, src in enumerate(sources, 1):
                                st.caption(f"**{i}.** {src}")
                                
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })

# --- TAB 3: DASHBOARD ---
with tab_dashboard:
    st.markdown("<h2>System Analytics</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    total_docs = len(list(RAW_DIR.glob("*")))
    total_vectors = st.session_state.engine.indexer.index.ntotal if hasattr(st.session_state.engine.indexer, 'index') else 0
    
    with col1:
        st.markdown(f"""
        <div class="glass-metric">
            <div class="glass-metric-icon">📄</div>
            <div class="glass-metric-value">{total_docs}</div>
            <div class="glass-metric-label">RAW DOCUMENTS</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-metric">
            <div class="glass-metric-icon">🧮</div>
            <div class="glass-metric-value">{total_vectors}</div>
            <div class="glass-metric-label">VECTOR EMBEDDINGS</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-metric">
            <div class="glass-metric-icon">⚡</div>
            <div class="glass-metric-value" style="font-size:1.8rem; margin-top:0.45rem;">Online</div>
            <div class="glass-metric-label">SYSTEM STATUS</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="glass-metric">
            <div class="glass-metric-icon">🤖</div>
            <div class="glass-metric-value" style="font-size:1.8rem; margin-top:0.45rem;">{model_name}</div>
            <div class="glass-metric-label">ACTIVE LLM</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📜 System Logs")
    log_file = LOG_DIR / "app.log"
    if log_file.exists():
        with open(log_file, "r") as f:
            lines = "".join(f.readlines()[-20:])
            st.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)

# --- TAB 4: WEB CRAWLER ---
with tab_scraper:
    st.markdown("<h2>Automated Scraper</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-secondary);'>Fetch updates dynamically from the university website.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns([2, 1, 1])
        
        with sc1:
            if st.button("🚀 Execute Spider Module", type="primary", use_container_width=True):
                with st.spinner("Spider initiating operations..."):
                    try:
                        from src.scraper import NoticesCrawler
                        crawler = NoticesCrawler()
                        downloaded = crawler.crawl(limit=config['scraping']['download_limit'])
                        st.success(f"Download sequence complete. Acquired {downloaded} new notices.")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during execution: {e}")
        
        with sc2:
            st.markdown(f"""
            <div class="glass-metric" style="padding: 1rem;">
                <div class="glass-metric-value" style="font-size: 1.5rem;">{config['scraping'].get('max_depth', 2)}</div>
                <div class="glass-metric-label">MAX DEPTH</div>
            </div>
            """, unsafe_allow_html=True)
            
        with sc3:
            st.markdown(f"""
            <div class="glass-metric" style="padding: 1rem;">
                <div class="glass-metric-value" style="font-size: 1.5rem;">{config['scraping'].get('download_limit', 20)}</div>
                <div class="glass-metric-label">PAYLOAD LIMIT</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("### 📡 Scraper Telemetry")
    scraper_log = LOG_DIR / "Scraper.log"
    
    if scraper_log.exists():
        with open(scraper_log, "r") as f:
            lines = "".join(f.readlines()[-20:])
            st.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)
    else:
        st.info("No crawler telemetry acquired yet.")
