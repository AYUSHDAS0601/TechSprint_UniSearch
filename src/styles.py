def get_css():
    return """
    <style>
        /* Import Premium Modern Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Fira+Code&display=swap');

        /* === PREMIUM GLASSMORPHISM DARK THEME === */
        
        :root {
            --bg-color: #0b0f19;
            --surface-color: rgba(30, 41, 59, 0.7);
            --surface-hover: rgba(30, 41, 59, 0.9);
            --border-color: rgba(148, 163, 184, 0.15);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-primary: #6366f1; /* Indigo */
            --accent-secondary: #0ea5e9; /* Teal */
            --accent-tertiary: #a855f7; /* Purple */
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }

        /* Global Reset & Typography */
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
        }

        /* Main Application Background with Ambient Glows */
        .stApp {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 85% 20%, rgba(168, 85, 247, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(14, 165, 233, 0.1) 0%, transparent 40%);
            background-attachment: fixed;
        }

        /* Clean up Block Container */
        .main .block-container {
            padding-top: 2.5rem;
            max-width: 1200px;
        }

        /* === HEADINGS === */
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        
        h1 {
            background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem !important;
        }
        
        h2 {
            color: var(--text-primary) !important;
            font-size: 1.8rem !important;
        }
        
        h3 {
            color: var(--text-secondary) !important;
            font-size: 1.25rem !important;
            font-weight: 600 !important;
        }

        /* === GLASS CARDS (RESULT CARDS) === */
        
        .result-card {
            background: var(--surface-color);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.75rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .result-card:hover {
            transform: translateY(-4px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 10px 40px -10px rgba(99, 102, 241, 0.2);
            background: var(--surface-hover);
        }

        /* Elegant Left Border Accent on Hover */
        .result-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, var(--accent-primary), var(--accent-secondary));
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .result-card:hover::before {
            opacity: 1;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1.25rem;
            gap: 1rem;
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            font-family: 'Outfit', sans-serif;
            color: var(--text-primary);
            flex: 1;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .card-meta {
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
            margin-top: 0.5rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }

        /* Match Score Ring */
        .score-circle {
            background: rgba(15, 23, 42, 0.6);
            border: 2px solid;
            border-radius: 12px;
            padding: 0.75rem;
            min-width: 80px;
            text-align: center;
            backdrop-filter: blur(4px);
        }

        /* Content Snippet Area */
        .card-content {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
            background: rgba(15, 23, 42, 0.4);
            padding: 1.25rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin: 1.25rem 0;
        }

        /* === MODERN PILL TAGS === */
        
        .tag-pill {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            padding: 0.35rem 0.85rem;
            border-radius: 99px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
        }
        
        .tag-pill:hover {
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* Keyword Highlights */
        mark.keyword-highlight {
            background: rgba(99, 102, 241, 0.2);
            color: #818cf8;
            padding: 0.15rem 0.3rem;
            border-radius: 4px;
            font-weight: 600;
            box-shadow: 0 0 8px rgba(99, 102, 241, 0.1);
        }
        
        .keyword-badge {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.15));
            color: #a5b4fc;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        /* === METRIC CARDS (DASHBOARD) === */
        
        .glass-metric {
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: left;
            transition: transform 0.3s ease;
        }
        
        .glass-metric:hover {
            transform: translateY(-2px);
            border-color: rgba(14, 165, 233, 0.3);
        }
        
        .glass-metric-icon {
            font-size: 1.75rem;
            margin-bottom: 1rem;
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            padding: 0.75rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .glass-metric-value {
            font-size: 2.25rem;
            font-weight: 700;
            font-family: 'Outfit', sans-serif;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .glass-metric-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* === TERMINAL LOGS === */
        
        .log-box {
            background: #0f172a;
            color: #a5b4fc;
            font-family: 'Fira Code', monospace;
            padding: 1.5rem;
            border-radius: 12px;
            max-height: 350px;
            overflow-y: auto;
            font-size: 0.85rem;
            border: 1px solid rgba(99, 102, 241, 0.2);
            box-shadow: inset 0 2px 15px rgba(0,0,0,0.4);
            line-height: 1.6;
        }
        
        .log-box::-webkit-scrollbar { width: 8px; }
        .log-box::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.2); border-radius: 4px; }
        .log-box::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.4); border-radius: 4px; }

        /* === CHAT INTERFACE OVERRIDES === */
        [data-testid="stChatMessage"] {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(8px);
        }
        
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: rgba(99, 102, 241, 0.1);
            border-color: rgba(99, 102, 241, 0.2);
        }

        /* === STREAMLIT COMPONENT OVERRIDES === */
        
        /* Sidebar layout */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border-right: 1px solid var(--border-color);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-primary) 0%, #4f46e5 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            padding: 0.5rem 1.5rem;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.23);
        }

        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Inputs */
        div[data-baseweb="input"] {
            background-color: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        
        div[data-baseweb="input"]:focus-within {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 1px var(--accent-primary);
        }
        
        div[data-baseweb="input"] input {
            color: var(--text-primary);
        }
        
        /* File Uploader */
        [data-testid="stFileUploader"] {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 12px;
            border: 1px dashed rgba(148, 163, 184, 0.3);
            padding: 1rem;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: var(--accent-secondary);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: rgba(15, 23, 42, 0.6);
            padding: 0.5rem 0.5rem 0 0.5rem;
            border-radius: 12px 12px 0 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-family: 'Outfit', sans-serif;
            color: var(--text-secondary);
            border: none;
            background: transparent;
        }
        
        .stTabs [aria-selected="true"] {
            color: var(--text-primary) !important;
            background: rgba(255, 255, 255, 0.05);
            border-bottom: 2px solid var(--accent-primary) !important;
        }

        hr {
            border-color: var(--border-color);
            margin: 2rem 0;
        }

    </style>
    """

def highlight_keywords(text, keywords, highlight_class="keyword-highlight"):
    """
    Highlight keywords in text with HTML spans.
    Returns tuple: (highlighted_html, occurrence_count)
    """
    if not keywords or not text:
        return text, 0
    
    import re
    if isinstance(keywords, str):
        keywords = [keywords]
    
    highlighted = text
    total_count = 0
    
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        matches = pattern.findall(highlighted)
        total_count += len(matches)
        
        highlighted = pattern.sub(
            lambda m: f'<mark class="{highlight_class}">{m.group()}</mark>',
            highlighted
        )
    
    return highlighted, total_count

def result_card_html(title, summary, tags, score, size, file_type, query=None):
    tags_html = "".join([f'<span class="tag-pill">{t}</span>' for t in tags])
    
    occurrence_badge = ""
    if query:
        summary, count = highlight_keywords(summary, query)
        if count > 0:
            occurrence_badge = f'<span class="keyword-badge">🔥 {count} Matches</span>'
    
    # Elegant color gradients based on score
    if score >= 75:
        score_gradient = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        border_color = "rgba(16, 185, 129, 0.3)"
    elif score >= 50:
        score_gradient = "linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)"
        border_color = "rgba(14, 165, 233, 0.3)"
    else:
        score_gradient = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        border_color = "rgba(245, 158, 11, 0.3)"
        
    file_icons = {
        'PDF': '📄', 'DOC': '📝', 'IMG': '🖼️', 'TXT': '📋',
        'SUMMARY': '💡', 'CHUNK': '🧩', 'UNKNOWN': '📎'
    }
    file_icon = file_icons.get(file_type.upper(), '📎')
    
    return f"""
<div class="result-card">
    <div class="card-header">
        <div style="flex: 1;">
            <div class="card-title">{file_icon} {title}</div>
            <div class="card-meta">
                <span style="background: rgba(255,255,255,0.05); padding: 0.25rem 0.6rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">{size} KB</span>
                <span style="background: rgba(255,255,255,0.05); padding: 0.25rem 0.6rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">{file_type}</span>
                {occurrence_badge}
            </div>
        </div>
        <div class="score-circle" style="border-color: {border_color};">
            <div style="font-size: 1.5rem; font-weight: 800; font-family: 'Outfit', sans-serif; background: {score_gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {score:.0f}%
            </div>
            <div style="font-size: 0.65rem; color: #94a3b8; font-weight: 600; margin-top: 2px;">RELEVANCE</div>
        </div>
    </div>
    <div class="card-content">
        {summary}
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; padding-top: 0.5rem;">
        {tags_html}
    </div>
</div>
"""
