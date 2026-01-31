"""
Example usage and demonstrations of the Local RAG System.
"""

from src.main import LocalRAGSystem
from pathlib import Path


def example_documentation_query():
    """Example: Querying documentation."""
    print("\n" + "="*70)
    print("EXAMPLE 1: DOCUMENTATION QUERY")
    print("="*70)
    
    rag = LocalRAGSystem()
    
    query = "What are the main cyber security measures for nuclear plant control systems?"
    result = rag.query(query, verbose=True)
    
    print(f"\nResponse:\n{result['response']}")
    if result['sources']:
        print(f"\nSources: {', '.join(result['sources'])}")


def example_incident_analysis():
    """Example: Analyzing an incident."""
    print("\n" + "="*70)
    print("EXAMPLE 2: INCIDENT ANALYSIS")
    print("="*70)
    
    rag = LocalRAGSystem()
    
    query = "What should be the response procedure if unauthorized access is detected in the nuclear plant?"
    result = rag.query(query, verbose=True)
    
    print(f"\nAnalysis:\n{result['response']}")
    if result['sources']:
        print(f"\nSources: {', '.join(result['sources'])}")


def example_summarization():
    """Example: Summarizing documents."""
    print("\n" + "="*70)
    print("EXAMPLE 3: DOCUMENT SUMMARIZATION")
    print("="*70)
    
    rag = LocalRAGSystem()
    
    query = "Summarize the physical security measures for nuclear plants"
    result = rag.query(query, verbose=True)
    
    print(f"\nSummary:\n{result['response']}")
    if result['sources']:
        print(f"\nSources: {', '.join(result['sources'])}")


def example_action_request():
    """Example: Generating structured output."""
    print("\n" + "="*70)
    print("EXAMPLE 4: ACTION REQUEST")
    print("="*70)
    
    rag = LocalRAGSystem()
    
    query = "List the key access control requirements for nuclear plant critical areas"
    result = rag.query(query, verbose=True)
    
    print(f"\nGenerated Output:\n{result['response']}")
    if result['sources']:
        print(f"\nSources: {', '.join(result['sources'])}")


def example_batch_queries():
    """Example: Processing multiple queries."""
    print("\n" + "="*70)
    print("EXAMPLE 5: BATCH QUERY PROCESSING")
    print("="*70)
    
    rag = LocalRAGSystem()
    
    queries = [
        "What authentication methods are recommended for nuclear plant systems?",
        "What are the perimeter security requirements?",
        "How should cyber security monitoring be implemented?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i}/{len(queries)} ---")
        print(f"Q: {query}")
        
        result = rag.query(query, verbose=False)
        
        print(f"A: {result['response']}")


def example_system_info():
    """Example: Getting system information."""
    print("\n" + "="*70)
    print("EXAMPLE 6: SYSTEM INFORMATION")
    print("="*70)
    
    rag = LocalRAGSystem()
    info = rag.get_system_info()
    
    print("\nSystem Configuration:")
    print(f"  System: {info['system']}")
    print(f"\nModels:")
    print(f"  Intent Classifier: {info['components']['intent_classifier']['model']}")
    print(f"  Embeddings: {info['components']['embedding_model']['model']}")
    print(f"  Reasoning: {info['components']['reasoning_engine']['model']}")
    print(f"\nVector Store:")
    print(f"  Collection: {info['vector_store']['collection_name']}")
    print(f"  Documents: {info['vector_store']['document_count']}")
    print(f"  Storage: {info['vector_store']['storage_path']}")
    print(f"\nPrivacy: {info['privacy']}")


def example_custom_documents():
    """Example: Ingesting custom documents."""
    print("\n" + "="*70)
    print("EXAMPLE 7: CUSTOM DOCUMENT INGESTION")
    print("="*70)
    
    # Create sample documents
    sample_dir = Path("data/documents/examples")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a sample document
    sample_doc = sample_dir / "sample_security_checklist.md"
    if not sample_doc.exists():
        content = """# Nuclear Plant Security Checklist

## Daily Security Checks
- Review all access logs for anomalies
- Verify all security cameras are operational
- Test intrusion detection systems
- Check perimeter fence integrity

## Weekly Security Tasks
- Update security personnel schedules
- Review and update visitor logs
- Test emergency communication systems
- Conduct random security drills

## Monthly Security Tasks
- Full security audit of all systems
- Review and update access credentials
- Evaluate security incident reports
- Update security protocols as needed

## Security Incident Response
- Unauthorized access: Immediate lockdown and investigation
- Cyber intrusion: Isolate affected systems, notify authorities
- Physical breach: Activate emergency protocols, secure critical areas
"""
        sample_doc.write_text(content)
        print(f"Created sample document: {sample_doc}")
    
    # Ingest documents
    rag = LocalRAGSystem()
    count = rag.ingest_documents(sample_dir.parent)
    
    print(f"\nIngested {count} document chunks")
    
    # Query the ingested document
    query = "What are the daily security checks for a nuclear plant?"
    result = rag.query(query, verbose=False)
    
    print(f"\nQuery: {query}")
    print(f"Response: {result['response']}")


def run_all_examples():
    """Run all examples."""
    print("\n" + "="*70)
    print("LOCAL RAG SYSTEM - COMPLETE EXAMPLES")
    print("="*70)
    
    try:
        example_system_info()
        
        # Check if documents exist
        from src.config import DOCUMENTS_DIR
        doc_count = sum(1 for _ in DOCUMENTS_DIR.rglob('*') if _.is_file())
        
        if doc_count == 0:
            print("\nNo documents found. Creating sample documents...")
            example_custom_documents()
        
        example_documentation_query()
        example_incident_analysis()
        example_summarization()
        example_action_request()
        example_batch_queries()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Verify models are available: ollama list")
        print("3. Check documents directory has files")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        
        examples = {
            "1": example_documentation_query,
            "2": example_incident_analysis,
            "3": example_summarization,
            "4": example_action_request,
            "5": example_batch_queries,
            "6": example_system_info,
            "7": example_custom_documents,
        }
        
        if example_name in examples:
            examples[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print("Available examples: 1-7, or run without args for all")
    else:
        run_all_examples()

