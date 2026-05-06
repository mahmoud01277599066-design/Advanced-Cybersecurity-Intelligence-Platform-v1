import json
import os
from datetime import datetime, timezone

# Execution Meta
EXEC_ID = "SEC-SIM-2026-X81"
START_TIME = "2026-04-13T15:30:00Z"
END_TIME = "2026-04-13T15:30:15Z"

output_dir = "simulation_output"
os.makedirs(output_dir, exist_ok=True)

# 1. execution_metadata.json
metadata = {
    "execution_id": EXEC_ID,
    "start_time": START_TIME,
    "end_time": END_TIME,
    "total_duration_ms": 15000,
    "status": "COMPLETED",
    "environment": "Production-Cluster-01"
}

# 2. pipeline_steps.json
steps = [
    {"step_id": 1, "timestamp": "2026-04-13T15:30:01Z", "component": "SAST Parser Pod", "type": "pod", "action": "parse_sarif", "status": "success", "execution_time_ms": 140},
    {"step_id": 2, "timestamp": "2026-04-13T15:30:02Z", "component": "SAST Router", "type": "router", "action": "route_vulnerability", "status": "success", "execution_time_ms": 45},
    {"step_id": 3, "timestamp": "2026-04-13T15:30:04Z", "component": "Prioritization Pod", "type": "pod", "action": "calculate_risk", "status": "success", "execution_time_ms": 210},
    {"step_id": 4, "timestamp": "2026-04-13T15:30:08Z", "component": "Auto-Patcher Pod", "type": "pod", "action": "generate_remediation", "status": "success", "execution_time_ms": 4200},
    {"step_id": 5, "timestamp": "2026-04-13T15:30:10Z", "component": "Ticket Creator Pod", "type": "pod", "action": "create_jira", "status": "success", "execution_time_ms": 850},
    {"step_id": 6, "timestamp": "2026-04-13T15:30:12Z", "component": "Tracking Pod", "type": "pod", "action": "log_remediation", "status": "success", "execution_time_ms": 95},
    {"step_id": 7, "timestamp": "2026-04-13T15:30:14Z", "component": "Professional Report Pod", "type": "pod", "action": "generate_executive_audit", "status": "success", "execution_time_ms": 1100}
]

# 3. agents_summary.json
summary = {
    "total_agents_invoked": 7,
    "successful_executions": 7,
    "failed_executions": 0,
    "critical_alerts_handled": 1,
    "average_latency_ms": 1105
}

# 4. findings.json
findings = [
    {
        "finding_id": "FIND-8821",
        "cwe": "CWE-89",
        "title": "SQL Injection in auth.py",
        "severity": 9.8,
        "location": "modules/auth/login.py:42",
        "detector": "SAST Parser Pod"
    }
]

# 5. routing_decisions.json
routing = [
    {
        "router": "SAST Router",
        "input_severity": 9.8,
        "decision": "DEEP_ANALYSIS",
        "next_node": "prioritization_pod",
        "reasoning": "Severity above 8.5 threshold requires automated patching pipeline."
    }
]

# 6. patches.json
patches = [
    {
        "patch_id": "PATCH-X1",
        "target_file": "modules/auth/login.py",
        "original_code": "cursor.execute(f\"SELECT * FROM users WHERE id='{uid}'\")",
        "patched_code": "cursor.execute(\"SELECT * FROM users WHERE id=?\", (uid,))",
        "ai_explanation": "Replaced string interpolation with parameterized query to prevent SQL injection."
    }
]

# 7. tickets.json
tickets = [
    {
        "ticket_id": "SEC-2024-001",
        "system": "Jira",
        "status": "OPEN",
        "priority": "Highest",
        "assignee": "Security-On-Call"
    }
]

# 8. tracking.json
tracking = {
    "workflow_status": "PENDING_APPROVAL",
    "last_checkpoint": "Tracking Pod",
    "remediation_validated": True,
    "soc_notified": True
}

# 9. soc_classification.json
soc_class = {
    "alert_type": "INTERNAL_VULNERABILITY",
    "threat_level": "RED",
    "action_required": "IMMEDIATE_REVIEW",
    "automated_response": "PATCH_GENERATED"
}

# 10. network_recommendations.json
network = {
    "firewall_rules": [
        "BLOCK_IP 192.168.1.45 (Unauthorized scan pattern detection)"
    ],
    "waf_update": "Enable SQL Injection protection rule #4002"
}

# Write files
files = {
    "execution_metadata.json": metadata,
    "pipeline_steps.json": steps,
    "agents_summary.json": summary,
    "findings.json": findings,
    "routing_decisions.json": routing,
    "patches.json": patches,
    "tickets.json": tickets,
    "tracking.json": tracking,
    "soc_classification.json": soc_class,
    "network_recommendations.json": network
}

for filename, content in files.items():
    with open(os.path.join(output_dir, filename), "w") as f:
        json.dump(content, f, indent=4)

# logs.txt
with open(os.path.join(output_dir, "logs.txt"), "w") as f:
    for step in steps:
        f.write(f"[{step['timestamp']}] [{step['component']}] {step['action'].upper()} -> {step['status'].upper()} ({step['execution_time_ms']}ms)\n")

print("Files generated successfully in simulation_output/")
