import json
import os
import sys
import time

# Add root to sys.path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph

def test_production_log_triage():
    print("Starting Production Log Triage System Test...", flush=True)
    
    # Raw Wazuh Alert (as provided by USER)
    wazuh_alert = {
        "rule_id": "31151",
        "description": "SQL injection attempt detected",
        "src_ip": "192.168.1.10",
        "full_log": "GET /login?user=admin' OR 1=1 --",
        "timestamp": "2026-04-13T10:00:00Z",
        "agent": "web-server-01"
    }
    
    # The input for the master_router to classify as log_triage
    user_input = f"Log Triage requested for this alert: {json.dumps(wazuh_alert)}"
    
    print("\n--- Invoking LangGraph Orchestrator ---", flush=True)
    app = build_soc_graph()
    initial_state = {"user_input": user_input}
    
    # Run the graph
    print("Graph execution started...", flush=True)
    result_state = app.invoke(initial_state)
    print("Graph execution finished.", flush=True)
    
    print("\n--- Processing Complete ---", flush=True)
    
    final_output = result_state.get("current_node_output", {})
    print(f"Final Node Status: {final_output.get('status')}", flush=True)
    
    # Verification of SOC Logs (This is the best way to verify each stage)
    print("\n--- Verifying SOC JSON Logs (The Audit Trail) ---", flush=True)
    
    log_dirs = {
        "Normalization Phase (log_triage_pod)": os.path.join(ROOT_DIR, "logs", "pods", "log_triage_pod"),
        "Classification Phase (ai_triage_router)": os.path.join(ROOT_DIR, "logs", "router", "ai_triage_router")
    }
    
    success = True
    found_classification = "Unknown"

    for layer, path in log_dirs.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith(".json")]
            if files:
                latest_file = max([os.path.join(path, f) for f in files], key=os.path.getmtime)
                print(f"[OK] Found {layer} log: {os.path.basename(latest_file)}", flush=True)
                
                # Extract classification from the router log
                if "ai_triage_router" in path:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                        found_classification = log_data.get("output", {}).get("classification", "Unknown")
                        print(f"     Decision: {found_classification}", flush=True)
                        print(f"     Reasoning: {str(log_data.get('output', {}).get('reasoning'))[:100]}...", flush=True)
            else:
                print(f"[FAIL] No {layer} logs found in {path}", flush=True)
                success = False
        else:
            print(f"[FAIL] {layer} Log directory missing: {path}", flush=True)
            success = False

    if success and found_classification == "True Positive":
        print("\nTEST SUCCESSFUL: Pipeline executed correctly and identified the threat.", flush=True)
        return True
    else:
        print(f"\nTEST FAILED: Issues found in pipeline or classification. (Classification: {found_classification})", flush=True)
        return False

if __name__ == "__main__":
    if test_production_log_triage():
        sys.exit(0)
    else:
        sys.exit(1)
