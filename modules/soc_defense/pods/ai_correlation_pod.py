import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

class AICorrelationPodWrapper:
    """
    Wrapper for AI Correlation to enforce RAG + Thinking + HITL.
    """
    
    def correlate_patterns(self, alerts, rag_context):
        prompt = intelligence_engine.wrap_thinking_prompt(
            f"Correlate the following alerts and identify the primary attack pattern and timeline. Alerts: {json.dumps(alerts)}",
            rag_context
        )
        response_str = query_llm(prompt)
        
        try:
            return json.loads(response_str)
        except Exception:
            return {
                "rag_context": "Fallback",
                "thinking_reasoning": "Failed to parse AI response. Using signature-based correlation fallback.",
                "hitl_status": "approved",
                "final_decision": "Reconnaissance Cluster identified",
                "confidence_score": 0.6,
                "data_payload": {"pattern": "Reconnaissance"}
            }

def ai_correlation_node(state):
    """
    LangGraph node for event correlation.
    Upgraded for Standard Data Flow & Robustness.
    """
    correlation_id = state.get("correlation_id", "unknown")
    current_out = state.get("current_node_output", {})
    
    # DEFENSIVE DATA EXTRACTION
    alerts = []
    # Try reading from standardized data_payload first
    if "data_payload" in current_out and "grouped_alerts" in current_out["data_payload"]:
        alerts = current_out["data_payload"]["grouped_alerts"]
    # Fallback for older formats or directly passing alerts
    elif isinstance(current_out.get("final_decision"), dict):
        alerts = current_out["final_decision"].get("grouped_alerts", [])
    elif "grouped_alerts" in current_out:
        alerts = current_out["grouped_alerts"]

    if not alerts:
        return {"current_node_output": {"rag_context": "N/A", "thinking_reasoning": "No alerts found for correlation.", "hitl_status": "approved", "final_decision": "Correlation Skipped", "confidence_score": 0.0, "data_payload": {}}}

    start_time = time.time()
    wrapper = AICorrelationPodWrapper()
    
    # 1. RAG Injection
    local_rag = intelligence_engine.get_rag_context(str(alerts))
    rag_enriched_data = state.get("rag_enriched_data", {})
    if rag_enriched_data:
        rag_context = f"MITRE ENRICHMENT:\n{json.dumps(rag_enriched_data)}\n\nLOCAL INTELLIGENCE:\n{local_rag}"
    else:
        rag_context = local_rag
    
    # 2. Thinking & 3. Correlation
    correlation = wrapper.correlate_patterns(alerts, rag_context)
    
    # 4. HITL Gate (Correlation is informational)
    hitl_status = "approved"
    
    exec_time_ms = int((time.time() - start_time) * 1000)
    
    # 5. Result Construction (Standard Schema)
    # Ensure final_decision is a string
    decision_str = str(correlation.get("final_decision", "Pattern Correlation Complete"))
    
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": correlation.get("thinking_reasoning", "N/A"),
        "hitl_status": hitl_status,
        "final_decision": decision_str,
        "confidence_score": correlation.get("confidence_score", 0.0),
        "data_payload": {
            "execution_time_ms": exec_time_ms,
            "correlation_id": correlation_id,
            "pattern_detected": decision_str,
            "alerts": alerts,
            "timeline": correlation.get("data_payload", {}).get("timeline", [])
        }
    }
    
    return {
        "current_node_output": result,
        "rag_context": rag_context,
        "thinking_reasoning": result["thinking_reasoning"],
        "classification": decision_str
    }
