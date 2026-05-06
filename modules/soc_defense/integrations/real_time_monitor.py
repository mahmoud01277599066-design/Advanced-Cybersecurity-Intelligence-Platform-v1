"""
Real-time host monitor that sends SOC alerts to ACIP.

Usage:
  python modules/soc_defense/integrations/real_time_monitor.py
  python modules/soc_defense/integrations/real_time_monitor.py --endpoint http://127.0.0.1:8080/api/v1/soc/ingest --cpu-threshold 90 --mem-threshold 90
"""

from __future__ import annotations

import argparse
import socket
import time
from datetime import datetime, timezone
from typing import Any, Dict

import requests

try:
    import psutil
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "psutil is required for real_time_monitor.py. Install with: pip install psutil"
    ) from exc


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_alert(alert_type: str, severity: float, title: str, description: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
    ts = utc_now_iso()
    return {
        "alert_id": f"soc-host-{int(time.time())}",
        "alert_type": alert_type,
        "severity": severity,
        "title": title,
        "description": description,
        "source_module": "soc",
        "affected_target": socket.gethostname(),
        "code_snippet": None,
        "file_path": None,
        "network_details": None,
        "raw_data": raw_data,
        "timestamp": ts,
    }


def send_alert(endpoint: str, payload: Dict[str, Any], timeout: int = 5) -> None:
    response = requests.post(endpoint, json=payload, timeout=timeout)
    response.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser(description="ACIP SOC real-time monitor sender")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8080/api/v1/soc/ingest", help="SOC ingest endpoint")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval in seconds")
    parser.add_argument("--cpu-threshold", type=float, default=90.0, help="CPU percentage threshold")
    parser.add_argument("--mem-threshold", type=float, default=90.0, help="Memory percentage threshold")
    args = parser.parse_args()

    print("[ACIP Monitor] Started")
    print(f"[ACIP Monitor] Endpoint: {args.endpoint}")
    print(f"[ACIP Monitor] Thresholds: CPU>{args.cpu_threshold}%, MEM>{args.mem_threshold}%")

    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent

        if cpu_usage > args.cpu_threshold:
            payload = build_alert(
                alert_type="resource_exhaustion",
                severity=min(10.0, 4.0 + (cpu_usage - args.cpu_threshold) / 10.0),
                title=f"High CPU Usage Detected: {cpu_usage:.1f}%",
                description="System CPU usage exceeded configured threshold.",
                raw_data={
                    "metric": "cpu_percent",
                    "value": cpu_usage,
                    "threshold": args.cpu_threshold,
                },
            )
            try:
                send_alert(args.endpoint, payload)
                print(f"[ACIP Monitor] CPU alert sent: {payload['alert_id']}")
            except Exception as exc:  # pragma: no cover
                print(f"[ACIP Monitor] Failed to send CPU alert: {exc}")

        if mem_usage > args.mem_threshold:
            payload = build_alert(
                alert_type="resource_exhaustion",
                severity=min(10.0, 4.0 + (mem_usage - args.mem_threshold) / 10.0),
                title=f"High Memory Usage Detected: {mem_usage:.1f}%",
                description="System memory usage exceeded configured threshold.",
                raw_data={
                    "metric": "memory_percent",
                    "value": mem_usage,
                    "threshold": args.mem_threshold,
                },
            )
            try:
                send_alert(args.endpoint, payload)
                print(f"[ACIP Monitor] Memory alert sent: {payload['alert_id']}")
            except Exception as exc:  # pragma: no cover
                print(f"[ACIP Monitor] Failed to send memory alert: {exc}")

        time.sleep(max(args.interval, 1))


if __name__ == "__main__":
    main()
