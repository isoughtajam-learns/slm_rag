"""
System verification and health check script.
Run this to verify the Local RAG system is properly configured.
"""

import sys
from pathlib import Path

def check_mark():
    return "[OK]"

def cross_mark():
    return "[X]"

def check_python_version():
    """Check Python version."""
    print("\n1. Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   {check_mark()} Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   {cross_mark()} Python {version.major}.{version.minor}.{version.micro}")
        print(f"   Required: Python 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("\n2. Checking dependencies...")
    
    required = [
        'ollama',
        'chromadb', 
        'sentence_transformers',
        'pypdf',
        'docx',
        'pydantic',
        'rich'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"   {check_mark()} {package}")
        except ImportError:
            print(f"   {cross_mark()} {package}")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_ollama_connection():
    """Check if Ollama is accessible."""
    print("\n3. Checking Ollama connection...")
    
    try:
        import ollama
        client = ollama.Client(host="http://localhost:11434")
        models = client.list()
        print(f"   {check_mark()} Ollama is running")
        return True, models
    except Exception as e:
        print(f"   {cross_mark()} Cannot connect to Ollama")
        print(f"   Error: {e}")
        print(f"   Start Ollama with: ollama serve")
        return False, None

def check_models(models_list):
    """Check if required models are available."""
    print("\n4. Checking required models...")
    
    required_models = [
        "hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16",
        "hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16",
        "all-minilm:latest"
    ]
    
    available = [m['name'] for m in models_list['models']]
    
    all_found = True
    for model in required_models:
        if model in available:
            print(f"   {check_mark()} {model}")
        else:
            print(f"   {cross_mark()} {model}")
            all_found = False
    
    if not all_found:
        print(f"\n   Pull missing models:")
        for model in required_models:
            if model not in available:
                print(f"   ollama pull {model}")
    
    return all_found

def check_directories():
    """Check if required directories exist."""
    print("\n5. Checking directory structure...")
    
    from config import DATA_DIR, DOCUMENTS_DIR, CHROMA_DB_DIR
    
    dirs = [
        ("Data directory", DATA_DIR),
        ("Documents directory", DOCUMENTS_DIR),
        ("ChromaDB directory", CHROMA_DB_DIR)
    ]
    
    for name, path in dirs:
        if path.exists():
            print(f"   {check_mark()} {name}: {path}")
        else:
            print(f"   {cross_mark()} {name}: {path}")
            path.mkdir(parents=True, exist_ok=True)
            print(f"       Created directory")
    
    return True

def check_documents():
    """Check if documents are available."""
    print("\n6. Checking documents...")
    
    from config import DOCUMENTS_DIR
    
    files = list(DOCUMENTS_DIR.rglob('*'))
    doc_files = [f for f in files if f.is_file()]
    
    if doc_files:
        print(f"   {check_mark()} Found {len(doc_files)} document(s)")
        for doc in doc_files[:5]:  # Show first 5
            print(f"       - {doc.name}")
        if len(doc_files) > 5:
            print(f"       ... and {len(doc_files) - 5} more")
        return True
    else:
        print(f"   {cross_mark()} No documents found")
        print(f"   Add documents to: {DOCUMENTS_DIR}")
        print(f"   Then run: python main.py --ingest")
        return False

def check_vector_store():
    """Check vector store status."""
    print("\n7. Checking vector store...")
    
    try:
        from retrieval_system import RetrievalSystem
        retrieval = RetrievalSystem()
        stats = retrieval.get_stats()
        
        if stats['document_count'] > 0:
            print(f"   {check_mark()} Vector store has {stats['document_count']} chunks")
            return True
        else:
            print(f"   {cross_mark()} Vector store is empty")
            print(f"   Run: python main.py --ingest")
            return False
    except Exception as e:
        print(f"   {cross_mark()} Error checking vector store: {e}")
        return False

def run_simple_test():
    """Run a simple end-to-end test."""
    print("\n8. Running simple test...")
    
    try:
        from retrieval_system import RetrievalSystem
        retrieval = RetrievalSystem()
        stats = retrieval.get_stats()
        
        if stats['document_count'] == 0:
            print(f"   Skipped (no documents ingested)")
            return True
        
        # Try a simple query
        from intent_classifier import IntentClassifier
        classifier = IntentClassifier()
        
        test_query = "How do I configure the system?"
        result = classifier.classify(test_query)
        
        print(f"   {check_mark()} Intent classification works")
        print(f"       Query: {test_query}")
        print(f"       Intent: {result['intent']}")
        
        return True
        
    except Exception as e:
        print(f"   {cross_mark()} Test failed: {e}")
        return False

def main():
    """Main verification function."""
    print("="*70)
    print("LOCAL RAG SYSTEM - HEALTH CHECK")
    print("="*70)
    
    checks = []
    
    # Run all checks
    checks.append(("Python version", check_python_version()))
    checks.append(("Dependencies", check_dependencies()))
    
    ollama_ok, models = check_ollama_connection()
    checks.append(("Ollama connection", ollama_ok))
    
    if ollama_ok and models:
        checks.append(("Required models", check_models(models)))
    else:
        checks.append(("Required models", False))
    
    checks.append(("Directory structure", check_directories()))
    checks.append(("Documents", check_documents()))
    checks.append(("Vector store", check_vector_store()))
    checks.append(("Simple test", run_simple_test()))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = check_mark() if result else cross_mark()
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n" + "="*70)
        print("SUCCESS! System is ready to use.")
        print("="*70)
        print("\nNext steps:")
        print("  1. Add documents to data/documents/ (if not done)")
        print("  2. Run: python main.py --ingest")
        print("  3. Run: python main.py")
        print("\nOr try examples:")
        print("  python examples.py")
        return 0
    else:
        print("\n" + "="*70)
        print("Some checks failed. Please fix the issues above.")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

