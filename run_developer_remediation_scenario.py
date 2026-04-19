"""
ACIP DevSecOps - Developer Remediation Reporting Scenario
======================================================
This script demonstrates the generation of a high-quality technical 
remediation report for developers encountering security vulnerabilities.

Target: dev_vulnerability_lab/ping_service.py (Command Injection)
Flow: Discovery -> Assessment -> Technical Guidance
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.devsecops.core_orchestrator.main_graph import wrap_node_with_json_logger
from modules.devsecops.core_orchestrator.state_schema import INITIAL_STATE
from modules.devsecops.src.core.logger import save_agent_json
from modules.devsecops.pods.source_scanner_pod import source_scanner_node
from modules.devsecops.pods.prioritization_pod import prioritization_node
from modules.devsecops.pods.developer_remediation_pod import developer_remediation_node

# Terminal Colors
class C:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    print(f"\n{C.CYAN}{C.BOLD}" + "="*80)
    print("                ACIP DEVSECOPS - DEVELOPER REMEDIATION SCENARIO")
    print("                   Expert AI Guidance for Secure Coding")
    print("="*80 + f"{C.RESET}\n")

def run_scenario():
    print_banner()
    
    # 1. Initialize State
    target_dir = os.path.join(PROJECT_ROOT, "dev_vulnerability_lab")
    state = INITIAL_STATE.copy()
    state["data_payload"] = {"directory_path": target_dir}
    state["messages"] = ["[Scenario] Starting developer guidance workflow for new lab."]
    
    # Wrap nodes for Microservice Logging
    wrapped_scanner = wrap_node_with_json_logger("source_scanner", source_scanner_node)
    wrapped_prioritizer = wrap_node_with_json_logger("prioritization", prioritization_node)
    wrapped_remediation_pod = wrap_node_with_json_logger("developer_remediation", developer_remediation_node)
    
    start_time = time.time()
    
    # --- STEP 1: Discovery ---
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 1: Discovery (Command Injection Detection)...{C.RESET}")
    state.update(wrapped_scanner(state))
    print(f"      Findings Detected: {len(state.get('parsed_findings', []))}")
    
    # --- STEP 2: Assessment ---
    if state.get("parsed_findings"):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 2: Assessment (Risk Impact)...{C.RESET}")
        state.update(wrapped_prioritizer(state))
        print(f"      Risk Score: {C.RED}{state.get('final_priority_score')}{C.RESET}")
        
        # --- STEP 3: Technical Guidance ---
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 3: Expert Guidance (Generating Technical Report)...{C.RESET}")
        state.update(wrapped_remediation_pod(state))
        print(f"      Guide Generated: {C.GREEN}DEVELOPER_REMEDIATION_GUIDE.md{C.RESET}")
    else:
        print(f"{C.RED}FAILED: No vulnerabilities detected in the lab environment.{C.RESET}")
        return

    # Finish & Independent Script Persistence
    end_time = time.time()
    print(f"\n{C.GREEN}{C.BOLD}SUCCESS: DEVELOPER REMEDIATION SCENARIO COMPLETED{C.RESET} in {(end_time - start_time):.2f}s")
    
    print(f"\n[ACIP] Persisting script execution metadata...")
    script_log = {
        "execution_id": f"dev_remediation_{int(end_time)}",
        "duration": end_time - start_time,
        "target_dir": target_dir,
        "report_generated": "DEVELOPER_REMEDIATION_GUIDE.md",
        "status": "COMPLETED"
    }
    save_agent_json("developer_remediation_runner", "scripts", script_log)

if __name__ == "__main__":
    run_scenario()
