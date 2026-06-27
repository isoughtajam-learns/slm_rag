"""
Document ingestion and embedding pipeline.
Processes documents and generates embeddings using local models.
"""

import ollama
from pathlib import Path
from typing import List, Dict, Optional
import json
from src.config import (
    DOCUMENTS_DIR,
    OLLAMA_BASE_URL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EmbeddingModel,
)


class DocumentProcessor:
    """Handles document loading and preprocessing."""
    
    @staticmethod
    def load_text_file(file_path: Path) -> Dict[str, any]:
        """
        Load a text file and extract metadata.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dict with content and metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "content": content,
            "source": str(file_path),
            "filename": file_path.name,
            "type": file_path.suffix
        }
    
    @staticmethod
    def load_pdf(file_path: Path) -> Dict[str, any]:
        """
        Load a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict with content and metadata
        """
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text() + "\n"
            
            return {
                "content": content,
                "source": str(file_path),
                "filename": file_path.name,
                "type": ".pdf",
                "pages": len(reader.pages)
            }
        except ImportError:
            print("pypdf not installed. Install with: pip install pypdf")
            return None
    
    @staticmethod
    def load_docx(file_path: Path) -> Dict[str, any]:
        """
        Load a Word document.
        
        Args:
            file_path: Path to the .docx file
            
        Returns:
            Dict with content and metadata
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            return {
                "content": content,
                "source": str(file_path),
                "filename": file_path.name,
                "type": ".docx"
            }
        except ImportError:
            print("python-docx not installed. Install with: pip install python-docx")
            return None
    
    def load_documents(self, directory: Path = DOCUMENTS_DIR) -> List[Dict[str, any]]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory: Path to documents directory
            
        Returns:
            List of document dicts
        """
        documents = []
        
        for file_path in directory.rglob('*'):
            if not file_path.is_file():
                continue
            
            doc = None
            suffix = file_path.suffix.lower()
            
            if suffix in ['.txt', '.md', '.log', '.json', '.yaml', '.yml']:
                doc = self.load_text_file(file_path)
            elif suffix == '.pdf':
                doc = self.load_pdf(file_path)
            elif suffix == '.docx':
                doc = self.load_docx(file_path)
            
            if doc and doc.get('content'):
                documents.append(doc)
        
        return documents


class TextChunker:
    """Splits documents into smaller chunks for embedding."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, document: Dict[str, any]) -> List[Dict[str, any]]:
        """
        Split a document into chunks.
        
        Args:
            document: Document dict with content and metadata
            
        Returns:
            List of chunk dicts
        """
        content = document['content']
        chunks = []
        
        # Validate parameters to prevent infinite loops
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than "
                f"chunk_size ({self.chunk_size})"
            )
        
        # Simple character-based chunking
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence endings
                for delimiter in ['. ', '.\n', '!\n', '?\n']:
                    last_delimiter = content[start:end].rfind(delimiter)
                    if last_delimiter != -1:
                        end = start + last_delimiter + len(delimiter)
                        break
            else:
                # Clamp end to content length
                end = len(content)
            
            chunk_text = content[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "content": chunk_text,
                    "chunk_id": chunk_id,
                    "source": document['source'],
                    "filename": document['filename'],
                    "metadata": {
                        "chunk_index": chunk_id,
                        "total_chunks": None,  # Will be updated later
                        **{k: v for k, v in document.items() 
                           if k not in ['content']}
                    }
                })
                chunk_id += 1
            
            # Ensure forward progress
            next_start = end - self.chunk_overlap
            if next_start <= start:
                # Safety check: always advance at least 1 character
                next_start = start + 1
            start = next_start
        
        # Update total chunks count
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = len(chunks)
        
        return chunks


class LocalEmbedder:
    """Generates embeddings using local Ollama models."""
    
    def __init__(self, model_name: str = EmbeddingModel.ALL_MINILM):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the Ollama embedding model
        """
        self.model_name = model_name
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings(
                model=self.model_name,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def embed_documents(self, documents: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            documents: List of document/chunk dicts
            
        Returns:
            Documents with embeddings added
        """
        for i, doc in enumerate(documents):
            if i % 10 == 0:
                print(f"Embedding document {i+1}/{len(documents)}")
            
            embedding = self.embed_text(doc['content'])
            if embedding:
                doc['embedding'] = embedding
        
        return documents


# Example usage
if __name__ == "__main__":
    print("Document Ingestion Pipeline Test\n" + "="*50)
    
    # Load documents
    processor = DocumentProcessor()
    documents = processor.load_documents()
    print(f"\nLoaded {len(documents)} documents")
    
    # Chunk documents
    chunker = TextChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)
    print(f"Created {len(all_chunks)} chunks")
    
    # Generate embeddings
    embedder = LocalEmbedder()
    embedded_chunks = embedder.embed_documents(all_chunks)
    print(f"Generated embeddings for {len(embedded_chunks)} chunks")

