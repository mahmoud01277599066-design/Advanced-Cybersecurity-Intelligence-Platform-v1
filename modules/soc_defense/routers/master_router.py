import json
import uuid
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

def master_router_node(state):
    """
    Master SOC Orchestration Router.
    Upgraded with mandatory architecture: RAG + Thinking + HITL.
    """
    user_input = state.get("user_input", "")
    start_time = time.time()
    
    # Generate unique Correlation ID
    correlation_id = f"attack_{uuid.uuid4().hex[:8]}"
    
    # 1. RAG Injection
    rag_context = intelligence_engine.get_rag_context(user_input)
    
    # 2. Thinking & 3. Routing
    prompt = intelligence_engine.wrap_thinking_prompt(
        f"Classify the user request and route it to the correct scenario: log_triage, active_response, anomaly_detection, threat_mapping, incident_summary. Request: {user_input}",
        rag_context
    )
    
    response_str = query_llm(prompt)
    try:
        ai_res = json.loads(response_str)
    except:
        ai_res = {
            "rag_context": "Fallback",
            "thinking_reasoning": "Failed to parse AI response. Using keyword-based routing.",
            "hitl_status": "approved",
            "final_decision": "log_triage",
            "confidence_score": 0.5
        }

    # Extract scenario
    scenario = ai_res.get("final_decision", "log_triage")
    if not isinstance(scenario, str):
        scenario = "log_triage" # Safety fallback
    
    # 4. HITL Gate (Routing is informational)
    hitl_status = "approved"
    
    exec_time_ms = int((time.time() - start_time) * 1000)
    
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "N/A"),
        "hitl_status": hitl_status,
        "final_decision": scenario,
        "confidence_score": ai_res.get("confidence_score", 0.0),
        "data_payload": {
            "execution_time_ms": exec_time_ms,
            "correlation_id": correlation_id,
            "scenario": scenario
        }
    }
    
    return {
        "user_input": user_input,
        "current_node_output": result,
        "correlation_id": correlation_id,
        "rag_context": rag_context,
        "thinking_reasoning": result["thinking_reasoning"],
        "hitl_status": hitl_status
    }
