# Digital Archaeology (Streamlit)

🏛️ **AI-Powered Semantic Search Engine for University Notices**

## Overview

Digital Archaeology is a **Streamlit** application that provides semantic search capabilities for notices (PDFs/images) using embeddings + FAISS, plus optional local LLM Q&A via **Ollama (Mistral)**.

- 🔍 **Semantic Search** - Find documents using natural language queries
- 💬 **AI Q&A** - Ask questions and get answers powered by Mistral AI
- 📊 **Dashboard** - Monitor system statistics and activity logs
- 🕸️ **Web Crawler** - Automatically download notices from university websites
- 🎨 **Dark Cyberpunk Theme** - Stunning neon-accented UI with glassmorphism effects

## Tech Stack

- **UI**: Streamlit
- **AI/ML**: Python (sentence-transformers, FAISS, Mistral via Ollama)
- **OCR**: Tesseract + PyMuPDF

## Prerequisites

- Python 3.10+
- Tesseract OCR
- Ollama with Mistral model (for Q&A features)

## Installation

### 1. Install System Dependencies (Arch)

```bash
# Arch Linux
sudo pacman -S python tesseract tesseract-data-eng poppler

# Install Ollama and Mistral
curl https://ollama.ai/install.sh | sh
ollama pull mistral
```

### 2. Set Up Python Environment

```bash
./setup_arch.sh
```

## Running the Application

### Quick Start

```bash
./run.sh
```

Open: `http://localhost:8501`

## Project Structure

```
digital-archaeology/
├── src/                    # Python modules
│   ├── search.py          # Search engine
│   ├── qa_engine.py       # Q&A with Mistral
│   ├── processor.py       # Document processing
│   └── scraper.py         # Web crawler
├── config/                # Configuration files
├── data/                  # Data directories
└── run.sh                 # Streamlit launcher
```

## Features

### Semantic Search
Search documents using natural language queries. The system uses sentence transformers to create embeddings and FAISS for fast similarity search.

### AI Q&A
Ask questions about your documents and get intelligent answers powered by Mistral AI running locally via Ollama.

### Web Crawler
Automatically discover and download PDF notices from configured university websites.

### Dark Cyberpunk Theme
Stunning UI with:
- Neon colors (cyan, magenta, green)
- Glowing effects and animations
- Glassmorphism cards
- Terminal-inspired fonts
- Responsive design

## Configuration

Edit `.env` files in root, `backend/`, and `frontend/` directories to customize:
- API ports
- MongoDB connection
- Python virtual environment path
- CORS settings
- Upload limits

## Development

### Backend Development
```bash
cd backend
npm run dev  # Uses nodemon for auto-reload
```

### Frontend Development
```bash
cd frontend
npm run dev  # Vite dev server with HMR
```

### Build for Production
```bash
cd frontend
npm run build
```

## Troubleshooting

**Mistral not responding:**
```bash
ollama pull mistral
ollama serve
```

**Python modules not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## License

MIT

## Version

v3.x - Streamlit app + local Ollama (Mistral)
