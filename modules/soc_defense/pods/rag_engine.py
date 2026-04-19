import json
import time

class RAGEngine:
    """
    RAG-based intelligence engine mapping events to MITRE ATT&CK.
    """
    def __init__(self):
        self.mitre_kb = {
            "port_scan": {"mitre": "T1595", "tactic": "Reconnaissance"},
            "failed_login": {"mitre": "T1110", "tactic": "Credential Access"},
            "sql_injection": {"mitre": "T1190", "tactic": "Initial Access"},
            "malware_download": {"mitre": "T1105", "tactic": "Command and Control"}
        }

    def enrich_events(self, events: list):
        enriched = []
        tactics_seen = []
        for event in events:
            # normalize
            e_lower = event.lower().strip()
            if e_lower in self.mitre_kb:
                info = self.mitre_kb[e_lower]
                enriched.append({
                    "event": event,
                    "mitre_technique": info["mitre"],
                    "tactic": info["tactic"],
                    "confidence": 0.92
                })
                tactics_seen.append(info["tactic"])
            else:
                 enriched.append({
                    "event": event,
                    "mitre_technique": "unknown_technique",
                    "tactic": "Unknown",
                    "confidence": 0.0
                })
        
        # Build attack chain
        chain = []
        for t in tactics_seen:
            if not chain or chain[-1] != t:
                chain.append(t)
        
        attack_chain_str = " -> ".join(chain) if chain else "Unknown"
        
        risk = "HIGH" if len(tactics_seen) > 1 else "MEDIUM"
        boost = 0.15 * len(tactics_seen)
        
        return {
            "rag_enriched_events": enriched,
            "attack_chain": [attack_chain_str] if attack_chain_str and attack_chain_str != "Unknown" else [],
            "risk_context": risk,
            "confidence_boost": round(min(boost, 1.0), 2)
        }

def rag_engine_node(state):
    """
    LangGraph compatible node.
    """
    start_time = time.time()
    engine = RAGEngine()
    
    events = state.get("events", [])
    if not events and "user_input" in state:
        try:
            user_in = state["user_input"]
            if "[" in user_in and "]" in user_in:
                json_str = user_in[user_in.find("["):user_in.rfind("]")+1]
                events = json.loads(json_str)
            else:
                events = [user_in]
        except Exception:
            pass

    enrichment = engine.enrich_events(events)
    exec_time_ms = int((time.time() - start_time) * 1000)
    
    # Store standard state
    result = {
        "rag_context": json.dumps(enrichment.get("attack_chain", [])),
        "thinking_reasoning": f"Enriched {len(events)} events with MITRE ATT&CK intelligence.",
        "hitl_status": "approved",
        "final_decision": "RAG Enrichment Complete",
        "confidence_score": 1.0,
        "data_payload": {
            **enrichment,
            "execution_time_ms": exec_time_ms
        }
    }
    
    return {
        "current_node_output": result,
        "rag_enriched_data": enrichment
    }
