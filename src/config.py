"""
Configuration for the local RAG system.
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent  # Project root directory
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
DOCUMENTS_DIR.mkdir(exist_ok=True)
CHROMA_DB_DIR.mkdir(exist_ok=True)

# Ollama model configuration
OLLAMA_BASE_URL = "http://localhost:11434"

# Intent classification model (sub-1B for routing)
INTENT_MODEL = "all-minilm:latest"

# Reasoning and synthesis model (1-3B for constrained reasoning)
REASONING_MODEL = "hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16"

# Embedding model for RAG
EMBEDDING_MODEL = "all-minilm:latest"

# Retrieval configuration
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 1.5  # ChromaDB uses L2 distance; lower=more similar, typical range 0.5-2.0

# Document chunking configuration
CHUNK_SIZE = 1500  # Characters per chunk (increased from 500)
CHUNK_OVERLAP = 200  # Overlap between chunks (increased from 50)

# Response generation configuration
MAX_RESPONSE_TOKENS = 2000  # Maximum tokens for response generation (increased from 500)
CONTEXT_WINDOW = 4096  # Context window size for the model
REASONING_TEMPERATURE = 0.3  # Temperature for reasoning (lower = more focused)

# Intent category descriptions for better matching (SINGLE SOURCE OF TRUTH)
INTENT_DESCRIPTIONS = {
    "documentation_query": "Questions about documentation, procedures, or how-to guides",
    "incident_analysis": "Questions about incidents, errors, or troubleshooting issues",
    "summarization": "Requests to summarize documents, reports, or content",
}

# System prompts
def get_intent_classification_prompt():
    """Generate intent classification prompt from INTENT_DESCRIPTIONS."""
    categories_text = "\n".join([f"- {cat}: {desc}" for cat, desc in INTENT_DESCRIPTIONS.items()])
    return f"""You are an intent classifier. Analyze the user query and classify it into ONE of these categories:
{categories_text}

User query: {{query}}

Respond with ONLY the category name, nothing else."""

INTENT_CLASSIFICATION_PROMPT = get_intent_classification_prompt()

# Intent categories derived from INTENT_DESCRIPTIONS
INTENT_CATEGORIES = list(INTENT_DESCRIPTIONS.keys())

REASONING_PROMPT = """You are an AI assistant analyzing retrieved documents to answer questions.

Context from relevant documents:
{context}

User question: {query}

Based on the retrieved context above, provide a clear, accurate answer. If the context doesn't contain enough information, say so. Do not make up information."""

STRUCTURED_OUTPUT_PROMPT = """You are an AI assistant that generates structured outputs.

Context from relevant documents:
{context}

User request: {query}

Generate a structured response in JSON format with relevant fields based on the request."""

