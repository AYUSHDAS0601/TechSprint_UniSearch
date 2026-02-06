import shutil
from pathlib import Path
import numpy as np
from src.search import SearchEngine
from src.indexer import FaissIndexer

# Mock Embedder to avoid loading heavy models for logic test
class MockEmbedder:
    def generate(self, text):
        return np.random.rand(384).astype('float32')

# Setup Test Data
TEST_DIR = Path("data_test")
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)
TEST_DIR.mkdir()

(TEST_DIR / "raw").mkdir()
(TEST_DIR / "index").mkdir()
(TEST_DIR / "metadata").mkdir()
(TEST_DIR / "processed").mkdir()
(TEST_DIR / "watch").mkdir()

print("Initializing Engine...")
engine = SearchEngine(TEST_DIR)
# patch embedder
engine.embedder = MockEmbedder()
# patch indexer to use valid path
engine.indexer = FaissIndexer(TEST_DIR / "index")

# Create Dummy Metadata
docs = [
    {"filename": "doc1.pdf", "categories": ["Exam"], "type": "summary", "id": "1"},
    {"filename": "doc2.pdf", "categories": ["Scholarship"], "type": "summary", "id": "2"},
    {"filename": "doc3.pdf", "categories": ["General", "Holiday"], "type": "summary", "id": "3"},
]

# Add to index
embeddings = np.random.rand(len(docs), 384).astype('float32')
engine.indexer.add_documents(embeddings, docs)

print(f"Total indexed: {engine.indexer.index.ntotal}")

# Test 1: No Filter
print("\nTest 1: No Filter")
results = engine.search("query", k=10)
print(f"Got {len(results)} results")
assert len(results) == 3

# Test 2: Filter Exam
print("\nTest 2: Filter Category='Exam'")
results = engine.search("query", k=10, filters={'categories': ['Exam']})
print(f"Got {len(results)} results")
for r in results:
    print(f" - {r['filename']} {r['categories']}")
assert len(results) == 1
assert results[0]['filename'] == "doc1.pdf"

# Test 3: Filter Scholarship
print("\nTest 3: Filter Category='Scholarship'")
results = engine.search("query", k=10, filters={'categories': ['Scholarship']})
assert len(results) == 1
assert results[0]['filename'] == "doc2.pdf"

# Test 4: Filter Multiple (OR logic if list passed as value in my impl? or AND?)
# Let's check impl: "if isinstance(value, list): if not any(...)" -> So it's OR logic for list of values.
print("\nTest 4: Filter Category=['Exam', 'Holiday']")
results = engine.search("query", k=10, filters={'categories': ['Exam', 'Holiday']})
print(f"Got {len(results)} results")
# Should match doc1 (Exam) and doc3 (Holiday)
assert len(results) == 2
filenames = sorted([r['filename'] for r in results])
assert filenames == ['doc1.pdf', 'doc3.pdf']

print("\nSUCCESS: All search logic tests passed!")
shutil.rmtree(TEST_DIR)
