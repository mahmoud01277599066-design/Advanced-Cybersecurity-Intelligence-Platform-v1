import json
import sys
import os

# ROOT_DIR setup
ROOT_DIR = r"c:\Advanced-Cybersecurity-Intelligence-Platform-Devsecops"
sys.path.append(ROOT_DIR)

from modules.soc_defense.pods.shift_report_pod import shift_report_node

def run_deterministic_api_test():
    print("Starting Hardened Deterministic SOC Intelligence API Verification...")
    print("="*70)
    
    # 🧪 Generator for 12,100 mock SOC events
    print("   [GEN] Generating 12,100 mock SOC events...")
    mock_alerts = []
    for i in range(12100):
        # Every 100th event is a Critical Exploitation
        if i % 100 == 0:
            mock_alerts.append({
                "correlation_id": f"attack_{i}",
                "src_ip": f"192.168.1.{i % 254}",
                "pattern": "Exploitation",
                "mitre": ["T1190"],
                "risk_score": 9.5,
                "classification": "True Positive"
            })
        else:
            mock_alerts.append({
                "correlation_id": f"recon_{i}",
                "src_ip": f"10.0.0.{i % 254}",
                "pattern": "Reconnaissance",
                "mitre": ["T1595"],
                "risk_score": 4.0,
                "classification": "False Positive"
            })
            
    state = {
        "shift_id": "SHIFT-DET-2026-04-16",
        "current_node_output": {
            "shift_id": "SHIFT-DET-2026-04-16",
            "total_events": 12100,
            "alerts": mock_alerts,
            "summary_stats": {
                "high_risk": 121,
                "medium_risk": 0,
                "low_risk": 11979,
                "true_positive": 121,
                "false_positive": 11979
            },
            "soar_actions": [
                "IP blocked via firewall",
                "WAF rule deployed",
                "Cloud security group updated"
            ]
        }
    }
    
    print("   [EXEC] Invoking deterministic shift_report_node...")
    result = shift_report_node(state)
    report = result.get("current_node_output", {})
    
    # 🔍 1. Telemetry Format Validation
    print("   [CHECK] Validating Telemetry Format (executive_summary)...")
    summary = report.get("executive_summary", "")
    expected_start = "EVENTS=12100 | TP=121 | HIGH=121 | MITRE="
    if summary.startswith(expected_start):
        print("   [PASS] Telemetry string follows strict KEY=VALUE format.")
    else:
        print(f"   [FAIL] Telemetry string mismatch. Got: {summary}")

    # 🔍 2. SOAR Action Normalization
    print("   [CHECK] Validating SOAR Action Normalization (Strict Enums)...")
    soar_actions = report.get("soar_actions_summary", [])
    allowed = ["firewall_block", "waf_block", "cloud_security_group_update", "manual_response"]
    if all(a in allowed for a in soar_actions) and len(soar_actions) == 3:
        print("   [PASS] SOAR actions correctly mapped to strict enums.")
    else:
        print(f"   [FAIL] Unauthorized SOAR actions found: {soar_actions}")

    # 🔍 3. Security Posture Logic
    print("   [CHECK] Validating Deterministic Posture (Critical if > 3 criticals)...")
    if report.get("security_posture") == "CRITICAL":
        print("   [PASS] Posture correctly identified as CRITICAL (121 alerts).")
    else:
        print(f"   [FAIL] Posture calculation error. Got: {report.get('security_posture')}")

    # 🔍 4. Fail-Fast (rejected_schema on missing_shift_data)
    print("   [CHECK] Validating Fail-Fast mechanism (missing_shift_data)...")
    bad_state_1 = {"current_node_output": {}} # Completely missing shift_id
    bad_res_1 = shift_report_node(bad_state_1)
    if bad_res_1.get("current_node_output", {}).get("status") == "rejected_schema" and \
       bad_res_1.get("current_node_output", {}).get("reason") == "missing_shift_data":
        print("   [PASS] Correctly rejected missing shift data.")
    else:
        print("   [FAIL] Fail-fast mechanism (missing_shift_data) did not trigger.")

    # 🔍 5. Fail-Fast (validation_failed on UNKNOWN shift_id)
    print("   [CHECK] Validating Fail-Fast mechanism (validation_failed on UNKNOWN ID)...")
    bad_state_2 = {"current_node_output": {"shift_id": "UNKNOWN", "total_events": 100}} # Invalid value
    bad_res_2 = shift_report_node(bad_state_2)
    if bad_res_2.get("current_node_output", {}).get("status") == "rejected_schema" and \
       bad_res_2.get("current_node_output", {}).get("reason") == "validation_failed":
        print("   [PASS] Correctly rejected UNKNOWN shift identifier.")
    else:
        print("   [FAIL] Fail-fast mechanism (validation_failed) did not trigger.")

    print("\n" + "="*70)
    print("Verification Completed.")

if __name__ == "__main__":
    run_deterministic_api_test()
