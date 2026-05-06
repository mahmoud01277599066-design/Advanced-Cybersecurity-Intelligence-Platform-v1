"""
DevSecOps Module - Auto-Patcher Pod
Generates AI-powered code patches for security vulnerabilities.
Uses qwen2.5-coder:7b via Ollama for code fix generation.
Requires HITL approval before applying patches.

Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any, Optional
from ..core_orchestrator.state_schema import DevSecOpsState
from ..core_orchestrator.hitl_manager import hitl_manager, update_state_for_hitl
from ..src.core.llm_client import llm_client
from ..src.core.config import settings
from ..src.core.logger import get_logger
import uuid

logger = get_logger(__name__)


def generate_patch(
    finding: Dict[str, Any],
    rag_context: str = "",
) -> Dict[str, Any]:
    """
    Generate an AI-powered code patch for a vulnerability.

    Args:
        finding: The vulnerability finding dict.
        rag_context: Additional context from RAG retriever.

    Returns:
        Dict with patch details: original_code, patched_code, explanation.
    """
    vulnerability = f"{finding.get('finding_id', 'Unknown')} - {finding.get('message', '')}"
    code_snippet = finding.get("code_snippet", "")
    file_path = finding.get("file_path", "N/A")

    if not code_snippet:
        return {
            "status": "no_code",
            "original_code": "",
            "patched_code": "",
            "explanation": (
                f"No code snippet available for finding {finding.get('finding_id')}. "
                f"Manual review required for file: {file_path}"
            ),
        }

    # Generate patch using LLM
    if llm_client.is_available:
        patch_response = llm_client.invoke_for_patch_generation(
            code_snippet=code_snippet,
            vulnerability=vulnerability,
        )
    else:
        patch_response = (
            f"[FALLBACK] Auto-patch unavailable (LLM offline).\n"
            f"Manual fix required for: {vulnerability}\n"
            f"File: {file_path}\n"
            f"Recommendation: Review and fix the vulnerability in the affected code."
        )

    return {
        "status": "generated",
        "finding_id": finding.get("finding_id"),
        "file_path": file_path,
        "original_code": code_snippet,
        "patched_code": patch_response,
        "explanation": f"AI-generated patch for {vulnerability}",
        "rag_context_used": bool(rag_context),
    }


def auto_patcher_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Generate automated code patches for high-priority findings.

    Workflow:
    1. Get the highest severity finding from parsed_findings.
    2. Generate a patch using the LLM.
    3. Request HITL approval before applying.
    4. Update state with patch suggestion and HITL flag.
    """
    findings = state.get("parsed_findings", [])
    final_score = state.get("final_priority_score", 0.0)

    thought_process = "[Auto-Patcher Pod] Starting automated patch generation. "

    if not findings:
        thought_process += "No findings to patch."
        logger.info("[Auto-Patcher Pod] No findings → Skipped")
        return {
            "pod_name": "auto_patcher_pod",
            "patch_suggestion": None,
            "remediation_status": "NO_PATCH_NEEDED",
            "ai_thought_process": thought_process,
            "human_approval_required": False,
            "data_payload": {},
            "messages": state.get("messages", []) + [
                "[Auto-Patcher] No findings to patch."
            ],
        }

    # Sort findings by severity and take the most critical
    sorted_findings = sorted(
        findings,
        key=lambda f: f.get("tool_severity", 0.0),
        reverse=True
    )
    target_finding = sorted_findings[0]

    thought_process += (
        f"Targeting highest severity finding: {target_finding.get('finding_id')} "
        f"(severity: {target_finding.get('tool_severity')}) in "
        f"{target_finding.get('file_path')}. "
    )

    # Generate patch
    logger.info(
        f"[Auto-Patcher Pod] Generating patch for: "
        f"{target_finding.get('finding_id')}"
    )
    patch_result = generate_patch(target_finding)

    thought_process += (
        f"Patch generation status: {patch_result['status']}. "
    )

    # Determine if HITL approval is needed
    needs_approval = hitl_manager.should_require_approval(
        action_type="apply_patch",
        risk_level="critical" if final_score >= 9.0 else "high"
    )

    if needs_approval:
        request_id = f"patch_{uuid.uuid4().hex[:8]}"
        hitl_manager.create_approval_request(
            request_id=request_id,
            action_type="apply_patch",
            description=(
                f"Auto-generated patch for {target_finding.get('finding_id')} "
                f"in {target_finding.get('file_path')}. "
                f"Priority score: {final_score}."
            ),
            risk_level="critical" if final_score >= 9.0 else "high",
            data=patch_result,
        )
        thought_process += (
            "This is a high-risk action. Requesting human approval "
            "before applying the patch."
        )

    hitl_message = None
    if needs_approval:
        hitl_message = (
            f"🔧 Auto-Patch Generated for {target_finding.get('finding_id')}\n"
            f"File: {target_finding.get('file_path')}\n"
            f"Severity: {target_finding.get('tool_severity')}\n"
            f"Score: {final_score}\n\n"
            f"Do you approve applying this patch?"
        )

    logger.info(
        f"[Auto-Patcher Pod] Patch generated | "
        f"HITL required: {needs_approval}"
    )

    return {
        "pod_name": "auto_patcher_pod",
        "patch_suggestion": patch_result.get("patched_code", ""),
        "remediation_status": "PATCH_GENERATED",
        "ai_thought_process": thought_process,
        "human_approval_required": needs_approval,
        "hitl_message": hitl_message,
        "data_payload": {
            "patch_result": patch_result,
            "target_finding": target_finding.get("finding_id"),
            "needs_approval": needs_approval,
        },
        "messages": state.get("messages", []) + [
            f"[Auto-Patcher] Patch generated for {target_finding.get('finding_id')} "
            f"(approval {'required' if needs_approval else 'not required'})"
        ],
    }
