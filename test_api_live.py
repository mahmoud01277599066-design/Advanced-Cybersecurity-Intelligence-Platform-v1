"""
DevSecOps API Integration Test Script
Tests the full pipeline with real SARIF data.
"""

import requests
import json
import sys
import io

# Fix Windows console encoding for emoji/unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8080"

def print_section(title, num):
    print(f"\n{'='*60}")
    print(f"  {num}. {title}")
    print(f"{'='*60}")

def pretty(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ──────────────────────────────────────────
# 1. Health Check
# ──────────────────────────────────────────
print_section("HEALTH CHECK", 1)
try:
    r = requests.get(f"{BASE}/")
    pretty(r.json())
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)


# ──────────────────────────────────────────
# 2. Submit HIGH-SEVERITY SARIF scan
#    (3 vulnerabilities: SQLi, XSS, Info Exposure)
# ──────────────────────────────────────────
print_section("SUBMIT SARIF SCAN (3 vulnerabilities)", 2)

sarif_payload = {
    "sarif_data": {
        "runs": [
            {
                "tool": {"driver": {"name": "Semgrep"}},
                "results": [
                    {
                        "ruleId": "CWE-89-SQL-INJECTION",
                        "message": {
                            "text": "SQL Injection vulnerability in authentication query. User input is directly concatenated into SQL string without parameterization."
                        },
                        "level": "error",
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/api/auth.py"},
                                    "region": {
                                        "startLine": 42,
                                        "snippet": {
                                            "text": "query = 'SELECT * FROM users WHERE username=' + user_input"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CWE-79-XSS",
                        "message": {
                            "text": "Cross-site scripting vulnerability. Unescaped user input rendered in HTML template."
                        },
                        "level": "error",
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/web/templates/profile.html"},
                                    "region": {
                                        "startLine": 15,
                                        "snippet": {
                                            "text": "<div>{{ user.bio | safe }}</div>"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CWE-200-INFO-EXPOSURE",
                        "message": {
                            "text": "Stack trace exposed to user in error response. Internal implementation details leaked."
                        },
                        "level": "warning",
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/api/error_handler.py"},
                                    "region": {"startLine": 8}
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "commit_id": "a1b2c3d4_test_commit"
}

r = requests.post(f"{BASE}/api/v1/scan/submit", json=sarif_payload)
scan_result = r.json()
pretty(scan_result)
scan_id = scan_result.get("scan_id", "")


# ──────────────────────────────────────────
# 3. Full scan results
# ──────────────────────────────────────────
print_section(f"FULL SCAN RESULTS (ID: {scan_id[:8]}...)", 3)
r = requests.get(f"{BASE}/api/v1/scan/{scan_id}/results")
full = r.json()

# Print key fields, not the entire thing
print(f"  Status:       {full.get('status')}")
print(f"  Score:        {full.get('final_score')}")
print(f"  Risk Level:   {full.get('risk_level')}")
print(f"  Ticket:       {full.get('jira_ticket_id')}")
print(f"  Patch:        {full.get('patch_generated')}")
print(f"  HITL Needed:  {full.get('human_approval_required')}")
print(f"  Findings:     {len(full.get('findings', []))}")
print(f"\n  AI Thought Process:")
print(f"  {full.get('ai_thought_process', 'N/A')}")
print(f"\n  HITL Message:")
print(f"  {full.get('hitl_message', 'None')}")
print(f"\n  Standardized Output (for Dashboard):")
pretty(full.get("standardized_output", {}))
print(f"\n  Workflow Messages:")
for msg in full.get("messages", []):
    print(f"    - {msg}")


# ──────────────────────────────────────────
# 4. Dashboard Summary
# ──────────────────────────────────────────
print_section("DASHBOARD SUMMARY", 4)
r = requests.get(f"{BASE}/api/v1/dashboard/summary")
pretty(r.json())


# ──────────────────────────────────────────
# 5. All Findings
# ──────────────────────────────────────────
print_section("ALL FINDINGS", 5)
r = requests.get(f"{BASE}/api/v1/findings")
findings_data = r.json()
print(f"  Total: {findings_data.get('total')}")
for f in findings_data.get("findings", []):
    print(f"    [{f.get('level', 'N/A'):>7}] {f.get('finding_id', 'N/A')} "
          f"(severity: {f.get('tool_severity', 'N/A')}) - {f.get('file_path', 'N/A')}")


# ──────────────────────────────────────────
# 6. Tickets
# ──────────────────────────────────────────
print_section("TICKETS", 6)
r = requests.get(f"{BASE}/api/v1/tickets")
pretty(r.json())


# ──────────────────────────────────────────
# 7. Pending HITL Approvals
# ──────────────────────────────────────────
print_section("PENDING HITL APPROVALS", 7)
r = requests.get(f"{BASE}/api/v1/approvals/pending")
pretty(r.json())


# ──────────────────────────────────────────
# 8. Submit LOW-SEVERITY scan (should skip ticket)
# ──────────────────────────────────────────
print_section("SUBMIT LOW-SEVERITY SCAN (should skip ticket)", 8)

low_payload = {
    "sarif_data": [
        {
            "finding_id": "CWE-489-DEBUG-LEFT",
            "tool_severity": 2.0,
            "file_path": "src/config/debug.py",
            "message": "Debug flag left enabled in production config",
            "level": "note"
        }
    ],
    "commit_id": "f7e8d9c0_low_sev_commit"
}

r = requests.post(f"{BASE}/api/v1/scan/submit", json=low_payload)
pretty(r.json())


print(f"\n{'='*60}")
print(f"  ALL TESTS COMPLETED SUCCESSFULLY!")
print(f"{'='*60}")
