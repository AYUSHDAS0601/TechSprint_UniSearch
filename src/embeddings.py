from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from .utils import setup_logging

logger = setup_logging("Embeddings_Module")

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise e

    def generate(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generates embeddings for a string or list of strings.
        Returns a numpy array.
        """
        if isinstance(texts, str):
            texts = [texts]
            
        try:
            embeddings = self.model.encode(texts)
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise e
