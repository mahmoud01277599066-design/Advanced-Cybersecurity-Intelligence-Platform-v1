"""
ACIP DevSecOps - Mandatory RAG SOC Scenario
========================================
This script demonstrates the full 5-step RAG pipeline:
1. Retrieval (Knowledge Base Search)
2. Context Injection (Enriching Input)
3. Routing (Decision Making)
4. Execution (Scanning/Automation)
5. Analysis (Intelligence Gathering)

Target: dev_vulnerability_lab/ping_service.py
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.devsecops.core_orchestrator.main_graph import devsecops_graph
from modules.devsecops.core_orchestrator.state_schema import INITIAL_STATE

# Terminal Colors
class C:
    GOLD = '\033[38;5;214m'
    BLUE = '\033[94m'
    YELL = '\033[93m'
    GREN = '\033[92m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    print(f"\n{C.GOLD}{C.BOLD}" + "="*80)
    print("                ACIP SOC ORCHESTRATOR - MANDATORY RAG FLOW")
    print("              (Retrieval -> Injection -> Route -> Execute -> Analyze)")
    print("="*80 + f"{C.RESET}\n")

def run_rag_scenario():
    print_banner()
    
    # 1. Initialize State with a high-level target
    target_dir = os.path.join(PROJECT_ROOT, "dev_vulnerability_lab")
    state = INITIAL_STATE.copy()
    state["data_payload"] = {"directory_path": target_dir}
    state["messages"] = ["[SOC Orchestrator] Triggering RAG-first security audit."]
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {C.BOLD}>>> PHASE 1: STARTING MANDATORY PIPELINE{C.RESET}")
    
    # 2. RUN GRAPH (Starting with Retrieval Node automatically)
    # We will simulate the execution of the compiled graph
    start_time = time.time()
    
    # In a real LangGraph setup, we'd use graph.invoke(state)
    # Here we invoke the compiled graph
    final_state = devsecops_graph.invoke(state)
    
    end_time = time.time()
    
    # 3. Present distributed outputs
    trace = final_state.get("execution_trace", [])
    
    print(f"\n{C.BLUE}{C.BOLD}--- DISTRIBUTED MULTI-AGENT OUTPUTS ---{C.RESET}")
    for step in trace:
        comp = step.get("component")
        ctype = step.get("type").upper()
        print(f"[{C.YELL}{ctype}{C.RESET}] {comp:25} -> {C.GREN}Independent JSON Persisted{C.RESET}")

    print(f"\n{C.GOLD}{C.BOLD}RAG ENRICHMENT VERIFICATION:{C.RESET}")
    rt_docs = final_state.get("retrieved_docs", [])
    print(f"  * Knowledge Docs Retrieved: {len(rt_docs)}")
    for d in rt_docs:
        print(f"    - [{d['document_id']}] {d['title']} (Score: {d['relevance_score']})")

    print(f"\n{C.GREN}{C.BOLD}SUCCESS: FULL 5-STEP RAG WORKFLOW COMPLETED IN {(end_time - start_time):.2f}s{C.RESET}")
    print(f"All artifacts are available in logs/pods/ and logs/scripts/")

if __name__ == "__main__":
    run_rag_scenario()
