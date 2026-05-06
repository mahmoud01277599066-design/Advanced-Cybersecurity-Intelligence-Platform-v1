"""
DevSecOps Module - SAST Router
Routes SAST (Static Application Security Testing) scan results
to the appropriate processing pods.

Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any
from ..core_orchestrator.state_schema import DevSecOpsState, build_standardized_output
from ..src.core.logger import get_logger

logger = get_logger(__name__)

# ── Routing Paths ─────────────────────────────────────────────
SAST_PATHS = {
    "DEEP_ANALYSIS": "prioritization_pod",
    "QUICK_REPORT": "tracking_pod",
    "AUTO_PATCH": "auto_patcher_pod",
}


def sast_router_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Router Node: Receives parsed SAST findings and decides the processing path.

    Routing Logic:
    - If any finding has severity >= 8.0 → DEEP_ANALYSIS (prioritization + patch)
    - If findings exist but all low severity → QUICK_REPORT (just track)
    - If no findings → END

    Updates the state with the routing decision and standardized output.
    """
    findings = state.get("parsed_findings", [])
    commit_id = state.get("commit_id", "UNKNOWN")

    thought_process = (
        f"[SAST Router] Evaluating {len(findings)} findings from commit {commit_id}. "
    )

    if not findings:
        decision = "END_WORKFLOW"
        thought_process += "No findings detected. Ending workflow."
        logger.info("[SAST Router] No findings → END_WORKFLOW")
    else:
        # Check for high-severity findings
        max_severity = max(
            (f.get("tool_severity", 0.0) for f in findings),
            default=0.0
        )

        if max_severity >= 8.0:
            decision = "DEEP_ANALYSIS"
            thought_process += (
                f"High-severity finding detected (max severity: {max_severity}). "
                f"Routing to deep analysis pipeline for prioritization and auto-patching."
            )
            logger.info(f"[SAST Router] High severity ({max_severity}) → DEEP_ANALYSIS")
        else:
            decision = "QUICK_REPORT"
            thought_process += (
                f"All findings are low-medium severity (max: {max_severity}). "
                f"Routing to quick report and tracking."
            )
            logger.info(f"[SAST Router] Low severity ({max_severity}) → QUICK_REPORT")

    return {
        "routing_decision": decision,
        "router_name": "sast_router",
        "pod_name": "routing_decision",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            "total_findings": len(findings),
            "routing_decision": decision,
            "commit_id": commit_id,
        },
        "messages": state.get("messages", []) + [
            f"[SAST Router] Decision: {decision} ({len(findings)} findings)"
        ],
    }


def route_after_sast(state: DevSecOpsState) -> str:
    """
    Conditional edge function: reads the routing decision from state.

    Returns:
        str: "DEEP_ANALYSIS", "QUICK_REPORT", or "END_WORKFLOW"
    """
    decision = state.get("routing_decision", "END_WORKFLOW")
    logger.info(f"[SAST Router] Conditional edge → {decision}")
    return decision
