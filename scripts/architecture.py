"""
ASCII Art visualization of the Local RAG System architecture.
"""

SYSTEM_ARCHITECTURE = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                     LOCAL RAG SYSTEM ARCHITECTURE                         ║
║                    (Privacy-Preserving AI Assistant)                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

                              ┌─────────────┐
                              │ USER QUERY  │
                              └──────┬──────┘
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │         STEP 1: INTENT CLASSIFICATION                  │
        │  ┌──────────────────────────────────────────────────┐  │
        │  │ Model: LFM2-350M-Math (350M params, ~711 MB)     │  │
        │  │ Purpose: Route query to appropriate handler      │  │
        │  └──────────────────────────────────────────────────┘  │
        │  Output: intent + needs_retrieval                      │
        └─────────────────────┬──────────────────────────────────┘
                              │
                 ┌────────────┴───────────┐
                 │                        │
          needs_retrieval=True    needs_retrieval=False
                 │                        │
                 ▼                        │
        ┌────────────────────────────────┐│
        │  STEP 2: DOCUMENT RETRIEVAL    ││
        │  ┌──────────────────────────┐  ││
        │  │ Embedding Model:         │  ││
        │  │ all-minilm (22M, ~45MB) │  ││
        │  ├──────────────────────────┤  ││
        │  │ Vector Database:         │  ││
        │  │ ChromaDB (local/persist) │  ││
        │  └──────────────────────────┘  ││
        │  Output: Top-K relevant chunks  ││
        └────────────────┬───────────────┘│
                         │                │
                         └────────┬───────┘
                                  │
                                  ▼
        ┌────────────────────────────────────────────────────────┐
        │         STEP 3: REASONING & SYNTHESIS                  │
        │  ┌──────────────────────────────────────────────────┐  │
        │  │ Model: LFM2.5-1.2B-Thinking (1.2B, ~2.3 GB)     │  │
        │  │ Purpose: Generate response from context          │  │
        │  └──────────────────────────────────────────────────┘  │
        │  Intent-specific processing:                           │
        │   • documentation_query → Q&A response                 │
        │   • incident_analysis → Root cause analysis            │
        │   • summarization → Document summary                   │
        │   • action_request → Structured output (JSON)          │
        └─────────────────────┬──────────────────────────────────┘
                              │
                              ▼
                   ┌────────────────────┐
                   │  FINAL RESPONSE    │
                   │  + Source Refs     │
                   └────────────────────┘

═══════════════════════════════════════════════════════════════════════════

                           DATA FLOW - INGESTION

    ┌─────────────┐
    │ Documents   │ (.txt, .md, .pdf, .docx, .log, .json, .yaml)
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │ Load & Parse    │ (DocumentProcessor)
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │ Chunk Text      │ (500 chars, 50 overlap)
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │ Generate        │ (all-minilm embeddings)
    │ Embeddings      │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │ Store in        │ (ChromaDB - Local Persistent)
    │ Vector DB       │
    └─────────────────┘

═══════════════════════════════════════════════════════════════════════════

                          PRIVACY & SECURITY

    ┌───────────────────────────────────────────────────────────┐
    │                                                           │
    │  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
    │  ┃        YOUR LOCAL INFRASTRUCTURE                 ┃  │
    │  ┃                                                   ┃  │
    │  ┃  ┌─────────────┐  ┌──────────────┐  ┌─────────┐ ┃  │
    │  ┃  │ Documents   │  │ Vector DB    │  │ Models  │ ┃  │
    │  ┃  └─────────────┘  └──────────────┘  └─────────┘ ┃  │
    │  ┃         │                 │                │     ┃  │
    │  ┃         └─────────────────┴────────────────┘     ┃  │
    │  ┃                        │                         ┃  │
    │  ┃                 ┌──────▼──────┐                  ┃  │
    │  ┃                 │  RAG System │                  ┃  │
    │  ┃                 └─────────────┘                  ┃  │
    │  ┃                                                   ┃  │
    │  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
    │                                                           │
    │  ✓ No external API calls                                 │
    │  ✓ Data never leaves your infrastructure                 │
    │  ✓ GDPR compliant by design                              │
    │  ✓ Full audit trail                                      │
    │                                                           │
    └───────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════

                          COMPONENTS OVERVIEW

┌──────────────────────┬─────────────────┬────────────────────────────┐
│ Component            │ Model/Tech      │ Purpose                    │
├──────────────────────┼─────────────────┼────────────────────────────┤
│ Intent Classifier    │ LFM2-350M      │ Route queries              │
│ Embedding Generator  │ all-minilm     │ Create vectors             │
│ Vector Store         │ ChromaDB       │ Store & search docs        │
│ Reasoning Engine     │ LFM2.5-1.2B    │ Generate responses         │
│ Document Processor   │ pypdf, docx    │ Load various formats       │
│ Orchestrator         │ Python         │ Coordinate pipeline        │
└──────────────────────┴─────────────────┴────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════

                        PERFORMANCE METRICS

┌─────────────────────────┬──────────────┬────────────────────────────┐
│ Operation               │ Latency      │ Notes                      │
├─────────────────────────┼──────────────┼────────────────────────────┤
│ Intent Classification   │ ~100-200ms   │ 350M model                 │
│ Document Retrieval      │ ~50-100ms    │ ChromaDB search            │
│ Response Generation     │ ~500-2000ms  │ 1.2B model (varies)        │
│ Total Query Time        │ ~1-3 seconds │ End-to-end                 │
├─────────────────────────┼──────────────┼────────────────────────────┤
│ Document Ingestion      │ ~1-2 sec/doc │ Includes embedding         │
└─────────────────────────┴──────────────┴────────────────────────────┘

Hardware: 
  • Minimum: 4 CPU cores, 8GB RAM
  • Recommended: 8 CPU cores or GPU, 16GB RAM

═══════════════════════════════════════════════════════════════════════════
"""

def print_architecture():
    """Print the system architecture."""
    print(SYSTEM_ARCHITECTURE)

if __name__ == "__main__":
    print_architecture()

