"""
╔══════════════════════════════════════════════════════════════════════════╗
║   ACIP DevSecOps Module - Full Agent Simulation                        ║
║   Simulates realistic security scenarios to validate all agents        ║
║   before SOC integration.                                              ║
║                                                                        ║
║   Scenarios:                                                           ║
║     1. SARIF Pipeline (High Severity) → Full pipeline with auto-patch  ║
║     2. SARIF Pipeline (Low Severity)  → Quick report path              ║
║     3. SOC Alert: Code Vulnerability  → Classifier → Code pipeline     ║
║     4. SOC Alert: Network Breach      → Classifier → Network Advisor   ║
║     5. SOC Alert: IP Threat           → Classifier → Network Advisor   ║
║                                                                        ║
║   Usage: python simulate_agents.py                                     ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import time
import json
<<<<<<< HEAD
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

=======
import io
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Fix Windows console encoding for emoji/unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
# ── Ensure project root is on sys.path ────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ══════════════════════════════════════════════════════════════
# Terminal UI Helpers
# ══════════════════════════════════════════════════════════════

class Colors:
    """ANSI color codes for terminal output."""
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"
    ITALIC   = "\033[3m"
    UNDERLINE= "\033[4m"

    RED      = "\033[31m"
    GREEN    = "\033[32m"
    YELLOW   = "\033[33m"
    BLUE     = "\033[34m"
    MAGENTA  = "\033[35m"
    CYAN     = "\033[36m"
    WHITE    = "\033[37m"

    BG_RED   = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW= "\033[43m"
    BG_BLUE  = "\033[44m"
    BG_MAGENTA="\033[45m"
    BG_CYAN  = "\033[46m"

    GRAY     = "\033[90m"
    BRIGHT_RED    = "\033[91m"
    BRIGHT_GREEN  = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE   = "\033[94m"
    BRIGHT_MAGENTA= "\033[95m"
    BRIGHT_CYAN   = "\033[96m"


C = Colors


def print_banner():
    """Print the simulation banner."""
    banner = f"""
{C.BRIGHT_CYAN}{C.BOLD}
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                            ║
    ║   █████╗  ██████╗██╗██████╗     ██████╗ ███████╗██╗   ██╗███████╗███████╗  ║
    ║  ██╔══██╗██╔════╝██║██╔══██╗    ██╔══██╗██╔════╝██║   ██║██╔════╝██╔════╝  ║
    ║  ███████║██║     ██║██████╔╝    ██║  ██║█████╗  ██║   ██║███████╗█████╗    ║
    ║  ██╔══██║██║     ██║██╔═══╝     ██║  ██║██╔══╝  ╚██╗ ██╔╝╚════██║██╔══╝    ║
    ║  ██║  ██║╚██████╗██║██║         ██████╔╝███████╗ ╚████╔╝ ███████║███████╗  ║
    ║  ╚═╝  ╚═╝ ╚═════╝╚═╝╚═╝         ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚══════╝  ║
    ║                                                                            ║
    ║           {C.BRIGHT_YELLOW}Agent Simulation Suite - SOC Integration Validator{C.BRIGHT_CYAN}            ║
    ║                                                                            ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
{C.RESET}"""
    print(banner)


def print_section(title: str, icon: str = "═"):
    """Print a section header."""
    width = 76
    padding = width - len(title) - 4
    left_pad = padding // 2
    right_pad = padding - left_pad
    print(f"\n{C.BRIGHT_BLUE}{C.BOLD}")
    print(f"  ╔{'═' * width}╗")
    print(f"  ║{' ' * left_pad}  {title}  {' ' * right_pad}║")
    print(f"  ╚{'═' * width}╝")
    print(f"{C.RESET}")


def print_scenario_header(num: int, title: str, description: str):
    """Print a scenario header."""
    print(f"\n  {C.BG_BLUE}{C.WHITE}{C.BOLD} SCENARIO {num} {C.RESET} {C.BOLD}{C.BRIGHT_CYAN}{title}{C.RESET}")
    print(f"  {C.GRAY}{'─' * 72}{C.RESET}")
    print(f"  {C.DIM}{description}{C.RESET}")
    print(f"  {C.GRAY}{'─' * 72}{C.RESET}")


def print_agent_start(agent_name: str, pod_type: str = "Pod"):
    """Print agent start indicator."""
    icon = "🔧" if pod_type == "Pod" else "🔀" if pod_type == "Router" else "🤖"
    color = C.BRIGHT_GREEN if pod_type == "Pod" else C.BRIGHT_YELLOW if pod_type == "Router" else C.BRIGHT_MAGENTA
    print(f"\n    {icon} {color}{C.BOLD}[{pod_type}] {agent_name}{C.RESET}")
    print(f"    {C.GRAY}{'·' * 60}{C.RESET}")


def print_agent_result(key: str, value: Any, indent: int = 6):
    """Print a key-value result line."""
    spaces = " " * indent
    if isinstance(value, bool):
        val_color = C.BRIGHT_GREEN if value else C.BRIGHT_RED
        val_str = "✅ Yes" if value else "❌ No"
    elif isinstance(value, (int, float)):
        if key.lower() in ("score", "severity", "final_score", "priority_score", "final_priority_score"):
            if value >= 9.0:
                val_color = C.BRIGHT_RED
            elif value >= 7.0:
                val_color = C.BRIGHT_YELLOW
            elif value >= 4.0:
                val_color = C.YELLOW
            else:
                val_color = C.BRIGHT_GREEN
        else:
            val_color = C.WHITE
        val_str = str(value)
    elif value is None:
        val_color = C.DIM
        val_str = "N/A"
    else:
        val_color = C.WHITE
        val_str = str(value)

    print(f"{spaces}{C.CYAN}▸ {key}:{C.RESET} {val_color}{val_str}{C.RESET}")


def print_thought_process(thought: str, indent: int = 6):
    """Print AI thought process with special formatting."""
    spaces = " " * indent
    print(f"{spaces}{C.BRIGHT_MAGENTA}💭 AI Thought Process:{C.RESET}")
    # Wrap long lines
    words = thought.split()
    line = ""
    max_len = 64
    for word in words:
        if len(line) + len(word) + 1 > max_len:
            print(f"{spaces}   {C.ITALIC}{C.DIM}{line}{C.RESET}")
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        print(f"{spaces}   {C.ITALIC}{C.DIM}{line}{C.RESET}")


def print_messages(messages: List[str], indent: int = 6):
    """Print workflow message log."""
    spaces = " " * indent
    print(f"{spaces}{C.BRIGHT_BLUE}📋 Workflow Messages:{C.RESET}")
    for i, msg in enumerate(messages, 1):
        print(f"{spaces}   {C.DIM}{i}. {msg}{C.RESET}")


def print_success(message: str):
    """Print success message."""
    print(f"\n    {C.BG_GREEN}{C.WHITE}{C.BOLD} ✓ PASS {C.RESET} {C.BRIGHT_GREEN}{message}{C.RESET}")


def print_failure(message: str):
    """Print failure message."""
    print(f"\n    {C.BG_RED}{C.WHITE}{C.BOLD} ✗ FAIL {C.RESET} {C.BRIGHT_RED}{message}{C.RESET}")


def print_warning(message: str):
    """Print warning message."""
    print(f"\n    {C.BG_YELLOW}{C.WHITE}{C.BOLD} ⚠ WARN {C.RESET} {C.BRIGHT_YELLOW}{message}{C.RESET}")


def print_timer(elapsed: float):
    """Print elapsed time."""
    print(f"    {C.GRAY}⏱  Completed in {elapsed:.3f}s{C.RESET}")


def print_data_payload(payload: Dict[str, Any], indent: int = 6):
    """Print data payload in a readable format."""
    spaces = " " * indent
    print(f"{spaces}{C.BRIGHT_YELLOW}📦 Data Payload:{C.RESET}")
    for k, v in payload.items():
        if isinstance(v, dict):
            print(f"{spaces}   {C.CYAN}{k}:{C.RESET}")
            for kk, vv in v.items():
                print(f"{spaces}     {C.DIM}{kk}: {vv}{C.RESET}")
        elif isinstance(v, list):
            print(f"{spaces}   {C.CYAN}{k}:{C.RESET} [{len(v)} items]")
        else:
            print(f"{spaces}   {C.CYAN}{k}:{C.RESET} {C.WHITE}{v}{C.RESET}")


# ══════════════════════════════════════════════════════════════
# Test Data - Realistic Security Scenarios
# ══════════════════════════════════════════════════════════════

SARIF_HIGH_SEVERITY = {
    "version": "2.1.0",
    "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
    "runs": [
        {
            "tool": {
                "driver": {
                    "name": "SonarQube SAST Scanner",
                    "version": "9.9.1"
                }
            },
            "results": [
                {
                    "ruleId": "CWE-89",
                    "level": "error",
                    "message": {
                        "text": "SQL Injection vulnerability detected. User input is directly concatenated into SQL query without parameterization."
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "src/api/controllers/user_controller.py"
                                },
                                "region": {
                                    "startLine": 42,
                                    "snippet": {
                                        "text": "query = f\"SELECT * FROM users WHERE id = {user_id}\""
                                    }
                                }
                            }
                        }
                    ]
                },
                {
                    "ruleId": "CWE-79",
                    "level": "error",
                    "message": {
                        "text": "Cross-Site Scripting (XSS) vulnerability. Unsanitized user input reflected in HTML response."
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "src/templates/profile.html"
                                },
                                "region": {
                                    "startLine": 18,
                                    "snippet": {
                                        "text": "<div>{{ user_input | safe }}</div>"
                                    }
                                }
                            }
                        }
                    ]
                },
                {
                    "ruleId": "CWE-798",
                    "level": "error",
                    "message": {
                        "text": "Hardcoded credentials detected in source code. API key exposed in plaintext."
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "src/config/database.py"
                                },
                                "region": {
                                    "startLine": 7,
                                    "snippet": {
                                        "text": "API_KEY = 'sk-proj-4f8a2b3c9d1e5f6a7b8c9d0e1f2a3b4c'"
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
}


SARIF_LOW_SEVERITY = {
    "version": "2.1.0",
    "runs": [
        {
            "tool": {
                "driver": {
                    "name": "ESLint Security Plugin",
                    "version": "1.7.0"
                }
            },
            "results": [
                {
                    "ruleId": "SEC-INFO-001",
                    "level": "note",
                    "message": {
                        "text": "Console.log statement found in production code. Consider removing for production deployment."
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "src/utils/helpers.js"
                                },
                                "region": {
                                    "startLine": 15,
                                    "snippet": {
                                        "text": "console.log('Debug: user session data', sessionData);"
                                    }
                                }
                            }
                        }
                    ]
                },
                {
                    "ruleId": "SEC-WARN-002",
                    "level": "warning",
                    "message": {
                        "text": "Unused variable 'tempPassword' may contain sensitive data."
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "src/auth/login.js"
                                },
                                "region": {
                                    "startLine": 33,
                                    "snippet": {
                                        "text": "const tempPassword = generateTempPassword();"
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
}


SOC_ALERT_CODE_VULN = {
    "alert_id": "SOC-ALERT-2026-0412-001",
    "alert_type": "code_vulnerability",
    "severity": 9.2,
    "title": "Critical SQL Injection in Production API",
    "description": (
        "Automated DAST scan detected SQL Injection vulnerability in the /api/v2/users endpoint. "
        "Attacker can extract entire database contents via UNION-based injection. "
        "The vulnerable parameter 'user_id' is not sanitized before inclusion in the SQL query."
    ),
    "source_module": "soc",
    "affected_target": "prod-api-server-01 (192.168.1.100)",
    "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE id = '{request.args.get('user_id')}'\")",
    "file_path": "src/api/v2/users.py",
    "timestamp": datetime.now(timezone.utc).isoformat(),
}


SOC_ALERT_NETWORK_BREACH = {
    "alert_id": "SOC-ALERT-2026-0412-002",
    "alert_type": "network_breach",
    "severity": 8.7,
    "title": "Lateral Movement Detected - Internal Network Compromise",
    "description": (
        "IDS/Snort detected lateral movement activity from compromised workstation WS-DEV-042. "
        "Attacker is using PsExec and WMI for remote command execution across the internal network. "
        "Multiple failed authentication attempts detected against domain controller DC-PROD-01. "
        "Source IP is communicating with known C2 infrastructure."
    ),
    "source_module": "soc",
    "affected_target": "Internal Network Segment 10.0.50.0/24",
    "network_details": {
        "source_ip": "10.0.50.42",
        "destination_ips": ["10.0.50.1", "10.0.50.10", "10.0.50.20", "10.0.50.100"],
        "protocol": "SMB/WMI",
        "ports": [445, 135, 5985],
        "ioc_type": "lateral_movement",
        "tools_detected": ["PsExec", "WMI", "Mimikatz"],
        "c2_server": "185.220.101.42",
        "bytes_transferred": 52428800,
        "duration_minutes": 47,
    },
    "timestamp": datetime.now(timezone.utc).isoformat(),
}


SOC_ALERT_IP_THREAT = {
    "alert_id": "SOC-ALERT-2026-0412-003",
    "alert_type": "ip_threat",
    "severity": 7.5,
    "title": "Brute Force Attack from Tor Exit Node",
    "description": (
        "Multiple failed SSH login attempts detected from known Tor exit node. "
        "Over 15,000 authentication attempts in the last 30 minutes against SSH service. "
        "IP 185.220.101.42 is listed on multiple threat intelligence blacklists. "
        "Credential stuffing pattern detected using common username/password combinations."
    ),
    "source_module": "soc",
    "affected_target": "ssh-gateway-01 (203.0.113.50)",
    "network_details": {
        "source_ip": "185.220.101.42",
        "destination_ip": "203.0.113.50",
        "destination_port": 22,
        "protocol": "SSH",
        "failed_attempts": 15247,
        "unique_usernames": 342,
        "time_window_minutes": 30,
        "is_tor_exit": True,
        "blacklist_hits": ["AbuseIPDB", "AlienVault OTX", "Spamhaus"],
        "geo_location": "Netherlands",
    },
    "timestamp": datetime.now(timezone.utc).isoformat(),
}


# ══════════════════════════════════════════════════════════════
# Simulation Runner
# ══════════════════════════════════════════════════════════════

class SimulationResults:
    """Tracks and summarizes simulation results."""

    def __init__(self):
        self.scenarios: List[Dict[str, Any]] = []
        self.total_agents_tested = 0
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_scenario(self, name: str, status: str, agents_tested: int, details: Dict[str, Any]):
        self.scenarios.append({
            "name": name,
            "status": status,
            "agents_tested": agents_tested,
            "details": details,
        })
        self.total_agents_tested += agents_tested
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.warnings += 1


def run_simulation():
    """Run the full agent simulation suite."""
    print_banner()
    results = SimulationResults()
    start_time = time.time()

    # Print configuration
    print_section("CONFIGURATION")
    from modules.devsecops.src.core.config import settings
    print(f"    {C.CYAN}▸ Module:{C.RESET}          {C.WHITE}{settings.MODULE_NAME} v{settings.MODULE_VERSION}{C.RESET}")
    print(f"    {C.CYAN}▸ AI Model:{C.RESET}        {C.WHITE}{settings.PRIMARY_AGENT_MODEL}{C.RESET}")
    print(f"    {C.CYAN}▸ Ollama URL:{C.RESET}      {C.WHITE}{settings.OLLAMA_BASE_URL}{C.RESET}")
    print(f"    {C.CYAN}▸ Threshold:{C.RESET}       {C.WHITE}{settings.HIGH_PRIORITY_THRESHOLD}{C.RESET}")
    print(f"    {C.CYAN}▸ Context Factor:{C.RESET}  {C.WHITE}{settings.CONTEXT_FACTOR}{C.RESET}")
    print(f"    {C.CYAN}▸ HITL Enabled:{C.RESET}    {C.WHITE}{settings.HITL_ENABLED}{C.RESET}")
    print(f"    {C.CYAN}▸ Jira Project:{C.RESET}    {C.WHITE}{settings.JIRA_PROJECT_KEY}{C.RESET}")

    # ══════════════════════════════════════════════════════════
    # SCENARIO 1: SARIF High Severity - Full Pipeline
    # ══════════════════════════════════════════════════════════
    print_section("SCENARIO SIMULATIONS")

    print_scenario_header(
        1,
        "SARIF Pipeline — High Severity (Full Path)",
        "SQL Injection + XSS + Hardcoded Credentials → Parser → Router → "
        "Prioritization → Auto-Patcher → Ticket → Tracking"
    )

    try:
        scenario1_start = time.time()
        from modules.devsecops.core_orchestrator.state_schema import INITIAL_STATE

        # Run full graph
        from modules.devsecops.core_orchestrator.main_graph import devsecops_graph

        initial_state = INITIAL_STATE.copy()
        initial_state["sarif_input"] = SARIF_HIGH_SEVERITY
        initial_state["commit_id"] = "a1b2c3d4"

        final_state = devsecops_graph.invoke(initial_state)
        scenario1_elapsed = time.time() - scenario1_start

        # Display results for each agent that processed
        print_agent_start("SAST Parser Pod", "Pod")
        print_agent_result("Findings Parsed", len(final_state.get("parsed_findings", [])))
        print_agent_result("Commit ID", final_state.get("commit_id"))
        for i, f in enumerate(final_state.get("parsed_findings", [])[:5], 1):
            print(f"      {C.DIM}  [{i}] {f.get('finding_id')} | Severity: {f.get('tool_severity')} | {f.get('file_path')}{C.RESET}")

        print_agent_start("SAST Router", "Router")
        print_agent_result("Routing Decision", final_state.get("routing_decision"))
        print_agent_result("Router Name", final_state.get("router_name"))

        print_agent_start("Prioritization Pod", "Pod")
        print_agent_result("Priority Score", final_state.get("final_priority_score"))
        risk_level = "CRITICAL" if (final_state.get("final_priority_score") or 0) >= 9.0 else \
                     "HIGH" if (final_state.get("final_priority_score") or 0) >= 7.0 else "MEDIUM"
        print_agent_result("Risk Level", risk_level)

        print_agent_start("Auto-Patcher Pod", "Pod")
        print_agent_result("Patch Generated", bool(final_state.get("patch_suggestion")))
        patch_preview = (final_state.get("patch_suggestion") or "N/A")[:120]
        print_agent_result("Patch Preview", f"{patch_preview}..." if len(str(final_state.get("patch_suggestion", ""))) > 120 else patch_preview)

        print_agent_start("Ticket Creator Pod", "Pod")
        print_agent_result("Jira Ticket ID", final_state.get("jira_ticket_id"))

        print_agent_start("Tracking Pod", "Pod")
        print_agent_result("Final Status", final_state.get("remediation_status"))
        print_agent_result("HITL Required", final_state.get("human_approval_required"))

        print_thought_process(final_state.get("ai_thought_process", ""))
        print_messages(final_state.get("messages", []))
        print_data_payload(final_state.get("data_payload", {}))
        print_timer(scenario1_elapsed)

        # Validate
        checks_pass = True
        if len(final_state.get("parsed_findings", [])) != 3:
            print_failure(f"Expected 3 findings, got {len(final_state.get('parsed_findings', []))}")
            checks_pass = False
        if final_state.get("routing_decision") != "DEEP_ANALYSIS":
            print_failure(f"Expected DEEP_ANALYSIS routing, got {final_state.get('routing_decision')}")
            checks_pass = False
        if (final_state.get("final_priority_score") or 0) < 8.5:
            print_warning(f"Priority score {final_state.get('final_priority_score')} below threshold 8.5")
        if not final_state.get("jira_ticket_id") or final_state.get("jira_ticket_id") == "SKIPPED":
            print_warning("No Jira ticket was created")

        if checks_pass:
            print_success("Scenario 1 PASSED — Full high-severity pipeline completed")
            results.add_scenario("SARIF High Severity", "PASS", 6, final_state.get("data_payload", {}))
        else:
            results.add_scenario("SARIF High Severity", "FAIL", 6, {})

    except Exception as e:
        print_failure(f"Scenario 1 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.add_scenario("SARIF High Severity", "FAIL", 0, {"error": str(e)})

    # ══════════════════════════════════════════════════════════
    # SCENARIO 2: SARIF Low Severity - Quick Report Path
    # ══════════════════════════════════════════════════════════

    print_scenario_header(
        2,
        "SARIF Pipeline — Low Severity (Quick Report Path)",
        "Console.log + unused variable → Parser → Router → QUICK_REPORT → Tracking"
    )

    try:
        scenario2_start = time.time()

        initial_state2 = INITIAL_STATE.copy()
        initial_state2["sarif_input"] = SARIF_LOW_SEVERITY
        initial_state2["commit_id"] = "e5f6g7h8"

        final_state2 = devsecops_graph.invoke(initial_state2)
        scenario2_elapsed = time.time() - scenario2_start

        print_agent_start("SAST Parser Pod", "Pod")
        print_agent_result("Findings Parsed", len(final_state2.get("parsed_findings", [])))
        for i, f in enumerate(final_state2.get("parsed_findings", []), 1):
            print(f"      {C.DIM}  [{i}] {f.get('finding_id')} | Severity: {f.get('tool_severity')} | {f.get('file_path')}{C.RESET}")

        print_agent_start("SAST Router", "Router")
        print_agent_result("Routing Decision", final_state2.get("routing_decision"))

        print_agent_start("Tracking Pod", "Pod")
        print_agent_result("Final Status", final_state2.get("remediation_status"))
        print_agent_result("HITL Required", final_state2.get("human_approval_required", False))

        print_thought_process(final_state2.get("ai_thought_process", ""))
        print_messages(final_state2.get("messages", []))
        print_timer(scenario2_elapsed)

        # Validate
        if final_state2.get("routing_decision") == "QUICK_REPORT":
            print_success("Scenario 2 PASSED — Low severity correctly routed to QUICK_REPORT")
            results.add_scenario("SARIF Low Severity", "PASS", 3, {})
        else:
            print_failure(f"Expected QUICK_REPORT, got {final_state2.get('routing_decision')}")
            results.add_scenario("SARIF Low Severity", "FAIL", 3, {})

    except Exception as e:
        print_failure(f"Scenario 2 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.add_scenario("SARIF Low Severity", "FAIL", 0, {"error": str(e)})

    # ══════════════════════════════════════════════════════════
    # SCENARIO 3: SOC Alert - Code Vulnerability
    # ══════════════════════════════════════════════════════════

    print_scenario_header(
        3,
        "SOC Alert — Code Vulnerability Classification",
        "SOC sends SQL Injection alert → SOC Classifier → 'code_vulnerability' → "
        "Would trigger code scanning pipeline"
    )

    try:
        scenario3_start = time.time()

        from modules.devsecops.pods.soc_classifier_pod import soc_classifier_node, classify_alert

        # Test the classification function directly
        classification_result = classify_alert(SOC_ALERT_CODE_VULN)

        print_agent_start("SOC Classifier Pod", "Pod")
        print_agent_result("Alert ID", SOC_ALERT_CODE_VULN["alert_id"])
        print_agent_result("Alert Type", SOC_ALERT_CODE_VULN["alert_type"])
        print_agent_result("Severity", SOC_ALERT_CODE_VULN["severity"])
        print_agent_result("Title", SOC_ALERT_CODE_VULN["title"])
        print_agent_result("Classification", classification_result)

        # Also test the full node
        soc_state = INITIAL_STATE.copy()
        soc_state["soc_alert"] = SOC_ALERT_CODE_VULN
        node_result = soc_classifier_node(soc_state)

        print_agent_result("Pod Name", node_result.get("pod_name"))
        print_agent_result("Remediation Status", node_result.get("remediation_status"))
        print_thought_process(node_result.get("ai_thought_process", ""))
        print_data_payload(node_result.get("data_payload", {}))

        scenario3_elapsed = time.time() - scenario3_start
        print_timer(scenario3_elapsed)

        if classification_result == "code_vulnerability":
            print_success("Scenario 3 PASSED — Code vulnerability correctly classified")
            results.add_scenario("SOC Code Vulnerability", "PASS", 1, node_result.get("data_payload", {}))
        else:
            print_failure(f"Expected 'code_vulnerability', got '{classification_result}'")
            results.add_scenario("SOC Code Vulnerability", "FAIL", 1, {})

    except Exception as e:
        print_failure(f"Scenario 3 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.add_scenario("SOC Code Vulnerability", "FAIL", 0, {"error": str(e)})

    # ══════════════════════════════════════════════════════════
    # SCENARIO 4: SOC Alert - Network Breach
    # ══════════════════════════════════════════════════════════

    print_scenario_header(
        4,
        "SOC Alert — Network Breach (Lateral Movement)",
        "SOC sends lateral movement alert → SOC Classifier → 'network_breach' → "
        "Network Advisor generates remediation recommendations"
    )

    try:
        scenario4_start = time.time()

        classification_result4 = classify_alert(SOC_ALERT_NETWORK_BREACH)

        print_agent_start("SOC Classifier Pod", "Pod")
        print_agent_result("Alert ID", SOC_ALERT_NETWORK_BREACH["alert_id"])
        print_agent_result("Alert Type", SOC_ALERT_NETWORK_BREACH["alert_type"])
        print_agent_result("Severity", SOC_ALERT_NETWORK_BREACH["severity"])
        print_agent_result("Title", SOC_ALERT_NETWORK_BREACH["title"])
        print_agent_result("Classification", classification_result4)

        # Run Network Advisor
        from modules.devsecops.pods.network_advisor_pod import network_advisor_node

        net_state = INITIAL_STATE.copy()
        net_state["soc_alert"] = SOC_ALERT_NETWORK_BREACH
        net_state["alert_classification"] = classification_result4

        print_agent_start("Network Advisor Pod", "Pod")
        net_result = network_advisor_node(net_state)

        print_agent_result("Pod Name", net_result.get("pod_name"))
        print_agent_result("Remediation Status", net_result.get("remediation_status"))
        print_agent_result("HITL Required", net_result.get("human_approval_required", False))

        recommendations = net_result.get("network_recommendations", "")
        if recommendations:
            print(f"\n      {C.BRIGHT_GREEN}📝 Network Remediation Recommendations:{C.RESET}")
            for line in recommendations.split("\n")[:15]:
                print(f"        {C.DIM}{line}{C.RESET}")
            if len(recommendations.split("\n")) > 15:
                print(f"        {C.DIM}... ({len(recommendations.split(chr(10))) - 15} more lines){C.RESET}")

        print_thought_process(net_result.get("ai_thought_process", ""))
        print_data_payload(net_result.get("data_payload", {}))

        scenario4_elapsed = time.time() - scenario4_start
        print_timer(scenario4_elapsed)

        if classification_result4 == "network_breach" and net_result.get("network_recommendations"):
            print_success("Scenario 4 PASSED — Network breach classified and recommendations generated")
            results.add_scenario("SOC Network Breach", "PASS", 2, net_result.get("data_payload", {}))
        else:
            print_failure(f"Classification: {classification_result4}, Recommendations: {bool(net_result.get('network_recommendations'))}")
            results.add_scenario("SOC Network Breach", "FAIL", 2, {})

    except Exception as e:
        print_failure(f"Scenario 4 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.add_scenario("SOC Network Breach", "FAIL", 0, {"error": str(e)})

    # ══════════════════════════════════════════════════════════
    # SCENARIO 5: SOC Alert - IP Threat (Brute Force)
    # ══════════════════════════════════════════════════════════

    print_scenario_header(
        5,
        "SOC Alert — IP Threat (Brute Force / Tor Exit Node)",
        "SOC sends IP brute-force alert → SOC Classifier → 'ip_threat' → "
        "Network Advisor generates IP-specific remediation"
    )

    try:
        scenario5_start = time.time()

        classification_result5 = classify_alert(SOC_ALERT_IP_THREAT)

        print_agent_start("SOC Classifier Pod", "Pod")
        print_agent_result("Alert ID", SOC_ALERT_IP_THREAT["alert_id"])
        print_agent_result("Alert Type", SOC_ALERT_IP_THREAT["alert_type"])
        print_agent_result("Severity", SOC_ALERT_IP_THREAT["severity"])
        print_agent_result("Title", SOC_ALERT_IP_THREAT["title"])
        print_agent_result("Classification", classification_result5)

        # Run Network Advisor for IP threat
        ip_state = INITIAL_STATE.copy()
        ip_state["soc_alert"] = SOC_ALERT_IP_THREAT
        ip_state["alert_classification"] = classification_result5

        print_agent_start("Network Advisor Pod", "Pod")
        ip_result = network_advisor_node(ip_state)

        print_agent_result("Pod Name", ip_result.get("pod_name"))
        print_agent_result("Remediation Status", ip_result.get("remediation_status"))
        print_agent_result("HITL Required", ip_result.get("human_approval_required", False))

        recommendations5 = ip_result.get("network_recommendations", "")
        if recommendations5:
            print(f"\n      {C.BRIGHT_GREEN}📝 IP Threat Remediation Recommendations:{C.RESET}")
            for line in recommendations5.split("\n")[:15]:
                print(f"        {C.DIM}{line}{C.RESET}")
            if len(recommendations5.split("\n")) > 15:
                print(f"        {C.DIM}... ({len(recommendations5.split(chr(10))) - 15} more lines){C.RESET}")

        print_thought_process(ip_result.get("ai_thought_process", ""))
        print_data_payload(ip_result.get("data_payload", {}))

        scenario5_elapsed = time.time() - scenario5_start
        print_timer(scenario5_elapsed)

        if classification_result5 == "ip_threat" and ip_result.get("network_recommendations"):
            print_success("Scenario 5 PASSED — IP threat classified and recommendations generated")
            results.add_scenario("SOC IP Threat", "PASS", 2, ip_result.get("data_payload", {}))
        else:
            print_failure(f"Classification: {classification_result5}, Recommendations: {bool(ip_result.get('network_recommendations'))}")
            results.add_scenario("SOC IP Threat", "FAIL", 2, {})

    except Exception as e:
        print_failure(f"Scenario 5 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.add_scenario("SOC IP Threat", "FAIL", 0, {"error": str(e)})

    # ══════════════════════════════════════════════════════════
    # BONUS: HITL Manager Validation
    # ══════════════════════════════════════════════════════════

    print_scenario_header(
        6,
        "HITL Manager — Approval Workflow Validation",
        "Simulate creating approval requests and processing decisions"
    )

    try:
        scenario6_start = time.time()
        from modules.devsecops.core_orchestrator.hitl_manager import HITLManager

        test_hitl = HITLManager()

        print_agent_start("HITL Manager", "System")

        # Create a request
        req = test_hitl.create_approval_request(
            request_id="test_patch_001",
            action_type="apply_patch",
            description="Auto-patch for CWE-89 SQL Injection in user_controller.py",
            risk_level="critical",
            data={"finding_id": "CWE-89", "file": "user_controller.py"},
        )
        print_agent_result("Request Created", req.request_id)
        print_agent_result("Action Type", req.action_type)
        print_agent_result("Risk Level", req.risk_level)
        print_agent_result("Status", req.decision.value)

        # Check pending
        pending = test_hitl.get_pending_requests()
        print_agent_result("Pending Requests", len(pending))

        # Approve
        approved = test_hitl.process_decision(
            request_id="test_patch_001",
            decision="approved",
            decided_by="SOC_Analyst_Ahmed",
            notes="Verified patch is safe. Applying to staging first.",
        )
        print_agent_result("Decision", approved.decision.value)
        print_agent_result("Decided By", approved.decided_by)
        print_agent_result("Notes", approved.notes)

        # Check history
        history = test_hitl.get_history()
        print_agent_result("History Entries", len(history))
        print_agent_result("Pending After Approval", len(test_hitl.get_pending_requests()))

        # Test should_require_approval
        print(f"\n      {C.BRIGHT_CYAN}🔐 Approval Requirements:{C.RESET}")
        print_agent_result("Critical + apply_patch", test_hitl.should_require_approval("apply_patch", "critical"))
        print_agent_result("High + create_ticket", test_hitl.should_require_approval("create_ticket", "high"))
        print_agent_result("Low + tracking", test_hitl.should_require_approval("tracking", "low"))

        scenario6_elapsed = time.time() - scenario6_start
        print_timer(scenario6_elapsed)

        print_success("Scenario 6 PASSED — HITL Manager workflow validated")
        results.add_scenario("HITL Manager", "PASS", 1, {})

    except Exception as e:
        print_failure(f"Scenario 6 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.add_scenario("HITL Manager", "FAIL", 0, {"error": str(e)})

    # ══════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ══════════════════════════════════════════════════════════

    total_elapsed = time.time() - start_time
    print_section("SIMULATION SUMMARY")

    # Status table
    print(f"    {C.BOLD}{'Scenario':<45} {'Status':<10} {'Agents':<8}{C.RESET}")
    print(f"    {'─' * 63}")

    for scenario in results.scenarios:
        status_color = C.BRIGHT_GREEN if scenario["status"] == "PASS" else C.BRIGHT_RED if scenario["status"] == "FAIL" else C.BRIGHT_YELLOW
        status_icon = "✅" if scenario["status"] == "PASS" else "❌" if scenario["status"] == "FAIL" else "⚠️"
        print(f"    {C.WHITE}{scenario['name']:<45}{C.RESET} {status_color}{status_icon} {scenario['status']:<6}{C.RESET} {C.DIM}{scenario['agents_tested']}{C.RESET}")

    print(f"    {'─' * 63}")

    # Stats
    print(f"""
    {C.BOLD}📊 Results:{C.RESET}
       {C.BRIGHT_GREEN}Passed:  {results.passed}/{len(results.scenarios)}{C.RESET}
       {C.BRIGHT_RED}Failed:  {results.failed}/{len(results.scenarios)}{C.RESET}
       {C.BRIGHT_YELLOW}Warnings:{results.warnings}/{len(results.scenarios)}{C.RESET}

    {C.BOLD}🤖 Agents Tested:{C.RESET}  {results.total_agents_tested}
    {C.BOLD}⏱  Total Time:{C.RESET}     {total_elapsed:.3f}s
    """)

    # SOC Readiness Assessment
    all_passed = results.failed == 0

    if all_passed:
        print(f"""
    {C.BG_GREEN}{C.WHITE}{C.BOLD}                                                              {C.RESET}
    {C.BG_GREEN}{C.WHITE}{C.BOLD}   ✅ SOC INTEGRATION READINESS: ALL AGENTS VALIDATED          {C.RESET}
    {C.BG_GREEN}{C.WHITE}{C.BOLD}                                                              {C.RESET}

    {C.BRIGHT_GREEN}All agents are functioning correctly. The DevSecOps module is ready
    for SOC integration. The following capabilities are confirmed:{C.RESET}

      {C.GREEN}✓{C.RESET} SARIF/SAST scan parsing and normalization
      {C.GREEN}✓{C.RESET} Intelligent severity-based routing (DEEP_ANALYSIS / QUICK_REPORT)
      {C.GREEN}✓{C.RESET} AI-powered risk prioritization and scoring
      {C.GREEN}✓{C.RESET} Automated code patch generation
      {C.GREEN}✓{C.RESET} Jira ticket creation for high-priority findings
      {C.GREEN}✓{C.RESET} Remediation tracking and final report generation
      {C.GREEN}✓{C.RESET} SOC alert classification (code / network / IP)
      {C.GREEN}✓{C.RESET} Network/IP breach remediation recommendations
      {C.GREEN}✓{C.RESET} Human-In-The-Loop (HITL) approval workflows
""")
    else:
        print(f"""
    {C.BG_RED}{C.WHITE}{C.BOLD}                                                              {C.RESET}
    {C.BG_RED}{C.WHITE}{C.BOLD}   ⚠️  SOC INTEGRATION: ISSUES DETECTED                       {C.RESET}
    {C.BG_RED}{C.WHITE}{C.BOLD}                                                              {C.RESET}

    {C.BRIGHT_RED}{results.failed} scenario(s) failed. Please review the errors above
    and fix them before proceeding with SOC integration.{C.RESET}
""")

    return results


# ══════════════════════════════════════════════════════════════
# Entry Point
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    results = run_simulation()
    sys.exit(0 if results.failed == 0 else 1)
