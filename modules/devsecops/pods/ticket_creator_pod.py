"""
DevSecOps Module - Ticket Creator Pod
Creates Jira/Azure DevOps tickets for high-priority security findings.
Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any
from ..core_orchestrator.state_schema import DevSecOpsState
from ..src.core.config import settings
from ..src.core.logger import get_logger
import uuid

logger = get_logger(__name__)


def create_jira_ticket(
    finding_id: str,
    severity: float,
    description: str,
    file_path: str,
    patch_available: bool = False,
) -> Dict[str, Any]:
    """
    Create a Jira ticket for a security finding.

    Currently simulated. Replace with actual Jira API call in production.

    Args:
        finding_id: The vulnerability identifier.
        severity: The severity score.
        description: Detailed description of the finding.
        file_path: Affected file path.
        patch_available: Whether an auto-patch was generated.

    Returns:
        Dict with ticket details.
    """
    ticket_id = f"JIRA-{uuid.uuid4().hex[:6].upper()}"

    # TODO: Replace with actual Jira REST API call
    # import requests
    # response = requests.post(
    #     f"{settings.JIRA_API_URL}/rest/api/3/issue",
    #     headers={"Authorization": f"Bearer {settings.JIRA_API_KEY}"},
    #     json={
    #         "fields": {
    #             "project": {"key": settings.JIRA_PROJECT_KEY},
    #             "summary": f"[Security] {finding_id} - Priority {severity}",
    #             "description": description,
    #             "issuetype": {"name": "Bug"},
    #             "priority": {"name": "Critical" if severity >= 9.0 else "High"},
    #             "labels": ["security", "auto-generated", "devsecops"],
    #         }
    #     }
    # )

    ticket_data = {
        "ticket_id": ticket_id,
        "finding_id": finding_id,
        "severity": severity,
        "file_path": file_path,
        "patch_available": patch_available,
        "status": "OPEN",
        "project_key": settings.JIRA_PROJECT_KEY,
        "assignee": "unassigned",
    }

    logger.info(f"[Ticket Creator] Created ticket: {ticket_id} for {finding_id}")
    return ticket_data


def skip_ticket(score: float) -> Dict[str, Any]:
    """Log and return skip result for low-priority findings."""
    logger.info(f"[Ticket Creator] Score {score} below threshold. Ticket skipped.")
    return {
        "ticket_id": "SKIPPED",
        "reason": f"Score {score} below threshold {settings.HIGH_PRIORITY_THRESHOLD}",
    }


def ticket_creator_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Create a Jira ticket for high-priority security findings.

    Only creates tickets when the priority score meets the threshold.
    Includes patch availability info in the ticket.
    """
    final_score = state.get("final_priority_score", 0.0)
    findings = state.get("parsed_findings", [])
    patch = state.get("patch_suggestion")
    threshold = settings.HIGH_PRIORITY_THRESHOLD

    thought_process = (
        f"[Ticket Creator Pod] Evaluating ticket creation. "
        f"Score: {final_score}, Threshold: {threshold}. "
    )

    if final_score >= threshold and findings:
        # Get the highest severity finding for the ticket
        target = max(findings, key=lambda f: f.get("tool_severity", 0.0))

        ticket_data = create_jira_ticket(
            finding_id=target.get("finding_id", "UNKNOWN"),
            severity=target.get("tool_severity", 0.0),
            description=target.get("message", "Security vulnerability detected"),
            file_path=target.get("file_path", "N/A"),
            patch_available=bool(patch),
        )

        thought_process += (
            f"Score meets threshold. Created ticket {ticket_data['ticket_id']} "
            f"for finding {target.get('finding_id')}. "
            f"Patch {'attached' if patch else 'not available'}."
        )

        return {
            "jira_ticket_id": ticket_data["ticket_id"],
            "pod_name": "ticket_creator_pod",
            "remediation_status": "TICKET_CREATED",
            "ai_thought_process": thought_process,
            "human_approval_required": False,
            "data_payload": {
                "ticket": ticket_data,
                "action": "ticket_created",
            },
            "messages": state.get("messages", []) + [
                f"[Ticket Creator] Created: {ticket_data['ticket_id']} "
                f"(Score: {final_score})"
            ],
        }
    else:
        skip_data = skip_ticket(final_score)
        thought_process += (
            f"Score below threshold ({final_score} < {threshold}). "
            f"No ticket created. Finding logged for tracking only."
        )

        return {
            "jira_ticket_id": "SKIPPED",
            "pod_name": "ticket_creator_pod",
            "remediation_status": "LOW_PRIORITY_SKIPPED",
            "ai_thought_process": thought_process,
            "human_approval_required": False,
            "data_payload": {
                "skip_info": skip_data,
                "action": "ticket_skipped",
            },
            "messages": state.get("messages", []) + [
                f"[Ticket Creator] Skipped (Score: {final_score} < {threshold})"
            ],
        }
