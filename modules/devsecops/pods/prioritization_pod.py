"""
DevSecOps Module - Prioritization Pod
Applies AI-enhanced risk scoring to security findings.
Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any, List
from ..core_orchestrator.state_schema import DevSecOpsState
from ..src.core.config import settings
from ..src.core.logger import get_logger

logger = get_logger(__name__)


def apply_risk_scoring(
    findings: List[Dict[str, Any]],
    commit_id: str,
    context_factor: float = None,
) -> float:
    """
    Risk Algorithm: Calculates final priority score.

    Formula: max(severity) * context_factor
    The context factor accounts for code criticality, recency, and exposure.

    Args:
        findings: List of normalized findings.
        commit_id: The associated commit ID.
        context_factor: Multiplier for context adjustment.

    Returns:
        float: The final priority score.
    """
    if not findings:
        return 0.0

    if context_factor is None:
        context_factor = settings.CONTEXT_FACTOR

    # Get highest severity from findings
    max_severity = max(
        (f.get("tool_severity", 0.0) for f in findings),
        default=0.0
    )

    # Calculate final score
    final_score = max_severity * context_factor

    return round(final_score, 2)


def categorize_risk(score: float) -> str:
    """Categorize a risk score into a human-readable level."""
    if score >= 9.0:
        return "CRITICAL"
    elif score >= 7.0:
        return "HIGH"
    elif score >= 4.0:
        return "MEDIUM"
    elif score > 0.0:
        return "LOW"
    else:
        return "NONE"


def prioritization_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Apply risk scoring algorithm to determine final priority.

    Uses the highest severity finding and context factor to calculate
    the overall priority score. Determines whether the findings warrant
    a ticket, auto-patch, or just tracking.
    """
    findings = state.get("parsed_findings", [])
    commit_id = state.get("commit_id", "N/A")

    thought_process = f"[Prioritization Pod] Scoring {len(findings)} findings. "

    if not findings:
        thought_process += "No findings to prioritize. Skipping."
        logger.info("[Prioritization Pod] No findings → Skipped")
        return {
            "final_priority_score": 0.0,
            "pod_name": "prioritization_pod",
            "remediation_status": "SKIPPED",
            "ai_thought_process": thought_process,
            "human_approval_required": False,
            "data_payload": {"risk_level": "NONE", "score": 0.0},
            "messages": state.get("messages", []) + [
                "Prioritization skipped: No findings."
            ],
        }

    # Calculate score
    final_priority = apply_risk_scoring(findings, commit_id)
    risk_level = categorize_risk(final_priority)
    threshold = settings.HIGH_PRIORITY_THRESHOLD

    thought_process += (
        f"Applied risk algorithm (context_factor={settings.CONTEXT_FACTOR}). "
        f"Final score: {final_priority}. Risk level: {risk_level}. "
        f"Threshold for ticket creation: {threshold}. "
    )

    if final_priority >= threshold:
        thought_process += (
            f"Score {final_priority} >= {threshold} → "
            f"Will create ticket and attempt auto-patch."
        )
    else:
        thought_process += (
            f"Score {final_priority} < {threshold} → "
            f"Will track but no automated action required."
        )

    logger.info(
        f"[Prioritization Pod] Score: {final_priority} | "
        f"Risk: {risk_level} | Threshold: {threshold}"
    )

    return {
        "final_priority_score": final_priority,
        "pod_name": "prioritization_pod",
        "remediation_status": "PRIORITIZED",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            "final_score": final_priority,
            "risk_level": risk_level,
            "threshold": threshold,
            "findings_count": len(findings),
        },
        "messages": state.get("messages", []) + [
            f"[Prioritization] Score: {final_priority} ({risk_level})"
        ],
    }
