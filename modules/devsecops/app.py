"""
DevSecOps Module - FastAPI Application
Provides REST API endpoints for the ACIP Dashboard and external integrations.

Endpoints are designed for frontend integration:
- Submit scans
- View findings and results
- Request auto-patches
- HITL approval workflow
- Dashboard summary
- Live AI thought stream (WebSocket)
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
<<<<<<< HEAD
from pydantic import BaseModel, Field
=======
from pydantic import BaseModel
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
from datetime import datetime, timezone
import uuid
import asyncio
import json

# ── Internal Imports ──────────────────────────────────────────
from .core_orchestrator.main_graph import devsecops_graph
from .core_orchestrator.state_schema import INITIAL_STATE, DevSecOpsState, build_standardized_output
from .core_orchestrator.hitl_manager import hitl_manager
from .src.core.config import settings
from .src.core.logger import get_logger

logger = get_logger(__name__)

# ══════════════════════════════════════════════════════════════
# FastAPI App
# ══════════════════════════════════════════════════════════════

app = FastAPI(
    title="ACIP DevSecOps Module API",
    description=(
        "DevSecOps Sub-Orchestrator API for the Advanced Cybersecurity "
        "Intelligence Platform (ACIP). Handles SAST/DAST scan processing, "
        "AI-powered vulnerability analysis, auto-patching, and HITL workflows."
    ),
    version=settings.MODULE_VERSION,
)

# ── CORS (for frontend integration) ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-Memory Storage (Phase 1) ──────────────────────────────
scan_results: Dict[str, Dict[str, Any]] = {}
<<<<<<< HEAD
endpoint_events: List[Dict[str, Any]] = []
endpoint_registry: Dict[str, Dict[str, Any]] = {}
=======
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
active_connections: List[WebSocket] = []


# ══════════════════════════════════════════════════════════════
# Request/Response Models
# ══════════════════════════════════════════════════════════════

class ScanSubmitRequest(BaseModel):
    """Request body for submitting a scan."""
    sarif_data: Any  # SARIF dict or pre-parsed findings list
    commit_id: Optional[str] = None

class ApprovalRequest(BaseModel):
    """Request body for HITL approval."""
    decision: str  # "approved", "rejected", "modified"
    decided_by: str = "analyst"
    notes: str = ""

class PatchRequest(BaseModel):
    """Request body for requesting an auto-patch."""
    vulnerability_type: Optional[str] = None


class SOCAlertRequest(BaseModel):
    """Request body for SOC alert ingestion."""
    alert_id: str
    alert_type: str
    severity: float
    title: str
    description: str
    source_module: str = "soc"
    affected_target: Optional[str] = None
    code_snippet: Optional[str] = None
    file_path: Optional[str] = None
    network_details: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


<<<<<<< HEAD
class EndpointEventRequest(BaseModel):
    """Request body for endpoint telemetry ingestion."""
    endpoint_id: str
    hostname: str
    platform: str
    event_type: str
    severity: float
    title: str
    description: str
    source_module: str = "endpoint"
    user_name: Optional[str] = None
    ip_address: Optional[str] = None
    process_name: Optional[str] = None
    process_path: Optional[str] = None
    parent_process: Optional[str] = None
    sha256: Optional[str] = None
    recommended_action: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    raw_event: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


=======
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
# ══════════════════════════════════════════════════════════════
# WebSocket Manager (Live AI Thought Stream)
# ══════════════════════════════════════════════════════════════

async def broadcast_message(message: Dict[str, Any]):
    """Broadcast a message to all connected WebSocket clients."""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.remove(conn)


# ══════════════════════════════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════════════════════════════

# ── Health & Status ───────────────────────────────────────────

@app.get("/", tags=["Health"])
def read_root():
    """Service health check."""
    return {
        "service_status": "Running",
        "module_name": settings.MODULE_NAME,
        "version": settings.MODULE_VERSION,
        "model": settings.PRIMARY_AGENT_MODEL,
        "ollama_url": settings.OLLAMA_BASE_URL,
    }


# ── Scan Submission ───────────────────────────────────────────

@app.post("/api/v1/scan/submit", tags=["Scans"])
def submit_scan(request: ScanSubmitRequest):
    """
    Submit SAST/DAST scan results for processing.

    Triggers the full DevSecOps pipeline:
    SAST Parser → Router → Prioritization → Auto-Patcher → Ticket → Tracking

    Returns:
        Scan ID and final pipeline results.
    """
    scan_id = str(uuid.uuid4())
    commit_id = request.commit_id or f"auto_{uuid.uuid4().hex[:8]}"

    logger.info(f"[API] Scan submitted: {scan_id} (commit: {commit_id})")

    try:
        # Prepare initial state
        initial_input = INITIAL_STATE.copy()
        initial_input["sarif_input"] = request.sarif_data
        initial_input["commit_id"] = commit_id

        # Run the pipeline
        final_state = devsecops_graph.invoke(initial_input)

        # Store results
        result = {
            "scan_id": scan_id,
            "commit_id": commit_id,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": final_state.get("remediation_status", "UNKNOWN"),
            "final_score": final_state.get("final_priority_score"),
            "risk_level": _categorize(final_state.get("final_priority_score", 0.0)),
            "jira_ticket_id": final_state.get("jira_ticket_id"),
            "patch_generated": bool(final_state.get("patch_suggestion")),
            "patch_suggestion": final_state.get("patch_suggestion"),
            "human_approval_required": final_state.get("human_approval_required", False),
            "hitl_message": final_state.get("hitl_message"),
            "ai_thought_process": final_state.get("ai_thought_process", ""),
            "findings": final_state.get("parsed_findings", []),
            "data_payload": final_state.get("data_payload", {}),
            "messages": final_state.get("messages", []),
            "standardized_output": build_standardized_output(final_state),
        }

        scan_results[scan_id] = result

        return {
            "scan_id": scan_id,
            "status": result["status"],
            "final_score": result["final_score"],
            "risk_level": result["risk_level"],
            "jira_ticket_id": result["jira_ticket_id"],
            "patch_generated": result["patch_generated"],
            "human_approval_required": result["human_approval_required"],
            "message": f"Scan processed successfully. {len(result['findings'])} findings analyzed.",
        }

    except Exception as e:
        logger.error(f"[API] Scan failed: {e}")
        error_result = {
            "scan_id": scan_id,
            "status": "FAILED",
            "error": str(e),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        scan_results[scan_id] = error_result
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


# ── Scan Results ──────────────────────────────────────────────

@app.get("/api/v1/scan/{scan_id}/status", tags=["Scans"])
def get_scan_status(scan_id: str):
    """Get the processing status of a submitted scan."""
    result = scan_results.get(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    return {
        "scan_id": scan_id,
        "status": result.get("status"),
        "final_score": result.get("final_score"),
        "risk_level": result.get("risk_level"),
    }


@app.get("/api/v1/scan/{scan_id}/results", tags=["Scans"])
def get_scan_results(scan_id: str):
    """Get the full analysis results for a completed scan."""
    result = scan_results.get(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    return result


# ── SOC Integration ───────────────────────────────────────────

@app.post("/api/v1/soc/alerts", tags=["SOC"])
def receive_soc_alert(request: SOCAlertRequest):
    """
    Receive a security alert from the SOC module.
    Classifies the alert and triggers the appropriate DevSecOps workflows.
    """
    logger.info(f"[API] SOC Alert received: {request.alert_id} ({request.alert_type})")
    
    # Store alert in scan_results using alert_id as the key for tracking
    # (In a real system, you'd use a dedicated database table for SOC alerts)
    scan_results[request.alert_id] = {
        "alert_id": request.alert_id,
        "status": "RECEIVED",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "classification": "pending",
        "raw_alert": request.dict(),
    }
    
    # Normally we'd run the Graph similarly to scans here, but adjusting the INITIAL_STATE
    # For now, we just acknowledge receipt and classification will process it
    try:
        from .pods.soc_classifier_pod import classify_alert
        classification = classify_alert(request.dict())
        
        scan_results[request.alert_id]["classification"] = classification
        scan_results[request.alert_id]["status"] = "PROCESSING"
        
        return {
            "status": "received",
            "alert_id": request.alert_id,
            "classification": classification,
            "processing_status": "processing",
            "message": "Alert received and classified. Processing initiated."
        }
    except Exception as e:
        logger.error(f"[API] Failed to process SOC alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


<<<<<<< HEAD
# -- Endpoint / EDR Integration ------------------------------------------------

@app.post("/api/v1/endpoints/events", tags=["Endpoint"])
def ingest_endpoint_event(request: EndpointEventRequest):
    """
    Receive endpoint / EDR-style telemetry and normalize it for the dashboard.
    High-severity events are marked for escalation so SOC/DevSecOps can act on them.
    """
    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    normalized_timestamp = request.timestamp or datetime.now(timezone.utc).isoformat()
    risk_level = _categorize(request.severity)
    status = "ESCALATED" if request.severity >= 8.0 else "INGESTED"
    recommended_action = request.recommended_action or _recommend_endpoint_action(
        request.event_type,
        request.severity,
    )

    event_record = {
        "event_id": event_id,
        "endpoint_id": request.endpoint_id,
        "hostname": request.hostname,
        "platform": request.platform,
        "event_type": request.event_type,
        "severity": request.severity,
        "risk_level": risk_level,
        "status": status,
        "title": request.title,
        "description": request.description,
        "source_module": request.source_module,
        "user_name": request.user_name,
        "ip_address": request.ip_address,
        "process_name": request.process_name,
        "process_path": request.process_path,
        "parent_process": request.parent_process,
        "sha256": request.sha256,
        "recommended_action": recommended_action,
        "tags": request.tags,
        "raw_event": request.raw_event or {},
        "timestamp": normalized_timestamp,
    }

    endpoint_events.append(event_record)
    endpoint_registry[request.endpoint_id] = {
        "endpoint_id": request.endpoint_id,
        "hostname": request.hostname,
        "platform": request.platform,
        "last_seen": normalized_timestamp,
        "latest_status": status,
        "latest_risk_level": risk_level,
        "open_high_alerts": sum(
            1
            for event in endpoint_events
            if event["endpoint_id"] == request.endpoint_id and event["severity"] >= 8.0
        ),
        "recent_event_types": _recent_endpoint_event_types(request.endpoint_id),
    }

    logger.info(
        f"[API] Endpoint event ingested: {event_id} for {request.endpoint_id} ({status})"
    )

    return {
        "status": "received",
        "event_id": event_id,
        "endpoint_id": request.endpoint_id,
        "risk_level": risk_level,
        "processing_status": status,
        "recommended_action": recommended_action,
        "message": "Endpoint telemetry ingested successfully.",
    }


@app.get("/api/v1/endpoints/summary", tags=["Endpoint"])
def endpoint_summary():
    """Return endpoint telemetry aggregation for the dashboard."""
    return {
        "total_events": len(endpoint_events),
        "total_endpoints": len(endpoint_registry),
        "escalated_events": sum(1 for event in endpoint_events if event["status"] == "ESCALATED"),
        "risk_distribution": _build_endpoint_risk_distribution(),
        "recent_events": endpoint_events[-10:],
    }


@app.get("/api/v1/endpoints/events", tags=["Endpoint"])
def list_endpoint_events(
    endpoint_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 50,
):
    """List ingested endpoint events with optional filtering."""
    events = endpoint_events

    if endpoint_id:
        events = [event for event in events if event["endpoint_id"] == endpoint_id]
    if risk_level:
        events = [
            event for event in events
            if event["risk_level"].lower() == risk_level.lower()
        ]

    return {
        "total": len(events),
        "events": events[:limit],
    }


@app.get("/api/v1/endpoints/{endpoint_id}", tags=["Endpoint"])
def get_endpoint_details(endpoint_id: str):
    """Get the current posture and recent events for a single endpoint."""
    endpoint = endpoint_registry.get(endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail=f"Endpoint {endpoint_id} not found")

    recent_events = [
        event for event in reversed(endpoint_events)
        if event["endpoint_id"] == endpoint_id
    ][:10]

    return {
        **endpoint,
        "recent_events": recent_events,
    }


=======
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
# ── Findings ──────────────────────────────────────────────────

@app.get("/api/v1/findings", tags=["Findings"])
def list_findings(
    risk_level: Optional[str] = None,
    limit: int = 50,
):
    """
    List all findings across all scans.
    Optionally filter by risk level.
    """
    all_findings = []

    for scan_id, result in scan_results.items():
        findings = result.get("findings", [])
        for finding in findings:
            finding_entry = {
                **finding,
                "scan_id": scan_id,
                "commit_id": result.get("commit_id"),
                "overall_score": result.get("final_score"),
            }
            all_findings.append(finding_entry)

    # Filter by risk level if specified
    if risk_level:
        all_findings = [
            f for f in all_findings
            if _categorize(f.get("tool_severity", 0.0)).lower() == risk_level.lower()
        ]

    return {
        "total": len(all_findings),
        "findings": all_findings[:limit],
    }


@app.get("/api/v1/findings/{finding_id}", tags=["Findings"])
def get_finding(finding_id: str):
    """Get details of a specific finding by ID."""
    for scan_id, result in scan_results.items():
        findings = result.get("findings", [])
        for finding in findings:
            if finding.get("finding_id") == finding_id:
                return {
                    **finding,
                    "scan_id": scan_id,
                    "commit_id": result.get("commit_id"),
                    "overall_score": result.get("final_score"),
                    "patch_available": result.get("patch_generated", False),
                    "patch_suggestion": result.get("patch_suggestion"),
                }

    raise HTTPException(status_code=404, detail=f"Finding {finding_id} not found")


# ── Auto-Patch ────────────────────────────────────────────────

@app.post("/api/v1/findings/{finding_id}/patch", tags=["Auto-Patch"])
def request_patch(finding_id: str, request: PatchRequest):
    """
    Request an AI-generated patch for a specific finding.
    The patch will require HITL approval before application.
    """
    # Find the finding
    for scan_id, result in scan_results.items():
        findings = result.get("findings", [])
        for finding in findings:
            if finding.get("finding_id") == finding_id:
                # Re-run just the auto-patcher with this finding
                from .pods.auto_patcher_pod import generate_patch
                patch_result = generate_patch(finding)

                return {
                    "finding_id": finding_id,
                    "patch_status": patch_result.get("status"),
                    "patched_code": patch_result.get("patched_code"),
                    "explanation": patch_result.get("explanation"),
                    "requires_approval": True,
                }

    raise HTTPException(status_code=404, detail=f"Finding {finding_id} not found")


# ── HITL Approval ─────────────────────────────────────────────

@app.get("/api/v1/approvals/pending", tags=["HITL"])
def get_pending_approvals():
    """Get all pending HITL approval requests."""
    return {
        "pending": hitl_manager.get_pending_requests(),
        "total": len(hitl_manager.get_pending_requests()),
    }


@app.post("/api/v1/findings/{finding_id}/approve", tags=["HITL"])
def approve_action(finding_id: str, request: ApprovalRequest):
    """
    Submit a HITL decision (approve/reject/modify) for a finding's action.
    """
    # Find matching pending request
    pending = hitl_manager.get_pending_requests()
    target_request = None

    for req in pending:
        if finding_id in req.get("description", "") or finding_id in str(req.get("data", {})):
            target_request = req
            break

    if not target_request:
        raise HTTPException(
            status_code=404,
            detail=f"No pending approval found for finding {finding_id}"
        )

    result = hitl_manager.process_decision(
        request_id=target_request["request_id"],
        decision=request.decision,
        decided_by=request.decided_by,
        notes=request.notes,
    )

    if not result:
        raise HTTPException(status_code=400, detail="Failed to process decision")

    return {
        "finding_id": finding_id,
        "decision": request.decision,
        "decided_by": request.decided_by,
        "status": "processed",
    }


@app.get("/api/v1/approvals/history", tags=["HITL"])
def get_approval_history():
    """Get the history of all processed HITL decisions."""
    return {
        "history": hitl_manager.get_history(),
        "total": len(hitl_manager.get_history()),
    }


# ── Tickets ───────────────────────────────────────────────────

@app.get("/api/v1/tickets", tags=["Tickets"])
def list_tickets():
    """List all created Jira tickets across all scans."""
    tickets = []

    for scan_id, result in scan_results.items():
        ticket_id = result.get("jira_ticket_id")
        if ticket_id and ticket_id not in ("SKIPPED", None):
            tickets.append({
                "ticket_id": ticket_id,
                "scan_id": scan_id,
                "commit_id": result.get("commit_id"),
                "final_score": result.get("final_score"),
                "risk_level": result.get("risk_level"),
                "status": result.get("status"),
                "patch_available": result.get("patch_generated", False),
            })

    return {
        "total": len(tickets),
        "tickets": tickets,
    }


# ── Dashboard Summary ────────────────────────────────────────

@app.get("/api/v1/dashboard/summary", tags=["Dashboard"])
def dashboard_summary():
    """
    Aggregated summary for the ACIP Dashboard.
    Provides an overview of all scans, findings, and remediation status.
    """
    total_scans = len(scan_results)
    total_findings = sum(
        len(r.get("findings", [])) for r in scan_results.values()
    )
    critical_findings = sum(
        1 for r in scan_results.values()
        for f in r.get("findings", [])
        if f.get("tool_severity", 0.0) >= 9.0
    )
    tickets_created = sum(
        1 for r in scan_results.values()
        if r.get("jira_ticket_id") and r.get("jira_ticket_id") not in ("SKIPPED", None)
    )
    patches_generated = sum(
        1 for r in scan_results.values()
        if r.get("patch_generated")
    )
    pending_approvals = len(hitl_manager.get_pending_requests())

    # Risk distribution
    risk_distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
    for result in scan_results.values():
        for finding in result.get("findings", []):
            level = _categorize(finding.get("tool_severity", 0.0))
            risk_distribution[level] = risk_distribution.get(level, 0) + 1

    return {
        "module_name": settings.MODULE_NAME,
        "model": settings.PRIMARY_AGENT_MODEL,
        "summary": {
            "total_scans": total_scans,
            "total_findings": total_findings,
            "critical_findings": critical_findings,
            "tickets_created": tickets_created,
            "patches_generated": patches_generated,
            "pending_approvals": pending_approvals,
<<<<<<< HEAD
            "endpoint_events": len(endpoint_events),
            "endpoint_assets": len(endpoint_registry),
            "endpoint_escalations": sum(
                1 for event in endpoint_events if event["status"] == "ESCALATED"
            ),
        },
        "risk_distribution": risk_distribution,
        "endpoint_summary": {
            "risk_distribution": _build_endpoint_risk_distribution(),
            "recent_endpoints": list(endpoint_registry.values())[-10:],
        },
=======
        },
        "risk_distribution": risk_distribution,
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
        "recent_scans": [
            {
                "scan_id": sid,
                "status": r.get("status"),
                "score": r.get("final_score"),
                "risk_level": r.get("risk_level"),
                "submitted_at": r.get("submitted_at"),
            }
            for sid, r in list(scan_results.items())[-10:]  # Last 10
        ],
    }


# ── Live Stream (WebSocket) ──────────────────────────────────

@app.websocket("/api/v1/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for live AI thought process streaming.
    The ACIP Dashboard connects here to show real-time AI decisions.
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"[WebSocket] New connection. Total: {len(active_connections)}")

    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back acknowledgment
            await websocket.send_json({
                "type": "ack",
                "message": f"Received: {data}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"[WebSocket] Disconnected. Total: {len(active_connections)}")


# ══════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════

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
<<<<<<< HEAD


def _recommend_endpoint_action(event_type: str, severity: float) -> str:
    """Generate a default recommended action for endpoint events."""
    normalized_type = (event_type or "").lower()

    if severity >= 9.0:
        return "Isolate the host immediately and trigger incident response."
    if "ransom" in normalized_type or "malware" in normalized_type:
        return "Quarantine the endpoint, collect artifacts, and block related hashes."
    if "powershell" in normalized_type or "script" in normalized_type:
        return "Review the executed script, validate parent process chain, and restrict execution policy."
    if "credential" in normalized_type or "login" in normalized_type:
        return "Reset affected credentials and verify lateral movement attempts."
    if severity >= 7.0:
        return "Escalate to SOC triage and review endpoint containment options."
    return "Monitor the endpoint and enrich the event with more telemetry."


def _build_endpoint_risk_distribution() -> Dict[str, int]:
    """Summarize risk levels across endpoint events."""
    distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
    for event in endpoint_events:
        distribution[event["risk_level"]] = distribution.get(event["risk_level"], 0) + 1
    return distribution


def _recent_endpoint_event_types(endpoint_id: str) -> List[str]:
    """Return a compact list of recent event types observed for an endpoint."""
    seen: List[str] = []
    for event in reversed(endpoint_events):
        if event["endpoint_id"] != endpoint_id:
            continue
        event_type = event["event_type"]
        if event_type not in seen:
            seen.append(event_type)
        if len(seen) == 5:
            break
    return list(reversed(seen))
=======
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
