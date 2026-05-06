"""
Wazuh -> ACIP SOC forwarder.

This script can be used as a Wazuh integration command.
It reads a Wazuh alert JSON (from file path argument or stdin),
normalizes it to ACIP SOC JSON schema, and posts it to:
  http://127.0.0.1:8080/api/v1/soc/ingest

Environment variables:
  SOC_INGEST_URL  Override ingest URL.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

DEFAULT_SOC_INGEST_URL = os.getenv("SOC_INGEST_URL", "http://127.0.0.1:8080/api/v1/soc/ingest")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def map_wazuh_level_to_severity(level: Any) -> float:
    lvl = safe_float(level, 0.0)
    # Wazuh rule level is usually 0-15
    return round(min(10.0, (lvl / 15.0) * 10.0), 2)


def classify_alert_type(description: str, full_log: str) -> str:
    text = f"{description} {full_log}".lower()
    if any(k in text for k in ["sql injection", "xss", "rce", "code", "deserialization"]):
        return "code_vulnerability"
    if any(k in text for k in ["brute force", "failed password", "ssh", "login failed"]):
        return "ip_threat"
    if any(k in text for k in ["scan", "portscan", "nmap", "lateral", "ddos"]):
        return "network_breach"
    return "network_breach"


def read_wazuh_payload() -> Dict[str, Any]:
    # Wazuh integrations often pass alert file as argv[1]
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback: stdin
    stdin_data = sys.stdin.read().strip()
    if stdin_data:
        return json.loads(stdin_data)

    raise ValueError("No Wazuh alert payload provided")


def normalize_wazuh_to_soc(payload: Dict[str, Any]) -> Dict[str, Any]:
    rule = payload.get("rule", {}) or {}
    agent = payload.get("agent", {}) or {}
    data = payload.get("data", {}) or {}

    rule_id = rule.get("id", "unknown")
    rule_level = rule.get("level", 0)
    rule_desc = str(rule.get("description", "Wazuh alert"))

    full_log = str(payload.get("full_log", ""))
    src_ip = data.get("srcip") or payload.get("srcip") or payload.get("src_ip")
    dst_ip = data.get("dstip") or payload.get("dstip") or payload.get("dst_ip")

    alert_type = classify_alert_type(rule_desc, full_log)
    severity = map_wazuh_level_to_severity(rule_level)

    timestamp = payload.get("timestamp") or payload.get("@timestamp") or utc_now_iso()
    alert_id = f"wazuh-{rule_id}-{int(time.time())}"

    return {
        "alert_id": alert_id,
        "alert_type": alert_type,
        "severity": severity,
        "title": f"Wazuh Rule {rule_id}: {rule_desc}",
        "description": rule_desc,
        "source_module": "soc",
        "affected_target": agent.get("name") or dst_ip or "unknown-host",
        "code_snippet": None,
        "file_path": None,
        "network_details": {
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "agent_id": agent.get("id"),
            "agent_name": agent.get("name"),
        },
        "raw_data": {
            "rule": rule,
            "wazuh_data": data,
            "full_log": full_log,
            "decoder": payload.get("decoder"),
            "location": payload.get("location"),
        },
        "timestamp": timestamp,
    }


def forward_soc_alert(alert: Dict[str, Any], endpoint: str = DEFAULT_SOC_INGEST_URL) -> requests.Response:
    response = requests.post(endpoint, json=alert, timeout=5)
    response.raise_for_status()
    return response


def main() -> int:
    try:
        wazuh_payload = read_wazuh_payload()
        soc_alert = normalize_wazuh_to_soc(wazuh_payload)
        response = forward_soc_alert(soc_alert)
        print(f"Forwarded Wazuh alert -> SOC ({response.status_code}) id={soc_alert['alert_id']}")
        return 0
    except Exception as exc:
        print(f"Wazuh forwarder failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
