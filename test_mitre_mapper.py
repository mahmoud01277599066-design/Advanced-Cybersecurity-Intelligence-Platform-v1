import json
import sys
import os

# ROOT_DIR setup
ROOT_DIR = r"c:\Advanced-Cybersecurity-Intelligence-Platform-Devsecops"
sys.path.append(ROOT_DIR)

from modules.soc_defense.pods.technique_mapper_pod import technique_mapper_node

def run_mitre_mapper_test():
    print("Starting RAG MITRE Threat Mapping Verification...")
    print("="*70)

    
    # CASE 1: Multi-stage Attack alerts
    state = {
        "correlation_id": "attack_001",
        "current_node_output": {
            "alerts": [
                {
                    "src_ip": "10.0.0.5",
                    "event": "port scan detected on multiple ports",
                    "timestamp": "2026-04-16T10:00:00Z"
                },
                {
                    "src_ip": "10.0.0.5",
                    "event": "multiple failed login attempts",
                    "timestamp": "2026-04-16T10:05:00Z"
                },
                {
                    "src_ip": "10.0.0.5",
                    "event": "SQL injection payload detected",
                    "timestamp": "2026-04-16T10:10:00Z"
                }
            ]
        }
    }
    
    print("   [INPUT] Multi-stage Alert sequence (Recon -> Creds -> Exploit)")
    result = technique_mapper_node(state)
    out = result.get("current_node_output", {})
    
    # 🕵️ Validation
    chain = out.get("attack_chain", [])
    mappings = out.get("mitre_mapping", [])
    risk = out.get("risk_assessment", {})
    
    print("\n   [RESULT] Attack Chain:")
    print(f"   { ' -> '.join(chain) or 'No chain detected' }")
    
    print("\n   [RESULT] MITRE Mappings:")
    for m in mappings:
        print(f"   - {m.get('event')}: {m.get('technique_id')} ({m.get('technique_name')}) | Confidence: {m.get('confidence')}")
        
    print("\n   [RESULT] Risk Assessment:")
    print(f"   Score: {risk.get('overall_risk_score')} / 10.0")
    print(f"   Level: {risk.get('risk_level')}")
    print(f"   Stage: {risk.get('attack_stage')}")
    
    print("\n   [RESULT] RAG Sources:")
    print(f"   {', '.join(out.get('rag_sources', []))}")
    
    # Logic Validation
    success = True
    if len(mappings) == 3:
        print("\nPASS: Successfully mapped all 3 alerts via RAG KB.")
    else:
        print("\nFAIL: Incomplete mapping.")
        success = False
        
    if risk.get("overall_risk_score", 0) > 7.0:
        print("PASS: Correctly identified High Risk score.")
    else:
        print("FAIL: Risk score calculation too low.")
        success = False

    print("\n" + "="*70)
    print("Verification Completed.")

if __name__ == "__main__":
    run_mitre_mapper_test()
