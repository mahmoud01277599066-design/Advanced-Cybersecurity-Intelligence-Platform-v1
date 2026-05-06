"""
DevSecOps Module - Source Scanner Pod (Real)
Performs an AI-powered white-box security audit of local source code files.
Unlike the SAST Parser, this pod reads files directly and identifies bugs via AI.
"""

import os
from typing import Dict, Any, List
from ..core_orchestrator.state_schema import DevSecOpsState
from ..core_orchestrator.model_router import model_router
from ..src.core.logger import get_logger

logger = get_logger(__name__)


def scan_source_file(file_path: str, root_dir: str) -> List[Dict[str, Any]]:
    """
    Read a source file and use the AI to detect vulnerabilities.
    """
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        rel_path = os.path.relpath(file_path, root_dir)
        extension = os.path.splitext(file_path)[1].lower()
        
        logger.info(f"[Source Scanner] Auditing file: {rel_path}")
        
        # Determine vulnerability description for the AI
        context = {
            "vulnerability": "Perform a general security code review. Look for SQLi, XSS, RCE, Secrets Leak, etc.",
            "file_path": rel_path,
            "code_snippet": content,
            "rag_context": "Standard OWASP Top 10 security audit principles."
        }
        
        # 1. AI Analysis
        ai_response = model_router.route("code_analysis", context)
        
        # 2. Heuristic Backup (Real-world SAST pattern)
        # If AI is in fallback or fails to catch it, use heuristic matching for common flaws
        has_vulnerability = "vulnerability" in ai_response.lower() or "critical" in ai_response.lower() or "high" in ai_response.lower()
        
        # SQL Injection Heuristic
        if not has_vulnerability and ".execute(" in content and ("f\"" in content or ".format(" in content):
             has_vulnerability = True
             ai_response = "[HEURISTIC] Detected potential SQL Injection: User-controlled string formatting used in a SQL execution call."

        # Command Injection Heuristic
        if not has_vulnerability and (".system(" in content or "subprocess." in content) and ("f\"" in content or ".format(" in content):
             has_vulnerability = True
             ai_response = "[HEURISTIC] Detected potential Command Injection: User-supplied input passed directly to a system command execution function."

        if has_vulnerability:
             # Create a finding based on analysis
             findings.append({
                "finding_id": f"AI-AUDIT-{rel_path.replace(os.sep, '-')}",
                "tool_name": "AI-WhiteBox-Scanner",
                "tool_severity": 9.0 if "critical" in ai_response.lower() else 7.5,
                "file_path": rel_path,
                "start_line": 1, # AI usually gives the block
                "code_snippet": content[:500] + "...", # Truncated
                "message": ai_response,
                "level": "error" if "critical" in ai_response.lower() else "warning",
            })
            
        return findings

    except Exception as e:
        logger.error(f"[Source Scanner] Failed to audit {file_path}: {e}")
        return []


def source_scanner_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Crawl a source directory and perform AI audit.
    """
    directory_path = state.get("data_payload", {}).get("directory_path")
    
    if not directory_path or not os.path.exists(directory_path):
        return {
            "pod_name": "source_scanner_pod",
            "ai_thought_process": "[Source Scanner] No valid directory path provided for audit.",
            "messages": state.get("messages", []) + ["[Source Scanner] Skipped: No target directory."]
        }

    thought_process = f"[Source Scanner Pod] Starting live audit of directory: {directory_path}. "
    all_findings = []
    scanned_files = []

    # Supported file types
    SUPPORTED = ('.py', '.js', '.ts', '.html')

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(SUPPORTED):
                full_path = os.path.join(root, file)
                scanned_files.append(file)
                file_findings = scan_source_file(full_path, directory_path)
                all_findings.extend(file_findings)

    thought_process += (
        f"Scanned {len(scanned_files)} files ({', '.join(scanned_files)}). "
        f"AI identified {len(all_findings)} potential vulnerabilities."
    )

    logger.info(f"[Source Scanner Pod] Completed. Found {len(all_findings)} issues.")

    return {
        "parsed_findings": all_findings,
        "pod_name": "source_scanner_pod",
        "remediation_status": "ANALYSIS_COMPLETE",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            "total_files_scanned": len(scanned_files),
            "findings_summary": all_findings,
            "directory_path": directory_path
        },
        "messages": state.get("messages", []) + [
            f"[Source Scanner] Audited {len(scanned_files)} files: Found {len(all_findings)} vulnerabilities."
        ],
    }
