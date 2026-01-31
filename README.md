# Local RAG System with Small Language Models

A fully local, privacy-preserving RAG (Retrieval-Augmented Generation) system using small language models, designed for enterprise environments with strict data locality requirements.

## 🚀 Quick Start

```bash
# 1. Setup environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure Ollama models are installed
ollama pull all-minilm:latest
ollama pull hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16
ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16

# 4. Run examples (uses pre-loaded sample documents)
python run_examples.py

# OR: Ingest your own documents and query
python run.py --ingest
python run.py --query "your question here"
```

## 📁 Project Structure

```
src/
├── src/                    # Core application package
│   ├── __init__.py
│   ├── config.py               # System configuration
│   ├── intent_classifier.py    # Intent classification module
│   ├── document_processor.py   # Document loading and chunking
│   ├── retrieval_system.py     # Vector DB and retrieval
│   ├── reasoning_engine.py     # Response generation
│   └── main.py                 # Main orchestration pipeline
│
├── examples/                   # Example scripts & demos
│   └── examples.py
│
├── docs/                       # Documentation
│   ├── README.md              # Full documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── PROJECT_STRUCTURE.md
│
├── scripts/                    # Utility & diagnostic scripts
│   ├── diagnose.py
│   ├── verify_system.py
│   └── architecture.py
│
├── data/                       # Data storage
│   ├── chroma_db/             # Vector database storage
│   └── documents/             # Place your documents here
│       ├── nuclear_plant_cyber_security.md    (sample)
│       └── nuclear_plant_physical_security.md (sample)
│
├── run.py                      # Main entry point
├── run_examples.py             # Examples entry point
├── requirements.txt            # Python dependencies
└── .venv/                      # Virtual environment
```

## 🎯 Usage

### Run the System

**Interactive Mode:**
```bash
python run.py
```

**Single Query:**
```bash
python run.py --query "What are the key security measures?"
```

**Ingest Documents:**
```bash
python run.py --ingest
```

**Show System Info:**
```bash
python run.py --info
```

**Advanced Options:**
```bash
python run.py --query "your question" --show-chunks --show-thinking
```

### Run Examples

**All examples:**
```bash
python run_examples.py
```

**Specific example:**
```bash
python run_examples.py 1  # Documentation query
python run_examples.py 2  # Incident analysis
python run_examples.py 6  # System info
```

### Run Scripts

**System diagnostics:**
```bash
python scripts/diagnose.py
```

**Verify installation:**
```bash
python scripts/verify_system.py
```

**Show architecture:**
```bash
python scripts/architecture.py
```

## 📚 Documentation

- **[Full Documentation](docs/README.md)** - Complete guide with all features
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Architecture overview

## 🎯 Key Features

- **100% Local** - All processing happens on-premise, no data leaves your system
- **Small Language Models** - Uses sub-1B and 1-3B models for efficient, focused tasks
- **Privacy-First** - Designed for GDPR compliance and enterprise data protection
- **Modular Architecture** - Separate components for intent classification, retrieval, and reasoning
- **Local Vector Database** - ChromaDB for document storage and retrieval

## 🏗️ Architecture

The system consists of three main components:

1. **Intent Classification** (LFM2-350M-Math, 350M parameters)
   - Classifies incoming requests
   - Determines if retrieval is needed
   - Routes to appropriate handlers

2. **Local Retrieval Layer** (ChromaDB + all-minilm)
   - Embeds and indexes private documents
   - Performs semantic search
   - Returns relevant context

3. **Reasoning & Synthesis** (LFM2.5-1.2B-Thinking, 1.2B parameters)
   - Analyzes retrieved context
   - Generates responses
   - Produces structured outputs

## 📋 Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Required Ollama models (see Quick Start)

## 🔒 Privacy & Security

- **No external API calls** - All processing happens locally
- **Data never leaves the system** - Documents stay on your infrastructure
- **GDPR compliant** - No data sent to third parties
- **Auditable** - Full control over models and data flow
- **Enterprise-ready** - Designed for regulated environments

## 📄 License

This is a reference implementation for educational and enterprise use.

## 🎓 Credits

Based on the architecture described in "Designing a Fully Local RAG Architecture with Small Language Models".

Models used:
- [LiquidAI LFM Models](https://huggingface.co/LiquidAI)
- [all-minilm](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) by Sentence Transformers

