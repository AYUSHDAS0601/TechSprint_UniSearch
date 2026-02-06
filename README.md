# Digital Archaeology 🏛️
**Semantic Search Engine for University Notices**

A hackathon-ready prototype built for Arch Linux + KDE Plasma. This tool ingests scanned PDFs/Images of university notices (exam schedules, scholarships, etc.), OCRs them using Tesseract, and provides a semantic search interface using Sentence Transformers and FAISS.

## 🚀 Features
- **Offline Capable**: Runs locally without internet (after setup).
- **Smart Search**: Understands "Java Lab Exam" vs "Java Course Syllabus".
- **Arch Native**: Optimized for `pacman` dependencies (`tesseract`, `poppler`).
- **Fast**: Uses FAISS CPU for sub-second vector search.

## 🛠️ System Requirements
- **OS**: Arch Linux
- **Python**: 3.12+
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: ~1GB (for ML models and dependencies)

## 📦 Installation
Total setup time: < 10 minutes.

1. **Clone/Navigate to folder**:
   ```bash
   cd digital-archaeology
   ```

2. **Run Setup Script**:
   This installs system dependencies (`tesseract`, `poppler`) and Python libs.
   ```bash
   chmod +x setup_arch.sh
   ./setup_arch.sh
   ```
   *Note: Requires `sudo` password for `pacman`.*

## 🏃 Usage

1. **Start the App**:
   ```bash
   ./run.sh
   ```
   The browser should open to `http://localhost:8501`.

2. **Ingest Data**:
   - Go to the sidebar.
   - Click **"Browse files"** to upload PDFs or Images.
   - Click **"Process & Index Files"**.
   - Watch the progress bar as it extracts text and builds vectors.

3. **Search**:
   - Type queries like:
     - *"When is the bus to the hostel?"*
     - *"Scholarship criteria for OBC students"*
     - *"Data Structures exam date"*

## 🧪 Testing
### Sample Queries (Mock Data)
Create a few dummy PDFs or images regarding:
- **Bus Schedule.pdf**: "Bus 5 leaves Campus at 5 PM for Hostel A."
- **Scholarship.img**: "OBC Scholarship 2024: Income < 2 Lakhs required."
- **Exam Notice.pdf**: "Final Exam: CS101 Java Lab on Oct 15th, 2024."

**Query** -> **Expected Result**
- "hostel bus timing" -> **Bus Schedule.pdf**
- "income limit for aid" -> **Scholarship.img**
- "CS101 practicals" -> **Exam Notice.pdf**

## 🔧 Troubleshooting on Arch
**Issue**: `tesseract: command not found`
**Fix**: Ensure base OCR is installed: `sudo pacman -S tesseract tesseract-data-eng`

**Issue**: `streamlit: command not found`
**Fix**: Ensure you are running with `./run.sh` which handles the virtual environment activation.

**Issue**: `Wayland/Display` errors in `app.py`
**Fix**: Streamlit runs in the browser, so it works seamlessly on KDE Plasma (Wayland or X11).

## 📂 Project Structure
```
digital-archaeology/
├── data/               # Local storage
├── src/
│   ├── ocr.py          # Tesseract Wrapper
│   ├── embeddings.py   # Vector Models
│   ├── indexer.py      # FAISS DB
│   └── search.py       # Core Logic
├── app.py              # UI
├── setup_arch.sh       # Installer
└── run.sh              # Launcher
```
