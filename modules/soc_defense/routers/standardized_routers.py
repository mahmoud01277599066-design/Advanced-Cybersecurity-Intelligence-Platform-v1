import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

def active_response_router_node(state):
    """
    Standardized Active Response Router.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Active Response routing logic.")
    prompt = intelligence_engine.wrap_thinking_prompt(
        f"Route this active response request to the correct pod (active_response_pod). Input: {json.dumps(state['current_node_output'])}",
        rag_context
    )
    ai_res = json.loads(query_llm(prompt))
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

def anomaly_detection_router_node(state):
    """
    Standardized Anomaly Detection Router.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Anomaly detection routing.")
    prompt = intelligence_engine.wrap_thinking_prompt("Route to anomaly detection pod.", rag_context)
    ai_res = json.loads(query_llm(prompt))
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing."),
        "hitl_status": "approved",
        "final_decision": "network_analysis",
        "confidence_score": 1.0,
        "data_payload": {"pod name": "network_analysis_pod"}
    }
    return {"current_node_output": result}

def incident_summary_router_node(state):
    """
    Standardized Incident Summary Router.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Incident Summary routing.")
    prompt = intelligence_engine.wrap_thinking_prompt("Route to reporting pod.", rag_context)
    ai_res = json.loads(query_llm(prompt))
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing."),
        "hitl_status": "approved",
        "final_decision": "pro_reporter",
        "confidence_score": 1.0,
        "data_payload": {"pod name": "pro_reporting_pod"}
    }
    return {"current_node_output": result}

def log_triage_router_node(state):
    """
    Standardized Log Triage Router.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Log Triage routing.")
    prompt = intelligence_engine.wrap_thinking_prompt("Route to normalization pod.", rag_context)
    ai_res = json.loads(query_llm(prompt))
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing."),
        "hitl_status": "approved",
        "final_decision": "log_triage_pod",
        "confidence_score": 1.0,
        "data_payload": {"pod name": "log_triage_pod"}
    }
    return {"current_node_output": result}

def threat_mapping_router_node(state):
    """
    Standardized Threat Mapping Router.
    """
    start_time = time.time()
    rag_context = intelligence_engine.get_rag_context("Threat Mapping routing.")
    prompt = intelligence_engine.wrap_thinking_prompt("Route to technique mapper pod.", rag_context)
    ai_res = json.loads(query_llm(prompt))
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_res.get("thinking_reasoning", "Routing."),
        "hitl_status": "approved",
        "final_decision": "technique_mapper",
        "confidence_score": 1.0,
        "data_payload": {"pod name": "technique_mapper_pod"}
    }
    return {"current_node_output": result}
