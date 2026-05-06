import sys
import os

# Add root to path
ROOT_DIR = os.getcwd()
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.hitl_gate import hitl_gate
from modules.soc_defense.pods.rag_engine import rag_engine_node
from modules.soc_defense.pods.log_triage_pod import log_triage_node
from modules.soc_defense.pods.ai_correlation_pod import ai_correlation_node
from modules.soc_defense.pods.active_response_pod import active_response_node

def run_pipeline():
    # Initial State
    state = {
        "user_input": "8.8.8.8",
        "events": ["port_scan", "failed_login", "sql_injection"],
        "current_node_output": {}
    }

    print("\n>>> STARTING SOC PIPELINE (INTERACTIVE MODE)")

    # 0. RAG Engine
    res = rag_engine_node(state)
    state.update(res)
    hitl_gate("RAG Engine (MITRE Mapping)", state.get("current_node_output", {}))

    # 1. Log Triage
    res = log_triage_node(state)
    state.update(res)
    hitl_gate("Log Triage", state.get("current_node_output", {}))

    # 2. Correlation
    res = ai_correlation_node(state)
    state.update(res)
    hitl_gate("Correlation", state.get("current_node_output", {}))

    # 3. Active Response
    res = active_response_node(state)
    state.update(res)
    hitl_gate("Active Response", state.get("current_node_output", {}))

    print("\n🎯 PIPELINE COMPLETE")

if __name__ == "__main__":
    run_pipeline()
