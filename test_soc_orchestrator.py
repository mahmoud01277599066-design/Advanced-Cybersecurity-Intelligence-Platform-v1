import json
from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph

def run_test_scenarios():
    print("[INFO] Initializing SOC & Defense Orchestrator Testing...")
    app = build_soc_graph()
    
    scenarios = [
        {
            "name": "Scenario 1: Log Triage (Wazuh)",
            "input": "I need you to pull the latest security logs from the system for analysis."
        },
        {
            "name": "Scenario 2: Active Response (Firewall)",
            "input": "Confirmed severe SQL injection from 10.0.0.55! Block it immediately!"
        },
        {
            "name": "Scenario 3: Anomaly Detection (Network)",
            "input": "I noticed some weird network behavior on the dmz, a bunch of syn packets hitting various ports. Can you analyze the pcap?"
        },
        {
            "name": "Scenario 4: Threat Mapping (MITRE)",
            "input": "We have an SSH brute force alert (rule 5716). Map this to MITRE ATT&CK."
        },
        {
            "name": "Scenario 5: Incident Summary (Reporting)",
            "input": "Generate an executive summary of the recent SOC activity and alerts we investigated."
        }
    ]

    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"[TEST] Testing {scenario['name']}")
        print(f"[INPUT] User Input: {scenario['input']}")
        print(f"{'='*60}\n")
        
        try:
            # Invoke the LangGraph Orchestrator
            result = app.invoke({"user_input": scenario['input']})
            
            # Extract and display the ACIP Standardized JSON Output
            output = result.get("current_node_output", {})
            print(json.dumps(output, indent=2))
            
            # Visual indicator for success
            if output.get("status") == "success":
                print("\n[SUCCESS] Scenario completed with ACIP Standard JSON.")
            else:
                print("\n[WARNING] Scenario returned an error or unexpected status.")
                
        except Exception as e:
            print(f"\n[ERROR] Error executing scenario: {str(e)}")

if __name__ == "__main__":
    run_test_scenarios()
