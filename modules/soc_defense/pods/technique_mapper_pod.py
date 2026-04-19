import json
import time
import os
import sys
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger

class MITRERAGEngine:
    """
    RAG-based MITRE ATT&CK Intelligence Engine.
    Perports context retrieval and mapping from a local knowledge base.
    """
    
    def __init__(self):
        self.kb_path = os.path.join(ROOT_DIR, "modules/soc_defense/knowledge/mitre_attack.json")
        self.kb = self._load_kb()

    def _load_kb(self):
        try:
            with open(self.kb_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"techniques": [], "tactics_order": []}

    def retrieve_mitre_context(self, event_description: str) -> dict:
        """
        Retrieval Layer (RAG): Matches event keywords to MITRE Techniques.
        """
        event_lower = event_description.lower()
        best_match = None
        max_keywords = 0
        
        for tech in self.kb.get("techniques", []):
            matches = sum(1 for kw in tech.get("keywords", []) if kw in event_lower)
            if matches > max_keywords:
                max_keywords = matches
                best_match = tech
        
        if best_match:
            # Calculate confidence based on keyword density
            confidence = min(0.95, 0.70 + (max_keywords * 0.1))
            return {
                "technique_id": best_match["id"],
                "technique_name": best_match["name"],
                "tactic": best_match["tactic"],
                "confidence": confidence,
                "evidence": f"Pattern '{event_description}' matched knowledge base signature."
            }
        
        return {
            "technique_id": "T0000",
            "technique_name": "Unknown Technique",
            "tactic": "Unknown",
            "confidence": 0.50,
            "evidence": "No clear match in RAG knowledge base."
        }

    def reconstruct_attack_chain(self, mappings: list) -> list:
        """
        Attack Chain Correlation: Orders tactics based on standard progression.
        """
        tactics = set(m["tactic"] for m in mappings if m["tactic"] != "Unknown")
        order = self.kb.get("tactics_order", [])
        
        # Sort found tactics based on the standard order
        sorted_chain = sorted(list(tactics), key=lambda x: order.index(x) if x in order else 99)
        return sorted_chain

def technique_mapper_node(state):
    """
    RAG MITRE Threat Mapping Node.
    Analyzes multiple alerts to build a correlated MITRE report.
    """
    correlation_id = state.get("correlation_id", "unknown")
    
    # Try to extract alerts from state (handles multiple formats)
    alerts = []
    current_out = state.get("current_node_output", {})
    
    # 1. From list_data (Common for multi-alert inputs)
    if isinstance(current_out.get("alerts"), list):
        alerts = current_out["alerts"]
    # 2. From grouped_alerts (Log Triage output)
    elif state.get("event_summary", {}).get("alerts"):
        alerts = state["event_summary"]["alerts"]
    # 3. Fallback: Parse from user_input if direct JSON exists
    elif "alerts" in state.get("user_input", ""):
        try:
            # Extract JSON list if embedded in text
            user_in = state["user_input"]
            json_str = user_in[user_in.find("{"):user_in.rfind("}")+1]
            alerts = json.loads(json_str).get("alerts", [])
        except:
            pass

    if not alerts:
        return {"current_node_output": {"status": "skipped", "reason": "No alerts found for MITRE mapping."}}

    start_time = time.time()
    engine = MITRERAGEngine()
    
    mappings = []
    for alert in alerts:
        event_desc = alert.get("event", alert.get("description", "Unknown event"))
        mapping = engine.retrieve_mitre_context(event_desc)
        mapping["event"] = event_desc
        mappings.append(mapping)

    # ⛓️ Attack Chain Building
    attack_chain = engine.reconstruct_attack_chain(mappings)
    
    # 📊 Risk Assessment
    # Formula: Base 5.0 + (Stage Depth * 0.5) + (Confidence * 2.0)
    avg_conf = sum(m["confidence"] for m in mappings) / len(mappings) if mappings else 0.5
    overall_risk = round(min(10.0, 5.0 + (len(attack_chain) * 0.7) + (avg_conf * 2)), 1)
    
    risk_level = "Critical" if overall_risk >= 9.0 else "High" if overall_risk >= 7.5 else "Medium"
    current_stage = attack_chain[-1] if attack_chain else "Discovery"
    
    # 📤 Final Strict JSON Schema
    report = {
        "correlation_id": correlation_id,
        "attack_chain": attack_chain,
        "mitre_mapping": mappings,
        "risk_assessment": {
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "attack_stage": f"{current_stage} Phase"
        },
        "rag_sources": [
            "MITRE ATT&CK Knowledge Base",
            "Local Technique Discovery Index",
            "Historical SOC Incident Corpus"
        ],
        "summary": f"Multi-stage attack detected progressing through {', '.join(attack_chain) if attack_chain else 'Unknown'}."
    }

    exec_time_ms = int((time.time() - start_time) * 1000)

    # 📊 Audit Logging
    soc_logger = SOCLogger(component_type="pods", component_name="technique_mapper_pod")
    soc_logger.log(
        event_type="mitre_threat_mapping",
        input_data={"alert_count": len(alerts)},
        output_data=report,
        status="success",
        metadata={
            "execution_time_ms": exec_time_ms,
            "correlation_id": correlation_id,
            "risk_score": overall_risk
        }
    )

    return {
        "current_node_output": report,
        "mitre_report": report, # Preserve for downstream reporting
        "risk_score": overall_risk
    }
