"""
Diagnostic script to troubleshoot "Found 0 relevant chunks" issue.
Checks both ingestion and retrieval processes.
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

from src.retrieval_system import RetrievalSystem
from src.document_processor import LocalEmbedder
from src.config import DOCUMENTS_DIR, SIMILARITY_THRESHOLD, TOP_K_RESULTS
from pathlib import Path

def diagnose_system():
    """Run comprehensive diagnostics on the RAG system."""
    
    print("="*70)
    print("RAG SYSTEM DIAGNOSTICS")
    print("="*70)
    
    # Initialize system
    print("\n[1] Initializing Retrieval System...")
    try:
        retrieval = RetrievalSystem()
        print("✓ Retrieval system initialized")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return
    
    # Check document storage
    print("\n[2] Checking Vector Store...")
    stats = retrieval.get_stats()
    print(f"  Collection name: {stats['collection_name']}")
    print(f"  Storage path: {stats['storage_path']}")
    print(f"  Document count: {stats['document_count']}")
    
    if stats['document_count'] == 0:
        print("\n  ⚠️  ISSUE FOUND: No documents in vector store!")
        print("     This means ingestion failed or hasn't been run.")
        print("\n  Checking ingestion process...")
        check_ingestion()
        return
    else:
        print(f"  ✓ Vector store contains {stats['document_count']} chunks")
    
    # Check if documents exist in filesystem
    print("\n[3] Checking Document Directory...")
    doc_files = list(DOCUMENTS_DIR.rglob('*'))
    doc_files = [f for f in doc_files if f.is_file()]
    print(f"  Document directory: {DOCUMENTS_DIR}")
    print(f"  Files found: {len(doc_files)}")
    for f in doc_files:
        print(f"    - {f.name}")
    
    # Test embeddings
    print("\n[4] Testing Embedding Generation...")
    embedder = LocalEmbedder()
    test_text = "How do I configure logging?"
    try:
        embedding = embedder.embed_text(test_text)
        if embedding:
            print(f"  ✓ Generated embedding vector (dim={len(embedding)})")
        else:
            print("  ✗ Failed to generate embedding (returned None)")
            return
    except Exception as e:
        print(f"  ✗ Embedding generation error: {e}")
        return
    
    # Test retrieval with raw query
    print("\n[5] Testing Retrieval...")
    test_query = "How do I configure logging?"
    print(f"  Query: '{test_query}'")
    print(f"  Top K: {TOP_K_RESULTS}")
    print(f"  Similarity threshold: {SIMILARITY_THRESHOLD}")
    
    try:
        # Get raw results from vector store
        print("\n  Querying vector store (before filtering)...")
        results_raw = retrieval.vector_store.collection.query(
            query_embeddings=[embedding],
            n_results=TOP_K_RESULTS
        )
        
        if results_raw['ids'] and results_raw['ids'][0]:
            print(f"  ✓ Vector store returned {len(results_raw['ids'][0])} results")
            print("\n  Results with distances:")
            for i in range(len(results_raw['ids'][0])):
                distance = results_raw['distances'][0][i]
                doc_id = results_raw['ids'][0][i]
                preview = results_raw['documents'][0][i][:80]
                print(f"    {i+1}. ID: {doc_id}")
                print(f"       Distance: {distance:.4f} (threshold: {SIMILARITY_THRESHOLD})")
                print(f"       Preview: {preview}...")
                
                if distance >= SIMILARITY_THRESHOLD:
                    print(f"       ⚠️  FILTERED OUT - distance >= threshold")
                else:
                    print(f"       ✓ PASSES threshold")
                print()
        else:
            print("  ✗ Vector store returned no results")
            return
        
        # Now test the actual retrieve method
        print("\n  Testing retrieve() method (with filtering)...")
        results_filtered = retrieval.retrieve(test_query, n_results=TOP_K_RESULTS)
        print(f"  Results after filtering: {len(results_filtered)}")
        
        if len(results_filtered) == 0:
            print("\n  ⚠️  ISSUE FOUND: All results filtered out!")
            print(f"     Problem: Similarity threshold ({SIMILARITY_THRESHOLD}) is too strict.")
            print(f"     All distances are >= {SIMILARITY_THRESHOLD}")
            print("\n  SOLUTION: Increase SIMILARITY_THRESHOLD in config.py")
            print(f"     Suggested value: 1.5 or 2.0 (ChromaDB uses L2 distance)")
        else:
            print(f"  ✓ {len(results_filtered)} results passed filtering")
            for i, result in enumerate(results_filtered):
                print(f"\n    {i+1}. {result['metadata'].get('filename', 'Unknown')}")
                print(f"       Distance: {result['distance']:.4f}")
                print(f"       Preview: {result['content'][:80]}...")
        
    except Exception as e:
        print(f"  ✗ Retrieval error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("DIAGNOSIS COMPLETE")
    print("="*70)


def check_ingestion():
    """Check if ingestion would work."""
    print("\n[INGESTION CHECK]")
    
    # Check documents exist
    doc_files = list(DOCUMENTS_DIR.rglob('*'))
    doc_files = [f for f in doc_files if f.is_file()]
    
    if len(doc_files) == 0:
        print("  ✗ No documents in data/documents/ directory")
        print("  Solution: Add documents to data/documents/ and run:")
        print("    python main.py --ingest")
        return
    
    print(f"  ✓ Found {len(doc_files)} files")
    
    # Try loading one document
    from document_processor import DocumentProcessor
    processor = DocumentProcessor()
    
    print("\n  Testing document loading...")
    try:
        docs = processor.load_documents(DOCUMENTS_DIR)
        if docs:
            print(f"  ✓ Successfully loaded {len(docs)} documents")
            print("\n  To ingest documents, run:")
            print("    python main.py --ingest")
        else:
            print("  ✗ No documents could be loaded")
            print("  Check that files have supported extensions (.txt, .md, .pdf, .docx)")
    except Exception as e:
        print(f"  ✗ Error loading documents: {e}")


if __name__ == "__main__":
    diagnose_system()

