"""
Configuration for the local RAG system.
"""
import base64
import gzip
import re
import zlib
from collections import defaultdict
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import List, TypedDict

from typing_extensions import LiteralString

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

class ModelType(StrEnum):
    REASONING = "reasoning"
    INTENT = "intent"
    EMBEDDING = "embedding"


class Model(TypedDict):
    name: str
    type: ModelType
    id: int


# Intent classification model (sub-1B for routing)
class IntentModel(StrEnum):
    ALL_MINILM = "all-minilm:latest"

# Reasoning and synthesis model (1-3B for constrained reasoning)
class ReasoningModel(StrEnum):
    LFM2_5__1_2B = "hf.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF:F16"
    GEMMA2 = "gemma2:latest"

# Embedding model for RAG
class EmbeddingModel(StrEnum):
    ALL_MINILM = "all-minilm:latest"
    SNOWFLAKE_ARCTIC = "snowflake-arctic-embed:latest"
    NOMIC = "nomic-embed-text:latest"

def configure_models() -> List[Model]:
    models = defaultdict(list)
    total = len(IntentModel) + len(ReasoningModel) + len(EmbeddingModel)
    generator = iter(range(total))
    for model_enum in (IntentModel, ReasoningModel, EmbeddingModel):
        models[model_enum.__name__] += [{
            "name": m.name,
            "type": m.__class__.__name__,
            "model_id": next(generator),
        } for m in list(model_enum)]

    return models

# Retrieval configuration
TOP_K_RESULTS = 10
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

def get_composite_model_id(model_names: List[str]) -> str:
    modified = ["_"]
    for model_name in model_names:
        modified.append(re.sub(r"[^0-9a-zA-Z_-]+", "", model_name))
    compressed = zlib.compress("_".join(modified).encode("utf-8"))
    return base64.b64encode(compressed).decode('ascii')

