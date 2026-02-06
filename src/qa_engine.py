import logging
import requests
import json
from pathlib import Path
from typing import List, Dict, Tuple
from .utils import setup_logging

logger = setup_logging("QA_Engine")

class MistralQAEngine:
    """
    Question-Answering engine using Mistral LLM via Ollama.
    Uses RAG (Retrieval-Augmented Generation) approach.
    """
    
    def __init__(self, model_url="http://localhost:11434/api/generate", model_name="mistral"):
        self.model_url = model_url
        self.model_name = model_name
        logger.info(f"Initialized Mistral Q&A Engine with model: {model_name}")
    
    def answer_question(self, question: str, context_docs: List[Dict]) -> Dict[str, str]:
        """
        Answer a question based on retrieved documents.
        
        Args:
            question: User's question
            context_docs: List of relevant documents from search
                         Each doc should have 'text', 'filename', 'summary' keys
        
        Returns:
            Dict with 'answer', 'sources', and 'confidence' keys
        """
        if not context_docs:
            return {
                "answer": "I couldn't find any relevant documents to answer your question.",
                "sources": [],
                "confidence": "low"
            }
        
        # Build context from top documents
        context_text = self._build_context(context_docs)
        
        # Create prompt
        prompt = self._create_qa_prompt(question, context_text)
        
        # Query Mistral
        try:
            response = self._query_mistral(prompt)
            
            # Extract sources
            sources = [doc.get('filename', 'Unknown') for doc in context_docs[:3]]
            
            return {
                "answer": response,
                "sources": sources,
                "confidence": "high" if len(context_docs) >= 2 else "medium"
            }
        except Exception as e:
            logger.error(f"Q&A generation failed: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}. Please ensure Ollama is running with Mistral model.",
                "sources": [],
                "confidence": "error"
            }
    
    def _build_context(self, docs: List[Dict], max_chars=3000) -> str:
        """Build context string from documents."""
        context_parts = []
        total_chars = 0
        
        for i, doc in enumerate(docs, 1):
            filename = doc.get('filename', 'Unknown')
            text = doc.get('text', '')
            summary = doc.get('summary', '')
            
            # Prefer summary if available, otherwise use truncated text
            content = summary if summary else text[:500]
            
            doc_context = f"[Document {i}: {filename}]\n{content}\n"
            
            if total_chars + len(doc_context) > max_chars:
                break
            
            context_parts.append(doc_context)
            total_chars += len(doc_context)
        
        return "\n".join(context_parts)
    
    def _create_qa_prompt(self, question: str, context: str) -> str:
        """Create a prompt for Q&A."""
        prompt = f"""You are a helpful assistant answering questions about university notices and documents.

Context (relevant documents):
{context}

Question: {question}

Instructions:
- Answer the question based ONLY on the information in the context above
- Be concise and specific
- If the context doesn't contain enough information, say so
- Cite specific details from the documents when possible

Answer:"""
        return prompt
    
    def _query_mistral(self, prompt: str, timeout=60) -> str:
        """Query Mistral via Ollama API."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more factual answers
                "num_predict": 300   # Max tokens in response
            }
        }
        
        response = requests.post(self.model_url, json=payload, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "").strip()


class MistralSummarizer:
    """Standalone Mistral summarizer for document processing."""
    
    def __init__(self, model_url="http://localhost:11434/api/generate", model_name="mistral"):
        self.model_url = model_url
        self.model_name = model_name

    def summarize(self, text: str) -> str:
        if not text or len(text.split()) < 20:
            return text

        prompt = f"""Summarize the following university notice in exactly 2-3 concise sentences. Focus on the key information like dates, deadlines, and actions required:

{text[:2000]}

Summary:"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_predict": 150
            }
        }

        try:
            response = requests.post(self.model_url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            logger.error(f"Mistral summarization failed (is Ollama running?): {e}")
            return text[:200] + "... (LLM Error)"
