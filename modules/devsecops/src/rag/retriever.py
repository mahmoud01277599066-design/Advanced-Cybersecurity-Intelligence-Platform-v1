"""
DevSecOps Module - Security Retriever
RAG retriever that enriches vulnerability context with knowledge base data.
"""

from typing import List, Dict, Any, Optional
from .chroma_manager import ChromaManager
from ..core.logger import get_logger

logger = get_logger(__name__)


class SecurityRetriever:
    """
    Retrieves relevant security context from the ChromaDB knowledge base
    to enrich vulnerability analysis and remediation suggestions.
    """

    def __init__(self, chroma_manager: Optional[ChromaManager] = None):
        self._chroma = chroma_manager or ChromaManager()

    @property
    def is_available(self) -> bool:
        """Check if the retriever has a working vector store."""
        return self._chroma.is_available

    def retrieve_for_vulnerability(
        self,
        vulnerability_type: str,
        code_context: str = "",
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant security knowledge for a given vulnerability.

        Args:
            vulnerability_type: e.g., "SQL Injection", "CWE-89"
            code_context: Optional code snippet for better matching.
            n_results: Number of results to return.

        Returns:
            List of relevant knowledge documents.
        """
        query = f"Vulnerability: {vulnerability_type}"
        if code_context:
            query += f"\nCode Context: {code_context[:200]}"

        results = self._chroma.query(query, n_results=n_results)

        logger.info(
            f"Retrieved {len(results)} documents for vulnerability: "
            f"'{vulnerability_type}'"
        )
        return results

    def retrieve_remediation_guide(
        self,
        cwe_id: str,
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve remediation guides for a specific CWE.

        Args:
            cwe_id: The CWE identifier (e.g., "CWE-89").
            n_results: Number of results to return.

        Returns:
            List of remediation guide documents.
        """
        query = f"Remediation guide for {cwe_id}"
        results = self._chroma.query(
            query,
            n_results=n_results,
            where={"type": "cwe"} if self._chroma.is_available else None,
        )
        return results

    def build_context_prompt(
        self,
        vulnerability_type: str,
        code_snippet: str = "",
    ) -> str:
        """
        Build an enriched context prompt using RAG results.
        This prompt is meant to be passed to the LLM for better analysis.

        Args:
            vulnerability_type: Type of vulnerability.
            code_snippet: The affected code.

        Returns:
            str: Enriched context string.
        """
        results = self.retrieve_for_vulnerability(
            vulnerability_type, code_snippet, n_results=3
        )

        if not results:
            return (
                f"No additional context found for '{vulnerability_type}'. "
                f"Analyze based on general security knowledge."
            )

        context_parts = [
            f"## Retrieved Security Knowledge for: {vulnerability_type}\n"
        ]
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"### Reference {i} (Relevance: {result.get('relevance_score', 'N/A'):.2f})\n"
                f"{result.get('content', 'No content')}\n"
            )

        return "\n".join(context_parts)
