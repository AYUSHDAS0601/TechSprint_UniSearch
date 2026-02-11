#!/usr/bin/env python3
"""
Comprehensive test script for Digital Archaeology application.
Tests all major features: OCR, Summarization, Search, Q&A, and Indexing.
"""

import sys
from pathlib import Path
import yaml
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.processor import DocumentProcessor
from src.search import SearchEngine
from src.qa_engine import MistralQAEngine
from src.utils import setup_logging

logger = setup_logging("TestSuite")

def load_config():
    """Load configuration from config.yaml"""
    with open("config/config.yaml", 'r') as f:
        return yaml.safe_load(f)

def test_mistral_connection(config):
    """Test Mistral/Ollama connectivity"""
    logger.info("=" * 60)
    logger.info("TEST 1: Mistral/Ollama Connection")
    logger.info("=" * 60)
    
    try:
        qa_engine = MistralQAEngine(
            model_url=config['summarization']['model_url'],
            model_name=config['summarization']['model_name'],
            timeout=config['summarization'].get('timeout', 120),
        )
        
        # Test with a simple question
        test_docs = [{
            'filename': 'test.txt',
            'text': 'The library will be closed on Friday for maintenance.',
            'summary': 'Library closure notice'
        }]
        
        result = qa_engine.answer_question("When is the library closed?", test_docs)
        
        if result and 'answer' in result and result['confidence'] != 'error':
            logger.info("✅ Mistral connection: SUCCESS")
            logger.info(f"   Answer: {result['answer'][:100]}...")
            logger.info(f"   Confidence: {result['confidence']}")
            return True
        else:
            logger.error("❌ Mistral connection: FAILED")
            logger.error(f"   Result: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Mistral connection: FAILED - {e}")
        return False

def test_document_processing(config):
    """Test document processing pipeline"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Document Processing Pipeline")
    logger.info("=" * 60)
    
    try:
        processor = DocumentProcessor(config)
        
        # Find a test file
        raw_dir = Path(config['directories']['raw'])
        test_files = list(raw_dir.glob("*.pdf"))[:1]
        
        if not test_files:
            logger.warning("⚠️  No PDF files found for testing")
            return True  # Not a failure, just no files
        
        test_file = test_files[0]
        logger.info(f"   Processing: {test_file.name}")
        
        result = processor.process_file(test_file)
        
        if result and result.get('processed'):
            logger.info("✅ Document processing: SUCCESS")
            logger.info(f"   Summary: {result.get('summary', 'N/A')[:100]}...")
            logger.info(f"   Categories: {result.get('categories', [])}")
            return True
        else:
            logger.error("❌ Document processing: FAILED")
            return False
            
    except Exception as e:
        logger.error(f"❌ Document processing: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_engine(config):
    """Test semantic search"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Semantic Search")
    logger.info("=" * 60)
    
    try:
        data_dir = Path(config['directories']['raw']).parent
        engine = SearchEngine(data_dir)
        
        # Test search
        query = "exam registration"
        results = engine.search(query, k=3)
        
        if results:
            logger.info(f"✅ Search: SUCCESS - Found {len(results)} results")
            for i, res in enumerate(results[:3], 1):
                logger.info(f"   {i}. {res.get('filename', 'Unknown')}")
                logger.info(f"      Type: {res.get('type', 'N/A')}")
                logger.info(f"      Score: {res.get('score', 0):.4f}")
            return True
        else:
            logger.warning("⚠️  Search returned no results (index may be empty)")
            return True  # Not necessarily a failure
            
    except Exception as e:
        logger.error(f"❌ Search: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qa_with_search(config):
    """Test Q&A with actual search results"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Q&A with Search Integration")
    logger.info("=" * 60)
    
    try:
        data_dir = Path(config['directories']['raw']).parent
        engine = SearchEngine(data_dir)
        qa_engine = MistralQAEngine(
            model_url=config['summarization']['model_url'],
            model_name=config['summarization']['model_name'],
            timeout=config['summarization'].get('timeout', 120),
        )
        
        # Search for relevant documents
        question = "What are the exam registration deadlines?"
        search_results = engine.search(question, k=3)
        
        if not search_results:
            logger.warning("⚠️  No search results for Q&A test")
            return True
        
        # Prepare context
        context_docs = []
        for res in search_results:
            text_content = res.get('content_snippet', '') or res.get('summary', '')
            context_docs.append({
                'filename': res.get('filename', 'Unknown'),
                'text': text_content,
                'summary': res.get('summary', '')
            })
        
        # Get answer
        result = qa_engine.answer_question(question, context_docs)
        
        if result and result['confidence'] != 'error':
            logger.info("✅ Q&A Integration: SUCCESS")
            logger.info(f"   Question: {question}")
            logger.info(f"   Answer: {result['answer'][:150]}...")
            logger.info(f"   Sources: {', '.join(result.get('sources', []))}")
            return True
        else:
            logger.error("❌ Q&A Integration: FAILED")
            return False
            
    except Exception as e:
        logger.error(f"❌ Q&A Integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_summarization(config):
    """Test summarization with Mistral"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Summarization (Mistral)")
    logger.info("=" * 60)
    
    try:
        from src.summarizer import DocumentSummarizer
        
        summarizer = DocumentSummarizer(
            method=config['summarization']['method'],
            sentences_count=config['summarization']['sentences'],
            model_url=config['summarization'].get('model_url'),
            model_name=config['summarization'].get('model_name', 'mistral'),
            timeout=config['summarization'].get('timeout', 90),
        )
        
        test_text = """
        OFFICIAL NOTICE: The semester end examinations for B.Tech students will be conducted
        from March 15th to March 30th, 2024. All students must register for the examinations
        by March 10th, 2024. Late registrations will not be accepted. Students should bring
        their ID cards and admit cards to the examination hall. The examination schedule
        has been posted on the university website.
        """
        
        summary = summarizer.summarize(test_text)
        
        if summary and len(summary) > 0:
            logger.info("✅ Summarization: SUCCESS")
            logger.info(f"   Original length: {len(test_text)} chars")
            logger.info(f"   Summary length: {len(summary)} chars")
            logger.info(f"   Summary: {summary}")
            return True
        else:
            logger.error("❌ Summarization: FAILED - Empty summary")
            return False
            
    except Exception as e:
        logger.error(f"❌ Summarization: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("\n" + "🏛️" * 30)
    logger.info("DIGITAL ARCHAEOLOGY - COMPREHENSIVE TEST SUITE")
    logger.info("🏛️" * 30 + "\n")
    
    # Load config
    config = load_config()
    
    # Run tests
    results = {
        "Mistral Connection": test_mistral_connection(config),
        "Document Processing": test_document_processing(config),
        "Semantic Search": test_search_engine(config),
        "Q&A Integration": test_qa_with_search(config),
        "Summarization": test_summarization(config)
    }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"TOTAL: {passed}/{total} tests passed")
    logger.info("=" * 60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
