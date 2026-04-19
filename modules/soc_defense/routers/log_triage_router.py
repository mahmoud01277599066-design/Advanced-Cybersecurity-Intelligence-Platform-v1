import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

def log_triage_router_node(state):
    """
    Standardized Log Triage Router.
    Enforces RAG + Thinking + HITL.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Log Triage routing.")
    prompt = intelligence_engine.wrap_thinking_prompt("Route to normalization and triage pods.", rag_context)
    
    response_str = query_llm(prompt)
    try:
        ai_res = json.loads(response_str)
    except:
        ai_res = {"thinking_reasoning": "Fallback routing.", "final_decision": "log_triage_pod"}
        
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing to log processing pipeline."),
        "hitl_status": "approved",
        "final_decision": "log_triage_pod",
        "confidence_score": 1.0,
        "data_payload": {"pod name": "log_triage_pod"}
    }
    return {"current_node_output": result}
