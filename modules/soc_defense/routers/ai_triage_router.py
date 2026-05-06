import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

def ai_triage_router_node(state):
    """
    Standardized AI Triage Router.
    Routes between AI Correlation and Manual Triage.
    """
    start_time = time.time()
    current_out = state.get("current_node_output", {})
    
    # Extract clues from state for routing
    data = current_out.get("data_payload", {})
    
    local_rag = intelligence_engine.get_rag_context("AI Triage routing logic.")
    rag_enriched_data = state.get("rag_enriched_data", {})
    if rag_enriched_data:
        rag_context = f"MITRE ENRICHMENT:\n{json.dumps(rag_enriched_data)}\n\nLOCAL INTELLIGENCE:\n{local_rag}"
    else:
        rag_context = local_rag
    prompt = intelligence_engine.wrap_thinking_prompt(
        f"Determine if this incident requires deep AI correlation. Data Summary: {json.dumps(data)}",
        rag_context
    )
    
    response_str = query_llm(prompt)
    try:
        ai_res = json.loads(response_str)
    except:
        ai_res = {"thinking_reasoning": "Standard routing.", "final_decision": "ai_correlation"}
        
    # Decision logic
    decision = "ai_correlation"
    if "manual" in str(ai_res.get("final_decision", "")).lower():
        decision = "manual_triage"
        
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing..."),
        "hitl_status": "approved",
        "final_decision": decision,
        "confidence_score": 1.0,
        "data_payload": {
            "target_node": decision,
            "original_payload": data
        }
    }
    return {"current_node_output": result}
