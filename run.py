#!/usr/bin/env python
"""
Main entry point for the Local RAG System.
Run this file from the root directory.
"""

import os
import sys

from src.config import EmbeddingModel, ReasoningModel
from src.config import IntentModel

# Disable ChromaDB telemetry before any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import LocalRAGSystem
import argparse


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Local RAG System - Privacy-preserving AI assistant"
    )

    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Ingest documents from data/documents/"
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Single query to execute"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show system information"
    )

    parser.add_argument(
        "--show-chunks",
        action="store_true",
        help="Show retrieved document chunks"
    )

    parser.add_argument(
        "--show-thinking",
        action="store_true",
        help="Show AI reasoning process"
    )

    parser.add_argument(
        "--embedding-model",
        default=EmbeddingModel.ALL_MINILM,
        help="Model for chunking text during ingestion"
    )

    parser.add_argument(
        "--intent-model",
        default=IntentModel.ALL_MINILM,
        help="Model for determining intent of requests"
    )

    parser.add_argument(
        "--reasoning-model",
        default=ReasoningModel.LFM2_5__1_2B,
        help="Model for piecing together responses"
    )

    args = parser.parse_args()

    intent_model = IntentModel(args.intent_model) if args.intent_model else IntentModel.ALL_MINILM

    embedding_model = EmbeddingModel(args.embedding_model) if args.embedding_model else EmbeddingModel.ALL_MINILM

    reasoning_model = ReasoningModel(args.reasoning_model) if args.reasoning_model else ReasoningModel.LFM2_5__1_2B

    # Initialize system
    rag = LocalRAGSystem(
        intent_model_name=intent_model,
        embedding_model_name=embedding_model,
        reasoning_model_name=reasoning_model
    )

    # Handle different commands
    if args.ingest:
        print("Ingesting documents...")
        count = rag.ingest_documents()
        print(f"\nIngestion complete: {count} chunks indexed")

    elif args.info:
        info = rag.get_system_info()
        print("\n" + "="*70)
        print("LOCAL RAG SYSTEM - INFORMATION")
        print("="*70)
        print(f"\nSystem: {info['system']}")
        print(f"\nModels:")
        print(f"  Intent Classifier: {info['components']['intent_classifier']['model']}")
        print(f"  Embeddings: {info['components']['embedding_model']['model']}")
        print(f"  Reasoning: {info['components']['reasoning_engine']['model']}")
        print(f"\nVector Store:")
        print(f"  Collection: {info['vector_store']['collection_name']}")
        print(f"  Documents: {info['vector_store']['document_count']}")
        print(f"  Storage: {info['vector_store']['storage_path']}")
        print(f"\nPrivacy: {info['privacy']}")
        print("="*70)

    elif args.query:
        verbose = args.show_chunks or args.show_thinking
        result = rag.query(args.query, verbose=verbose)

        if args.show_chunks and result.get('chunks'):
            print("\n" + "="*70)
            print("RETRIEVED CHUNKS")
            print("="*70)
            for i, chunk in enumerate(result['chunks'], 1):
                print(f"\n--- Chunk {i} (Score: {chunk.get('score', 'N/A'):.3f}) ---")
                print(f"Source: {chunk.get('source', 'Unknown')}")
                print(f"Content: {chunk.get('content', '')[:200]}...")

        print("\n" + "="*70)
        print("RESPONSE")
        print("="*70)
        print(f"\n{result['response']}")

        if result.get('sources'):
            print(f"\nSources: {', '.join(result['sources'])}")

        if args.show_thinking and result.get('intent'):
            print(f"\nIntent: {result['intent']}")

    else:
        # Interactive mode
        print("\n" + "="*70)
        print("LOCAL RAG SYSTEM - INTERACTIVE MODE")
        print("="*70)
        print("\nType 'info' for system stats, 'exit' to quit.\n")

        while True:
            try:
                query = input("You: ").strip()

                if not query:
                    continue

                if query.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break

                if query.lower() == 'info':
                    info = rag.get_system_info()
                    print(f"\nDocuments: {info['vector_store']['document_count']}")
                    print(f"Storage: {info['vector_store']['storage_path']}")
                    continue

                result = rag.query(query)
                print(f"\nAssistant: {result['response']}")

                if result.get('sources'):
                    print(f"\nSources: {', '.join(result['sources'])}")
                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Try again or type 'exit' to quit.\n")


if __name__ == "__main__":
    main()

