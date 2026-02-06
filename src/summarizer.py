import logging
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
import requests
import json
from .utils import setup_logging

logger = setup_logging("Summarizer")

class DocumentSummarizer:
    """
    AI-powered document summarizer using transformer models.
    Supports multiple backends: BART, T5, Mistral, or fallback to extractive (sumy).
    """
    
    def __init__(self, method="bart", language="english", sentences_count=3):
        """
        Initialize the summarizer.
        
        Args:
            method: "bart", "t5-small", "t5-base", "mistral", or "extract" (sumy fallback)
            language: Language for extractive summarization
            sentences_count: Number of sentences for extractive method
        """
        self.method = method
        self.language = language
        self.sentences_count = sentences_count
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.mistral_summarizer = None # Initialize Mistral summarizer instance
        
        logger.info(f"Initializing {method} summarizer...")
        
        if method == "bart":
            self._init_bart()
        elif method.startswith("t5"):
            self._init_t5(method)
        elif method == "mistral":
            self._init_mistral()
        elif method == "extract":
            self._init_extractive()
        else:
            logger.warning(f"Unknown method '{method}', falling back to extractive")
            self._init_extractive()
    
    def _init_bart(self):
        """Initialize Facebook BART model (best for summarization)."""
        try:
            model_name = "facebook/bart-large-cnn"
            logger.info(f"Loading {model_name}...")
            
            # Use GPU if available
            device = 0 if torch.cuda.is_available() else -1
            
            self.pipeline = pipeline(
                "summarization",
                model=model_name,
                device=device,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            logger.info("✓ BART model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BART: {e}")
            logger.info("Falling back to extractive summarization")
            self._init_extractive()
    
    def _init_t5(self, model_size="t5-small"):
        """Initialize T5 model (lighter alternative)."""
        try:
            model_name = f"google/{model_size}"
            logger.info(f"Loading {model_name}...")
            
            device = 0 if torch.cuda.is_available() else -1
            
            self.pipeline = pipeline(
                "summarization",
                model=model_name,
                device=device,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            logger.info(f"✓ {model_size} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load T5: {e}")
            logger.info("Falling back to extractive summarization")
            self._init_extractive()

    def _init_mistral(self):
        """Initialize Mistral summarizer (requires Ollama server)."""
        try:
            self.mistral_summarizer = MistralSummarizer()
            logger.info("✓ Mistral summarizer initialized (Ollama backend)")
        except Exception as e:
            logger.error(f"Failed to initialize Mistral summarizer: {e}")
            logger.info("Falling back to extractive summarization")
            self._init_extractive()
    
    def _init_extractive(self):
        """Initialize extractive summarization (LSA-based, no AI)."""
        try:
            from sumy.parsers.plaintext import PlaintextParser
            from sumy.nlp.tokenizers import Tokenizer
            from sumy.summarizers.lsa import LsaSummarizer
            from sumy.nlp.stemmers import Stemmer
            from sumy.utils import get_stop_words
            
            # Ensure NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                logger.info("Downloading NLTK 'punkt' tokenizer...")
                nltk.download('punkt', quiet=True)
                nltk.download('punkt_tab', quiet=True)
            
            self.stemmer = Stemmer(self.language)
            self.sumy_summarizer = LsaSummarizer(self.stemmer)
            self.sumy_summarizer.stop_words = get_stop_words(self.language)
            self.method = "extract"
            logger.info("✓ Extractive summarizer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize extractive summarizer: {e}")
            self.method = "none"
    
    def summarize(self, text: str) -> str:
        """
        Generate a summary of the provided text.
        
        Args:
            text: Input text to summarize
            
        Returns:
            Summary string
        """
        if not text:
            return ""
        
        # Handle very short texts
        if len(text.split()) < 50:
            return text[:300] + "..." if len(text) > 300 else text
        
        try:
            if self.method in ["bart", "t5-small", "t5-base"] and self.pipeline:
                return self._summarize_transformers(text)
            elif self.method == "mistral" and self.mistral_summarizer:
                return self.mistral_summarizer.summarize(text)
            elif self.method == "extract":
                return self._summarize_extractive(text)
            else:
                # Fallback: return beginning
                return text[:200] + "..." # Fallback
                
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return text[:200] + "..." # Fallback
    
    def _summarize_transformers(self, text: str) -> str:
        """Use transformer model for abstractive summarization."""
        try:
            # Chunk long texts (transformers have token limits)
            max_length = 1024
            words = text.split()
            
            if len(words) > max_length:
                # Take first chunk for summarization
                text = " ".join(words[:max_length])
            
            # Generate summary
            result = self.pipeline(
                text,
                max_length=150,  # Summary length
                min_length=30,
                do_sample=False,
                truncation=True
            )
            
            summary = result[0]['summary_text']
            logger.debug(f"Generated summary: {len(summary)} chars from {len(text)} chars")
            return summary
            
        except Exception as e:
            logger.error(f"Transformer summarization failed: {e}")
            return self._summarize_extractive(text)
    
    def _summarize_extractive(self, text: str) -> str:
        """Use extractive summarization (LSA)."""
        try:
            from sumy.parsers.plaintext import PlaintextParser
            from sumy.nlp.tokenizers import Tokenizer
            
            parser = PlaintextParser.from_string(text, Tokenizer(self.language))
            summary_sentences = self.sumy_summarizer(parser.document, self.sentences_count)
            summary = " ".join([str(s) for s in summary_sentences])
            return summary if summary else text[:300] + "..."
            
        except Exception as e:
            logger.error(f"Extractive summarization failed: {e}")
            return text[:300] + "..."
