"""
DevSecOps Module - Knowledge Retriever
Implements the 'Retrieval Phase' of the RAG Pipeline.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from .logger import save_agent_json, get_logger

logger = get_logger(__name__)

class KnowledgeRetriever:
    """
    Retrieval Engine for the Multi-Agent Cybersecurity Architecture.
    Performs keyword-based semantic search over the local knowledge base.
    """

    def __init__(self, kb_path: str = None):
        if not kb_path:
            # __file__ is in modules/devsecops/src/core/retriever.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.kb_path = os.path.abspath(os.path.join(current_dir, "..", "..", "knowledge_base"))
        else:
            self.kb_path = kb_path
            
        self.documents = self._load_kb()

    def _load_kb(self) -> List[Dict[str, Any]]:
        """Load all JSON knowledge files from the KB directory."""
        all_docs = []
        if not os.path.exists(self.kb_path):
            logger.warning(f"Knowledge base path not found: {self.kb_path}")
            return []

        for filename in os.listdir(self.kb_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.kb_path, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_docs.extend(data)
                        else:
                            all_docs.append(data)
                except Exception as e:
                    logger.error(f"Failed to load KB file {filename}: {e}")
        
        logger.info(f"Loaded {len(all_docs)} documents into Retrieval Engine.")
        return all_docs

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Step 1: Retrieval Phase.
        Matches query keywords against document content and tags.
        """
        if not query:
            return []

        query = query.lower()
        results = []

        for doc in self.documents:
            score = 0
            content = doc.get("content", "").lower()
            tags = [t.lower() for t in doc.get("tags", [])]
            title = doc.get("title", "").lower()

            # Simple scoring: title > tags > content
            if any(word in title for word in query.split()):
                score += 5
            if any(word in tags for word in query.split()):
                score += 3
            if any(word in content for word in query.split()):
                score += 1

            if score > 0:
                results.append({
                    "document_id": doc.get("id"),
                    "title": doc.get("title"),
                    "content": doc.get("content"),
                    "relevance_score": float(score)
                })

        # Sort by score descending
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_results = results[:top_k]

        # Mandatory Action: Log retrieval agent result independently
        retrieval_log = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results_count": len(top_results),
            "top_results": top_results
        }
        save_agent_json("knowledge_retriever", "scripts", retrieval_log)
        
        return top_results

# Singleton instance
knowledge_retriever = KnowledgeRetriever()
