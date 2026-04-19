"""
DevSecOps Module - Document Loader
Loads security knowledge documents (CWE, CVE, secure coding patterns)
into the ChromaDB vector store.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..core.logger import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """
    Loads and processes security knowledge documents for RAG ingestion.
    Supports JSON, Markdown, and plain text formats.
    """

    @staticmethod
    def load_json(file_path: str) -> List[Dict[str, Any]]:
        """Load documents from a JSON file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File not found: {file_path}")
                return []

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            return []

    @staticmethod
    def load_text(file_path: str, chunk_size: int = 1000) -> List[str]:
        """
        Load and chunk a text/markdown file.

        Args:
            file_path: Path to the text file.
            chunk_size: Maximum characters per chunk.

        Returns:
            List of text chunks.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File not found: {file_path}")
                return []

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple chunking by paragraphs then by size
            paragraphs = content.split("\n\n")
            chunks = []
            current_chunk = ""

            for para in paragraphs:
                if len(current_chunk) + len(para) <= chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"

            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            logger.info(f"Loaded {len(chunks)} chunks from {file_path}")
            return chunks

        except Exception as e:
            logger.error(f"Failed to load text file {file_path}: {e}")
            return []

    @staticmethod
    def load_cwe_entries(file_path: str) -> List[Dict[str, Any]]:
        """
        Load CWE (Common Weakness Enumeration) entries.

        Expected JSON format:
        [
            {
                "cwe_id": "CWE-89",
                "name": "SQL Injection",
                "description": "...",
                "remediation": "...",
                "severity": "Critical"
            }
        ]
        """
        entries = DocumentLoader.load_json(file_path)
        documents = []

        for entry in entries:
            doc_text = (
                f"CWE ID: {entry.get('cwe_id', 'Unknown')}\n"
                f"Name: {entry.get('name', 'Unknown')}\n"
                f"Description: {entry.get('description', '')}\n"
                f"Remediation: {entry.get('remediation', '')}\n"
                f"Severity: {entry.get('severity', 'Unknown')}"
            )
            documents.append({
                "content": doc_text,
                "metadata": {
                    "type": "cwe",
                    "id": entry.get("cwe_id", "Unknown"),
                    "severity": entry.get("severity", "Unknown"),
                }
            })

        logger.info(f"Loaded {len(documents)} CWE entries")
        return documents

    @staticmethod
    def load_directory(
        dir_path: str,
        extensions: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Load all supported documents from a directory.

        Args:
            dir_path: Path to the directory.
            extensions: File extensions to include (default: .json, .md, .txt).

        Returns:
            List of document dicts with content and metadata.
        """
        if extensions is None:
            extensions = [".json", ".md", ".txt"]

        path = Path(dir_path)
        if not path.exists():
            logger.warning(f"Directory not found: {dir_path}")
            return []

        documents = []
        for ext in extensions:
            for file in path.rglob(f"*{ext}"):
                if ext == ".json":
                    items = DocumentLoader.load_json(str(file))
                    for item in items:
                        if isinstance(item, dict):
                            documents.append({
                                "content": json.dumps(item, ensure_ascii=False),
                                "metadata": {"source": str(file), "type": "json"},
                            })
                else:
                    chunks = DocumentLoader.load_text(str(file))
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            "content": chunk,
                            "metadata": {
                                "source": str(file),
                                "chunk_index": i,
                                "type": ext.lstrip(".")
                            },
                        })

        logger.info(f"Loaded {len(documents)} documents from directory: {dir_path}")
        return documents
