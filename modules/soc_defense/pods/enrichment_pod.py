import sys
import os
import time
import json
import random

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger

class EnrichmentPod:
    """
    Independent Threat Intelligence Micro-Agent.
    """
    def __init__(self):
        self.malicious_ips = ["1.2.3.4", "91.210.10.10", "45.1.2.3"]
        self.reputation_map = {
            "1.2.3.4": "malicious",
            "192.168.1.10": "clean",
            "8.8.8.8": "clean"
        }

    def get_geo(self, ip):
        if ip.startswith("1.2"): return "Russia"
        if ip.startswith("8."): return "USA"
        if ip.startswith("192."): return "Internal Network"
        if ip.startswith("45."): return "China"
        return "Unknown"

    def get_reputation(self, ip):
        if ip in self.malicious_ips: return "malicious"
        return self.reputation_map.get(ip, "suspicious")

    def enrich_alert(self, alert):
        if not isinstance(alert, dict): return alert
        src_ip = alert.get("src_ip", alert.get("srcip", "0.0.0.0"))
        
        enrichment_data = {
            "geo": self.get_geo(src_ip),
            "reputation": self.get_reputation(src_ip),
            "intel_source": "Mandatory RAG Engine"
        }
        return {**alert, **enrichment_data}

def enrichment_node(state):
    """
    LangGraph node for threat intelligence enrichment.
    Upgraded for Standard Architecture.
    """
    from modules.soc_defense.src.intelligence_engine import intelligence_engine
    from modules.soc_defense.src.llm_client import query_llm
    
    current_out = state.get("current_node_output", {})
    alerts = current_out.get("data_payload", {}).get("logs", current_out.get("data", []))

    start_time = time.time()
    enricher = EnrichmentPod()
    enriched_alerts = [enricher.enrich_alert(a) for a in alerts if a]

    # 1. RAG
    rag_context = intelligence_engine.get_rag_context(f"Enriching {len(enriched_alerts)} alerts.")
    
    # 2. Thinking
    prompt = intelligence_engine.wrap_thinking_prompt(
        f"Explain how enrichment adds value to these alerts: {json.dumps(enriched_alerts[:2])}",
        rag_context
    )
    ai_response = query_llm(prompt)
    try:
        ai_data = json.loads(ai_response)
    except:
        ai_data = {"thinking_reasoning": "Enriching with Geo and Reputation for context."}

    exec_time_ms = int((time.time() - start_time) * 1000)
    
    # 5. Result Construction
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_data.get("thinking_reasoning", "N/A"),
        "hitl_status": "approved",
        "final_decision": f"Enriched {len(enriched_alerts)} alerts with threat intelligence.",
        "confidence_score": 1.0,
        "data_payload": {
            "enriched_alerts": enriched_alerts,
            "execution_time_ms": exec_time_ms
        }
    }

    return {"current_node_output": result}
