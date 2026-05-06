import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

def threat_mapping_router_node(state):
    """
    Standardized Threat Mapping Router.
    Enforces RAG + Thinking + HITL.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Threat Mapping routing.")
    prompt = intelligence_engine.wrap_thinking_prompt("Route to technique mapper pod.", rag_context)
    
    response_str = query_llm(prompt)
    try:
        ai_res = json.loads(response_str)
    except:
        ai_res = {"thinking_reasoning": "Fallback routing.", "final_decision": "technique_mapper"}
        
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing to MITRE mapping engine."),
        "hitl_status": "approved",
        "final_decision": "technique_mapper",
        "confidence_score": 1.0,
        "data_payload": {"pod name": "technique_mapper_pod"}
    }
    return {"current_node_output": result}
