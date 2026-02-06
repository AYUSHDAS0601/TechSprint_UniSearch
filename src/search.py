from pathlib import Path
from typing import List, Dict
import numpy as np
from .embeddings import EmbeddingGenerator
from .indexer import FaissIndexer
from .ocr import OCREngine
from .utils import setup_logging, get_file_list

logger = setup_logging("Search_Engine")

class SearchEngine:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw"
        self.index_dir = data_dir / "index"
        
        # Initialize components
        self.ocr = OCREngine()
        self.embedder = EmbeddingGenerator()
        self.indexer = FaissIndexer(self.index_dir)

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
        
        # Initialize processor if not already done (SearchEngine creates its own components usually, 
        # but better to share or re-init here. Since SearchEngine is long-lived, we init once)
        if not hasattr(self, 'processor'):
             # Re-construct config dict from data_dir path for now, 
             # or ideally pass config to SearchEngine. 
             # For now we'll assume standard structure relative to data_dir
             config = {
                 'directories': {
                     'index': str(self.data_dir / "index"),
                     'metadata': str(self.data_dir / "metadata"),
                     'processed': str(self.data_dir / "processed"),
                     'watch': str(self.data_dir / "watch")
                 },
                 'search': {'model_name': 'all-MiniLM-L6-v2'} # Default
             }
             from .processor import DocumentProcessor
             self.processor = DocumentProcessor(config)
             # Share the same indexer instance to avoid locking/sync issues if they were different,
             # but here Processor creates its own. 
             # Actually, Processor creates its own indexer. 
             # We should probably let Processor manage the index.
             # Or inject self.indexer into Processor?
             # For simplicity in this refactor, let's just let Processor do its thing
             # and reload the index here if needed, or just rely on Processor.
             # Wait, SearchEngine.indexer is used for search. 
             # If Processor updates the index on disk, SearchEngine.indexer (in memory) needs to reload.
             
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
