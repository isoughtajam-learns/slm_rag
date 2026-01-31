# Local RAG System with Small Language Models

A fully local, privacy-preserving RAG (Retrieval-Augmented Generation) system using small language models, designed for enterprise environments with strict data locality requirements.

## Overview

This system implements the architecture described in "Designing a Fully Local RAG Architecture with Small Language Models". It provides AI assistance for internal workflows without sending any data to external services.

### Key Features

- **100% Local**: All processing happens on-premise, no data leaves your system
- **Small Language Models**: Uses sub-1B and 1-3B models for efficient, focused tasks
- **Privacy-First**: Designed for GDPR compliance and enterprise data protection
- **Modular Architecture**: Separate components for intent classification, retrieval, and reasoning
- **Local Vector Database**: ChromaDB for document storage and retrieval

## Architecture

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

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Required Ollama models (see Installation)

## Quick Start Guide

**Complete workflow from setup to running queries:**

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

## Detailed Setup Instructions

### Complete Setup in 4 Steps

#### Step 1: Clone or download this repository

```bash
cd slm_rag
```

#### Step 2: Create and activate virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Verify Ollama models

Ensure these models are available in Ollama:

```bash
ollama list
```

Required models:
- `hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16` (Intent classification)
- `hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16` (Reasoning)
- `all-minilm:latest` (Embeddings)

If any are missing, pull them:

```bash
ollama pull all-minilm:latest
ollama pull hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16
ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16
```

### Quick Test - Run Examples

After installation, test the system with pre-built examples:

```bash
python run_examples.py
```

This will run all example queries and demonstrate the system's capabilities.

## Project Structure

```
src/
├── config.py                 # System configuration
├── intent_classifier.py      # Intent classification module
├── document_processor.py     # Document loading and chunking
├── retrieval_system.py       # Vector DB and retrieval
├── reasoning_engine.py       # Response generation
├── main.py                   # Main orchestration pipeline
├── requirements.txt          # Python dependencies
├── data/
│   ├── documents/           # Place your documents here
│   └── chroma_db/           # Vector database storage
└── README.md
```

## Usage Guide

### Option 1: Run Examples (Quickest Way to Test)

Run all built-in examples to see the system in action:

```bash
python run_examples.py
```

Or run specific examples individually:

```bash
python run_examples.py 1  # Documentation query
python run_examples.py 2  # Incident analysis
python run_examples.py 3  # Document summarization
python run_examples.py 4  # Action request
python run_examples.py 5  # Batch queries
python run_examples.py 6  # System information
python run_examples.py 7  # Custom document ingestion
```

The examples demonstrate various use cases with the included sample documents.

### Option 2: Use Your Own Documents

**Note:** The system includes **2 sample documents** in `data/documents/`:
- `nuclear_plant_cyber_security.md` - Cyber security measures and protocols
- `nuclear_plant_physical_security.md` - Physical security requirements

These documents are ready to use and demonstrate the system's capabilities. You can query them immediately or add your own documents.

#### Step 1: Add Your Documents

Place your documents in the `data/documents/` directory:

```
data/documents/
├── nuclear_plant_cyber_security.md      # (included sample)
├── nuclear_plant_physical_security.md   # (included sample)
├── procedures.md                        # (your documents)
├── incident_reports.pdf
├── configuration_guide.docx
└── logs/
    └── system.log
```

**Supported formats:**
- Text files: `.txt`, `.md`, `.log`, `.json`, `.yaml`
- PDF documents: `.pdf`
- Word documents: `.docx`

#### Step 2: Ingest Documents

Process and index your documents:

```bash
python run.py --ingest
```

This command will:
- Load all documents from `data/documents/`
- Split them into chunks (500 chars each, 50 char overlap)
- Generate embeddings using `all-minilm`
- Store in local ChromaDB at `data/chroma_db/`

**Expected output:**
```
Processing documents from: data\documents\
Ingesting documents...
Loaded 2 documents
Created 847 chunks
Ingestion complete: 847 chunks indexed
```

### Option 3: Query the System

#### A. Interactive Mode (Conversational)

Start an interactive session:

```bash
python run.py
```

Then enter your queries:

```
System initialized. Type 'info' for stats, 'exit' to quit.

You: How do I configure the logging system?
Assistant: To configure logging, edit the config.yaml file...

Sources: logging_guide.md, operations_manual.md
```

**Special commands:**
- Type `info` - Show system statistics (document count, models, etc.)
- Type `exit` - Quit the interactive session

#### B. Single Query Mode (Command Line)

Execute a single query and exit:

```bash
python run.py --query "What causes error 500 in the API?"
```

**Common command line queries:**

```bash
# Documentation lookup
python run.py --query "How do I restart the application?"

# Incident analysis
python run.py --query "Why is the database connection failing?"

# Summarization
python run.py --query "Summarize the security policies"

# Action request
python run.py --query "Generate a JSON config for production"
```

#### C. Advanced Query Options

**Show retrieved document chunks:**
```bash
python run.py --query "your question here" --show-chunks
```

**Show AI reasoning process:**
```bash
python run.py --query "your question here" --show-thinking
```

**Combine both:**
```bash
python run.py --query "your question here" --show-chunks --show-thinking
```

#### D. Get System Information

Display system status and configuration:

```bash
python run.py --info
```

**Output includes:**
- Document count and storage path
- Active models and their sizes
- Configuration settings
- Privacy status

## Running Examples

The system includes 7 built-in examples demonstrating different capabilities:

### Run All Examples

```bash
python run_examples.py
```

This runs all examples in sequence, demonstrating the full system capabilities.

### Run Individual Examples

**Example 1: Documentation Query**
```bash
python run_examples.py 1
```
Demonstrates querying documentation for cyber security measures.

**Example 2: Incident Analysis**
```bash
python run_examples.py 2
```
Shows how to analyze security incidents and get response procedures.

**Example 3: Document Summarization**
```bash
python run_examples.py 3
```
Summarizes physical security measures from multiple documents.

**Example 4: Action Request**
```bash
python run_examples.py 4
```
Generates structured lists of security requirements.

**Example 5: Batch Query Processing**
```bash
python run_examples.py 5
```
Processes multiple queries efficiently in sequence.

**Example 6: System Information**
```bash
python run_examples.py 6
```
Displays detailed system configuration and statistics.

**Example 7: Custom Document Ingestion**
```bash
python run_examples.py 7
```
Creates and ingests a sample document, then queries it.

### What Each Example Demonstrates

| Example | Use Case | Intent Type | Key Features |
|---------|----------|-------------|--------------|
| 1 | Documentation Query | `documentation_query` | Semantic search, context retrieval |
| 2 | Incident Analysis | `incident_analysis` | Problem-solving, procedural guidance |
| 3 | Summarization | `summarization` | Multi-document synthesis |
| 4 | Action Request | `action_request` | Structured output generation |
| 5 | Batch Processing | Mixed | Efficient multi-query handling |
| 6 | System Info | N/A | Configuration and statistics |
| 7 | Custom Ingestion | N/A | Document processing pipeline |

### Example Output

When you run `python run_examples.py 1`, you'll see:

```
======================================================================
EXAMPLE 1: DOCUMENTATION QUERY
======================================================================

Intent: documentation_query (confidence: 0.95)
Retrieved 5 relevant chunks

Response:
The main cyber security measures for nuclear plant control systems include:
1. Network segmentation and isolation
2. Multi-factor authentication
3. Continuous monitoring and intrusion detection
...

Sources: nuclear_plant_cyber_security.md
```

## Intent Categories

The system automatically classifies queries into these categories:

- **documentation_query**: Questions about docs, procedures, guides
- **incident_analysis**: Troubleshooting, errors, incidents
- **action_request**: Generate commands or structured outputs
- **summarization**: Summarize documents or reports
- **general_question**: Other questions

## Configuration

Edit `src/config.py` to customize:

```python
# Models
INTENT_MODEL = "hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16"
REASONING_MODEL = "hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16"
EMBEDDING_MODEL = "all-minilm:latest"

# Retrieval
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# Chunking
# Edit in document_processor.py
chunk_size = 500
chunk_overlap = 50
```

## Example Use Cases

### Documentation Queries

```
Query: "How do I restart the application?"
→ Searches documentation, returns step-by-step guide
```

### Incident Analysis

```
Query: "Database connection timeout errors"
→ Analyzes logs, suggests causes and fixes
```

### Summarization

```
Query: "Summarize last week's incident reports"
→ Retrieves and summarizes relevant reports
```

### Structured Outputs

```
Query: "Generate a JSON config for production deployment"
→ Returns structured JSON based on documentation
```

## Privacy & Security

- **No external API calls**: All processing happens locally
- **Data never leaves the system**: Documents stay on your infrastructure
- **GDPR compliant**: No data sent to third parties
- **Auditable**: Full control over models and data flow
- **Enterprise-ready**: Designed for regulated environments

## Performance

### Hardware Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 8 GB
- Storage: 10 GB

**Recommended**:
- CPU: 8 cores or GPU
- RAM: 16 GB
- Storage: 50 GB

### Latency

- Intent classification: ~100-200ms
- Document retrieval: ~50-100ms
- Response generation: ~500-2000ms

Total per query: 1-3 seconds (varies with response length)

## Troubleshooting

### "No documents in system"

Add documents to `data/documents/` and run:
```bash
python run.py --ingest
```

### "Connection refused to Ollama"

Ensure Ollama is running:
```bash
# Check if running
curl http://localhost:11434

# Start Ollama
ollama serve
```

### "Model not found"

Pull the required model:
```bash
ollama pull all-minilm:latest
```

### Slow performance

- Use a GPU if available
- Reduce `TOP_K_RESULTS` in config.py
- Reduce `chunk_size` for faster retrieval

## Testing Individual Components

Each module can be tested independently:

```bash
# Test intent classification
python -m slm_rag.intent_classifier

# Test document processing
python -m slm_rag.document_processor

# Test retrieval system
python -m slm_rag.retrieval_system

# Test reasoning engine
python -m slm_rag.reasoning_engine
```

## Further Reading

See the included article: [Designing a Fully Local RAG Architecture with Small Language Models.md](Designing%20a%20Fully%20Local%20RAG%20Architecture%20with%20Small%20Language%20Models.md)

## Contributing

This is an implementation of the architecture described in the article. Feel free to:
- Add support for more document types
- Implement additional intent categories
- Optimize chunking strategies
- Add post-processing modules

## License

This is a reference implementation for educational and enterprise use.

## Credits

Based on the architecture described in "Designing a Fully Local RAG Architecture with Small Language Models".

Models used:
- [LiquidAI LFM Models](https://huggingface.co/LiquidAI)
- [all-minilm](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) by Sentence TransformersLocal RAG System with Small Language Models

A fully local, privacy-preserving RAG (Retrieval-Augmented Generation) system using small language models, designed for enterprise environments with strict data locality requirements.

## 🎯 Overview

This system implements the architecture described in "Designing a Fully Local RAG Architecture with Small Language Models". It provides AI assistance for internal workflows without sending any data to external services.

### Key Features

- **100% Local**: All processing happens on-premise, no data leaves your system
- **Small Language Models**: Uses sub-1B and 1-3B models for efficient, focused tasks
- **Privacy-First**: Designed for GDPR compliance and enterprise data protection
- **Modular Architecture**: Separate components for intent classification, retrieval, and reasoning
- **Local Vector Database**: ChromaDB for document storage and retrieval

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
- Required Ollama models (see Installation)

## ⚡ Quick Start Guide

**Complete workflow from setup to running queries:**

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

## 🚀 Detailed Setup Instructions

### Complete Setup in 4 Steps

#### Step 1: Clone or download this repository

```bash
cd slm_rag
```

#### Step 2: Create and activate virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Verify Ollama models

Ensure these models are available in Ollama:

```bash
ollama list
```

Required models:
- `hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16` (Intent classification)
- `hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16` (Reasoning)
- `all-minilm:latest` (Embeddings)

If any are missing, pull them:

```bash
ollama pull all-minilm:latest
ollama pull hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16
ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16
```

### Quick Test - Run Examples

After installation, test the system with pre-built examples:

```bash
python run_examples.py
```

This will run all example queries and demonstrate the system's capabilities.

## 📁 Project Structure

```
src/
├── config.py                 # System configuration
├── intent_classifier.py      # Intent classification module
├── document_processor.py     # Document loading and chunking
├── retrieval_system.py       # Vector DB and retrieval
├── reasoning_engine.py       # Response generation
├── main.py                   # Main orchestration pipeline
├── requirements.txt          # Python dependencies
├── data/
│   ├── documents/           # Place your documents here
│   └── chroma_db/           # Vector database storage
└── README.md
```

## 📚 Usage Guide

### Option 1: Run Examples (Quickest Way to Test)

Run all built-in examples to see the system in action:

```bash
python run_examples.py
```

Or run specific examples individually:

```bash
python run_examples.py 1  # Documentation query
python run_examples.py 2  # Incident analysis
python run_examples.py 3  # Document summarization
python run_examples.py 4  # Action request
python run_examples.py 5  # Batch queries
python run_examples.py 6  # System information
python run_examples.py 7  # Custom document ingestion
```

The examples demonstrate various use cases with the included sample documents.

### Option 2: Use Your Own Documents

#### Step 1: Add Your Documents

Place your documents in the `data/documents/` directory:

```
data/documents/
├── procedures.md
├── incident_reports.pdf
├── configuration_guide.docx
└── logs/
    └── system.log
```

**Supported formats:**
- Text files: `.txt`, `.md`, `.log`, `.json`, `.yaml`
- PDF documents: `.pdf`
- Word documents: `.docx`

#### Step 2: Ingest Documents

Process and index your documents:

```bash
python run.py --ingest
```

This command will:
- 📄 Load all documents from `data/documents/`
- ✂️ Split them into chunks (500 chars each, 50 char overlap)
- 🧮 Generate embeddings using `all-minilm`
- 💾 Store in local ChromaDB at `data/chroma_db/`

**Expected output:**
```
Processing documents from: data\documents\
Ingesting documents...
Loaded 2 documents
Created 847 chunks
Ingestion complete: 847 chunks indexed
```

### Option 3: Query the System

#### A. Interactive Mode (Conversational)

Start an interactive session:

```bash
python run.py
```

Then enter your queries:

```
System initialized. Type 'info' for stats, 'exit' to quit.

You: How do I configure the logging system?
Assistant: To configure logging, edit the config.yaml file...

Sources: logging_guide.md, operations_manual.md
```

**Special commands:**
- Type `info` - Show system statistics (document count, models, etc.)
- Type `exit` - Quit the interactive session

#### B. Single Query Mode (Command Line)

Execute a single query and exit:

```bash
python run.py --query "What causes error 500 in the API?"
```

**Common command line queries:**

```bash
# Documentation lookup
python run.py --query "How do I restart the application?"

# Incident analysis
python run.py --query "Why is the database connection failing?"

# Summarization
python run.py --query "Summarize the security policies"

# Action request
python run.py --query "Generate a JSON config for production"
```

#### C. Advanced Query Options

**Show retrieved document chunks:**
```bash
python run.py --query "your question here" --show-chunks
```

**Show AI reasoning process:**
```bash
python run.py --query "your question here" --show-thinking
```

**Combine both:**
```bash
python run.py --query "your question here" --show-chunks --show-thinking
```

#### D. Get System Information

Display system status and configuration:

```bash
python run.py --info
```

**Output includes:**
- Document count and storage path
- Active models and their sizes
- Configuration settings
- Privacy status

- Privacy status

## 🎯 Running Examples

The system includes 7 built-in examples demonstrating different capabilities:

### Run All Examples

```bash
python run_examples.py
```

This runs all examples in sequence, demonstrating the full system capabilities.

### Run Individual Examples

**Example 1: Documentation Query**
```bash
python run_examples.py 1
```
Demonstrates querying documentation for cyber security measures.

**Example 2: Incident Analysis**
```bash
python run_examples.py 2
```
Shows how to analyze security incidents and get response procedures.

**Example 3: Document Summarization**
```bash
python run_examples.py 3
```
Summarizes physical security measures from multiple documents.

**Example 4: Action Request**
```bash
python run_examples.py 4
```
Generates structured lists of security requirements.

**Example 5: Batch Query Processing**
```bash
python run_examples.py 5
```
Processes multiple queries efficiently in sequence.

**Example 6: System Information**
```bash
python run_examples.py 6
```
Displays detailed system configuration and statistics.

**Example 7: Custom Document Ingestion**
```bash
python run_examples.py 7
```
Creates and ingests a sample document, then queries it.

### What Each Example Demonstrates

| Example | Use Case | Intent Type | Key Features |
|---------|----------|-------------|--------------|
| 1 | Documentation Query | `documentation_query` | Semantic search, context retrieval |
| 2 | Incident Analysis | `incident_analysis` | Problem-solving, procedural guidance |
| 3 | Summarization | `summarization` | Multi-document synthesis |
| 4 | Action Request | `action_request` | Structured output generation |
| 5 | Batch Processing | Mixed | Efficient multi-query handling |
| 6 | System Info | N/A | Configuration and statistics |
| 7 | Custom Ingestion | N/A | Document processing pipeline |

### Example Output

When you run `python run_examples.py 1`, you'll see:

```
======================================================================
EXAMPLE 1: DOCUMENTATION QUERY
======================================================================

Intent: documentation_query (confidence: 0.95)
Retrieved 5 relevant chunks

Response:
The main cyber security measures for nuclear plant control systems include:
1. Network segmentation and isolation
2. Multi-factor authentication
3. Continuous monitoring and intrusion detection
...

Sources: nuclear_plant_cyber_security.md
```

## 🎭 Intent Categories

The system automatically classifies queries into these categories:

- **documentation_query**: Questions about docs, procedures, guides
- **incident_analysis**: Troubleshooting, errors, incidents
- **action_request**: Generate commands or structured outputs
- **summarization**: Summarize documents or reports
- **general_question**: Other questions

## 🔧 Configuration

Edit `src/config.py` to customize:

```python
# Models
INTENT_MODEL = "hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16"
REASONING_MODEL = "hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16"
EMBEDDING_MODEL = "all-minilm:latest"

# Retrieval
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# Chunking
# Edit in document_processor.py
chunk_size = 500
chunk_overlap = 50
```

## 💡 Example Use Cases

### Documentation Queries

```
Query: "How do I restart the application?"
→ Searches documentation, returns step-by-step guide
```

### Incident Analysis

```
Query: "Database connection timeout errors"
→ Analyzes logs, suggests causes and fixes
```

### Summarization

```
Query: "Summarize last week's incident reports"
→ Retrieves and summarizes relevant reports
```

### Structured Outputs

```
Query: "Generate a JSON config for production deployment"
→ Returns structured JSON based on documentation
```

## 🔒 Privacy & Security

- **No external API calls**: All processing happens locally
- **Data never leaves the system**: Documents stay on your infrastructure
- **GDPR compliant**: No data sent to third parties
- **Auditable**: Full control over models and data flow
- **Enterprise-ready**: Designed for regulated environments

## 🎯 Performance

### Hardware Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 8 GB
- Storage: 10 GB

**Recommended**:
- CPU: 8 cores or GPU
- RAM: 16 GB
- Storage: 50 GB

### Latency

- Intent classification: ~100-200ms
- Document retrieval: ~50-100ms
- Response generation: ~500-2000ms

Total per query: 1-3 seconds (varies with response length)

## 🐛 Troubleshooting

### "No documents in system"

Add documents to `data/documents/` and run:
```bash
python run.py --ingest
```

### "Connection refused to Ollama"

Ensure Ollama is running:
```bash
# Check if running
curl http://localhost:11434

# Start Ollama
ollama serve
```

### "Model not found"

Pull the required model:
```bash
ollama pull all-minilm:latest
```

### Slow performance

- Use a GPU if available
- Reduce `TOP_K_RESULTS` in config.py
- Reduce `chunk_size` for faster retrieval

## 🔬 Testing Individual Components

Each module can be tested independently:

```bash
# Test intent classification
python -m slm_rag.intent_classifier

# Test document processing
python -m slm_rag.document_processor

# Test retrieval system
python -m slm_rag.retrieval_system

# Test reasoning engine
python -m slm_rag.reasoning_engine
```

## 📖 Further Reading

See the included article: [Designing a Fully Local RAG Architecture with Small Language Models.md](Designing%20a%20Fully%20Local%20RAG%20Architecture%20with%20Small%20Language%20Models.md)

## 🤝 Contributing

This is an implementation of the architecture described in the article. Feel free to:
- Add support for more document types
- Implement additional intent categories
- Optimize chunking strategies
- Add post-processing modules

## 📄 License

This is a reference implementation for educational and enterprise use.

## 🎓 Credits

Based on the architecture described in "Designing a Fully Local RAG Architecture with Small Language Models".

Models used:
- [LiquidAI LFM Models](https://huggingface.co/LiquidAI)
- [all-minilm](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) by Sentence Transformers



