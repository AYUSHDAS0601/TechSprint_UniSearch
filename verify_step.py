import time
import shutil
import sys
from pathlib import Path
import json

def verify_pipeline():
    print("Starting verification...")
    
    # 1. Setup paths
    base_dir = Path("data")
    watch_dir = base_dir / "watch"
    meta_dir = base_dir / "metadata"
    index_dir = base_dir / "index"
    
    watch_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. visual check
    print(f"Watch dir: {watch_dir}")
    
    # 3. Create a dummy PDF/Text file in watch dir
    # We'll use a simple wrapper to simulate a file arriving
    # Note: The monitor must be running separately for this to be picked up automatically.
    # But for this script, we can also just manually invoke the processor if we want to unit test that.
    # However, to test the daemon, we need the daemon running.
    
    test_file = watch_dir / "test_notice.txt"
    with open(test_file, "w") as f:
        f.write("OFFICIAL NOTICE: The library will be closed on Friday for maintenance. please plan accordingly.")
    
    print(f"Created {test_file}")
    
    # 4. Wait for processing (Assuming daemon is running!)
    # Since I cannot easily spawn the daemon and keep it alive in this script without complex process management 
    # in this environment, I will rely on the user/agent to have started the daemon OR I will test the processor directly here.
    
    # Let's test the Processor directly first to ensure logic is sound.
    # Then we can assert the Daemon would work if connected.
    
    print("Testing Processor logic directly...")
    sys.path.append(".")
    from src.processor import DocumentProcessor
    import yaml
    
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
        
    processor = DocumentProcessor(config)
    result = processor.process_file(test_file)
    
    if not result:
        print("❌ Processor returned None!")
        return
        
    print("✅ Processor returned result")
    
    # 5. Verify Metadata
    meta_file = meta_dir / "test_notice.txt.json"
    if meta_file.exists():
        print("✅ Metadata file created")
        with open(meta_file) as f:
            data = json.load(f)
            print(f"   Summary: {data.get('summary')}")
            print(f"   Categories: {data.get('categories')}")
            if data.get('summary'): 
                 print("✅ Summary generated")
            else:
                 print("❌ Summary missing")
    else:
        print("❌ Metadata file missing")

    # 6. Verify Index
    # We can inspect the FAISS index
    import faiss
    import pickle
    
    index_path = index_dir / "faiss_index.bin"
    meta_pkl = index_dir / "metadata.pkl"
    
    if index_path.exists() and meta_pkl.exists():
        print("✅ Index files exist")
        index = faiss.read_index(str(index_path))
        print(f"   Index contains {index.ntotal} vectors")
        
        with open(meta_pkl, "rb") as f:
            meta = pickle.load(f)
            print(f"   Metadata entries: {len(meta)}")
            
            # Check for 'summary' and 'chunk' types
            types = [m.get('type') for m in meta]
            print(f"   Types found: {set(types)}")
            
            if 'summary' in types and 'chunk' in types:
                print("✅ Hybrid indexing verified (Summary + Chunks found)")
            elif 'summary' in types:
                print("⚠️ Only summaries found (small text?)")
            else:
                print("❌ Missing expected types")
    else:
        print("❌ Index files missing")

if __name__ == "__main__":
    verify_pipeline()
