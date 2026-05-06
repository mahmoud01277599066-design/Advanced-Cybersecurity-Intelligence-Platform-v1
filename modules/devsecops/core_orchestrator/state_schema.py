"""
DevSecOps Module - State Schema
Defines the shared state for the LangGraph DevSecOps sub-orchestrator.
Compliant with the ACIP Standardized Output Protocol.
"""

from typing import TypedDict, List, Dict, Optional, Any


class DevSecOpsState(TypedDict):
    """
    Represents the current system state of the DevSecOps module in LangGraph.
    Fields align with the ACIP Standardized Output Protocol for dashboard rendering
    and Grand Orchestrator data passing.
    """

    # ── Input Data ────────────────────────────────────────────
    sarif_input: Any
    """Raw SARIF/scan data from CI/CD pipeline (dict or list)."""

    commit_id: str
    """Git commit identifier associated with the scan."""

    # ── Parsed Findings ───────────────────────────────────────
    parsed_findings: List[Dict[str, Any]]
    """Normalized list of security findings after SAST parsing."""

    # ── Prioritization ────────────────────────────────────────
    final_priority_score: Optional[float]
    """Calculated risk priority score."""

    # ── Ticket Management ─────────────────────────────────────
    jira_ticket_id: Optional[str]
    """Created Jira/DevOps ticket ID."""

    # ── Auto-Patch ────────────────────────────────────────────
    patch_suggestion: Optional[str]
    """AI-generated code patch for the vulnerability."""

    # ── Remediation Tracking ──────────────────────────────────
    remediation_status: str
    """Current workflow stage status."""

<<<<<<< HEAD
    # ── Routing ───────────────────────────────────────────────
=======
    # RAG Components
    retrieved_docs: List[Dict[str, Any]]
    enriched_context: str
    
    # Analysis & Routing ───────────────────────────────────────────────
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
    routing_decision: Optional[str]
    """Router agent's path decision."""

    # ── ACIP Standardized Output Protocol Fields ──────────────
    module_name: str
    """Module identifier: always 'devsecops'."""

    router_name: Optional[str]
    """Which Router Agent managed the task."""

    pod_name: Optional[str]
    """Which Pod executed the work."""

    ai_thought_process: str
    """AI's internal dialogue — streamed live to the dashboard terminal."""

    human_approval_required: bool
    """True if the action changes target state (e.g., applying a patch)."""

    hitl_message: Optional[str]
    """Message shown in the dashboard HITL popup."""

    data_payload: Dict[str, Any]
    """Module-specific data, findings, or tool outputs."""

    # ── Message Log ───────────────────────────────────────────
    messages: List[str]
    """Running log of workflow messages."""

    # ── SOC Alert Data ────────────────────────────────────────
    soc_alert: Optional[Dict[str, Any]]
    """Raw SOC alert data received from the SOC module."""

    alert_classification: Optional[str]
    """Classification result: 'code_vulnerability', 'network_breach', or 'ip_threat'."""

    network_recommendations: Optional[str]
    """AI-generated network/IP security recommendations (for non-code breaches)."""

<<<<<<< HEAD
=======
    # ── Pipeline Tracing ──────────────────────────────────────
    execution_trace: List[Dict[str, Any]]
    """Master sequential trace of every agent execution step."""

>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f

# ── Default Initial State ─────────────────────────────────────
INITIAL_STATE: DevSecOpsState = {
    "sarif_input": [],
    "commit_id": "",
    "parsed_findings": [],
    "final_priority_score": None,
    "jira_ticket_id": None,
    "patch_suggestion": None,
    "remediation_status": "START_PROCESSING",
    "routing_decision": None,
    "module_name": "devsecops",
    "router_name": None,
    "pod_name": None,
    "ai_thought_process": "",
    "human_approval_required": False,
    "hitl_message": None,
    "data_payload": {},
    "messages": ["DevSecOps Orchestrator workflow initialized."],
    "soc_alert": None,
    "alert_classification": None,
    "network_recommendations": None,
<<<<<<< HEAD
=======
    "execution_trace": [],
    "retrieved_docs": [],
    "enriched_context": "",
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
}


def build_standardized_output(
    state: DevSecOpsState,
    router_name: Optional[str] = None,
    pod_name: Optional[str] = None,
    thought_process: str = "",
    approval_required: bool = False,
    hitl_msg: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a Standardized Output Protocol JSON from the current state.
    This is the format the Dashboard and Grand Orchestrator expect.

    Returns:
        Dict matching the ACIP output schema.
    """
    return {
        "module_name": "devsecops",
        "router_name": router_name or state.get("router_name"),
        "pod_name": pod_name or state.get("pod_name"),
        "status": state.get("remediation_status", "UNKNOWN"),
        "ai_thought_process": thought_process or state.get("ai_thought_process", ""),
        "human_approval_required": approval_required,
        "hitl_message": hitl_msg,
        "data_payload": payload or state.get("data_payload", {}),
    }
