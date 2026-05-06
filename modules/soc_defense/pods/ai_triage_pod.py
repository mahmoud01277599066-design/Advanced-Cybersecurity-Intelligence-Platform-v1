import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

class AITriagePodWrapper:
    """
    Wrapper for AI Triage to enforce RAG + Thinking + HITL.
    """
    
    def triage_incident(self, state, rag_context):
        # Extract previous node's data
        current_out = state.get("current_node_output", {})
        data = current_out.get("data_payload", {})
        
        prompt = intelligence_engine.wrap_thinking_prompt(
            f"Triage this incident based on correlation results. Data: {json.dumps(data)}",
            rag_context
        )
        response_str = query_llm(prompt)
        
        try:
            return json.loads(response_str)
        except Exception:
            return {
                "rag_context": "Fallback",
                "thinking_reasoning": "Failed to parse AI response. Using emergency triage logic.",
                "hitl_status": "pending",
                "final_decision": "Suspected True Positive",
                "confidence_score": 0.5,
                "data_payload": {"risk_level": "Medium"}
            }

def ai_triage_node(state):
    """
    LangGraph node for AI triage.
    Standardized for Architecture v2.0.
    """
    start_time = time.time()
    wrapper = AITriagePodWrapper()
    
    # 1. RAG Injection
    rag_context = intelligence_engine.get_rag_context(str(state.get("current_node_output", {})))
    
    # 2. Thinking & 3. Triage
    triage_data = wrapper.triage_incident(state, rag_context)
    
    # 4. HITL Gate (Assess based on the decision and confidence)
    hitl_status = hitl_gate.assess_risk(str(triage_data.get("final_decision", "")), triage_data.get("confidence_score", 0.0))
    
    exec_time_ms = int((time.time() - start_time) * 1000)
    
    # 5. Result Construction (Standard Schema)
    decision_str = str(triage_data.get("final_decision", "Triage Complete"))
    
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": triage_data.get("thinking_reasoning", "N/A"),
        "hitl_status": hitl_status,
        "final_decision": decision_str,
        "confidence_score": triage_data.get("confidence_score", 0.0),
        "data_payload": {
            "execution_time_ms": exec_time_ms,
            "classification": decision_str,
            "risk_score": triage_data.get("confidence_score", 0.0) * 10,
            "original_data": state.get("current_node_output", {}).get("data_payload", {})
        }
    }
    
    return {
        "current_node_output": result,
        "risk_score": result["data_payload"]["risk_score"],
        "classification": decision_str,
        "hitl_status": hitl_status
    }
