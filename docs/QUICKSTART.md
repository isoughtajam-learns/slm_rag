# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Verify Ollama is Running

```powershell
# Check if Ollama is running
ollama list
```

You should see these models:
- `hf.co/LiquidAI/LFM2-350M-Math-GGUF:F16`
- `hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16`
- `all-minilm:latest`

### 2. Activate Virtual Environment

```powershell
.venv\Scripts\activate
```

### 3. Ingest Sample Documents

The system comes with sample documentation. Ingest it:

```powershell
python run.py --ingest
```

Expected output:
```
Loading documents from data\documents
Loaded 1 documents
Created X chunks
Generating embeddings...
✓ Ingestion complete
```

### 4. Try a Query

```powershell
python run.py --query "How do I configure logging?"
```

### 5. Interactive Mode

For a conversational experience:

```powershell
python run.py
```

Then type your questions:
```
You: What are the daily maintenance tasks?
Assistant: The daily maintenance tasks include...

You: How do I troubleshoot error 500?
Assistant: Error 500 (Internal Server Error) can be caused by...

You: exit
```

## 📚 Add Your Own Documents

1. Place your documents in `data/documents/`:

```
data/documents/
├── your_runbook.md
├── incident_report.pdf
├── config_guide.docx
└── ...
```

2. Re-ingest:

```powershell
python run.py --ingest
```

## 🎯 Example Queries

Try these queries to see the system in action:

### Documentation Queries
```
- "How do I configure the database?"
- "What is the recommended backup strategy?"
- "How do I set up logging?"
```

### Incident Analysis
```
- "We're seeing error 500, what could cause this?"
- "Database connection timeouts"
- "How to troubleshoot slow performance?"
```

### Summarization
```
- "Summarize the maintenance procedures"
- "What are the key troubleshooting steps?"
```

### Action Requests
```
- "Generate a backup configuration"
- "Create a JSON config for logging"
```

## 🔧 Verify Installation

Check system info:

```powershell
python run.py --info
```

Should show:
- Models configured
- Number of documents
- Storage location

## 📊 Run Examples

See complete examples:

```powershell
python run_examples.py
```

Or run specific examples:

```powershell
python run_examples.py 1  # Documentation query
python run_examples.py 2  # Incident analysis
python run_examples.py 6  # System info
```

## ⚠️ Troubleshooting

### "Connection refused to Ollama"

Start Ollama:
```powershell
ollama serve
```

### "No documents in system"

Add documents and ingest:
```powershell
# Add files to data/documents/
python run.py --ingest
```

### "Model not found"

Verify models are available:
```powershell
ollama list
```

If missing, pull them:
```powershell
ollama pull all-minilm:latest
```

## 🎓 Next Steps

1. **Add your documents**: Copy your internal docs to `data/documents/`
2. **Customize models**: Edit `src/config.py` to use different models
3. **Adjust retrieval**: Tune `TOP_K_RESULTS` and `SIMILARITY_THRESHOLD`
4. **Test components**: Run individual module tests

```powershell
python scripts/diagnose.py
python scripts/verify_system.py
python scripts/architecture.py
```

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.

## 🎉 You're Ready!

Your fully local RAG system is now running. All processing happens on your machine - no data leaves your system!

