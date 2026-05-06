"""
DevSecOps Module - Human-In-The-Loop (HITL) Manager
Manages approval workflows for high-risk actions such as applying patches
or modifying CI/CD configurations.
"""

from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from .state_schema import DevSecOpsState
from ..src.core.logger import get_logger
from ..src.core.config import settings

logger = get_logger(__name__)


class HITLDecision(str, Enum):
    """Possible HITL decisions."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class HITLRequest:
    """Represents a pending HITL approval request."""

    def __init__(
        self,
        request_id: str,
        action_type: str,
        description: str,
        risk_level: str,
        data: Dict[str, Any],
    ):
        self.request_id = request_id
        self.action_type = action_type
        self.description = description
        self.risk_level = risk_level
        self.data = data
        self.decision = HITLDecision.PENDING
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.decided_at: Optional[str] = None
        self.decided_by: Optional[str] = None
        self.notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the request to a dictionary."""
        return {
            "request_id": self.request_id,
            "action_type": self.action_type,
            "description": self.description,
            "risk_level": self.risk_level,
            "data": self.data,
            "decision": self.decision.value,
            "created_at": self.created_at,
            "decided_at": self.decided_at,
            "decided_by": self.decided_by,
            "notes": self.notes,
        }


class HITLManager:
    """
    Manages Human-In-The-Loop approval workflows.

    Actions requiring HITL approval:
    - Applying auto-generated patches to code
    - Creating high-priority security tickets
    - Modifying CI/CD pipeline configurations
    """

    def __init__(self):
        self._pending_requests: Dict[str, HITLRequest] = {}
        self._history: list = []

    def create_approval_request(
        self,
        request_id: str,
        action_type: str,
        description: str,
        risk_level: str = "high",
        data: Optional[Dict[str, Any]] = None,
    ) -> HITLRequest:
        """
        Create a new HITL approval request.

        Args:
            request_id: Unique identifier for this request.
            action_type: Type of action (e.g., "apply_patch", "create_ticket").
            description: Human-readable description for the dashboard.
            risk_level: "critical", "high", "medium", "low".
            data: Associated data (patch content, ticket details, etc.).

        Returns:
            HITLRequest: The created request.
        """
        request = HITLRequest(
            request_id=request_id,
            action_type=action_type,
            description=description,
            risk_level=risk_level,
            data=data or {},
        )

        self._pending_requests[request_id] = request
        logger.info(
            f"[HITL] Approval request created: {request_id} "
            f"(action: {action_type}, risk: {risk_level})"
        )
        return request

    def process_decision(
        self,
        request_id: str,
        decision: str,
        decided_by: str = "analyst",
        notes: str = "",
    ) -> Optional[HITLRequest]:
        """
        Process a HITL decision (approve/reject/modify).

        Args:
            request_id: The request to process.
            decision: One of "approved", "rejected", "modified".
            decided_by: Who made the decision.
            notes: Optional notes about the decision.

        Returns:
            The updated request, or None if not found.
        """
        request = self._pending_requests.get(request_id)
        if not request:
            logger.warning(f"[HITL] Request not found: {request_id}")
            return None

        try:
            request.decision = HITLDecision(decision)
        except ValueError:
            logger.error(f"[HITL] Invalid decision: {decision}")
            return None

        request.decided_at = datetime.now(timezone.utc).isoformat()
        request.decided_by = decided_by
        request.notes = notes

        # Move to history
        self._history.append(request.to_dict())
        del self._pending_requests[request_id]

        logger.info(
            f"[HITL] Decision processed: {request_id} → {decision} "
            f"(by: {decided_by})"
        )
        return request

    def get_pending_requests(self) -> list:
        """Return all pending approval requests."""
        return [req.to_dict() for req in self._pending_requests.values()]

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pending request."""
        req = self._pending_requests.get(request_id)
        return req.to_dict() if req else None

    def get_history(self) -> list:
        """Return all processed decisions."""
        return self._history.copy()

    def should_require_approval(self, action_type: str, risk_level: str) -> bool:
        """
        Determine if an action requires HITL approval based on settings.

        Args:
            action_type: Type of action.
            risk_level: Risk level of the action.

        Returns:
            bool: True if approval is required.
        """
        if not settings.HITL_ENABLED:
            return False

        # Always require approval for critical actions
        if risk_level in ("critical", "high"):
            return True

        # Auto-approve low risk if setting is enabled
        if risk_level == "low" and settings.AUTO_APPROVE_LOW_RISK:
            return False

        return True


def update_state_for_hitl(
    state: DevSecOpsState,
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Helper to update LangGraph state when HITL approval is needed.

    Returns:
        Dict of state updates that will pause the workflow for human input.
    """
    return {
        "human_approval_required": True,
        "hitl_message": message,
        "data_payload": data or state.get("data_payload", {}),
        "remediation_status": "AWAITING_APPROVAL",
        "messages": state.get("messages", []) + [
            f"[HITL] Waiting for human approval: {message}"
        ],
    }


# ── Module-level convenience instance ─────────────────────────
hitl_manager = HITLManager()
