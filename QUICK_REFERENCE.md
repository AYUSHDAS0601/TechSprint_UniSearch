# Digital Archaeology - Quick Reference

## 🚀 Running the Application

### Streamlit App (Main Interface)
```bash
cd /home/pookie/Documents/TechSprint/digital-archaeology
source venv/bin/activate
streamlit run app.py
```
Access at: http://localhost:8501

## 🧪 Testing

### Run All Tests
```bash
source venv/bin/activate
python test_all_features.py
```

### Check Ollama Status
```bash
ollama list
curl http://127.0.0.1:11434/api/tags
```

## 📁 Key Files

- **Config**: `config/config.yaml`
- **Environment**: `.env`
- **Main App**: `app.py`
- **Q&A Engine**: `src/qa_engine.py`
- **Summarizer**: `src/summarizer.py`
- **Search**: `src/search.py`
- **Processor**: `src/processor.py`

## ⚙️ Configuration

### Mistral Settings (config.yaml)
```yaml
summarization:
  method: "mistral"
  model_url: "http://127.0.0.1:11434/api/generate"
  model_name: "mistral"
  timeout: 120
```

## ✅ What's Working

- ✅ Mistral integration (Q&A + Summarization)
- ✅ Semantic search (124 vectors indexed)
- ✅ Document processing (OCR, classification)
- ✅ File upload and indexing
- ✅ Dashboard and statistics
- ✅ Category filtering

## 🔧 Recent Fixes

1. Added `MistralSummarizer` import to `src/summarizer.py`
2. Fixed Q&A context mapping in `app.py`
3. Increased timeouts: Q&A (120s), Summarization (90s)
4. Added timeout config to `config.yaml`

## 📊 System Status

- **Ollama**: Running ✓
- **Mistral Model**: Available (4.4 GB) ✓
- **Index Size**: 124 vectors
- **Documents**: 41 PDFs
- **Dependencies**: All installed ✓
