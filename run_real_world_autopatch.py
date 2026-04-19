"""
ACIP DevSecOps - Real-World Auto-Patching Scenario
=================================================
This script demonstrates the full end-to-end security pipeline on a 
vulnerable application.

Flow:
1. Discovery (Source Scanner) -> Find SQL Injection
2. Assessment (Prioritization) -> Score the risk
3. Remediation (Auto-Patcher) -> Generate the Fix
4. Compliance (Professional Report) -> Create Audit Document
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
from modules.devsecops.pods.auto_patcher_pod import auto_patcher_node
from modules.devsecops.pods.professional_report_pod import professional_report_node
from modules.devsecops.routers.sast_router import sast_router_node

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
    print("                ACIP DEVSECOPS - REAL-WORLD AUTO-PATCH SCENARIO")
    print("                   Vulnerability Detection & AI Remediation")
    print("="*80 + f"{C.RESET}\n")

def run_scenario():
    print_banner()
    
    # 1. Initialize State
    target_dir = os.path.join(PROJECT_ROOT, "vulnerable_app_real_world")
    state = INITIAL_STATE.copy()
    state["data_payload"] = {"directory_path": target_dir}
    state["messages"] = ["[Scenario] Initiating real-world audit on login module."]
    
    # Wrap nodes to ensure logging and tracing
    wrapped_scanner = wrap_node_with_json_logger("source_scanner", source_scanner_node)
    wrapped_prioritizer = wrap_node_with_json_logger("prioritization", prioritization_node)
    wrapped_patcher = wrap_node_with_json_logger("auto_patcher", auto_patcher_node)
    wrapped_reporter = wrap_node_with_json_logger("professional_report", professional_report_node)
    wrapped_router = wrap_node_with_json_logger("sast_router", sast_router_node)
    
    start_time = time.time()
    
    # --- STEP 1: Discovery ---
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 1: Discovery (Code Scanning)...{C.RESET}")
    state.update(wrapped_scanner(state))
    print(f"      Findings Detected: {len(state.get('parsed_findings', []))}")
    
    # --- STEP 1.5: Routing ---
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 1.5: Routing (Task Distribution)...{C.RESET}")
    state.update(wrapped_router(state))
    print(f"      Decision: {C.CYAN}{state.get('routing_decision')}{C.RESET}")
    
    # --- STEP 2: Assessment ---
    if state.get("parsed_findings"):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 2: Assessment (Risk Scoring)...{C.RESET}")
        state.update(wrapped_prioritizer(state))
        print(f"      Risk Score: {C.RED}{state.get('final_priority_score')}{C.RESET}")
        
        # --- STEP 3: Remediation ---
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 3: Remediation (AI Auto-Patching)...{C.RESET}")
        state.update(wrapped_patcher(state))
        print(f"      Patch Status: {C.GREEN}GENERATED{C.RESET}")
        
        # --- STEP 4: Reporting ---
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {C.YELLOW}> STEP 4: Compliance (Reporting)...{C.RESET}")
        state.update(wrapped_reporter(state))
        print(f"      Report Saved: {C.CYAN}SECURITY_AUDIT_REPORT.md{C.RESET}")
    else:
        print(f"{C.RED}FAILED: No vulnerabilities detected by AI scan.{C.RESET}")
        return

    # Finish & Export Trace Snapshot (Independent Script Log)
    end_time = time.time()
    print(f"\n{C.GREEN}{C.BOLD}SUCCESS: SCENARIO COMPLETED SUCCESSFULLY{C.RESET} in {(end_time - start_time):.2f}s")
    
    print(f"\n[ACIP] Persisting script execution metadata...")
    script_log = {
        "execution_id": f"script_run_{int(end_time)}",
        "start_time": start_time,
        "end_time": end_time,
        "duration": end_time - start_time,
        "target_dir": target_dir,
        "status": "SUCCESS"
    }
    save_agent_json("real_world_autopatch_runner", "scripts", script_log)

if __name__ == "__main__":
    run_scenario()
