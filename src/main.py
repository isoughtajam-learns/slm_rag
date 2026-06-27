"""
Main orchestration pipeline for the local RAG system.
Coordinates intent classification, retrieval, and reasoning.
"""

import os
import time

# Disable ChromaDB telemetry before any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

from typing import Dict, List
from pathlib import Path

from src.intent_classifier import IntentClassifier
from src.retrieval_system import RetrievalSystem
from src.reasoning_engine import ReasoningEngine
from src.config import TOP_K_RESULTS, \
    EmbeddingModel, IntentModel, \
    ReasoningModel


class LocalRAGSystem:
    """
    Fully local RAG system using small language models.
    
    Architecture:
    1. Intent Classification (sub-1B SLM) - Routes requests
    2. Document Retrieval (local vector DB) - Finds relevant context
    3. Reasoning & Synthesis (1-3B SLM) - Generates responses
    """
    
    def __init__(
            self,
            collection_name: str = "docs",
            intent_model_name: str = IntentModel.ALL_MINILM,
            embedding_model_name: str = EmbeddingModel.ALL_MINILM,
            reasoning_model_name: str = ReasoningModel.LFM2_5__1_2B,
    ) -> None:
        """
        Initialize the RAG system.
        
        Args:
            collection_name: Name of the document collection
        """
        collection_name = collection_name + "_" + "-".join([
            IntentModel(intent_model_name).name,
            EmbeddingModel(embedding_model_name).name,
            ReasoningModel(reasoning_model_name).name
        ])
        print(f"Initializing Local RAG System for {collection_name}")
        
        # Initialize components
        self.intent_classifier = IntentClassifier(model_name=intent_model_name)
        self.retrieval_system = RetrievalSystem(collection_name, embedding_model_name)
        self.reasoning_engine = ReasoningEngine(model_name=reasoning_model_name)
        
        print("✓ System initialized")
    
    def ingest_documents(self, documents_dir: Path = None) -> int:
        """
        Ingest documents into the system.
        
        Args:
            documents_dir: Path to documents directory
            
        Returns:
            Number of chunks ingested
        """
        start = time.time()
        print("\n" + "="*60)
        print("DOCUMENT INGESTION")
        print("="*60)
        
        count = self.retrieval_system.ingest_documents(documents_dir)
        
        stats = self.retrieval_system.get_stats()
        print(f"Time taken to ingest: {time.time() - start} seconds")
        print(f"\n✓ Ingestion complete")
        print(f"  Total documents in system: {stats['document_count']}")
        
        return count
    
    def query(
        self,
        user_query: str,
        n_results: int = TOP_K_RESULTS,
        verbose: bool = True,
        show_chunks: bool = False,
        show_thinking: bool = False
    ) -> Dict[str, any]:
        """
        Process a user query through the full RAG pipeline.
        
        Args:
            user_query: The user's question or request
            n_results: Number of documents to retrieve
            verbose: Whether to print progress information
            show_chunks: Whether to display retrieved chunks
            show_thinking: Whether to show the <think></think> reasoning section
            
        Returns:
            Dict containing response and metadata
        """
        if verbose:
            print("\n" + "="*60)
            print(f"QUERY: {user_query}")
            print("="*60)
        
        # Step 1: Classify intent
        if verbose:
            print("\n[1/3] Classifying intent...")
        
        intent_result = self.intent_classifier.classify(user_query)
        intent = intent_result['intent']
        needs_retrieval = intent_result['needs_retrieval']
        
        if verbose:
            print(f"  Intent: {intent}")
            print(f"  Needs retrieval: {needs_retrieval}")
        
        # Step 2: Retrieve relevant documents (if needed)
        retrieved_docs = []
        if needs_retrieval:
            if verbose:
                print(f"\n[2/3] Retrieving relevant documents...")
            
            retrieved_docs = self.retrieval_system.retrieve(user_query, n_results)
            if not retrieved_docs:
                raise Exception("No documents retrieved, embeddings need to be generated with chosen models")
            
            if verbose:
                print(f"  Found {len(retrieved_docs)} relevant chunks")
            if retrieved_docs:
                print(f"  Sources: {', '.join(set(d['metadata'].get('filename', 'Unknown') for d in retrieved_docs))}")
            
            # Show chunks if requested
            if show_chunks and retrieved_docs:
                print("\n" + "="*60)
                print("RETRIEVED CHUNKS")
                print("="*60)
                for i, doc in enumerate(retrieved_docs, 1):
                    source = doc.get('metadata', {}).get('filename', 'Unknown')
                    chunk_idx = doc.get('metadata', {}).get('chunk_index', '?')
                    content = doc.get('content', '')
                    distance = doc.get('distance', 'N/A')
                    
                    print(f"\n[Chunk {i}] {source} (chunk #{chunk_idx})")
                    print(f"Distance: {distance}")
                    print("-" * 60)
                    print(content)
                    print("-" * 60)
        else:
            if verbose:
                print("\n[2/3] Skipping retrieval (not needed for this intent)")
        
        # Step 3: Generate response based on intent
        if verbose:
            print(f"\n[3/3] Generating response...")
        
        response = self._generate_response(intent, user_query, retrieved_docs, show_thinking)
        
        # Compile final result
        result = {
            "query": user_query,
            "intent": intent,
            "retrieved_docs_count": len(retrieved_docs),
            "response": response.get('response') or response.get('analysis') or response.get('summary'),
            "sources": response.get('sources', []),
            "metadata": {
                "intent_classification": intent_result,
                "retrieval": {
                    "chunks_retrieved": len(retrieved_docs),
                    "sources": response.get('sources', [])
                },
                "reasoning": {
                    "model_used": response.get('model_used'),
                    "response_type": intent
                }
            }
        }
        
        if verbose:
            print(f"\n✓ Response generated")
            print("="*60)
        
        return result
    
    def _generate_response(
        self,
        intent: str,
        query: str,
        retrieved_docs: List[Dict[str, any]],
        show_thinking: bool = False
    ) -> Dict[str, any]:
        """
        Generate response based on classified intent.
        
        Args:
            intent: Classified intent category
            query: User query
            retrieved_docs: Retrieved document chunks
            show_thinking: Whether to show the <think></think> reasoning section
            
        Returns:
            Response dict from reasoning engine
        """
        if intent == "documentation_query":
            return self.reasoning_engine.synthesize_response(query, retrieved_docs, show_thinking=show_thinking)
        
        elif intent == "incident_analysis":
            return self.reasoning_engine.analyze_incident(query, retrieved_docs, show_thinking=show_thinking)
        
        elif intent == "summarization":
            return self.reasoning_engine.summarize_documents(retrieved_docs, show_thinking=show_thinking)
        
        elif intent == "action_request":
            return self.reasoning_engine.generate_structured_output(query, retrieved_docs, show_thinking=show_thinking)
        
        else:  # general_question
            return self.reasoning_engine.synthesize_response(query, retrieved_docs, show_thinking=show_thinking)
    
    def get_system_info(self) -> Dict[str, any]:
        """Get information about the RAG system."""
        stats = self.retrieval_system.get_stats()
        
        return {
            "system": "Local RAG with Small Language Models",
            "components": {
                "intent_classifier": {
                    "model": self.intent_classifier.model_name,
                    "purpose": "Intent detection and routing"
                },
                "embedding_model": {
                    "model": self.retrieval_system.embedder.model_name,
                    "purpose": "Document and query embeddings"
                },
                "reasoning_engine": {
                    "model": self.reasoning_engine.model_name,
                    "purpose": "Reasoning and synthesis"
                }
            },
            "vector_store": stats,
            "privacy": "Fully local - no data leaves the system"
        }
    
    def interactive_mode(self):
        """Run the system in interactive mode."""
        print("\n" + "="*60)
        print("LOCAL RAG SYSTEM - INTERACTIVE MODE")
        print("="*60)
        print("\nEnter your queries (type 'exit' to quit, 'info' for system info)")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print("\nExiting...")
                    break
                
                if user_input.lower() == 'info':
                    info = self.get_system_info()
                    print("\nSystem Information:")
                    print(f"  Documents: {info['vector_store']['document_count']}")
                    print(f"  Intent Model: {info['components']['intent_classifier']['model']}")
                    print(f"  Reasoning Model: {info['components']['reasoning_engine']['model']}")
                    print(f"  Privacy: {info['privacy']}")
                    continue
                
                # Process query
                result = self.query(user_input, verbose=False)
                
                print(f"\nAssistant: {result['response']}")
                
                if result['sources']:
                    print(f"\nSources: {', '.join(result['sources'])}")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")


def main():
    """Main entry point for the RAG system."""
    import sys
    
    # Initialize system
    rag_system = LocalRAGSystem()
    
    # Check if documents need to be ingested
    stats = rag_system.retrieval_system.get_stats()
    if stats['document_count'] == 0:
        print("\n⚠ No documents in the system. Add documents to data/documents/ and run:")
        print("  python main.py --ingest")
        print("\nOr proceed to interactive mode (queries will return no results)")
        print()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--ingest':
            rag_system.ingest_documents()
            return
        
        elif sys.argv[1] == '--info':
            info = rag_system.get_system_info()
            print("\nSystem Information:")
            print("="*60)
            for key, value in info.items():
                print(f"{key}: {value}")
            return
        
        elif sys.argv[1] == '--query':
            if len(sys.argv) > 2:
                # Check for --show-chunks and --show-thinking flags
                show_chunks = '--show-chunks' in sys.argv
                show_thinking = '--show-thinking' in sys.argv
                args = [arg for arg in sys.argv[2:] if arg not in ['--show-chunks', '--show-thinking']]
                query = ' '.join(args)
                result = rag_system.query(query, verbose=True, show_chunks=show_chunks, show_thinking=show_thinking)
                print(f"\n\nRESPONSE:\n{result['response']}")
                if result['sources']:
                    print(f"\nSOURCES: {', '.join(result['sources'])}")
            else:
                print("Usage: python main.py --query <your question> [--show-chunks] [--show-thinking]")
            return
    
    # Default: interactive mode
    rag_system.interactive_mode()


if __name__ == "__main__":
    main()

