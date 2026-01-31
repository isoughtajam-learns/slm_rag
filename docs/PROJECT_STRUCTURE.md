# Local RAG System - Project Structure

```
slm_rag/
│
├── 📄 main.py                      # Main orchestration pipeline
├── 📄 config.py                    # System configuration
├── 📄 intent_classifier.py         # Intent detection (350M model)
├── 📄 document_processor.py        # Document loading and chunking
├── 📄 retrieval_system.py          # Vector DB and retrieval (ChromaDB)
├── 📄 reasoning_engine.py          # Response generation (1.2B model)
├── 📄 examples.py                  # Usage examples
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 README.md                    # Complete documentation
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 📄 .gitignore                   # Git ignore rules
├── 📄 Designing a Fully Local RAG Architecture with Small Language Models.md
│
├── 📁 .venv/                       # Python virtual environment
│
└── 📁 data/
    ├── 📁 documents/               # Your documents go here
    │   └── sample_documentation.md
    └── 📁 chroma_db/               # Vector database storage

```

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: INTENT CLASSIFICATION                              │
│  Model: LFM2-350M-Math (350M parameters)                    │
│  Purpose: Classify query and determine if retrieval needed  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: DOCUMENT RETRIEVAL (if needed)                     │
│  - Generate query embedding (all-minilm)                    │
│  - Search ChromaDB vector store                             │
│  - Return top-K relevant chunks                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: REASONING & SYNTHESIS                              │
│  Model: LFM2.5-1.2B-Thinking (1.2B parameters)              │
│  Purpose: Generate response based on retrieved context      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   FINAL RESPONSE                            │
│  - Natural language answer                                  │
│  - Source references                                        │
│  - Structured output (if requested)                         │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Component Details

### 1. Intent Classifier (`intent_classifier.py`)
- **Model**: LFM2-350M-Math-GGUF (350M params)
- **Function**: Classify queries into categories
- **Categories**: 
  - `documentation_query`
  - `incident_analysis`
  - `action_request`
  - `summarization`
  - `general_question`
- **Output**: Intent + needs_retrieval flag

### 2. Document Processor (`document_processor.py`)
- **DocumentProcessor**: Loads various file formats
- **TextChunker**: Splits documents into chunks (500 chars, 50 overlap)
- **LocalEmbedder**: Generates embeddings using all-minilm
- **Supported formats**: .txt, .md, .pdf, .docx, .log, .json, .yaml

### 3. Retrieval System (`retrieval_system.py`)
- **LocalVectorStore**: ChromaDB interface
- **RetrievalSystem**: High-level retrieval pipeline
- **Features**:
  - Local persistent storage
  - Semantic search
  - Metadata filtering
  - Similarity threshold

### 4. Reasoning Engine (`reasoning_engine.py`)
- **Model**: LFM2.5-1.2B-Thinking-GGUF (1.2B params)
- **Methods**:
  - `synthesize_response()`: General Q&A
  - `analyze_incident()`: Incident analysis
  - `summarize_documents()`: Summarization
  - `generate_structured_output()`: JSON output

### 5. Main Orchestration (`main.py`)
- **LocalRAGSystem**: Main class coordinating all components
- **Modes**:
  - Interactive mode (CLI chat)
  - Single query mode
  - Batch processing
  - Document ingestion

## 📊 Data Flow

### Document Ingestion Flow
```
Documents → Load → Chunk → Embed → Store in ChromaDB
             │       │       │           │
          .pdf/.md  500char  all-minilm  Local DB
```

### Query Processing Flow
```
Query → Classify → Retrieve → Reason → Response
         │           │          │         │
      350M model   ChromaDB   1.2B model  +Sources
```

## 🔧 Configuration (`config.py`)

Key settings:
- **INTENT_MODEL**: Classification model
- **REASONING_MODEL**: Response generation model
- **EMBEDDING_MODEL**: Embedding model
- **TOP_K_RESULTS**: Number of chunks to retrieve (default: 5)
- **SIMILARITY_THRESHOLD**: Minimum similarity score (default: 0.7)

## 🚀 Usage Patterns

### 1. Initial Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ingest Documents
```bash
python main.py --ingest
```

### 3. Query System
```bash
# Interactive
python main.py

# Single query
python main.py --query "Your question here"

# System info
python main.py --info
```

### 4. Run Examples
```bash
python examples.py
```

### 5. Test Components
```bash
python intent_classifier.py
python retrieval_system.py
python reasoning_engine.py
```

## 🔒 Privacy Features

- **100% Local**: All processing on-premise
- **No API Calls**: No external services
- **Data Locality**: Documents never leave system
- **GDPR Compliant**: No data transmission
- **Auditable**: Full control over pipeline

## 📈 Performance Characteristics

### Model Sizes
- Intent: 350M params (~711 MB)
- Reasoning: 1.2B params (~2.3 GB)
- Embeddings: 22M params (~45 MB)

### Expected Latency (CPU)
- Intent classification: ~100-200ms
- Retrieval: ~50-100ms
- Response generation: ~500-2000ms
- **Total**: 1-3 seconds per query

### Hardware Requirements
- **Minimum**: 4 CPU cores, 8GB RAM
- **Recommended**: 8 CPU cores or GPU, 16GB RAM

## 🎓 Extension Points

Areas for customization:
1. **Add document types**: Extend `DocumentProcessor`
2. **Custom intents**: Modify `INTENT_CATEGORIES` in config
3. **Chunking strategy**: Adjust `TextChunker` parameters
4. **Retrieval tuning**: Modify `TOP_K_RESULTS` and `SIMILARITY_THRESHOLD`
5. **Post-processing**: Add validation or formatting layers
6. **Different models**: Replace models in config

## 📚 Dependencies

Core packages:
- `chromadb`: Local vector database
- `ollama`: LLM inference
- `sentence-transformers`: Embeddings
- `pypdf`, `python-docx`: Document parsing
- `pydantic`: Data validation
- `rich`: Terminal formatting

## 🏁 Quick Reference

### Common Commands
```bash
# Setup
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt

# Ingest
python main.py --ingest

# Query
python main.py --query "How do I configure logging?"

# Interactive
python main.py

# Examples
python examples.py
```

### Key Files to Modify
- `config.py`: Change models, parameters
- `data/documents/`: Add your documents
- `intent_classifier.py`: Customize intents
- `reasoning_engine.py`: Modify prompts

## 🎉 Ready to Use!

The system is fully functional and ready for enterprise deployment. All components are modular, testable, and designed for privacy-preserving AI assistance.
