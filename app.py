import streamlit as st
import time
import yaml
import subprocess
from pathlib import Path
import pandas as pd
from src.search import SearchEngine
from src.utils import setup_logging
from src.styles import get_css, result_card_html
from src.qa_engine import MistralQAEngine

# Page Config
st.set_page_config(
    page_title="Digital Archaeology",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
st.markdown(get_css(), unsafe_allow_html=True)

# Initialize paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
LOG_DIR = BASE_DIR / "logs"

# Load Config
def load_config():
    with open(BASE_DIR / "config/config.yaml", 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize Session State
if 'engine' not in st.session_state:
    with st.spinner("Initializing Search Engine..."):
        st.session_state.engine = SearchEngine(DATA_DIR)

if 'qa_engine' not in st.session_state:
    st.session_state.qa_engine = MistralQAEngine(
        model_url=config['summarization']['model_url'],
        model_name=config['summarization']['model_name']
    )

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; background: rgba(0, 0, 0, 0.5); border-radius: 12px; border: 2px solid #00f0ff; box-shadow: 0 0 30px rgba(0, 240, 255, 0.3); margin-bottom: 1rem;">
        <div style="font-family: 'Share Tech Mono', monospace; color: #00ff41; font-size: 0.7rem; margin-bottom: 0.5rem; letter-spacing: 0.2em;">
            ╔═══════════════════════════╗<br>
            ║  SYSTEM INITIALIZED  ║<br>
            ╚═══════════════════════════╝
        </div>
        <h1 style="font-size: 1.8rem; margin: 0; font-family: 'Orbitron', sans-serif; color: #00f0ff; text-shadow: 0 0 20px rgba(0, 240, 255, 0.8); letter-spacing: 0.05em;">
            🏛️ DIGITAL<br>ARCHAEOLOGY
        </h1>
        <p style="color: #ff00ff; margin-top: 0.75rem; font-size: 0.85rem; font-family: 'Rajdhani', sans-serif; font-weight: 700; letter-spacing: 0.15em; text-shadow: 0 0 10px rgba(255, 0, 255, 0.6);">
            [ SEMANTIC SEARCH ENGINE ]
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background: rgba(0, 240, 255, 0.05); 
                padding: 1.25rem; border-radius: 12px; margin-bottom: 1.5rem; border: 2px solid #00f0ff; box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);">
        <h3 style="margin: 0 0 0.75rem 0; color: #00f0ff; font-size: 1rem; font-weight: 700; font-family: 'Orbitron', sans-serif; letter-spacing: 0.1em; text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);">
            📤 DOCUMENT INGESTION
        </h3>
        <p style="color: #00ff41; font-size: 0.8rem; margin: 0; font-family: 'Rajdhani', sans-serif;">
            &gt; Upload PDFs or images to process and index
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload Notices", 
        type=['pdf', 'png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.info(f"📎 {len(uploaded_files)} file(s) selected")
        if st.button("🚀 Process & Index", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save files
            for i, uploaded_file in enumerate(uploaded_files):
                file_path = RAW_DIR / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("🔄 Running Indexing...")
            st.session_state.engine.ingest_new_files()
            st.success(f"✅ Processed {len(uploaded_files)} files successfully!")

    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; background: rgba(0, 0, 0, 0.5); border-radius: 8px; border: 1px solid rgba(0, 240, 255, 0.3);">
        <p style="color: #00ff41; font-size: 0.75rem; margin: 0; font-family: 'Share Tech Mono', monospace;">
            <strong style="color: #00f0ff; text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);">v3.0 CYBERPUNK</strong> | NEON BUILD
        </p>
        <p style="color: #ff00ff; font-size: 0.7rem; margin-top: 0.5rem; font-family: 'Rajdhani', sans-serif;">
            &gt; POWERED BY AI &lt;
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main Tabs
tab_search, tab_qa, tab_dashboard, tab_scraper = st.tabs(["🔍 Search", "💬 Ask AI", "📊 Dashboard", "🕸️ Scraper"])

# --- TAB 1: SEARCH ---
with tab_search:
    st.markdown("""
    <div style="margin-bottom: 2rem; background: rgba(0, 0, 0, 0.5); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #00f0ff; box-shadow: 0 0 30px rgba(0, 240, 255, 0.2);">
        <h2 style="margin-bottom: 0.5rem;">🔍 SEMANTIC SEARCH</h2>
        <p style="color: #00ff41; font-size: 1rem; margin: 0; font-family: 'Rajdhani', sans-serif;">
            &gt; Find what you need instantly with AI-powered semantic search
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Holographic search bar container
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.5); border: 2px solid #00f0ff;
                padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 0 30px rgba(0, 240, 255, 0.3); margin-bottom: 2rem;">
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Query", 
            placeholder="🔎 e.g., 'Java Lab Exam Schedule' or 'Scholarship application deadline'", 
            label_visibility="collapsed"
        )
    with col2:
        category_filter = st.multiselect(
            "Filter", 
            ["Exam", "General", "Scholarship", "Holiday"], 
            default=[], 
            label_visibility="collapsed", 
            placeholder="🏷️ Category"
        )

    if query:
        start_time = time.time()
        filters = {'categories': category_filter} if category_filter else None
        results = st.session_state.engine.search(query, k=config['search']['top_k'], filters=filters)
        end_time = time.time()
        
        st.markdown(f"""
        <div style="background: rgba(0, 240, 255, 0.05); border: 2px solid #00f0ff;
                    padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 2rem; 
                    box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);">
            <p style="color: #00f0ff; margin: 0; font-weight: 700; font-size: 1rem; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);">
                ⚡ FOUND <span style="color: #ff00ff; font-weight: 900;">{len(results)}</span> RESULT(S) IN 
                <span style="color: #00ff41; font-weight: 900;">{end_time - start_time:.3f}s</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        for res in results:
            # Prepare data for card
            categories = res.get('categories', ['General'])
            res_type = res.get('type', 'unknown')
            
            summary_text = ""
            if res_type == 'summary':
                summary_text = res.get('summary', '')
            elif res_type == 'chunk':
                summary_text = f"...{res.get('content_snippet', '')}..."
            
            # Fallback if empty
            if not summary_text:
                summary_text = str(res.get('content_snippet', 'No preview available.'))[:250] + "..."

            # Render Card with keyword highlighting
            html = result_card_html(
                title=res.get('filename', 'Unknown'),
                summary=summary_text,
                tags=categories,
                score=res.get('score', 0) * 100, # Approx %
                size=res.get('file_size', 0)//1024,
                file_type=res.get('type', 'doc').upper(),
                query=query  # Pass query for highlighting
            )
            st.markdown(html, unsafe_allow_html=True)

# --- TAB 2: Q&A WITH AI ---
with tab_qa:
    st.markdown("""
    <div style="margin-bottom: 2rem; background: rgba(0, 0, 0, 0.5); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ff00ff; box-shadow: 0 0 30px rgba(255, 0, 255, 0.2);">
        <h2 style="margin-bottom: 0.5rem;">💬 AI QUERY INTERFACE</h2>
        <p style="color: #00ff41; font-size: 1rem; margin: 0; font-family: 'Rajdhani', sans-serif;">
            &gt; Get intelligent answers powered by Mistral AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Holographic question input area
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.5); border: 2px solid #ff00ff;
                padding: 2rem; border-radius: 12px; 
                box-shadow: 0 0 30px rgba(255, 0, 255, 0.3); margin-bottom: 1.5rem;">
    </div>
    """, unsafe_allow_html=True)
    
    # Question input
    question = st.text_input(
        "Your Question",
        placeholder="💭 e.g., 'When is the exam registration deadline for B.Tech students?'",
        key="qa_question"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("🤖 Ask Mistral", type="primary", use_container_width=True)
    
    if ask_button and question:
        with st.spinner("🔍 Searching relevant documents..."):
            # First, search for relevant documents
            search_results = st.session_state.engine.search(question, k=5)
        
        if not search_results:
            st.warning("No relevant documents found for your question.")
        else:
            with st.spinner("🧠 Generating answer with Mistral..."):
                # Prepare context documents
                context_docs = []
                for res in search_results:
                    context_docs.append({
                        'filename': res.get('filename', 'Unknown'),
                        'text': res.get('text', ''),
                        'summary': res.get('summary', '')
                    })
                
                # Get answer from Q&A engine
                qa_result = st.session_state.qa_engine.answer_question(question, context_docs)
            
            # Display answer with enhanced styling
            st.markdown("### 📝 Answer")
            
            # Confidence indicator
            confidence = qa_result.get('confidence', 'medium')
            confidence_colors = {
                'high': '#10B981',
                'medium': '#F59E0B',
                'low': '#EF4444',
                'error': '#DC2626'
            }
            confidence_icons = {
                'high': '✅',
                'medium': '⚠️',
                'low': '❌',
                'error': '🚫'
            }
            confidence_color = confidence_colors.get(confidence, '#94A3B8')
            confidence_icon = confidence_icons.get(confidence, '❓')
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%); 
                        backdrop-filter: blur(10px);
                        padding: 2rem; 
                        border-radius: 20px; 
                        border-left: 6px solid {confidence_color};
                        margin-bottom: 1.5rem;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        position: relative;
                        overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 200px; height: 200px; 
                            background: radial-gradient(circle, {confidence_color}20 0%, transparent 70%);
                            border-radius: 50%; transform: translate(50%, -50%);"></div>
                <div style="color: #E2E8F0; font-size: 1.1rem; line-height: 1.8; position: relative; z-index: 1;">
                    {qa_result['answer']}
                </div>
                <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px solid rgba(71, 85, 105, 0.5);
                            display: flex; align-items: center; gap: 0.75rem; position: relative; z-index: 1;">
                    <span style="font-size: 1.5rem;">{confidence_icon}</span>
                    <span style="color: #94A3B8; font-size: 0.9rem; font-weight: 600;">
                        Confidence Level: <span style="color: {confidence_color}; font-weight: 800; font-size: 1rem;">{confidence.upper()}</span>
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display sources
            if qa_result.get('sources'):
                st.markdown("### 📚 Sources")
                st.markdown("*Answer based on the following documents:*")
                for i, source in enumerate(qa_result['sources'], 1):
                    st.markdown(f"- **{i}.** {source}")
            
            # Show relevant documents
            with st.expander("🔍 View Retrieved Documents"):
                for i, res in enumerate(search_results[:3], 1):
                    st.markdown(f"**{i}. {res.get('filename', 'Unknown')}**")
                    st.caption(res.get('summary', res.get('text', '')[:200]))
                    st.markdown("---")

# --- TAB 3: DASHBOARD ---
with tab_dashboard:
    st.markdown("""
    <div style="margin-bottom: 2rem; background: rgba(0, 0, 0, 0.5); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #00ff41; box-shadow: 0 0 30px rgba(0, 255, 65, 0.2);">
        <h2 style="margin-bottom: 0.5rem;">📊 SYSTEM DIAGNOSTICS</h2>
        <p style="color: #00ff41; font-size: 1rem; margin: 0; font-family: 'Rajdhani', sans-serif;">
            &gt; Monitor your system performance and statistics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Custom Metric Cards
    total_docs = len(list(RAW_DIR.glob("*")))
    total_vectors = st.session_state.engine.indexer.index.ntotal if hasattr(st.session_state.engine.indexer, 'index') else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📄</div>
            <div class="metric-value">{total_docs}</div>
            <div class="metric-label">Total Documents</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔢</div>
            <div class="metric-value">{total_vectors}</div>
            <div class="metric-label">Indexed Vectors</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
         st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✅</div>
            <div class="metric-value" style="font-size: 1.5rem;">Active</div>
            <div class="metric-label">System Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚡</div>
            <div class="metric-value" style="font-size: 1.5rem;">v2.1</div>
            <div class="metric-label">Version</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📜 Activity Log")
    log_file = LOG_DIR / "app.log"
    if log_file.exists():
        with open(log_file, "r") as f:
            lines = "".join(f.readlines()[-15:])
            st.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)

# --- TAB 4: WEB CRAWLER ---
with tab_scraper:
    st.markdown("""
    <div style="margin-bottom: 2rem; background: rgba(0, 0, 0, 0.5); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ff00ff; box-shadow: 0 0 30px rgba(255, 0, 255, 0.2);">
        <h2 style="margin-bottom: 0.5rem;">🕸️ WEB CRAWLER</h2>
        <p style="color: #00ff41; font-size: 1rem; margin: 0; font-family: 'Rajdhani', sans-serif;">
            &gt; Automatically discover and download notices from the university website
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.5); border: 2px solid #ff00ff;
                    padding: 2rem; border-radius: 12px; 
                    box-shadow: 0 0 30px rgba(255, 0, 255, 0.3); margin-bottom: 2rem;">
            <h3 style="margin: 0 0 1.5rem 0; color: #ff00ff; font-size: 1.2rem; font-weight: 700; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px rgba(255, 0, 255, 0.6); letter-spacing: 0.1em;">
                🎮 CRAWLER CONTROL PANEL
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("▶️ Start Crawling", type="primary", use_container_width=True):
                with st.spinner("🕷️ Crawling website (this may take a minute)..."):
                    try:
                        from src.scraper import NoticesCrawler
                        crawler = NoticesCrawler()
                        downloaded = crawler.crawl(limit=config['scraping']['download_limit'])
                        st.success(f"✅ Downloaded {downloaded} new files!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())
        
        with col2:
            st.markdown(f"""
            <div class="metric-container" style="padding: 1.5rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📏</div>
                <div class="metric-value" style="font-size: 2rem;">{config['scraping'].get('max_depth', 2)}</div>
                <div class="metric-label">Max Depth</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container" style="padding: 1.5rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📥</div>
                <div class="metric-value" style="font-size: 2rem;">{config['scraping'].get('download_limit', 20)}</div>
                <div class="metric-label">Download Limit</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### 📡 Live Logs")
    scraper_log = LOG_DIR / "Scraper.log"
    
    # Auto-refresh mechanism via button
    if st.button("🔄 Refresh Logs"):
        pass
        
    if scraper_log.exists():
        with open(scraper_log, "r") as f:
            lines = "".join(f.readlines()[-30:])
            st.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)
    else:
        st.info("No crawler logs found yet.")

# Cyberpunk Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: rgba(0, 0, 0, 0.5);
            border-radius: 12px; margin-top: 3rem; border: 1px solid rgba(0, 240, 255, 0.3); box-shadow: 0 0 30px rgba(0, 240, 255, 0.2);">
    <p style="color: #00f0ff; font-size: 0.9rem; margin: 0.5rem 0; font-family: 'Orbitron', sans-serif; font-weight: 700; text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);">
        DIGITAL ARCHAEOLOGY v3.0 CYBERPUNK
    </p>
    <p style="color: #00ff41; font-size: 0.75rem; margin: 0.5rem 0; font-family: 'Share Tech Mono', monospace;">
        &gt; BUILT WITH AI • POWERED BY NEON &lt;
    </p>
    <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1.5rem;">
        <span style="color: #00f0ff; font-size: 1.2rem; text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);">🏛️</span>
        <span style="color: #ff00ff; font-size: 1.2rem; text-shadow: 0 0 10px rgba(255, 0, 255, 0.6);">🔍</span>
        <span style="color: #00ff41; font-size: 1.2rem; text-shadow: 0 0 10px rgba(0, 255, 65, 0.6);">💬</span>
        <span style="color: #00f0ff; font-size: 1.2rem; text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);">📊</span>
    </div>
</div>
""", unsafe_allow_html=True)
