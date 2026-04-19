"""
Tests for DevSecOps Module - FastAPI endpoints.
Focuses on the Endpoint / EDR ingestion flows added for dashboard integration.
"""

from fastapi.testclient import TestClient

from modules.devsecops.app import app, endpoint_events, endpoint_registry


client = TestClient(app)


class TestEndpointApi:
    """API tests for endpoint telemetry ingestion."""

    def setup_method(self):
        """Reset in-memory endpoint stores before each test."""
        endpoint_events.clear()
        endpoint_registry.clear()

    def test_ingest_endpoint_event_and_fetch_details(self):
        """A posted endpoint event should be stored and exposed by the API."""
        payload = {
            "endpoint_id": "host-001",
            "hostname": "finance-laptop-01",
            "platform": "windows",
            "event_type": "powershell_suspicious_script",
            "severity": 8.4,
            "title": "Suspicious PowerShell execution",
            "description": "Encoded command execution detected from Office parent process.",
            "user_name": "analyst1",
            "process_name": "powershell.exe",
            "parent_process": "winword.exe",
            "tags": ["edr", "powershell", "lolbin"],
        }

        response = client.post("/api/v1/endpoints/events", json=payload)

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "received"
        assert body["risk_level"] == "HIGH"
        assert body["processing_status"] == "ESCALATED"

        details_response = client.get("/api/v1/endpoints/host-001")
        assert details_response.status_code == 200

        details = details_response.json()
        assert details["endpoint_id"] == "host-001"
        assert details["latest_status"] == "ESCALATED"
        assert len(details["recent_events"]) == 1
        assert details["recent_events"][0]["process_name"] == "powershell.exe"

    def test_endpoint_summary_reflects_ingested_events(self):
        """Endpoint summary should aggregate ingested telemetry."""
        events = [
            {
                "endpoint_id": "host-001",
                "hostname": "finance-laptop-01",
                "platform": "windows",
                "event_type": "malware_detection",
                "severity": 9.3,
                "title": "Malware detected",
                "description": "Known malicious hash observed on disk.",
            },
            {
                "endpoint_id": "host-002",
                "hostname": "dev-mac-02",
                "platform": "macos",
                "event_type": "failed_login_burst",
                "severity": 5.5,
                "title": "Multiple failed logins",
                "description": "Repeated login failures detected over a short interval.",
            },
        ]

        for event in events:
            response = client.post("/api/v1/endpoints/events", json=event)
            assert response.status_code == 200

        summary_response = client.get("/api/v1/endpoints/summary")
        assert summary_response.status_code == 200

        summary = summary_response.json()
        assert summary["total_events"] == 2
        assert summary["total_endpoints"] == 2
        assert summary["escalated_events"] == 1
        assert summary["risk_distribution"]["CRITICAL"] == 1
        assert summary["risk_distribution"]["MEDIUM"] == 1
