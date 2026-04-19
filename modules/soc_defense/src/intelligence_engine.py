import json
import os

class IntelligenceEngine:
    """
    Unified engine for RAG (Knowledge Augmentation) and Thinking (Reasoning Layer).
    Ensures every SOC module follows the mandatory architecture rules.
    """
    
    def __init__(self, knowledge_path=None):
        if knowledge_path is None:
            knowledge_path = os.path.join(os.path.dirname(__file__), "../knowledge/mitre_attack.json")
        
        self.knowledge_path = knowledge_path
        self.mitre_data = self._load_knowledge()

    def _load_knowledge(self):
        try:
            with open(self.knowledge_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"ERROR: Failed to load knowledge base: {e}")
            return {}

    def get_rag_context(self, input_text: str) -> str:
        """
        Retrieves contextual intelligence from MITRE ATT&CK and historical patterns.
        """
        # Simple keyword-based retrieval for demonstration
        # In production, this would use a vector database (FAISS/ChromaDB)
        input_lower = input_text.lower()
        context_parts = []
        
        # 1. MITRE ATT&CK Context
        techniques = self.mitre_data.get("techniques", [])
        for tech in techniques:
            if tech.get("name", "").lower() in input_lower or tech.get("id", "").lower() in input_lower:
                context_parts.append(f"MITRE Technique [{tech['id']}]: {tech['name']} - {tech.get('description', '')}")
        
        # 2. Historical Incidents (Mock)
        if "sql" in input_lower or "union" in input_lower:
            context_parts.append("Historical Context: Similar patterns were seen in Incident #9042 (SQLi attempt on DB-01). Path: /api/v1/users.")
        elif "brute" in input_lower or "login" in input_lower:
            context_parts.append("Historical Context: Pattern matches 'SSH Brute Force' cluster observed in prior 24 hours.")
        
        if not context_parts:
            return "No specific threat intelligence context found for the current input."
        
        return "\n".join(context_parts)

    def wrap_thinking_prompt(self, base_prompt: str, context: str) -> str:
        """
        Wraps the base prompt with mandatory Thinking and RAG requirements.
        """
        return f"""🧠 MANDATORY REASONING LAYER (THINKING SYSTEM)
Perform step-by-step reasoning before producing any final decision.
Explain correlations, attack stages, and decision logic internally.

📚 RAG CONTEXT (KNOWLEDGE AUGMENTATION)
The following intelligence context has been retrieved for this task:
{context}

---
📥 BASE TASK/INPUT:
{base_prompt}

---
⚠️ OUTPUT REQUIREMENT:
You MUST return a valid JSON object with the following structure:
{{
  "rag_context": "Summary of the intelligence used",
  "thinking_reasoning": "Step-by-step reasoning and pattern identification",
  "hitl_status": "approved | pending | rejected",
  "final_decision": "The actual technical output or decision",
  "confidence_score": 0.0 to 1.0,
  "data_payload": {{ "additional": "technical data" }}
}}
"""

intelligence_engine = IntelligenceEngine()
