import json
import os
import sys
import time

# Add root to sys.path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph

def test_advanced_correlation_system():
    print("Starting ADVANCED Production SOC Correlation Pipeline Test...", flush=True)
    
    # 1. Multi-Alert Input (Attack Pattern: Recon -> Brute Force -> Exploit)
    multi_alerts = [
        {
            "rule_id": "1001",
            "description": "Nmap network scan detected",
            "src_ip": "10.0.0.51",
            "user_agent": "nmap/7.80",
            "endpoint": "/",
            "timestamp": "2026-04-13T10:00:01Z",
            "agent": "firewall-01"
        },
        {
            "rule_id": "2001",
            "description": "Failed login attempt (root)",
            "src_ip": "10.0.0.51",
            "user_agent": "Mozilla/5.0",
            "endpoint": "/login",
            "timestamp": "2026-04-13T10:00:05Z",
            "agent": "web-server-01"
        },
        {
            "rule_id": "31151",
            "description": "SQL injection attempt detected",
            "src_ip": "10.0.0.51",
            "user_agent": "Mozilla/5.0",
            "endpoint": "/api/v1/search",
            "full_log": "GET /search?id=1' OR 1=1 --",
            "timestamp": "2026-04-13T10:00:10Z",
            "agent": "web-server-01"
        }
    ]
    
    user_input = f"Log Triage for multi-stage alerts: {json.dumps(multi_alerts)}"
    
    print("\n--- Invoking LangGraph Orchestrator (Advanced Scoring Engine) ---", flush=True)
    app = build_soc_graph()
    initial_state = {"user_input": user_input, "time_window": 30}
    
    # Run the graph
    print("Graph execution started...", flush=True)
    result_state = app.invoke(initial_state)
    print("Graph execution finished.", flush=True)
    
    print("\n--- Correlation & Triage Processing Complete ---", flush=True)
    
    final_output = result_state.get("current_node_output", {})
    payload = final_output.get("data_payload", {})
    diagnostics = payload.get("diagnostics", {})
    
    correlation_id = result_state.get("correlation_id")
    risk_score = result_state.get("risk_score", 0.0)
    classification = result_state.get("classification", "Unknown")
    
    # Get summary from data_payload
    summary = payload.get("summary", {})
    if not summary: # Fallback to state if payload missed it (though it should be there now)
        summary = result_state.get("event_summary", {})
    pattern = payload.get("pattern_detected", "Unknown")
    
    print(f"Correlation ID: {correlation_id}", flush=True)
    print(f"Primary Pattern: {pattern}", flush=True)
    print(f"AI Decision: {classification}", flush=True)
    print(f"Final Risk Score: {risk_score} / 10.0", flush=True)
    
    # Display Summary (Fixed Key Access)
    total = summary.get("total_attempts", 0)
    dur = summary.get("duration_seconds", 0)
    print(f"Timeline Summary: {total} attempts over {dur} seconds.", flush=True)
    print(f"Diagnostics: Dampening={diagnostics.get('dampening')}, ConfWeight={diagnostics.get('conf_weight')}", flush=True)
    
    time.sleep(2) # Disk sync

    # Verification of SOC Logs
    print("\n--- Verifying SOC JSON Logs (Correlation Audit) ---", flush=True)
    
    log_dirs = {
        "Grouping Phase": os.path.join(ROOT_DIR, "logs", "pods", "log_triage_pod"),
        "Correlation (Engine)": os.path.join(ROOT_DIR, "logs", "pods", "ai_correlation_pod"),
        "Final Decision (Scoring)": os.path.join(ROOT_DIR, "logs", "router", "ai_triage_router")
    }
    
    success = True
    for layer, path in log_dirs.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith(".json")]
            found_log = False
            for f in files:
                try:
                    with open(os.path.join(path, f), 'r', encoding='utf-8') as log_file:
                        if correlation_id in log_file.read():
                            print(f"[OK] Found {layer} log for ID {correlation_id}", flush=True)
                            found_log = True
                            break
                except: continue
            if not found_log:
                print(f"[FAIL] No logs found for ID {correlation_id} in {layer}", flush=True)
                success = False
        else:
            print(f"[FAIL] Directory missing: {layer}", flush=True)
            success = False

    # Validation Logic
    # We expect 'Exploitation' to override 'Recon'
    # We expect risk_score to be reasonably high for SQLi but dampened if scanners found
    if success and pattern == "Exploitation" and classification == "True Positive":
        print("\nSUCCESS: Advanced Correlation and Scoring Logic Verified.", flush=True)
        return True
    else:
        print(f"\nFAILURE: Issues in scoring logic. Pattern: {pattern}, Risk: {risk_score}", flush=True)
        return False

if __name__ == "__main__":
    if test_advanced_correlation_system():
        sys.exit(0)
    else:
        sys.exit(1)
