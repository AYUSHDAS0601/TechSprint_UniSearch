#!/usr/bin/env python3
"""
API Wrapper for Digital Archaeology
Provides CLI interface for Node.js to communicate with Python modules via JSON
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.search import SearchEngine
from src.qa_engine import MistralQAEngine
from src.processor import DocumentProcessor
from src.scraper import NoticesCrawler
import yaml


def load_config():
    """Load configuration from config.yaml"""
    config_path = project_root / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def handle_search(data, config):
    """Handle search request"""
    query = data.get('query', '')
    k = data.get('k', 5)
    filters = data.get('filters')
    
    data_dir = project_root / "data"
    engine = SearchEngine(data_dir)
    results = engine.search(query, k=k, filters=filters)
    
    return {
        'success': True,
        'results': results
    }


def handle_qa(data, config):
    """Handle Q&A request"""
    question = data.get('question', '')
    context_docs = data.get('context_docs', [])
    
    qa_engine = MistralQAEngine(
        model_url=config['summarization']['model_url'],
        model_name=config['summarization']['model_name']
    )
    
    result = qa_engine.answer_question(question, context_docs)
    
    return {
        'success': True,
        'answer': result.get('answer', ''),
        'confidence': result.get('confidence', 'medium'),
        'sources': result.get('sources', [])
    }


def handle_process(data, config):
    """Handle file processing request"""
    file_path = data.get('file_path', '')
    
    if not os.path.exists(file_path):
        return {
            'success': False,
            'error': f'File not found: {file_path}'
        }
    
    data_dir = project_root / "data"
    processor = DocumentProcessor(data_dir)
    
    # Process the file
    result = processor.process_document(Path(file_path))
    
    return {
        'success': True,
        'processed': True,
        'file': file_path
    }


def handle_scrape(data, config):
    """Handle scraping request"""
    limit = data.get('limit', 20)
    
    crawler = NoticesCrawler()
    downloaded = crawler.crawl(limit=limit)
    
    return {
        'success': True,
        'downloaded': downloaded,
        'message': f'Downloaded {downloaded} files'
    }


def handle_stats(data, config):
    """Handle stats request"""
    data_dir = project_root / "data"
    engine = SearchEngine(data_dir)
    
    # Get index stats
    total_vectors = 0
    if hasattr(engine.indexer, 'index') and engine.indexer.index:
        total_vectors = engine.indexer.index.ntotal
    
    # Count documents
    raw_dir = data_dir / "raw"
    total_docs = 0
    if raw_dir.exists():
        total_docs = len(list(raw_dir.glob("*.pdf"))) + \
                     len(list(raw_dir.glob("*.jpg"))) + \
                     len(list(raw_dir.glob("*.jpeg"))) + \
                     len(list(raw_dir.glob("*.png")))
    
    return {
        'success': True,
        'total_documents': total_docs,
        'indexed_vectors': total_vectors,
        'system_status': 'active'
    }


def main():
    """Main entry point"""
    try:
        # Read JSON input from stdin
        input_data = sys.stdin.read()
        
        if not input_data:
            print(json.dumps({'error': 'No input data provided'}))
            sys.exit(1)
        
        data = json.loads(input_data)
        action = data.get('action', '')
        
        # Load config
        config = load_config()
        
        # Route to appropriate handler
        if action == 'search':
            result = handle_search(data, config)
        elif action == 'qa':
            result = handle_qa(data, config)
        elif action == 'process':
            result = handle_process(data, config)
        elif action == 'scrape':
            result = handle_scrape(data, config)
        elif action == 'stats':
            result = handle_stats(data, config)
        else:
            result = {
                'success': False,
                'error': f'Unknown action: {action}'
            }
        
        # Output JSON result
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == '__main__':
    main()
