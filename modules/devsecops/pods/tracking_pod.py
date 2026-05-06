"""
DevSecOps Module - Tracking Pod
Tracks remediation status and generates summary reports.
This is the final pod in the pipeline.
Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any
from datetime import datetime, timezone
from ..core_orchestrator.state_schema import DevSecOpsState
from ..src.core.logger import get_logger

logger = get_logger(__name__)


def tracking_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Track remediation status and produce final summary.

    This pod:
    1. Aggregates all pipeline results into a final status report.
    2. Logs the complete workflow timeline.
    3. Produces the final standardized output for the dashboard.
    """
    ticket_id = state.get("jira_ticket_id", "N/A")
    final_score = state.get("final_priority_score", 0.0)
    patch = state.get("patch_suggestion")
    findings = state.get("parsed_findings", [])
    commit_id = state.get("commit_id", "N/A")

    # Determine final status
    if ticket_id and ticket_id not in ("N/A", "SKIPPED"):
        tracking_status = "TRACKING_ACTIVE"
        action_summary = f"Ticket {ticket_id} created and being tracked."
    elif findings:
        tracking_status = "MONITORING"
        action_summary = "Findings logged for monitoring. No ticket required."
    else:
        tracking_status = "CLEAN"
        action_summary = "No security findings detected. All clear."

    # Build remediation timeline
    messages = state.get("messages", [])
    timeline = []
    for i, msg in enumerate(messages):
        timeline.append({
            "step": i + 1,
            "action": msg,
        })

    # Build final report
    report = {
        "commit_id": commit_id,
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_findings": len(findings),
        "final_priority_score": final_score,
        "risk_level": _categorize(final_score),
        "ticket_id": ticket_id,
        "patch_generated": bool(patch),
        "tracking_status": tracking_status,
        "action_summary": action_summary,
        "workflow_steps": len(timeline),
        "timeline": timeline,
    }

    thought_process = (
        f"[Tracking Pod] Final report generated for commit {commit_id}. "
        f"Status: {tracking_status}. "
        f"Findings: {len(findings)}, Score: {final_score}, "
        f"Ticket: {ticket_id}, Patch: {'Yes' if patch else 'No'}. "
        f"Total workflow steps: {len(timeline)}."
    )

    logger.info(
        f"[Tracking Pod] {tracking_status} | Commit: {commit_id} | "
        f"Findings: {len(findings)} | Score: {final_score} | "
        f"Ticket: {ticket_id}"
    )

    return {
        "pod_name": "tracking_pod",
        "remediation_status": tracking_status,
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": report,
        "messages": state.get("messages", []) + [
            f"[Tracking] Final status: {tracking_status} | {action_summary}"
        ],
    }


def _categorize(score: float) -> str:
    """Categorize risk score to level string."""
    if score is None:
        return "NONE"
    if score >= 9.0:
        return "CRITICAL"
    elif score >= 7.0:
        return "HIGH"
    elif score >= 4.0:
        return "MEDIUM"
    elif score > 0.0:
        return "LOW"
    return "NONE"
