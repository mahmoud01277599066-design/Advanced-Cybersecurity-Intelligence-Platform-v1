"""
DevSecOps Module - Pipeline Router
Routes CI/CD pipeline security events to appropriate processing pods.

Handles events like: dependency checks, config audits, scan triggers.
Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any
from ..core_orchestrator.state_schema import DevSecOpsState
from ..src.core.logger import get_logger

logger = get_logger(__name__)

# ── Routing Paths ─────────────────────────────────────────────
PIPELINE_PATHS = {
    "SCAN_RESULTS": "sast_parser_pod",
    "DEPENDENCY_CHECK": "prioritization_pod",
    "CONFIG_AUDIT": "tracking_pod",
}


def pipeline_router_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Router Node: Receives CI/CD pipeline events and determines the processing path.

    Routing Logic:
    - SARIF/scan data present → SCAN_RESULTS (parse with SAST parser)
    - Dependency manifest present → DEPENDENCY_CHECK
    - Config file changes → CONFIG_AUDIT
    - Default → SCAN_RESULTS
    """
    sarif_input = state.get("sarif_input", [])
    commit_id = state.get("commit_id", "UNKNOWN")

    thought_process = f"[Pipeline Router] Analyzing pipeline event for commit {commit_id}. "

    # Determine input type
    if isinstance(sarif_input, dict) and "runs" in sarif_input:
        decision = "SCAN_RESULTS"
        thought_process += "Detected SARIF format scan results. Routing to SAST parser."
    elif isinstance(sarif_input, list) and sarif_input:
        # Check if it's pre-parsed findings
        first_item = sarif_input[0] if sarif_input else {}
        if isinstance(first_item, dict) and "finding_id" in first_item:
            decision = "SCAN_RESULTS"
            thought_process += "Detected pre-parsed findings list. Routing to SAST parser."
        elif isinstance(first_item, dict) and "dependency" in first_item:
            decision = "DEPENDENCY_CHECK"
            thought_process += "Detected dependency check results. Routing to prioritization."
        else:
            decision = "SCAN_RESULTS"
            thought_process += "Unknown list format. Defaulting to SAST parser."
    else:
        decision = "SCAN_RESULTS"
        thought_process += "No specific data detected. Defaulting to SAST parser."

    logger.info(f"[Pipeline Router] Decision: {decision}")

    return {
        "routing_decision": decision,
        "router_name": "pipeline_router",
        "pod_name": "routing_decision",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            "pipeline_event": decision,
            "commit_id": commit_id,
        },
        "messages": state.get("messages", []) + [
            f"[Pipeline Router] Decision: {decision}"
        ],
    }


def route_after_pipeline(state: DevSecOpsState) -> str:
    """
    Conditional edge function: reads the routing decision from state.

    Returns:
        str: "SCAN_RESULTS", "DEPENDENCY_CHECK", or "CONFIG_AUDIT"
    """
    decision = state.get("routing_decision", "SCAN_RESULTS")
    return decision
