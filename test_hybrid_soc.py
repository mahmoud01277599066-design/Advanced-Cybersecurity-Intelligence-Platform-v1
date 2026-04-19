"""
Hybrid SOC Architecture - Integration Test Suite
Tests: LangGraph build, routing paths, SOCLogger JSON telemetry
"""
import sys
import os
import json

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"
WARN = "[WARN]"

results = {"passed": 0, "failed": 0, "warnings": 0}


def header(title):
    print(f"\n{'=' * 58}")
    print(f"  {title}")
    print(f"{'=' * 58}")


def check(label, condition, warn=False):
    if condition:
        print(f"  {PASS} {label}")
        results["passed"] += 1
    elif warn:
        print(f"  {WARN} {label}")
        results["warnings"] += 1
    else:
        print(f"  {FAIL} {label}")
        results["failed"] += 1


def read_ndjson(filepath):
    """Read newline-delimited JSON file and return list of entries."""
    entries = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


# -------------------------------------------------------
# TEST 1: LangGraph Graph Build
# -------------------------------------------------------
header("TEST 1: LangGraph Graph Build")
try:
    from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph
    app = build_soc_graph()
    check("Graph compiled without errors", True)
    check("Graph has invoke() method", callable(getattr(app, "invoke", None)))
except Exception as e:
    check(f"Graph build FAILED: {e}", False)
    print("\n  Cannot continue - aborting remaining tests.")
    sys.exit(1)


# -------------------------------------------------------
# TEST 2: Active Response Path
# -------------------------------------------------------
header("TEST 2: Active Response Path  (Block IP -> rule_generator)")
try:
    res = app.invoke({"user_input": "Block attacker IP 91.210.10.10 immediately - confirmed intrusion"})
    out = res.get("current_node_output", {})
    check("Graph returned output", bool(out))
    check("Status is success", out.get("status") == "success")
    print(f"  {INFO} Output keys: {list(out.keys())}")
except Exception as e:
    check(f"Active Response path FAILED: {e}", False)


# -------------------------------------------------------
# TEST 3: Log Triage Path
# -------------------------------------------------------
header("TEST 3: Log Triage Path  (SQL Injection -> enrichment -> triage -> report)")
try:
    res = app.invoke({"user_input": "[log_triage] SQL injection in apache logs: admin' UNION SELECT passwd--"})
    out = res.get("current_node_output", {})
    check("Graph returned output", bool(out))
    check("Status is success", out.get("status") == "success")
    print(f"  {INFO} Output keys: {list(out.keys())}")
except Exception as e:
    check(f"Log Triage path FAILED: {e}", False)


# -------------------------------------------------------
# TEST 4: Anomaly Detection Path
# -------------------------------------------------------
header("TEST 4: Anomaly Detection Path  (Port Scan -> network_analysis -> report)")
try:
    res = app.invoke({"user_input": "[anomaly_detection] Port scan from 1.2.3.4, 150 ports in 5 seconds"})
    out = res.get("current_node_output", {})
    check("Graph returned output", bool(out))
    check("Status is success", out.get("status") == "success")
    print(f"  {INFO} Output keys: {list(out.keys())}")
except Exception as e:
    check(f"Anomaly Detection path FAILED: {e}", False)


# -------------------------------------------------------
# TEST 5: SOCLogger JSON Telemetry Files
# -------------------------------------------------------
header("TEST 5: SOCLogger JSON Telemetry Files")

log_checks = {
    "logs/router/master_router":            "Master Router decisions",
    "logs/router/active_response_router":   "Active Response routing",
    "logs/router/log_triage_router":        "Log Triage routing",
    "logs/router/anomaly_detection_router": "Anomaly Detection routing",
    "logs/pods/wazuh_fetcher_pod":          "Wazuh Fetcher ingestion",
    "logs/pods/enrichment_pod":             "Enrichment telemetry",
    "logs/pods/ai_triage_pod":              "AI Triage decisions",
    "logs/pods/network_analysis_pod":       "Network Analysis",
    "logs/pods/pro_reporting_pod":          "Reporting telemetry",
    "logs/scripts/master_pipeline":         "Script layer startup events",
}

for path, label in log_checks.items():
    abs_path = os.path.join(ROOT_DIR, path)
    if os.path.isdir(abs_path):
        files = sorted([f for f in os.listdir(abs_path) if f.endswith(".json")])
        if files:
            latest = os.path.join(abs_path, files[-1])
            try:
                entries = read_ndjson(latest)
                count = len(entries)
                check(f"{label}  [{files[-1]}, {count} entries]", count > 0)
            except Exception as e:
                check(f"{label} - read error: {e}", False)
        else:
            check(f"{label} - dir exists but no JSON files yet", False, warn=True)
    else:
        check(f"{label} - not yet created", False, warn=True)


# -------------------------------------------------------
# TEST 6: JSON Entry Schema Validation
# -------------------------------------------------------
header("TEST 6: JSON Entry Schema Validation")
required_keys = {"timestamp", "component_type", "component_name",
                 "event_type", "input", "output", "status"}

sample_path = os.path.join(ROOT_DIR, "logs/router/master_router")
if os.path.isdir(sample_path):
    files = sorted([f for f in os.listdir(sample_path) if f.endswith(".json")])
    if files:
        entries = read_ndjson(os.path.join(sample_path, files[-1]))
        if entries:
            sample = entries[-1]
            missing = required_keys - set(sample.keys())
            check("All required schema keys present", not missing)
            if missing:
                print(f"  {WARN}  Missing keys: {missing}")
            else:
                print(f"  {INFO} Sample entry (latest):")
                for k, v in sample.items():
                    val_str = str(v)[:70] + "..." if len(str(v)) > 70 else str(v)
                    print(f"         {k}: {val_str}")
        else:
            check("No valid entries found in master_router log", False, warn=True)
    else:
        check("No JSON files to validate", False, warn=True)
else:
    check("master_router log dir not found", False, warn=True)


# -------------------------------------------------------
# SUMMARY
# -------------------------------------------------------
header("TEST RESULTS SUMMARY")
total = results["passed"] + results["failed"] + results["warnings"]
print(f"  Total Checks : {total}")
print(f"  PASSED       : {results['passed']}")
print(f"  FAILED       : {results['failed']}")
print(f"  WARNINGS     : {results['warnings']}  (log dirs not yet created - normal before first SOC run)")
print()
if results["failed"] == 0:
    print("  [SUCCESS] ALL TESTS PASSED - Hybrid SOC Architecture is OPERATIONAL!")
else:
    print("  [WARNING] Some tests failed. Review errors above.")
print()
