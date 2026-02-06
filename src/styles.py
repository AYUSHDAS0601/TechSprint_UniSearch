def get_css():
    return """
    <style>
        /* Import Cyberpunk Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

        /* === CYBERPUNK DARK THEME === */
        
        /* Global Reset & Dark Foundation */
        html, body, [class*="css"] {
            font-family: 'Rajdhani', sans-serif;
            color: #00f0ff;
            background: #0a0e27;
        }
        
        /* Animated Particle Background */
        .stApp {
            background: #0a0e27;
            position: relative;
            overflow-x: hidden;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 90% 80%, rgba(255, 0, 255, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(0, 255, 65, 0.03) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
            animation: pulse-bg 8s ease-in-out infinite;
        }
        
        @keyframes pulse-bg {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        /* Floating Particles */
        .stApp::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20% 30%, #00f0ff, transparent),
                radial-gradient(2px 2px at 60% 70%, #ff00ff, transparent),
                radial-gradient(1px 1px at 50% 50%, #00ff41, transparent),
                radial-gradient(1px 1px at 80% 10%, #00f0ff, transparent),
                radial-gradient(2px 2px at 90% 60%, #ff00ff, transparent),
                radial-gradient(1px 1px at 33% 80%, #00ff41, transparent);
            background-size: 200% 200%;
            background-position: 0% 0%;
            opacity: 0.4;
            animation: particles-float 20s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }
        
        @keyframes particles-float {
            0%, 100% { 
                background-position: 0% 0%;
                opacity: 0.4;
            }
            50% { 
                background-position: 100% 100%;
                opacity: 0.6;
            }
        }
        
        .main .block-container {
            background: transparent;
            padding-top: 2rem;
            padding-bottom: 2rem;
            position: relative;
            z-index: 1;
        }

        /* === NEON TYPOGRAPHY === */
        
        h1, h2, h3 {
            font-family: 'Orbitron', sans-serif;
            font-weight: 900 !important;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #00f0ff;
            text-shadow: 
                0 0 10px rgba(0, 240, 255, 0.8),
                0 0 20px rgba(0, 240, 255, 0.6),
                0 0 30px rgba(0, 240, 255, 0.4),
                0 0 40px rgba(0, 240, 255, 0.2);
            animation: neon-flicker 3s ease-in-out infinite;
        }
        
        @keyframes neon-flicker {
            0%, 100% { opacity: 1; }
            94%, 96% { opacity: 0.9; }
            95% { opacity: 1; }
        }
        
        h2 {
            font-size: 2.5rem !important;
            margin-bottom: 2rem !important;
            color: #ff00ff;
            text-shadow: 
                0 0 10px rgba(255, 0, 255, 0.8),
                0 0 20px rgba(255, 0, 255, 0.6),
                0 0 30px rgba(255, 0, 255, 0.4);
        }
        
        h3 {
            font-size: 1.5rem !important;
            color: #00ff41;
            text-shadow: 
                0 0 10px rgba(0, 255, 65, 0.8),
                0 0 20px rgba(0, 255, 65, 0.6);
        }

        /* === HOLOGRAPHIC CARDS === */
        
        .result-card {
            background: linear-gradient(135deg, rgba(13, 17, 23, 0.95) 0%, rgba(10, 14, 39, 0.95) 100%);
            border: 2px solid transparent;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 
                0 0 20px rgba(0, 240, 255, 0.2),
                inset 0 0 20px rgba(0, 240, 255, 0.05);
            animation: card-enter 0.6s ease-out;
        }
        
        @keyframes card-enter {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Holographic Border Effect */
        .result-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 16px;
            padding: 2px;
            background: linear-gradient(
                45deg,
                #00f0ff,
                #ff00ff,
                #00ff41,
                #00f0ff
            );
            -webkit-mask: 
                linear-gradient(#fff 0 0) content-box, 
                linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0.6;
            animation: border-rotate 4s linear infinite;
        }
        
        @keyframes border-rotate {
            0% { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }
        
        .result-card:hover {
            transform: translateY(-10px) perspective(1000px) rotateX(2deg);
            box-shadow: 
                0 0 40px rgba(0, 240, 255, 0.4),
                0 0 60px rgba(255, 0, 255, 0.2),
                inset 0 0 30px rgba(0, 240, 255, 0.1);
        }
        
        .result-card:hover::before {
            opacity: 1;
        }
        
        /* Scan Line Effect */
        .result-card::after {
            content: '';
            position: absolute;
            top: -100%;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00f0ff, transparent);
            animation: scan-line 3s ease-in-out infinite;
            opacity: 0.5;
        }
        
        @keyframes scan-line {
            0% { top: -100%; }
            100% { top: 200%; }
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1.5rem;
            gap: 1rem;
            position: relative;
            z-index: 1;
        }
        
        .card-title {
            font-size: 1.4rem;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
            color: #00f0ff;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
            flex: 1;
            letter-spacing: 0.02em;
        }

        .card-meta {
            font-size: 0.9rem;
            color: #00ff41;
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
            font-family: 'Share Tech Mono', monospace;
        }

        /* === NEON TAGS === */
        
        .tag {
            background: rgba(0, 240, 255, 0.1);
            color: #00f0ff;
            padding: 0.4rem 1rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-family: 'Orbitron', sans-serif;
            border: 1px solid #00f0ff;
            box-shadow: 
                0 0 10px rgba(0, 240, 255, 0.3),
                inset 0 0 10px rgba(0, 240, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .tag:hover {
            background: rgba(0, 240, 255, 0.2);
            box-shadow: 
                0 0 20px rgba(0, 240, 255, 0.6),
                inset 0 0 15px rgba(0, 240, 255, 0.2);
            transform: scale(1.05);
        }

        /* === NEON BUTTONS === */
        
        .stButton > button {
            background: rgba(0, 240, 255, 0.1);
            color: #00f0ff;
            border: 2px solid #00f0ff;
            border-radius: 8px;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
            padding: 0.75rem 2rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 
                0 0 20px rgba(0, 240, 255, 0.3),
                inset 0 0 20px rgba(0, 240, 255, 0.05);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(0, 240, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .stButton > button:hover {
            background: rgba(0, 240, 255, 0.2);
            box-shadow: 
                0 0 40px rgba(0, 240, 255, 0.6),
                0 0 60px rgba(0, 240, 255, 0.3),
                inset 0 0 30px rgba(0, 240, 255, 0.1);
            transform: translateY(-2px);
        }
        
        .stButton > button:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }

        /* === HEXAGONAL METRICS === */
        
        .metric-container {
            background: linear-gradient(135deg, rgba(13, 17, 23, 0.9) 0%, rgba(10, 14, 39, 0.9) 100%);
            border: 2px solid #00f0ff;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            box-shadow: 
                0 0 30px rgba(0, 240, 255, 0.3),
                inset 0 0 30px rgba(0, 240, 255, 0.05);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(
                from 0deg,
                transparent,
                rgba(0, 240, 255, 0.1),
                transparent 30%
            );
            animation: metric-rotate 4s linear infinite;
            opacity: 0;
            transition: opacity 0.4s;
        }
        
        @keyframes metric-rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .metric-container:hover {
            transform: translateY(-8px) scale(1.05);
            box-shadow: 
                0 0 50px rgba(0, 240, 255, 0.5),
                0 0 80px rgba(255, 0, 255, 0.2),
                inset 0 0 40px rgba(0, 240, 255, 0.1);
            border-color: #ff00ff;
        }
        
        .metric-container:hover::before {
            opacity: 1;
        }
        
        .metric-value {
            font-size: 3rem;
            font-weight: 900;
            font-family: 'Orbitron', sans-serif;
            color: #00f0ff;
            text-shadow: 
                0 0 20px rgba(0, 240, 255, 0.8),
                0 0 40px rgba(0, 240, 255, 0.4);
            position: relative;
            z-index: 1;
            animation: value-pulse 2s ease-in-out infinite;
        }
        
        @keyframes value-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .metric-label {
            color: #00ff41;
            font-size: 0.9rem;
            font-weight: 700;
            font-family: 'Rajdhani', sans-serif;
            margin-top: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            position: relative;
            z-index: 1;
        }

        /* === TERMINAL-STYLE LOGS === */
        
        .log-box {
            background: #000000;
            color: #00ff41;
            font-family: 'Share Tech Mono', monospace;
            padding: 1.5rem;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
            font-size: 0.85rem;
            box-shadow: 
                0 0 30px rgba(0, 255, 65, 0.3),
                inset 0 0 30px rgba(0, 255, 65, 0.05);
            border: 1px solid #00ff41;
            position: relative;
        }
        
        /* CRT Screen Effect */
        .log-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 255, 65, 0.05) 0px,
                transparent 1px,
                transparent 2px,
                rgba(0, 255, 65, 0.05) 3px
            );
            pointer-events: none;
            animation: scan 8s linear infinite;
        }
        
        @keyframes scan {
            0% { transform: translateY(0); }
            100% { transform: translateY(10px); }
        }
        
        .log-box::-webkit-scrollbar {
            width: 10px;
        }
        
        .log-box::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
        }
        
        .log-box::-webkit-scrollbar-thumb {
            background: #00ff41;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        /* === KEYWORD HIGHLIGHTING === */
        
        mark.keyword-highlight {
            background: rgba(255, 0, 255, 0.3);
            color: #ff00ff;
            font-weight: 700;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            border: 1px solid #ff00ff;
            box-shadow: 
                0 0 15px rgba(255, 0, 255, 0.5),
                inset 0 0 10px rgba(255, 0, 255, 0.2);
            animation: highlight-glow 2s ease-in-out infinite;
        }
        
        @keyframes highlight-glow {
            0%, 100% { 
                box-shadow: 
                    0 0 15px rgba(255, 0, 255, 0.5),
                    inset 0 0 10px rgba(255, 0, 255, 0.2);
            }
            50% { 
                box-shadow: 
                    0 0 25px rgba(255, 0, 255, 0.8),
                    inset 0 0 15px rgba(255, 0, 255, 0.3);
            }
        }
        
        .keyword-badge {
            background: rgba(255, 0, 255, 0.2);
            color: #ff00ff;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
            border: 1px solid #ff00ff;
            box-shadow: 0 0 15px rgba(255, 0, 255, 0.4);
            animation: badge-float 3s ease-in-out infinite;
        }
        
        @keyframes badge-float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }

        /* === ENHANCED SIDEBAR === */
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 14, 39, 0.98) 0%, rgba(13, 17, 23, 0.98) 100%);
            border-right: 2px solid #00f0ff;
            box-shadow: 0 0 40px rgba(0, 240, 255, 0.2);
        }

        /* === INPUT FIELDS === */
        
        .stTextInput > div > div > input {
            background: rgba(0, 0, 0, 0.5);
            border: 2px solid #00f0ff;
            border-radius: 8px;
            color: #00f0ff;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 
                0 0 20px rgba(0, 240, 255, 0.2),
                inset 0 0 20px rgba(0, 240, 255, 0.05);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #ff00ff;
            box-shadow: 
                0 0 30px rgba(255, 0, 255, 0.5),
                inset 0 0 30px rgba(255, 0, 255, 0.1);
            outline: none;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(0, 240, 255, 0.5);
        }

        /* === ENHANCED TABS === */
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: rgba(0, 0, 0, 0.5);
            padding: 0.75rem;
            border-radius: 12px;
            border: 1px solid rgba(0, 240, 255, 0.3);
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
            color: #00f0ff;
            transition: all 0.3s ease;
            border: 1px solid transparent;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(0, 240, 255, 0.1);
            border-color: #00f0ff;
        }
        
        .stTabs [aria-selected="true"] {
            background: rgba(0, 240, 255, 0.2);
            color: #00f0ff;
            border: 1px solid #00f0ff;
            box-shadow: 
                0 0 20px rgba(0, 240, 255, 0.4),
                inset 0 0 20px rgba(0, 240, 255, 0.1);
        }

        /* === FILE UPLOADER === */
        
        .stFileUploader {
            border-radius: 12px;
            border: 2px dashed #00f0ff;
            background: rgba(0, 240, 255, 0.05);
            transition: all 0.3s ease;
        }
        
        .stFileUploader:hover {
            border-color: #ff00ff;
            background: rgba(255, 0, 255, 0.05);
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.2);
        }

        /* === PROGRESS BAR === */
        
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #00f0ff 0%, #ff00ff 50%, #00ff41 100%);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.6);
        }

        /* === MULTISELECT === */
        
        .stMultiSelect > div > div {
            background: rgba(0, 0, 0, 0.5);
            border: 2px solid #00f0ff;
            border-radius: 8px;
        }

        /* === HIDE STREAMLIT BRANDING === */
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* === GLITCH EFFECT === */
        
        @keyframes glitch {
            0% {
                transform: translate(0);
            }
            20% {
                transform: translate(-2px, 2px);
            }
            40% {
                transform: translate(-2px, -2px);
            }
            60% {
                transform: translate(2px, 2px);
            }
            80% {
                transform: translate(2px, -2px);
            }
            100% {
                transform: translate(0);
            }
        }

        /* === RESPONSIVE === */
        
        @media (max-width: 768px) {
            .metric-value {
                font-size: 2rem;
            }
            
            .card-title {
                font-size: 1.1rem;
            }
            
            h2 {
                font-size: 1.8rem !important;
            }
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
    # Support both string and list of keywords
    if isinstance(keywords, str):
        keywords = [keywords]
    
    highlighted = text
    total_count = 0
    
    for keyword in keywords:
        # Case-insensitive matching
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        matches = pattern.findall(highlighted)
        total_count += len(matches)
        
        # Replace with highlighted version
        highlighted = pattern.sub(
            lambda m: f'<mark class="{highlight_class}">{m.group()}</mark>',
            highlighted
        )
    
    return highlighted, total_count

def result_card_html(title, summary, tags, score, size, file_type, query=None):
    tags_html = "".join([f'<span class="tag">{t}</span>' for t in tags])
    
    # Highlight keywords if query provided
    occurrence_badge = ""
    if query:
        summary, count = highlight_keywords(summary, query)
        if count > 0:
            occurrence_badge = f'<span class="keyword-badge">⚡ {count} MATCHES</span>'
    
    # Score color based on relevance
    score_color = "#00ff41" if score >= 70 else "#00f0ff" if score >= 50 else "#ff00ff"
    
    # File type icon
    file_icons = {
        'PDF': '📄',
        'DOC': '📝',
        'IMG': '🖼️',
        'TXT': '📋',
        'SUMMARY': '🔮',
        'CHUNK': '⚡',
        'UNKNOWN': '📎'
    }
    file_icon = file_icons.get(file_type.upper(), '📎')
    
    return f"""
<div class="result-card">
    <div class="card-header">
        <div style="flex: 1;">
            <div class="card-title">{file_icon} {title}</div>
            <div class="card-meta" style="margin-top: 0.75rem;">
                <span style="background: rgba(0, 240, 255, 0.1); padding: 0.3rem 0.8rem; border-radius: 4px; font-weight: 700; color: #00f0ff; border: 1px solid #00f0ff;">{size} KB</span>
                <span style="background: rgba(255, 0, 255, 0.1); padding: 0.3rem 0.8rem; border-radius: 4px; font-weight: 700; color: #ff00ff; border: 1px solid #ff00ff;">{file_type}</span>
                {occurrence_badge}
            </div>
        </div>
        <div style="background: rgba({int(score_color[1:3], 16)}, {int(score_color[3:5], 16)}, {int(score_color[5:7], 16)}, 0.1); padding: 1rem 1.5rem; border-radius: 8px; text-align: center; min-width: 90px; border: 2px solid {score_color}; box-shadow: 0 0 20px {score_color}50;">
            <div style="font-size: 1.8rem; font-weight: 900; color: {score_color}; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px {score_color};">{score:.0f}%</div>
            <div style="font-size: 0.65rem; color: #00f0ff; font-weight: 700; margin-top: 0.25rem; letter-spacing: 0.1em;">MATCH</div>
        </div>
    </div>
    <div style="margin: 1.5rem 0; color: #cbd5e1; font-size: 1rem; line-height: 1.8; background: rgba(0, 0, 0, 0.3); padding: 1.25rem; border-radius: 8px; border-left: 3px solid #00f0ff;">
        {summary}
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0, 240, 255, 0.2);">
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">{tags_html}</div>
    </div>
</div>
"""
