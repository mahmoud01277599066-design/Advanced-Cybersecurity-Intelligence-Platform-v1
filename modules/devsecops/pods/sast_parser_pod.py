"""
DevSecOps Module - SAST Parser Pod
Parses SARIF and other SAST tool outputs into normalized findings.
Output follows the ACIP Standardized Output Protocol.
"""

from typing import Dict, Any, List
from ..core_orchestrator.state_schema import DevSecOpsState
from ..src.core.logger import get_logger

logger = get_logger(__name__)


def parse_sarif_findings(sarif_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse SARIF format data and extract security findings.

    Args:
        sarif_data: SARIF format JSON data (with "runs" key).

    Returns:
        List of parsed findings with standardized format.
    """
    findings = []

    try:
        runs = sarif_data.get("runs", [])

        for run in runs:
            tool_name = run.get("tool", {}).get("driver", {}).get("name", "Unknown Tool")
            results = run.get("results", [])

            for result in results:
                rule_id = result.get("ruleId", "UNKNOWN")
                message = result.get("message", {}).get("text", "")
                level = result.get("level", "warning")

                severity_map = {
                    "error": 9.0,
                    "warning": 6.0,
                    "note": 3.0,
                    "none": 0.0,
                }
                severity = severity_map.get(level, 5.0)

                # Extract location
                locations = result.get("locations", [])
                file_path = "N/A"
                start_line = 0
                code_snippet = ""

                if locations:
                    phys_loc = locations[0].get("physicalLocation", {})
                    artifact_loc = phys_loc.get("artifactLocation", {})
                    file_path = artifact_loc.get("uri", "N/A")
                    region = phys_loc.get("region", {})
                    start_line = region.get("startLine", 0)
                    code_snippet = region.get("snippet", {}).get("text", "")

                findings.append({
                    "finding_id": rule_id,
                    "tool_name": tool_name,
                    "tool_severity": severity,
                    "file_path": file_path,
                    "start_line": start_line,
                    "code_snippet": code_snippet,
                    "message": message,
                    "level": level,
                })

        return findings

    except Exception as e:
        logger.error(f"Failed to parse SARIF data: {e}")
        return []


def normalize_findings(raw_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize a list of pre-parsed findings to ensure consistent schema.

    Args:
        raw_findings: List of finding dicts (possibly from direct input).

    Returns:
        List of normalized finding dicts.
    """
    normalized = []

    for f in raw_findings:
        normalized.append({
            "finding_id": f.get("finding_id", f.get("ruleId", "UNKNOWN")),
            "tool_name": f.get("tool_name", "Unknown"),
            "tool_severity": float(f.get("tool_severity", f.get("severity", 5.0))),
            "file_path": f.get("file_path", f.get("uri", "N/A")),
            "start_line": int(f.get("start_line", 0)),
            "code_snippet": f.get("code_snippet", ""),
            "message": f.get("message", ""),
            "level": f.get("level", "warning"),
        })

    return normalized


def sast_parser_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    Pod Node: Parse and normalize SAST scan results.

    Accepts both:
    - Raw SARIF format (dict with "runs" key)
    - Pre-parsed findings list (list of dicts with "finding_id")

    Updates state with normalized findings and standardized output.
    """
    sarif_input = state.get("sarif_input", [])
    commit_id = state.get("commit_id", "UNKNOWN")

    thought_process = f"[SAST Parser Pod] Processing scan data for commit {commit_id}. "

    # Determine input format and parse
    if isinstance(sarif_input, dict):
        findings = parse_sarif_findings(sarif_input)
        thought_process += f"Parsed SARIF format input. "
    elif isinstance(sarif_input, list):
        findings = normalize_findings(sarif_input)
        thought_process += f"Normalized pre-parsed findings list. "
    else:
        findings = []
        thought_process += "No valid scan data found. "

    thought_process += f"Extracted {len(findings)} findings. "

    # Log findings summary
    if findings:
        severity_counts = {"error": 0, "warning": 0, "note": 0}
        for f in findings:
            level = f.get("level", "warning")
            severity_counts[level] = severity_counts.get(level, 0) + 1

        thought_process += (
            f"Breakdown: {severity_counts.get('error', 0)} critical, "
            f"{severity_counts.get('warning', 0)} warning, "
            f"{severity_counts.get('note', 0)} info."
        )

        for idx, finding in enumerate(findings[:5], 1):
            logger.info(
                f"  Finding {idx}: {finding['finding_id']} - "
                f"Severity: {finding['tool_severity']} - "
                f"File: {finding['file_path']}"
            )

    logger.info(f"[SAST Parser Pod] Parsed {len(findings)} findings")

    return {
        "parsed_findings": findings,
        "commit_id": commit_id,
        "pod_name": "sast_parser_pod",
        "remediation_status": "ANALYSIS_COMPLETE",
        "ai_thought_process": thought_process,
        "human_approval_required": False,
        "data_payload": {
            "total_findings": len(findings),
            "findings_summary": findings[:10],  # First 10 for payload
            "commit_id": commit_id,
        },
        "messages": state.get("messages", []) + [
            f"[SAST Parser] Analyzed commit {commit_id}: {len(findings)} findings"
        ],
    }
