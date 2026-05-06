"""
DevSecOps Module - Network Advisor Pod
Generates AI-powered remediation suggestions for network/IP security breaches.
Unlike the Auto-Patcher, this pod does NOT produce code patches — it only
provides actionable security recommendations.

Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any
from ..core_orchestrator.state_schema import DevSecOpsState
from ..core_orchestrator.model_router import model_router
from ..src.core.llm_client import llm_client
from ..src.core.logger import get_logger

logger = get_logger(__name__)


def generate_network_recommendations(alert: Dict[str, Any]) -> str:
    """
    Use the AI model to generate network/IP security remediation suggestions.

    Args:
        alert: The SOC alert dictionary containing breach details.

    Returns:
        str: AI-generated remediation recommendations.
    """
    alert_type = alert.get("alert_type", "Unknown")
    title = alert.get("title", "No title")
    description = alert.get("description", "No description")
    affected_target = alert.get("affected_target", "Unknown")
    severity = alert.get("severity", 0.0)
    network_details = alert.get("network_details") or {}

    # Format network details for the prompt
    network_info = ""
    if network_details:
        for key, value in network_details.items():
            network_info += f"  - {key}: {value}\n"
    else:
        network_info = "  No additional network details provided.\n"

    context = {
        "alert_description": (
            f"Alert Type: {alert_type}\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Severity: {severity}/10"
        ),
        "affected_target": affected_target,
        "network_details": network_info,
    }

    try:
        return model_router.route("network_remediation", context)
    except Exception as e:
        logger.error(f"[Network Advisor] LLM call failed: {e}")
        return _fallback_recommendations(alert)


def _fallback_recommendations(alert: Dict[str, Any]) -> str:
    """Deterministic fallback when LLM is unavailable."""
    alert_type = alert.get("alert_type", "Unknown")
    target = alert.get("affected_target", "Unknown")
    severity = alert.get("severity", 0.0)

    recommendations = [
        f"[FALLBACK] AI model unavailable — providing standard recommendations for {alert_type}.",
        "",
        "## Immediate Actions",
        f"1. Isolate the affected target ({target}) from the network.",
        "2. Block the suspicious IP addresses at the firewall level.",
        "3. Enable enhanced logging on all related network devices.",
        "",
        "## Investigation Steps",
        "4. Review firewall and IDS/IPS logs for related activity.",
        "5. Check for lateral movement indicators.",
        "6. Verify no data exfiltration occurred.",
        "",
        "## Long-term Recommendations",
        "7. Update firewall rules and IDS signatures.",
        "8. Implement network segmentation for critical assets.",
        "9. Schedule a full security audit of the affected segment.",
        "10. Review and update incident response procedures.",
    ]

    if severity >= 8.0:
        recommendations.insert(2, "⚠️ HIGH SEVERITY — Escalate to security team immediately.")

    return "\n".join(recommendations)


def network_advisor_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Generate remediation suggestions for network/IP breaches.

    Workflow:
    1. Read the SOC alert from state.
    2. Use the AI model to generate network security recommendations.
    3. Store recommendations in state (NO code patches, NO HITL approval).
    4. Return standardized output for the dashboard.
    """
    alert = state.get("soc_alert") or {}
    classification = state.get("alert_classification", "network_breach")

    thought_process = "[Network Advisor Pod] Starting network remediation analysis. "

    if not alert:
        thought_process += "No alert data found — skipping."
        logger.info("[Network Advisor] No alert data — skipped.")
        return {
            "pod_name": "network_advisor_pod",
            "network_recommendations": None,
            "remediation_status": "NO_ALERT",
            "ai_thought_process": thought_process,
            "human_approval_required": False,
            "data_payload": {},
            "messages": state.get("messages", []) + [
                "[Network Advisor] No alert data — skipped."
            ],
        }

    thought_process += (
        f"Analyzing {classification} alert: {alert.get('title', 'N/A')} "
        f"(severity: {alert.get('severity', 0.0)}/10). "
        f"Target: {alert.get('affected_target', 'N/A')}. "
    )

    # Generate recommendations
    logger.info(
        f"[Network Advisor] Generating recommendations for alert "
        f"{alert.get('alert_id')}"
    )
    recommendations = generate_network_recommendations(alert)

    thought_process += (
        "AI-generated network remediation recommendations ready. "
        "No code patch required for this type of breach. "
        "Sending recommendations to dashboard."
    )

    logger.info(
        f"[Network Advisor] Recommendations generated for "
        f"{alert.get('alert_id')} ({classification})"
    )

    return {
        "pod_name": "network_advisor_pod",
        "network_recommendations": recommendations,
        "remediation_status": "RECOMMENDATIONS_GENERATED",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            "alert_id": alert.get("alert_id"),
            "classification": classification,
            "affected_target": alert.get("affected_target"),
            "severity": alert.get("severity"),
            "recommendations": recommendations,
        },
        "messages": state.get("messages", []) + [
            f"[Network Advisor] Recommendations generated for "
            f"{alert.get('alert_id')} ({classification})"
        ],
    }
