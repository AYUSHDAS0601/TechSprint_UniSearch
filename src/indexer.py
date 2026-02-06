import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .utils import setup_logging

logger = setup_logging("Indexer_Module")

class FaissIndexer:
    def __init__(self, index_path: Path, dimension: int = 384):
        self.index_path = index_path
        self.index_file = index_path / "faiss_index.bin"
        self.metadata_file = index_path / "metadata.pkl"
        self.dimension = dimension
        self.index = None
        self.metadata = [] # List of dicts, index matches FAISS id

        self._load_or_create_index()

    def _load_or_create_index(self):
        if self.index_file.exists() and self.metadata_file.exists():
            try:
                logger.info("Loading existing index and metadata...")
                self.index = faiss.read_index(str(self.index_file))
                with open(self.metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded index with {self.index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Failed to load index, creating new one: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        logger.info(f"Creating new FAISS index (dim={self.dimension})...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []

    def add_documents(self, embeddings: np.ndarray, docs_metadata: List[Dict]):
        """
        Adds vectors and corresponding metadata to the index.
        """
        if len(docs_metadata) != embeddings.shape[0]:
            logger.error("Mismatch between embeddings count and metadata count.")
            return

        try:
            self.index.add(embeddings)
            self.metadata.extend(docs_metadata)
            self._save_index()
            logger.info(f"Added {len(docs_metadata)} documents to index. Total: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Error adding documents to index: {e}")

    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[List[Dict], List[float]]:
        """
        Searches the index for the k nearest neighbors.
        Returns a tuple of (metadata_list, distances).
        """
        if self.index.ntotal == 0:
            return [], []

        distances, indices = self.index.search(query_vector, k)
        
        results = []
        result_distances = []
        
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
                result_distances.append(distances[0][i])
                
        return results, result_distances

    def _save_index(self):
        try:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, "wb") as f:
                pickle.dump(self.metadata, f)
            logger.info("Index and metadata saved to disk.")
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    def add_single_document(self, embedding: np.ndarray, doc_metadata: Dict):
        """
        Adds a single document vector to the index.
        """
        # Ensure 2D array (1, dim)
        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)
            
        self.add_documents(embedding, [doc_metadata])
