"""
Local vector database and retrieval system using ChromaDB.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path
import json

from src.config import EmbeddingModel

# Monkey-patch ChromaDB telemetry to suppress errors
try:
    from chromadb.telemetry.product.posthog import Posthog
    original_capture = Posthog.capture
    def silent_capture(self, *args, **kwargs):
        try:
            return original_capture(self)
        except:
            pass
    Posthog.capture = silent_capture
except:
    pass

from src.config import CHROMA_DB_DIR, TOP_K_RESULTS, SIMILARITY_THRESHOLD
from src.document_processor import DocumentProcessor, TextChunker, LocalEmbedder


class LocalVectorStore:
    """Manages document storage and retrieval using ChromaDB."""
    
    def __init__(self, collection_name: str = "enterprise_docs", embedding_model_name: str = EmbeddingModel.ALL_MINILM):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        
        # Initialize ChromaDB with local persistence
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Enterprise documents for RAG"}
        )
        
        self.embedder = LocalEmbedder(model_name=embedding_model_name)
    
    def add_documents(self, documents: List[Dict[str, any]]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dicts with content and metadata
        """
        if not documents:
            print("No documents to add")
            return
        
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []
        
        for i, doc in enumerate(documents):
            # Generate unique ID
            doc_id = f"{doc.get('filename', 'doc')}_{doc.get('chunk_id', i)}"
            ids.append(doc_id)
            
            # Get or generate embedding
            if 'embedding' in doc:
                embeddings.append(doc['embedding'])
            else:
                embedding = self.embedder.embed_text(doc['content'])
                if embedding:
                    embeddings.append(embedding)
                else:
                    continue
            
            # Prepare metadata
            metadata = doc.get('metadata', {})
            # Convert all values to strings for ChromaDB compatibility
            metadata = {k: str(v) for k, v in metadata.items()}
            metadatas.append(metadata)
            
            # Store document text
            documents_text.append(doc['content'])
        
        # Add to collection
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
            print(f"Added {len(ids)} documents to vector store")
    
    def query(
        self, 
        query_text: str, 
        n_results: int = TOP_K_RESULTS,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Query the vector store for relevant documents.
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant document chunks with scores
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query_text)
        
        if not query_embedding:
            print("Failed to generate query embedding")
            return []
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                }
                
                # Filter by similarity threshold (distance < threshold for similarity)
                # ChromaDB uses L2 distance, lower is better
                if result['distance'] < SIMILARITY_THRESHOLD:
                    formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, any]:
        """Get statistics about the vector store collection."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "storage_path": str(CHROMA_DB_DIR)
        }
    
    def reset_collection(self) -> None:
        """Delete all documents from the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        print(f"Reset collection: {self.collection_name}")


class RetrievalSystem:
    """High-level retrieval system with document processing pipeline."""
    
    def __init__(self, collection_name: str = "enterprise_docs", embedding_model_name: str = EmbeddingModel.ALL_MINILM):
        """
        Initialize the retrieval system.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.vector_store = LocalVectorStore(collection_name=collection_name, embedding_model_name=embedding_model_name)
        self.document_processor = DocumentProcessor()
        self.chunker = TextChunker(chunk_size=500, chunk_overlap=50)
        self.embedder = LocalEmbedder(model_name=embedding_model_name)
    
    def ingest_documents(self, documents_dir: Path = None) -> int:
        """
        Ingest documents from a directory into the vector store.
        
        Args:
            documents_dir: Path to documents directory
            
        Returns:
            Number of chunks ingested
        """
        if documents_dir is None:
            from src.config import DOCUMENTS_DIR
            documents_dir = DOCUMENTS_DIR
        
        print(f"Loading documents from {documents_dir}")
        documents = self.document_processor.load_documents(documents_dir)
        
        if not documents:
            print("No documents found")
            return 0
        
        print(f"Loaded {len(documents)} documents")
        
        # Chunk documents
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} chunks")
        
        # Generate embeddings
        print("Generating embeddings...")
        embedded_chunks = self.embedder.embed_documents(all_chunks)
        
        # Add to vector store
        self.vector_store.add_documents(embedded_chunks)
        
        return len(embedded_chunks)
    
    def retrieve(self, query: str, n_results: int = TOP_K_RESULTS) -> List[Dict[str, any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        return self.vector_store.query(query, n_results)
    
    def get_stats(self) -> Dict[str, any]:
        """Get retrieval system statistics."""
        return self.vector_store.get_collection_stats()


# Example usage
if __name__ == "__main__":
    print("Local Retrieval System Test\n" + "="*50)
    
    # Initialize retrieval system
    retrieval = RetrievalSystem()
    
    # Get stats
    stats = retrieval.get_stats()
    print(f"\nCurrent collection stats:")
    print(f"  Documents: {stats['document_count']}")
    print(f"  Storage: {stats['storage_path']}")
    
    # Example query
    test_query = "How do I configure logging?"
    print(f"\nTest query: {test_query}")
    results = retrieval.retrieve(test_query, n_results=3)
    
    print(f"\nFound {len(results)} relevant chunks:")
    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['metadata'].get('filename', 'Unknown')}")
        print(f"   Distance: {result['distance']:.4f}")
        print(f"   Preview: {result['content'][:100]}...")

