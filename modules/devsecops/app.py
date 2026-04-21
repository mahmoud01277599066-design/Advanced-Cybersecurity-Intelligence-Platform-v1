"""
DevSecOps Module - FastAPI Application
Provides REST API endpoints for the ACIP Dashboard and external integrations.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-Memory Storage ───────────────────────────────────────
scan_results: Dict[str, Dict[str, Any]] = {}
endpoint_events: List[Dict[str, Any]] = []
endpoint_registry: Dict[str, Dict[str, Any]] = {}
active_connections: List[WebSocket] = []

# ══════════════════════════════════════════════════════════════
# Request/Response Models
# ══════════════════════════════════════════════════════════════

class ScanSubmitRequest(BaseModel):
    sarif_data: Any
    commit_id: Optional[str] = None

class ApprovalRequest(BaseModel):
    decision: str
    decided_by: str = "analyst"
    notes: str = ""

class PatchRequest(BaseModel):
    vulnerability_type: Optional[str] = None

class SOCAlertRequest(BaseModel):
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

class EndpointEventRequest(BaseModel):
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

# ══════════════════════════════════════════════════════════════
# WebSocket Manager
# ══════════════════════════════════════════════════════════════

async def broadcast_message(message: Dict[str, Any]):
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

@app.get("/", tags=["Health"])
def read_root():
    return {
        "service_status": "Running",
        "module_name": settings.MODULE_NAME,
        "version": settings.MODULE_VERSION,
        "model": settings.PRIMARY_AGENT_MODEL,
    }

@app.post("/api/v1/scan/submit", tags=["Scans"])
def submit_scan(request: ScanSubmitRequest):
    scan_id = str(uuid.uuid4())
    commit_id = request.commit_id or f"auto_{uuid.uuid4().hex[:8]}"
    try:
        initial_input = INITIAL_STATE.copy()
        initial_input["sarif_input"] = request.sarif_data
        initial_input["commit_id"] = commit_id
        final_state = devsecops_graph.invoke(initial_input)
        
        result = {
            "scan_id": scan_id,
            "commit_id": commit_id,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": final_state.get("remediation_status", "UNKNOWN"),
            "final_score": final_state.get("final_priority_score"),
            "risk_level": _categorize(final_state.get("final_priority_score", 0.0)),
            "findings": final_state.get("parsed_findings", []),
            "patch_generated": bool(final_state.get("patch_suggestion")),
        }
        scan_results[scan_id] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/soc/alerts", tags=["SOC"])
async def receive_soc_alert(request: SOCAlertRequest):
    """يستقبل التنبيهات من الـ SOC ويعرضها فوراً"""
    alert_id = request.alert_id
    scan_results[alert_id] = {
        **request.dict(),
        "status": "RECEIVED",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "risk_level": _categorize(request.severity)
    }
    # إرسال تنبيه فوري للـ Dashboard عبر WebSocket
    await broadcast_message({"type": "new_soc_alert", "data": request.dict()})
    return {"status": "received", "alert_id": alert_id}

@app.post("/api/v1/endpoints/events", tags=["Endpoint"])
def ingest_endpoint_event(request: EndpointEventRequest):
    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    event_record = {
        **request.dict(),
        "event_id": event_id,
        "risk_level": _categorize(request.severity),
        "status": "ESCALATED" if request.severity >= 8.0 else "INGESTED",
        "timestamp": request.timestamp or datetime.now(timezone.utc).isoformat()
    }
    endpoint_events.append(event_record)
    endpoint_registry[request.endpoint_id] = event_record
    return {"status": "received", "event_id": event_id}

@app.get("/api/v1/dashboard/summary", tags=["Dashboard"])
def dashboard_summary():
    """الخلاصة المجمعة لعرضها في الـ Dashboard"""
    return {
        "summary": {
            "total_scans": len([s for s in scan_results.values() if "alert_type" not in s]),
            "total_findings": sum(len(r.get("findings", [])) for r in scan_results.values() if "findings" in r),
            "soc_alerts": len([s for s in scan_results.values() if "alert_type" in s]),
            "endpoint_events": len(endpoint_events),
            "critical_issues": sum(1 for e in endpoint_events if e["severity"] >= 9.0)
        },
        "risk_distribution": _build_risk_distribution(),
        "recent_activities": list(scan_results.values())[-10:]
    }

@app.get("/api/v1/findings", tags=["Findings"])
def list_findings(risk_level: Optional[str] = None):
    all_findings = []
    for sid, res in scan_results.items():
        if "findings" in res:
            for f in res["findings"]:
                all_findings.append({**f, "scan_id": sid})
    return {"total": len(all_findings), "findings": all_findings}

@app.websocket("/api/v1/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# ── Utilities ────────────────────────────────────────────────

def _categorize(score: float) -> str:
    if score is None: return "NONE"
    if score >= 9.0: return "CRITICAL"
    elif score >= 7.0: return "HIGH"
    elif score >= 4.0: return "MEDIUM"
    elif score > 0.0: return "LOW"
    return "NONE"

def _build_risk_distribution():
    dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for res in scan_results.values():
        level = _categorize(res.get("severity", res.get("final_score", 0)))
        if level in dist: dist[level] += 1
    return dist