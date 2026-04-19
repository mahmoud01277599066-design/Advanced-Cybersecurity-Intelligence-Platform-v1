"""
DevSecOps Module - Dependency Auditor Pod (Real SCA Tool)
Performs Software Composition Analysis (SCA) on a project path.
Searches for requirements.txt or package.json and streams them to the AI 
model to detect CVEs and outdated vulnerable libraries.
"""

import os
import re
from typing import Dict, Any, List
from ..core_orchestrator.state_schema import DevSecOpsState
from ..core_orchestrator.model_router import model_router
from ..src.core.logger import get_logger

logger = get_logger(__name__)


def audit_manifest(file_path: str, root_dir: str) -> List[Dict[str, Any]]:
    """Reads a dependency file and asks the LLM to find CVEs."""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        rel_path = os.path.relpath(file_path, root_dir)
        logger.info(f"[Dependency Auditor] Auditing manifest: {rel_path}")
        
        context = {
            "file_path": rel_path,
            "file_content": content,
        }
        
        ai_response = model_router.route("dependency_audit", context)
        
        # Simple extraction logic based on our strict prompt:
        # PACKAGE: <name>
        # VERSION: <version>
        # SEVERITY: <score>
        # CVE: <CVE>
        # DESCRIPTION: <text>
        
        blocks = ai_response.split("PACKAGE:")
        for block in blocks[1:]:
            try:
                # Basic regex extraction
                name_match = re.search(r"^\s*(.*?)\n", block)
                version_match = re.search(r"VERSION:\s*(.*?)\n", block)
                severity_match = re.search(r"SEVERITY:\s*([\d.]+)", block)
                cve_match = re.search(r"CVE:\s*(.*?)\n", block)
                desc_match = re.search(r"DESCRIPTION:\s*(.*)", block, re.DOTALL)
                
                if name_match and version_match:
                    pkg_name = name_match.group(1).strip()
                    severity = float(severity_match.group(1)) if severity_match else 7.0
                    cve = cve_match.group(1).strip() if cve_match else "CVE-UNKNOWN"
                    
                    findings.append({
                        "finding_id": f"SCA-{rel_path.replace(os.sep, '-')}-{pkg_name}",
                        "tool_name": "AI-Dependency-Auditor",
                        "tool_severity": severity,
                        "file_path": rel_path,
                        "start_line": 1,
                        "code_snippet": f"Package: {pkg_name} v{version_match.group(1).strip()}",
                        "message": f"Detected vulnerable dependency {pkg_name}. {cve}. " + 
                                   (desc_match.group(1).strip()[:200] + "..." if desc_match else ""),
                        "level": "error" if severity >= 7.0 else "warning",
                    })
            except Exception as parse_e:
                logger.warning(f"[Dependency Auditor] Failed to parse a block from AI: {parse_e}")
                
        return findings

    except Exception as e:
        logger.error(f"[Dependency Auditor] Failed to audit {file_path}: {e}")
        return []


def dependency_auditor_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Find dependency manifests and audit them.
    """
    directory_path = state.get("data_payload", {}).get("directory_path")
    
    if not directory_path or not os.path.exists(directory_path):
        return {
            "pod_name": "dependency_auditor_pod",
            "ai_thought_process": "[Dependency Auditor] No valid directory path provided for audit.",
            "messages": state.get("messages", []) + ["[Dependency Auditor] Skipped: No target directory."]
        }

    thought_process = f"[Dependency Auditor Pod] Scanning directory {directory_path} for manifests... "
    all_findings = []
    scanned_files = []

    # Targeting standard manifests
    TARGETS = ('requirements.txt', 'package.json')

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file in TARGETS:
                full_path = os.path.join(root, file)
                scanned_files.append(file)
                file_findings = audit_manifest(full_path, directory_path)
                all_findings.extend(file_findings)

    if not scanned_files:
        thought_process += "No manifest files found. "
    else:
        thought_process += (
            f"Found {len(scanned_files)} manifest(s) ({', '.join(scanned_files)}). "
            f"AI identified {len(all_findings)} outdated or vulnerable dependencies."
        )

    logger.info(f"[Dependency Auditor Pod] Completed. Found {len(all_findings)} CVEs.")

    # We append findings to existing parsed_findings to support chaining with other scanners
    existing_findings = state.get("parsed_findings", [])
    combined_findings = existing_findings + all_findings

    return {
        "parsed_findings": combined_findings,
        "pod_name": "dependency_auditor_pod",
        "remediation_status": "DEPENDENCY_AUDIT_COMPLETE",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            **state.get("data_payload", {}),
            "manifests_scanned": len(scanned_files),
            "dependency_findings": all_findings,
        },
        "messages": state.get("messages", []) + [
            f"[Dependency Auditor] Audited {len(scanned_files)} manifests: Found {len(all_findings)} vulnerable dependencies."
        ],
    }
