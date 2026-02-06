import time
import yaml
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

from .processor import DocumentProcessor
from .utils import setup_logging

logger = setup_logging("Monitor")

class DocumentHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        # Initialize the central processor
        self.processor = DocumentProcessor(config)
        
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() not in self.config['monitoring']['extensions']:
            return

        logger.info(f"New file detected: {file_path}")
        
        # Debounce
        time.sleep(self.config['monitoring']['debounce_seconds'])
        
        self._process_file(file_path)

    def _process_file(self, file_path):
        # Delegate to the processor
        result = self.processor.process_file(file_path)
        if result:
            logger.info(f"Successfully processed and indexed: {file_path.name}")
        else:
            logger.error(f"Failed to process: {file_path.name}")

def start_monitoring():
    # Load Config
    with open("config/config.yaml", 'r') as f:
        config = yaml.safe_load(f)
        
    watch_dir = Path(config['directories']['watch'])
    watch_dir.mkdir(parents=True, exist_ok=True)
    
    event_handler = DocumentHandler(config)
    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=False)
    
    logger.info(f"Starting Watchdog on: {watch_dir}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()
