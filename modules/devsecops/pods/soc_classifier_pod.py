"""
DevSecOps Module - SOC Classifier Pod
Classifies incoming SOC alerts to determine the type of breach:
  - code_vulnerability  → code scanning + AI patch + HITL approval
  - network_breach      → AI-generated network remediation suggestions only
  - ip_threat           → AI-generated IP/network remediation suggestions only

Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any, Optional
from ..core_orchestrator.state_schema import DevSecOpsState
from ..src.core.logger import get_logger

logger = get_logger(__name__)

# ── Keywords used for heuristic classification ────────────────
CODE_KEYWORDS = [
    "sql_injection", "xss", "cross_site_scripting", "code_injection",
    "command_injection", "path_traversal", "buffer_overflow",
    "insecure_deserialization", "hardcoded_credentials", "code_vulnerability",
    "sast", "cwe-", "cve-", "vulnerable_code", "injection",
    "remote_code_execution", "rce",
]

NETWORK_KEYWORDS = [
    "network_breach", "ddos", "dos", "man_in_the_middle", "mitm",
    "arp_spoofing", "dns_poisoning", "network_intrusion",
    "lateral_movement", "network_scan", "port_scan",
    "unauthorized_access", "network",
]

IP_KEYWORDS = [
    "ip_threat", "brute_force", "ip_blacklist", "suspicious_ip",
    "malicious_ip", "ip_reputation", "geo_anomaly", "ip_spoofing",
    "c2_communication", "botnet", "tor_exit_node",
]


def classify_alert(alert: Dict[str, Any]) -> str:
    """
    Classify a SOC alert into one of three categories.

    Classification logic (priority order):
    1. Explicit alert_type from SOC takes priority if it's a known type.
    2. Presence of code_snippet + file_path → code_vulnerability.
    3. Keyword matching in alert_type, title, and description.
    4. Presence of network_details → network_breach.
    5. Default → network_breach (safe fallback — no code changes).

    Args:
        alert: The SOC alert dictionary.

    Returns:
        str: "code_vulnerability", "network_breach", or "ip_threat"
    """
    alert_type = (alert.get("alert_type") or "").lower().strip()
    title = (alert.get("title") or "").lower()
    description = (alert.get("description") or "").lower()
    searchable = f"{alert_type} {title} {description}"

    # ── 1. Explicit type match ────────────────────────────────
    if alert_type in ("code_vulnerability", "code"):
        return "code_vulnerability"
    if alert_type in ("network_breach", "network"):
        return "network_breach"
    if alert_type in ("ip_threat", "ip"):
        return "ip_threat"

    # ── 2. Code artefacts present ─────────────────────────────
    has_code = bool(alert.get("code_snippet"))
    has_file = bool(alert.get("file_path"))
    if has_code or has_file:
        return "code_vulnerability"

    # ── 3. Keyword matching ───────────────────────────────────
    for kw in CODE_KEYWORDS:
        if kw in searchable:
            return "code_vulnerability"

    for kw in IP_KEYWORDS:
        if kw in searchable:
            return "ip_threat"

    for kw in NETWORK_KEYWORDS:
        if kw in searchable:
            return "network_breach"

    # ── 4. Network details present ────────────────────────────
    if alert.get("network_details"):
        return "network_breach"

    # ── 5. Default ────────────────────────────────────────────
    return "network_breach"


def soc_classifier_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Classify an incoming SOC alert.

    Reads ``soc_alert`` from state, determines the breach type, and
    writes ``alert_classification`` back so that downstream routing
    can direct the alert to the correct processing path.
    """
    alert = state.get("soc_alert") or {}

    if not alert:
        logger.info("[SOC Classifier] No SOC alert in state — skipping.")
        return {
            "pod_name": "soc_classifier_pod",
            "alert_classification": None,
            "ai_thought_process": "[SOC Classifier] No alert to classify.",
            "human_approval_required": False,
            "data_payload": {},
            "messages": state.get("messages", []) + [
                "[SOC Classifier] No alert data — skipped."
            ],
        }

    classification = classify_alert(alert)

    thought_process = (
        f"[SOC Classifier] Received alert '{alert.get('alert_id', 'N/A')}' "
        f"(type: {alert.get('alert_type', 'N/A')}). "
        f"Classification result: {classification}. "
    )

    if classification == "code_vulnerability":
        thought_process += (
            "This is a code-level vulnerability. "
            "Routing to code scanning → AI patch generation → HITL approval."
        )
    elif classification == "network_breach":
        thought_process += (
            "This is a network-level breach. "
            "Routing to network advisor for AI-generated remediation suggestions."
        )
    else:
        thought_process += (
            "This is an IP-level threat. "
            "Routing to network advisor for AI-generated remediation suggestions."
        )

    logger.info(
        f"[SOC Classifier] Alert {alert.get('alert_id')} → {classification}"
    )

    return {
        "pod_name": "soc_classifier_pod",
        "alert_classification": classification,
        "remediation_status": "CLASSIFIED",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            "alert_id": alert.get("alert_id"),
            "alert_type": alert.get("alert_type"),
            "classification": classification,
            "severity": alert.get("severity"),
            "affected_target": alert.get("affected_target"),
        },
        "messages": state.get("messages", []) + [
            f"[SOC Classifier] Alert {alert.get('alert_id')} "
            f"classified as: {classification}"
        ],
    }
