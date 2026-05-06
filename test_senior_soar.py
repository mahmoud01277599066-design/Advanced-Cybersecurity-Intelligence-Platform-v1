import json
import sys
import os
import time
import sqlite3
from datetime import datetime, timedelta

# ROOT_DIR setup
ROOT_DIR = r"c:\Advanced-Cybersecurity-Intelligence-Platform-Devsecops"
sys.path.append(ROOT_DIR)

from modules.soc_defense.pods.active_response_pod import active_response_node
from modules.soc_defense.core.database import init_db, DB_PATH

def run_advanced_soar_tests():
    print("Starting Enterprise SOAR Engine Verification Library...")
    print("="*70)
    
    init_db() # Ensure tables exist
    
    # helper to clean DB for clean starts
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM active_rules")
    conn.commit()
    conn.close()

    scenarios = [
        {
            "id": 1,
            "name": "High Risk + High Confidence (Valid Block)",
            "state": {
                "correlation_id": "attack_999",
                "src_ip": "1.2.3.4",
                "attack_stage": "Exploitation",
                "classification": "True Positive",
                "risk_score": 9.5,
                "confidence": 0.95
            },
            "expected_action": "pending_approval"
        },
        {
            "id": 2,
            "name": "Low Risk Threshold (Risk = 6.5)",
            "state": {
                "correlation_id": "recon_001",
                "src_ip": "1.2.3.5",
                "attack_stage": "Reconnaissance",
                "classification": "True Positive",
                "risk_score": 6.5,
                "confidence": 0.8
            },
            "expected_action": "no_action"
        },
        {
            "id": 3,
            "name": "Internal IP Safety Gate (10.0.0.1)",
            "state": {
                "correlation_id": "internal_noise",
                "src_ip": "10.0.0.1",
                "attack_stage": "Exploitation",
                "classification": "True Positive",
                "risk_score": 9.0,
                "confidence": 0.9
            },
            "expected_action": "no_action"
        },
        {
            "id": 4,
            "name": "Duplicate Active Rule (Registry Lock)",
            "state": {
                "correlation_id": "attack_999_repeat",
                "src_ip": "1.2.3.4", # Same as Scenario 1
                "attack_stage": "Exploitation",
                "classification": "True Positive",
                "risk_score": 9.5,
                "confidence": 0.95
            },
            "expected_action": "no_action"
        },
        {
            "id": 5,
            "name": "Expired Rule Lifecycle (Allow Re-block)",
            "state": {
                "correlation_id": "attack_999_reblock",
                "src_ip": "1.2.3.4",
                "attack_stage": "Exploitation",
                "classification": "True Positive",
                "risk_score": 9.5,
                "confidence": 0.95
            },
            "setup": lambda: simulate_expiry("1.2.3.4"),
            "expected_action": "pending_approval"
        },
        {
            "id": 6,
            "name": "Same IP + Different Attack Stage (Contextual Block)",
            "state": {
                "correlation_id": "attack_stage_shift",
                "src_ip": "1.2.3.4",
                "attack_stage": "Data Exfiltration", # Different from Exploitation
                "classification": "True Positive",
                "risk_score": 10.0,
                "confidence": 1.0
            },
            "expected_action": "pending_approval"
        }
    ]

    for scenario in scenarios:
        print(f"\n[RUNNING Scenario {scenario['id']}] {scenario['name']}")
        
        if "setup" in scenario:
            scenario["setup"]()
            
        result = active_response_node(scenario["state"])
        out = result.get("current_node_output", {})
        action = out.get("action")
        
        if action == scenario["expected_action"]:
            print(f"PASS: Action correctly determined as {action}")
        else:
            print(f"FAIL: Action was {action}, expected {scenario['expected_action']}")
            print(f"Reason: {out.get('reason')}")


    print("\n" + "="*70)
    print("Verification Completed.")

def simulate_expiry(ip):
    print(f"   (Simulating rule expiry for {ip}...)")
    conn = sqlite3.connect(DB_PATH)
    past_time = (datetime.now() - timedelta(minutes=15)).isoformat()
    conn.execute("UPDATE active_rules SET expire_at = ? WHERE src_ip = ?", (past_time, ip))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_advanced_soar_tests()
