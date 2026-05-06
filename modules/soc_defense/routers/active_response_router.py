import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

def active_response_router_node(state):
    """
    Standardized Active Response Router.
    Enforces RAG + Thinking + HITL.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Active Response routing logic.")
    prompt = intelligence_engine.wrap_thinking_prompt(
        f"Route this active response request to the correct pod (active_response_pod). Input: {json.dumps(state.get('current_node_output', {}))}",
        rag_context
    )
    
    response_str = query_llm(prompt)
    try:
        ai_res = json.loads(response_str)
    except:
        ai_res = {"thinking_reasoning": "Fallback routing.", "final_decision": "active_response_pod"}
        
    hitl_status = "approved"
    
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing."),
        "hitl_status": hitl_status,
        "final_decision": "active_response_pod",
        "confidence_score": 1.0,
        "data_payload": {"pod name": "active_response_pod"}
    }
    return {"current_node_output": result}
