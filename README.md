# Digital Archaeology - MERN Stack

🏛️ **AI-Powered Semantic Search Engine with Dark Cyberpunk Theme**

## Overview

Digital Archaeology is a full-stack MERN application that provides semantic search capabilities for documents using AI-powered embeddings and natural language processing. Features include:

- 🔍 **Semantic Search** - Find documents using natural language queries
- 💬 **AI Q&A** - Ask questions and get answers powered by Mistral AI
- 📊 **Dashboard** - Monitor system statistics and activity logs
- 🕸️ **Web Crawler** - Automatically download notices from university websites
- 🎨 **Dark Cyberpunk Theme** - Stunning neon-accented UI with glassmorphism effects

## Tech Stack

- **Frontend**: React 18 + Vite
- **Backend**: Express.js (Node.js)
- **AI/ML**: Python (sentence-transformers, FAISS, Mistral via Ollama)
- **Database**: MongoDB (optional for development)
- **Styling**: Custom CSS with cyberpunk theme

## Prerequisites

- Node.js v18+ and npm
- Python 3.10+
- Tesseract OCR
- Ollama with Mistral model (for Q&A features)
- MongoDB (optional)

## Installation

### 1. Install System Dependencies

```bash
# Arch Linux
sudo pacman -S nodejs npm python tesseract

# Install Ollama and Mistral
curl https://ollama.ai/install.sh | sh
ollama pull mistral
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

The startup script will handle this automatically, or run manually:

```bash
# Backend
cd backend
npm install

# Frontend
cd ../frontend
npm install
```

## Running the Application

### Quick Start

```bash
./start.sh
```

This will:
1. Check for dependencies
2. Install npm packages if needed
3. Start backend server on port 5000
4. Start frontend dev server on port 3000
5. Open your browser to http://localhost:3000

### Manual Start

**Backend:**
```bash
cd backend
npm start
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Project Structure

```
digital-archaeology/
├── backend/                 # Express.js backend
│   ├── routes/             # API route handlers
│   ├── python_bridge.js    # Python integration layer
│   ├── server.js           # Main server file
│   └── package.json
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   ├── styles/        # CSS files
│   │   └── App.jsx        # Main app component
│   └── package.json
├── src/                    # Python modules
│   ├── search.py          # Search engine
│   ├── qa_engine.py       # Q&A with Mistral
│   ├── processor.py       # Document processing
│   └── scraper.py         # Web crawler
├── api_wrapper.py         # Python CLI wrapper for Node.js
├── config/                # Configuration files
├── data/                  # Data directories
└── start.sh              # Unified startup script
```

## API Endpoints

- `POST /api/search` - Semantic search
- `POST /api/qa` - Ask questions
- `POST /api/upload` - Upload files
- `POST /api/scraper/start` - Start web crawler
- `GET /api/stats` - System statistics
- `GET /api/stats/logs` - Application logs
- `GET /api/health` - Health check

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

**npm not found:**
```bash
sudo pacman -S npm
```

**Mistral not responding:**
```bash
ollama serve
ollama pull mistral
```

**Python modules not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## License

MIT

## Version

v3.0.0 - MERN Stack with Dark Cyberpunk Theme
