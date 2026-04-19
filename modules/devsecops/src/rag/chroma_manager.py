"""
DevSecOps Module - ChromaDB Vector Store Manager
Manages the local vector database for security knowledge retrieval.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)

# Try importing chromadb; provide fallback if not installed
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("chromadb not installed. RAG features will be disabled.")


class ChromaManager:
    """
    Manages ChromaDB collections for DevSecOps security knowledge.
    Stores CWE entries, CVE data, secure coding patterns, and remediation guides.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.persist_directory = persist_directory or settings.CHROMA_DB_PATH
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self._client = None
        self._collection = None

        if CHROMA_AVAILABLE:
            self._initialize()
        else:
            logger.warning("ChromaDB not available. Running without vector store.")

    def _initialize(self):
        """Initialize the ChromaDB client and collection."""
        try:
            # Ensure persist directory exists
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "DevSecOps security knowledge base"}
            )
            logger.info(
                f"ChromaDB initialized: collection='{self.collection_name}', "
                f"path='{self.persist_directory}', "
                f"documents={self._collection.count()}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self._client = None
            self._collection = None

    @property
    def is_available(self) -> bool:
        """Check if ChromaDB is ready."""
        return self._collection is not None

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> bool:
        """
        Add documents to the security knowledge collection.

        Args:
            documents: List of text content to store.
            metadatas: Optional metadata for each document.
            ids: Optional unique IDs for each document.

        Returns:
            bool: True if successful.
        """
        if not self.is_available:
            logger.warning("ChromaDB not available. Cannot add documents.")
            return False

        try:
            if ids is None:
                existing_count = self._collection.count()
                ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

            self._collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(f"Added {len(documents)} documents to collection.")
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store for relevant security knowledge.

        Args:
            query_text: The search query.
            n_results: Number of results to return.
            where: Optional metadata filter.

        Returns:
            List of matching documents with metadata.
        """
        if not self.is_available:
            logger.warning("ChromaDB not available. Returning empty results.")
            return []

        try:
            results = self._collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
            )

            # Format results
            formatted = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]

                for i, doc in enumerate(docs):
                    formatted.append({
                        "content": doc,
                        "metadata": metas[i] if i < len(metas) else {},
                        "relevance_score": 1 - (distances[i] if i < len(distances) else 0),
                    })

            logger.info(f"Query returned {len(formatted)} results for: '{query_text[:50]}...'")
            return formatted

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def get_count(self) -> int:
        """Return the number of documents in the collection."""
        if not self.is_available:
            return 0
        return self._collection.count()

    def reset(self) -> bool:
        """Clear all documents from the collection."""
        if not self.is_available:
            return False

        try:
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
            )
            logger.info("Collection reset successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False
