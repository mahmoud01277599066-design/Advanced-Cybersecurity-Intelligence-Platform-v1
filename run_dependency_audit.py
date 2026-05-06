"""
DevSecOps Scenario: Dependency Auditor
Executes the Software Composition Analysis workflow on a real directory.
"""

import sys
import os
import io
import time
from typing import Dict, Any

# Fix Windows console encoding for emoji/unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Ensure project root is on sys.path 
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.devsecops.core_orchestrator.main_graph import wrap_node_with_json_logger, export_pipeline_execution
from modules.devsecops.core_orchestrator.state_schema import INITIAL_STATE
from modules.devsecops.pods.dependency_auditor_pod import dependency_auditor_node
from modules.devsecops.pods.professional_report_pod import professional_report_node

# Terminal styling
class C:
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"
    CYAN     = "\033[36m"
    WHITE    = "\033[37m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    GRAY     = "\033[90m"

def print_banner():
    banner = f"""
{C.CYAN}{C.BOLD}
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                 ACIP DEVSECOPS - REAL-WORLD SCENARIO                         ║
    ║                         Dependency Auditor Workflow                          ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
{C.RESET}"""
    print(banner)

def print_result(pod_name: str, state: Dict[str, Any]):
    print(f"\n    🔧 {C.BRIGHT_GREEN}{C.BOLD}[Pod] {pod_name}{C.RESET}")
    print(f"    {C.GRAY}{'·' * 60}{C.RESET}")
    
    thought = state.get("ai_thought_process", "")
    print(f"      {C.BRIGHT_MAGENTA}💭 AI Thought Process:{C.RESET}")
    
    words = thought.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > 64:
            print(f"         {C.DIM}{line}{C.RESET}")
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        print(f"         {C.DIM}{line}{C.RESET}")
        
    print(f"\n      {C.CYAN}▸ Findings Detected:{C.RESET} {C.BOLD}{len(state.get('parsed_findings', []))}{C.RESET}")
    for idx, f in enumerate(state.get('parsed_findings', []), 1):
        print(f"           {C.DIM}[{idx}] {f['finding_id']} (Severity: {f['tool_severity']}){C.RESET}")

def main():
    print_banner()
    start_time = time.time()
    
    # Target directory is the vulnerable app we created
    target_dir = os.path.join(PROJECT_ROOT, "vulnerable_app_real")
    print(f"    {C.CYAN}▸ Target Environment:{C.RESET} {target_dir}")
    print(f"    {C.CYAN}▸ Connecting and initiating SCA Scan...{C.RESET}\n")
    
    # 1. Initialize State
    state = INITIAL_STATE.copy()
    state["data_payload"]["directory_path"] = target_dir
    
    # Wrap nodes to save JSON logs
    wrapped_dependency_auditor = wrap_node_with_json_logger("dependency_auditor", dependency_auditor_node)
    wrapped_professional_report = wrap_node_with_json_logger("professional_report_scenario", professional_report_node)
    
    # 2. Run Dependency Auditor Pod
    print(f"    {C.BRIGHT_YELLOW}Executing Dependency Auditor Node...{C.RESET}")
    # We simulate LangGraph node transition by passing and merging state
    auditor_result = wrapped_dependency_auditor(state)
    state.update(auditor_result)
    print_result("Dependency Auditor Pod", state)
    
    # 3. Run Professional Report Pod
    print(f"\n    {C.BRIGHT_YELLOW}Executing Professional Reporting Node...{C.RESET}")
    report_result = wrapped_professional_report(state)
    state.update(report_result)
    print_result("Professional Report Pod", state)
    
    # Summary
    end_time = time.time()
    
    print(f"\n    {C.BRIGHT_GREEN}✓ SCENARIO COMPLETED SUCCESSFULLY{C.RESET} in {(end_time - start_time):.2f}s")
    print(f"    Report generated at: {C.CYAN}SECURITY_AUDIT_REPORT.md{C.RESET}")
    
    # 4. Export Master Pipeline Execution JSON
    export_pipeline_execution(state)

if __name__ == "__main__":
    main()
