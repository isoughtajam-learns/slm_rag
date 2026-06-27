"""
Intent classification module using a sub-1B SLM.
Routes incoming requests to appropriate handlers.
"""

import ollama
import numpy as np
from typing import Dict, Optional
from src.config import INTENT_CATEGORIES, OLLAMA_BASE_URL, IntentModel


class IntentClassifier:
    """Classifies user queries into predefined intent categories using embedding similarity."""
    
    def __init__(self, model_name: str = IntentModel.ALL_MINILM):
        """
        Initialize the intent classifier.
        
        Args:
            model_name: Name of the Ollama model to use for classification
        """
        self.model_name = model_name
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
        self.intent_categories = INTENT_CATEGORIES
        
        # Intent category descriptions for better matching
        self.intent_descriptions = {
            "documentation_query": "Questions about documentation, procedures, or how-to guides",
            "incident_analysis": "Questions about incidents, errors, or troubleshooting issues",
            "summarization": "Requests to summarize documents, reports, or content",
        }
        
        print(f"[INIT] Loading intent embeddings using {model_name}...", end="")
        # Pre-compute embeddings for all intent categories
        self.intent_embeddings = [
            self.client.embeddings(model=self.model_name, prompt=desc)["embedding"]
            for desc in self.intent_descriptions.values()
        ]
        print("done")
    
    @staticmethod
    def cosine_similarity(a, b):
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
    def classify(self, query: str) -> Dict[str, any]:
        """
        Classify a user query into an intent category using embedding similarity.
        
        Args:
            query: The user's input query
            
        Returns:
            Dict containing intent, confidence, and reasoning
        """
        try:
            # Get embedding for the query
            query_embedding = self.client.embeddings(
                model=self.model_name,
                prompt=query
            )["embedding"]
            
            # Calculate similarity scores with each intent category
            scores = [
                self.cosine_similarity(query_embedding, intent_emb)
                for intent_emb in self.intent_embeddings
            ]
            
            # Get the best matching intent
            best_idx = int(np.argmax(scores))
            intent = self.intent_categories[best_idx]
            confidence = float(scores[best_idx])
            
            # Determine if retrieval is needed
            needs_retrieval = intent in [
                "documentation_query",
                "incident_analysis",
                "summarization"
            ]
            
            return {
                "intent": intent,
                "needs_retrieval": needs_retrieval,
                "confidence": confidence,
                "all_scores": {cat: float(score) for cat, score in zip(self.intent_categories, scores)},
                "model_used": self.model_name
            }
            
        except Exception as e:
            print(f"Error during intent classification: {e}")
            # Default to general_question if classification fails
            return {
                "intent": "general_question",
                "needs_retrieval": True,
                "error": str(e),
                "model_used": self.model_name
            }


# Example usage and testing
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    test_queries = [
        "How do I configure the logging system?",
        "We're seeing error 500 on the API server",
        "Generate a command to restart the service",
        "Summarize the incident report from last week",
        "What is machine learning?"
    ]
    
    print("\nTesting Intent Classification\n" + "="*50)
    for query in test_queries:
        result = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result.get('confidence', 'N/A'):.3f}")
        print(f"Needs Retrieval: {result['needs_retrieval']}")


