import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

from .ocr import OCREngine
from .embeddings import EmbeddingGenerator
from .indexer import FaissIndexer
from .summarizer import DocumentSummarizer
from .classifier import NoticeClassifier
from .utils import setup_logging

logger = setup_logging("DocumentProcessor")

class DocumentProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.ocr = OCREngine()
        self.embedder = EmbeddingGenerator(config['search'].get('model_name', 'all-MiniLM-L6-v2'))
        self.indexer = FaissIndexer(Path(config['directories']['index']))
        summarization_cfg = config.get('summarization', {})
        self.summarizer = DocumentSummarizer(
            method=summarization_cfg.get('method', 'extract'),
            language=summarization_cfg.get('language', 'english'),
            sentences_count=summarization_cfg.get('sentences', 3),
            model_url=summarization_cfg.get('model_url'),
            model_name=summarization_cfg.get('model_name', 'mistral'),
            timeout=summarization_cfg.get('timeout', 90),
        )
        self.classifier = NoticeClassifier()
        
        self.metadata_dir = Path(config['directories']['metadata'])
        self.processed_dir = Path(config['directories']['processed'])
        
        # Ensure directories exist
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_file(self, file_path: Path) -> Optional[Dict]:
        """
        Orchestrates the full processing pipeline for a single file.
        Returns the enhanced metadata dict if successful, None otherwise.
        """
        logger.info(f"Processing file: {file_path.name}")
        
        try:
            # 1. OCR Extraction
            data = self.ocr.process_file(file_path)
            if not data or not data.get('content'):
                logger.warning(f"No content extracted from {file_path.name}")
                return None

            text_content = data['content']
            
            # 2. Analysis (Summarization & Classification)
            summary = self.summarizer.summarize(text_content)
            categories = self.classifier.classify(text_content)
            
            # 3. Enhance Metadata
            data['summary'] = summary
            data['categories'] = categories
            data['ingest_date'] = datetime.now().isoformat()
            data['file_size'] = file_path.stat().st_size
            data['processed'] = True
            
            # 4. Save Metadata to Disk
            self._save_metadata(data, file_path.name)
            
            # 5. Indexing Strategy (Hybrid)
            self._index_document(data, text_content, summary, categories, file_path.name)
            
            return data

        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            return None

    def _save_metadata(self, data: Dict, filename: str):
        meta_pth = self.metadata_dir / f"{filename}.json"
        with open(meta_pth, 'w') as f:
            json.dump(data, f, indent=2)

    def _index_document(self, metadata: Dict, content: str, summary: str, categories: List[str], filename: str):
        """
        Implements Hybrid Indexing:
        1. Summary Vector: Metadata + Summary + Categories
        2. Content Chunks: Actual text content split into chunks
        """
        
        # --- A. Index Summary (High-level gist) ---
        # Rich representation for broad queries
        summary_text = f"{summary} {' '.join(categories)} {metadata.get('filename', '')}"
        summary_embedding = self.embedder.generate(summary_text)
        
        summary_meta = metadata.copy()
        summary_meta['type'] = 'summary'
        summary_meta['id'] = f"{filename}_summary"
        summary_meta['content_snippet'] = summary # Show summary as snippet
        if 'content' in summary_meta: 
            del summary_meta['content']
            
        self.indexer.add_single_document(summary_embedding, summary_meta)
        
        # --- B. Index Content Chunks (Specific details) ---
        chunks = self._chunk_text(content)
        if chunks:
            chunk_embeddings = self.embedder.generate(chunks)
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                c_meta = metadata.copy()
                c_meta['type'] = 'chunk'
                c_meta['id'] = f"{filename}_chunk_{i}"
                c_meta['content_snippet'] = chunk
                if 'content' in c_meta:
                    del c_meta['content']
                chunk_metadatas.append(c_meta)
                
            self.indexer.add_documents(chunk_embeddings, chunk_metadatas)

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        Simple paragraph-based chunking.
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = ""
        
        for p in paragraphs:
            if len(current_chunk) + len(p) < chunk_size:
                current_chunk += " " + p
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = p
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # Fallback if no paragraphs
        if not chunks and text:
            chunks = [text]
            
        return chunks
