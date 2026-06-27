"""
Reasoning and synthesis module using a 1-3B SLM.
Performs constrained reasoning over retrieved context.
"""

import ollama
from typing import List, Dict, Optional
import json

from src.config import (
    REASONING_PROMPT,
    STRUCTURED_OUTPUT_PROMPT,
    OLLAMA_BASE_URL,
    MAX_RESPONSE_TOKENS,
    CONTEXT_WINDOW,
    REASONING_TEMPERATURE,
    ReasoningModel,
)


class ReasoningEngine:
    """Performs reasoning and synthesis using a small language model."""
    
    def __init__(self, model_name: str = ReasoningModel.LFM2_5__1_2B):
        """
        Initialize the reasoning engine.
        
        Args:
            model_name: Name of the Ollama model to use for reasoning
        """
        self.model_name = model_name
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
    
    def _filter_thinking(self, text: str, show_thinking: bool = False) -> str:
        """
        Filter out <think></think> tags from the response.
        
        Args:
            text: The response text
            show_thinking: Whether to keep the thinking section
            
        Returns:
            Filtered text
        """
        if show_thinking:
            return text
        
        # Remove <think>...</think> sections
        import re
        filtered = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return filtered.strip()
    
    def synthesize_response(
        self,
        query: str,
        retrieved_docs: List[Dict[str, any]],
        temperature: float = REASONING_TEMPERATURE,
        max_tokens: int = MAX_RESPONSE_TOKENS,
        show_thinking: bool = False
    ) -> Dict[str, any]:
        """
        Synthesize a response based on retrieved documents.
        
        Args:
            query: User's query
            retrieved_docs: List of retrieved document chunks
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            show_thinking: Whether to show the <think></think> reasoning section
            
        Returns:
            Dict with response and metadata
        """
        # Format context from retrieved documents
        context = self._format_context(retrieved_docs)
        
        # Build prompt
        prompt = REASONING_PROMPT.format(
            context=context,
            query=query
        )
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": CONTEXT_WINDOW,
                }
            )
            
            response_text = self._filter_thinking(response['response'].strip(), show_thinking)
            
            return {
                "response": response_text,
                "model_used": self.model_name,
                "context_chunks": len(retrieved_docs),
                "sources": self._extract_sources(retrieved_docs)
            }
            
        except Exception as e:
            print(f"Error during reasoning: {e}")
            return {
                "response": f"Error generating response: {str(e)}",
                "error": str(e),
                "model_used": self.model_name
            }
    
    def generate_structured_output(
        self,
        query: str,
        retrieved_docs: List[Dict[str, any]],
        output_schema: Optional[Dict] = None,
        show_thinking: bool = False
    ) -> Dict[str, any]:
        """
        Generate structured output (e.g., JSON) based on retrieved documents.
        
        Args:
            query: User's query/request
            retrieved_docs: List of retrieved document chunks
            output_schema: Optional JSON schema for output validation
            
        Returns:
            Dict with structured output
        """
        context = self._format_context(retrieved_docs)
        
        prompt = STRUCTURED_OUTPUT_PROMPT.format(
            context=context,
            query=query
        )
        
        if output_schema:
            prompt += f"\n\nOutput schema:\n{json.dumps(output_schema, indent=2)}"
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.1,  # Low temp for structured output
                    "num_predict": 1200,
                    "num_ctx": CONTEXT_WINDOW,
                },
                format="json"  # Request JSON output
            )
            
            # Try to parse JSON response
            try:
                structured_data = json.loads(response['response'])
            except json.JSONDecodeError:
                structured_data = {"raw_output": response['response']}
            
            return {
                "structured_output": structured_data,
                "model_used": self.model_name,
                "sources": self._extract_sources(retrieved_docs)
            }
            
        except Exception as e:
            print(f"Error generating structured output: {e}")
            return {
                "error": str(e),
                "model_used": self.model_name
            }
    
    def summarize_documents(
        self,
        documents: List[Dict[str, any]],
        max_length: int = 300,
        show_thinking: bool = False
    ) -> Dict[str, any]:
        """
        Summarize a set of documents.
        
        Args:
            documents: List of document chunks to summarize
            max_length: Maximum length of summary
            show_thinking: Whether to show the <think></think> reasoning section
            
        Returns:
            Dict with summary and metadata
        """
        context = self._format_context(documents)
        
        prompt = f"""Provide a concise summary of the following documents:

{context}

Summary:"""
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.3,
                    "num_predict": max_length,
                    "num_ctx": CONTEXT_WINDOW,
                }
            )
            
            summary_text = self._filter_thinking(response['response'].strip(), show_thinking)
            
            return {
                "summary": summary_text,
                "model_used": self.model_name,
                "documents_summarized": len(documents),
                "sources": self._extract_sources(documents)
            }
            
        except Exception as e:
            print(f"Error summarizing documents: {e}")
            return {
                "error": str(e),
                "model_used": self.model_name
            }
    
    def analyze_incident(
        self,
        query: str,
        retrieved_docs: List[Dict[str, any]],
        show_thinking: bool = False
    ) -> Dict[str, any]:
        """
        Analyze an incident based on retrieved documentation and logs.
        
        Args:
            query: Incident description or question
            retrieved_docs: Relevant documents/logs
            show_thinking: Whether to show the <think></think> reasoning section
            
        Returns:
            Dict with analysis and recommendations
        """
        context = self._format_context(retrieved_docs)
        
        prompt = f"""Analyze the following incident based on available documentation:

Incident: {query}

Relevant Documentation:
{context}

Provide:
1. Possible causes
2. Recommended actions
3. Related documentation

Analysis:"""
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.2,
                    "num_predict": 1500,
                    "num_ctx": CONTEXT_WINDOW,
                }
            )
            
            analysis_text = self._filter_thinking(response['response'].strip(), show_thinking)
            
            return {
                "analysis": analysis_text,
                "model_used": self.model_name,
                "sources": self._extract_sources(retrieved_docs)
            }
            
        except Exception as e:
            print(f"Error analyzing incident: {e}")
            return {
                "error": str(e),
                "model_used": self.model_name
            }
    
    def _format_context(self, documents: List[Dict[str, any]]) -> str:
        """
        Format retrieved documents into context string.
        
        Args:
            documents: List of document chunks
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents):
            source = doc.get('metadata', {}).get('filename', 'Unknown')
            content = doc.get('content', '')
            context_parts.append(f"[Document {i+1} - {source}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _extract_sources(self, documents: List[Dict[str, any]]) -> List[str]:
        """
        Extract unique source files from documents.
        
        Args:
            documents: List of document chunks
            
        Returns:
            List of unique source filenames
        """
        sources = set()
        for doc in documents:
            source = doc.get('metadata', {}).get('filename')
            if source:
                sources.add(source)
        return sorted(list(sources))


# Example usage
if __name__ == "__main__":
    print("Reasoning Engine Test\n" + "="*50)
    
    engine = ReasoningEngine()
    
    # Mock retrieved documents
    mock_docs = [
        {
            "content": "To configure logging, edit the config.yaml file and set log_level to DEBUG or INFO.",
            "metadata": {"filename": "logging_guide.md"}
        },
        {
            "content": "Logs are stored in /var/log/app/ directory by default. Rotate logs weekly.",
            "metadata": {"filename": "operations_manual.md"}
        }
    ]
    
    # Test synthesis
    query = "How do I configure logging?"
    result = engine.synthesize_response(query, mock_docs)
    
    print(f"\nQuery: {query}")
    print(f"Response: {result['response']}")
    print(f"Sources: {result['sources']}")

