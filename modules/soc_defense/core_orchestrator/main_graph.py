import json
import sys
import os
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from langgraph.graph import StateGraph, START, END
from modules.soc_defense.core_orchestrator.state import SocState

# ─── Routers ────────────────────────────────────────────────────────────────
from modules.soc_defense.routers.master_router import master_router_node
from modules.soc_defense.routers.log_triage_router import log_triage_router_node
from modules.soc_defense.routers.active_response_router import active_response_router_node
from modules.soc_defense.routers.anomaly_detection_router import anomaly_detection_router_node
from modules.soc_defense.routers.threat_mapping_router import threat_mapping_router_node
from modules.soc_defense.routers.incident_summary_router import incident_summary_router_node
from modules.soc_defense.routers.ai_triage_router import ai_triage_router_node

# ─── Pods ─────────────────────────────────────────────────────────────────────
from modules.soc_defense.pods.log_triage_pod import log_triage_node
from modules.soc_defense.pods.ai_correlation_pod import ai_correlation_node
from modules.soc_defense.pods.ai_triage_pod import ai_triage_node
from modules.soc_defense.pods.active_response_pod import active_response_node
from modules.soc_defense.pods.pro_reporting_pod import pro_reporting_node
from modules.soc_defense.pods.shift_report_pod import shift_report_node

def hitl_gate_node(state):
    """
    Dedicated node for HITL Wait state.
    In a real production system, this would wait for an external signal.
    For this demo, we just finalize with the pending status.
    """
    print(">>> [HITL GATE] Action requires human approval. Execution paused.")
    return state

def finalize_output(state):
    """Terminal node — ensures final output follows the mandatory schema."""
    final = state.get("current_node_output", {})
    
    # Sync top-level state fields to the output
    final["hitl_status"] = state.get("hitl_status", final.get("hitl_status", "approved"))
    final["rag_context"] = state.get("rag_context", final.get("rag_context", "N/A"))
    final["thinking_reasoning"] = state.get("thinking_reasoning", final.get("thinking_reasoning", "N/A"))
    
    return {
        "current_node_output": final,
        "hitl_status": final["hitl_status"]
    }

# ─── Routing Logic ────────────────────────────────────────────────────────────

def check_hitl(state):
    """Conditional edge to check if we should pause for HITL."""
    if state.get("hitl_status") == "pending":
        return "hitl_gate"
    return "continue"

def master_to_scenario(state):
    output = state.get("current_node_output", {})
    scenario = output.get("final_decision", "")
    
    routes = {
        "log_triage":       "log_triage_router",
        "active_response":  "active_response_router",
        "anomaly_detection":"anomaly_detection_router",
        "threat_mapping":   "threat_mapping_router",
        "incident_summary": "incident_summary_router",
    }
    return routes.get(scenario, "finalize")

def build_soc_graph():
    workflow = StateGraph(SocState)
    
    # ── Nodes ──────────────────────────────────────────────────────────────────
    workflow.add_node("master_router",              master_router_node)
    workflow.add_node("log_triage_router",          log_triage_router_node)
    workflow.add_node("active_response_router",     active_response_router_node)
    workflow.add_node("anomaly_detection_router",   anomaly_detection_router_node)
    workflow.add_node("threat_mapping_router",      threat_mapping_router_node)
    workflow.add_node("incident_summary_router",    incident_summary_router_node)
    
    workflow.add_node("log_triage_pod",             log_triage_node)
    workflow.add_node("ai_correlation",             ai_correlation_node)
    workflow.add_node("ai_triage_router",           ai_triage_router_node)
    workflow.add_node("active_response_pod",        active_response_node)
    workflow.add_node("pro_reporter",               pro_reporting_node)
    workflow.add_node("shift_report",               shift_report_node)
    
    workflow.add_node("hitl_gate",                  hitl_gate_node)
    workflow.add_node("finalize",                   finalize_output)
    
    # ── Edges ──────────────────────────────────────────────────────────────────
    workflow.add_edge(START, "master_router")
    
    # Master -> Scenario
    workflow.add_conditional_edges(
        "master_router",
        master_to_scenario,
        {
            "log_triage_router":        "log_triage_router",
            "active_response_router":   "active_response_router",
            "anomaly_detection_router": "anomaly_detection_router",
            "threat_mapping_router":    "threat_mapping_router",
            "incident_summary_router":  "incident_summary_router",
            "finalize":                 "finalize"
        }
    )
    
    # Log Triage Path
    workflow.add_edge("log_triage_router", "log_triage_pod")
    workflow.add_edge("log_triage_pod", "ai_correlation")
    workflow.add_edge("ai_correlation", "ai_triage_router")
    
    # HITL Check after Triage Router (where risk might be identified)
    workflow.add_conditional_edges(
        "ai_triage_router",
        check_hitl,
        {"hitl_gate": "hitl_gate", "continue": "active_response_pod"}
    )
    
    # HITL Check after Active Response (the most risky node)
    workflow.add_conditional_edges(
        "active_response_pod",
        check_hitl,
        {"hitl_gate": "hitl_gate", "continue": "pro_reporter"}
    )
    
    # Closing paths
    workflow.add_edge("pro_reporter", "finalize")
    workflow.add_edge("shift_report", "finalize")
    workflow.add_edge("hitl_gate", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()

if __name__ == "__main__":
    app = build_soc_graph()
    print(">>> SOC Orchestrator (RAG + Thinking + HITL) Ready.")
    # Test with risky request
    test_req = "DDoS attack from 10.0.0.5. BLOCK IT NOW."
    res = app.invoke({"user_input": test_req})
    print(json.dumps(res.get("current_node_output", {}), indent=2))
