from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from .embeddings import EmbeddingGenerator
from .indexer import FaissIndexer
from .ocr import OCREngine
from .utils import setup_logging, get_file_list

logger = setup_logging("Search_Engine")

class SearchEngine:
    def __init__(
        self,
        data_dir: Path,
        config: Optional[Dict] = None,
    ):
        """
        Args:
            data_dir: Base data directory (contains raw/, index/, metadata/, etc.)
            config: Full app config dict (recommended). If omitted, a minimal config
                    will be derived from data_dir.
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.index_dir = self.data_dir / "index"

        self.config = config or self._default_config_from_data_dir(self.data_dir)
        
        # Initialize components
        self.ocr = OCREngine()
        model_name = (self.config.get("search", {}) or {}).get("model_name", "all-MiniLM-L6-v2")
        self.embedder = EmbeddingGenerator(model_name)
        self.indexer = FaissIndexer(self.index_dir)
        self.processor = None

    @staticmethod
    def _default_config_from_data_dir(data_dir: Path) -> Dict:
        data_dir = Path(data_dir)
        return {
            "directories": {
                "raw": str(data_dir / "raw"),
                "processed": str(data_dir / "processed"),
                "index": str(data_dir / "index"),
                "watch": str(data_dir / "watch"),
                "metadata": str(data_dir / "metadata"),
                "logs": str(data_dir.parent / "logs"),
            },
            "search": {"model_name": "all-MiniLM-L6-v2", "top_k": 5},
            "summarization": {
                "method": "extract",
                "sentences": 3,
                "language": "english",
                "model_url": "http://127.0.0.1:11434/api/generate",
                "model_name": "mistral",
                "timeout": 120,
            },
        }

    def ingest_new_files(self) -> List[str]:
        """
        Scans raw directory for files not yet indexed and processes them using DocumentProcessor.
        """
        logger.info("Starting ingestion process...")
        files = get_file_list(self.raw_dir)
        processed_files = {m['filename'] for m in self.indexer.metadata}
        
        new_files = [f for f in files if f.name not in processed_files]
        
        if not new_files:
            logger.info("No new files to ingest.")
            return []

        indexed_count = 0

        # Initialize processor once using the real config
        if self.processor is None:
            from .processor import DocumentProcessor
            self.processor = DocumentProcessor(self.config)
             
        for file_path in new_files:
            result = self.processor.process_file(file_path)
            if result:
                indexed_count += 1
        
        # Reload index after batch ingestion to see new vectors
        self.indexer._load_or_create_index()

        logger.info(f"Ingestion complete. Added {indexed_count} files.")
        return [f.name for f in new_files]

    def search(self, query: str, k: int = 5, filters: Dict = None) -> List[Dict]:
        """
        Performs semantic search with optional metadata filtering.
        """
        logger.info(f"Searching for: {query} with filters: {filters}")
        query_vector = self.embedder.generate(query)
        
        # Determine dimension (1, D)
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
            
        # Retrieve more candidates if filtering to ensure we have enough k results
        search_k = k * 3 if filters else k
        results, distances = self.indexer.search(query_vector, search_k)
        
        formatted_results = []
        for r, d in zip(results, distances):
            # Apply Filters
            if filters:
                match = True
                for key, value in filters.items():
                    # Simple list inclusion check for categories
                    if key == 'categories':
                        doc_cats = r.get('categories', [])
                        if isinstance(value, list):
                             # Match if ANY of the filter categories are present
                             if not any(c in doc_cats for c in value):
                                 match = False
                        elif value not in doc_cats:
                            match = False
                    # Add more filter logic here as needed
                if not match:
                    continue
            
            r['score'] = float(d) 
            formatted_results.append(r)
            
            if len(formatted_results) >= k:
                break
            
        return formatted_results

    def clear_database(self):
        self.indexer.clear()
        logger.info("Database cleared.")
