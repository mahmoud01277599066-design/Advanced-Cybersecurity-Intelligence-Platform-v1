import sys
import os

# Add root to path
ROOT_DIR = os.getcwd()
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.hitl_gate import hitl_gate

def simulate_intercept():
    print("\n--- SIMULATING SOC HI-FIDELITY INTERCEPT ---\n")
    
    # Mock data exactly matching the user's screenshot context
    pod_name = "Source Scanner Pod"
    thoughts = "[Source Scanner Pod] Starting live audit of directory: vulnerable_app_real_world. Scanned 1 files (app.py). AI identified 1 potential vulnerabilities."
    proposed_action = "Proceed to Routing (Task Distribution)"
    
    metadata = {
        "findings": 1,
        "severity": "9.0 (CRITICAL)",
        "file": "app.py"
    }
    
    # Trigger the intercept
    decision = hitl_gate.terminal_ui_intercept(pod_name, thoughts, proposed_action, metadata)
    
    print(f"\n[SYSTEM] Final decision based on operator input: {decision}")

if __name__ == "__main__":
    simulate_intercept()
