"""
Tests for DevSecOps Module - Pods
Tests each pod's node function in isolation.
"""

import pytest
from modules.devsecops.pods.sast_parser_pod import (
    sast_parser_node,
    parse_sarif_findings,
    normalize_findings,
)
from modules.devsecops.pods.prioritization_pod import (
    prioritization_node,
    apply_risk_scoring,
    categorize_risk,
)
from modules.devsecops.pods.ticket_creator_pod import ticket_creator_node
from modules.devsecops.pods.tracking_pod import tracking_node
from modules.devsecops.core_orchestrator.state_schema import INITIAL_STATE


# ══════════════════════════════════════════════════════════════
# SAST Parser Pod Tests
# ══════════════════════════════════════════════════════════════

class TestSASTParserPod:
    """Tests for the SAST Parser Pod."""

    def test_parse_pre_parsed_findings(self):
        """Should normalize a list of pre-parsed findings."""
        state = INITIAL_STATE.copy()
        state["sarif_input"] = [
            {
                "finding_id": "CWE-89-SQL-INJECTION",
                "tool_severity": 9.5,
                "file_path": "src/api/auth.py",
                "message": "SQL Injection vulnerability",
                "level": "error",
            }
        ]
        state["commit_id"] = "test_commit_001"

        result = sast_parser_node(state)

        assert result["remediation_status"] == "ANALYSIS_COMPLETE"
        assert len(result["parsed_findings"]) == 1
        assert result["parsed_findings"][0]["finding_id"] == "CWE-89-SQL-INJECTION"
        assert result["pod_name"] == "sast_parser_pod"

    def test_parse_sarif_format(self):
        """Should parse SARIF format input correctly."""
        sarif_data = {
            "runs": [
                {
                    "tool": {"driver": {"name": "TestTool"}},
                    "results": [
                        {
                            "ruleId": "CWE-79",
                            "message": {"text": "XSS vulnerability"},
                            "level": "error",
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": "src/web/form.py"},
                                        "region": {"startLine": 42},
                                    }
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        findings = parse_sarif_findings(sarif_data)
        assert len(findings) == 1
        assert findings[0]["finding_id"] == "CWE-79"
        assert findings[0]["tool_severity"] == 9.0
        assert findings[0]["file_path"] == "src/web/form.py"

    def test_empty_input(self):
        """Should handle empty input gracefully."""
        state = INITIAL_STATE.copy()
        state["sarif_input"] = []

        result = sast_parser_node(state)

        assert result["remediation_status"] == "ANALYSIS_COMPLETE"
        assert len(result["parsed_findings"]) == 0


# ══════════════════════════════════════════════════════════════
# Prioritization Pod Tests
# ══════════════════════════════════════════════════════════════

class TestPrioritizationPod:
    """Tests for the Prioritization Pod."""

    def test_high_severity_scoring(self):
        """High severity (9.0) should produce score >= 10.0 with context_factor 1.2."""
        findings = [{"tool_severity": 9.0}]
        score = apply_risk_scoring(findings, "test_commit")
        assert score == pytest.approx(10.8)

    def test_low_severity_scoring(self):
        """Low severity (3.0) should produce score of 3.6."""
        findings = [{"tool_severity": 3.0}]
        score = apply_risk_scoring(findings, "test_commit")
        assert score == pytest.approx(3.6)

    def test_empty_findings(self):
        """Empty findings should return 0.0."""
        score = apply_risk_scoring([], "test_commit")
        assert score == 0.0

    def test_categorize_risk(self):
        """Risk categorization should match expected levels."""
        assert categorize_risk(10.0) == "CRITICAL"
        assert categorize_risk(8.0) == "HIGH"
        assert categorize_risk(5.0) == "MEDIUM"
        assert categorize_risk(2.0) == "LOW"
        assert categorize_risk(0.0) == "NONE"

    def test_prioritization_node_state_update(self):
        """Prioritization node should correctly update state."""
        state = INITIAL_STATE.copy()
        state["parsed_findings"] = [
            {"finding_id": "V-101", "tool_severity": 8.0}
        ]
        state["commit_id"] = "test_id"

        result = prioritization_node(state)

        assert result["final_priority_score"] == pytest.approx(9.6)
        assert result["remediation_status"] == "PRIORITIZED"
        assert result["pod_name"] == "prioritization_pod"

    def test_prioritization_node_no_findings(self):
        """Prioritization node should skip when no findings."""
        state = INITIAL_STATE.copy()
        state["parsed_findings"] = []

        result = prioritization_node(state)

        assert result["final_priority_score"] == 0.0
        assert result["remediation_status"] == "SKIPPED"


# ══════════════════════════════════════════════════════════════
# Ticket Creator Pod Tests
# ══════════════════════════════════════════════════════════════

class TestTicketCreatorPod:
    """Tests for the Ticket Creator Pod."""

    def test_creates_ticket_high_score(self):
        """Should create ticket when score >= 8.5."""
        state = INITIAL_STATE.copy()
        state["final_priority_score"] = 10.8
        state["parsed_findings"] = [
            {"finding_id": "CWE-89", "tool_severity": 9.0, "message": "SQL Injection", "file_path": "auth.py"}
        ]

        result = ticket_creator_node(state)

        assert result["jira_ticket_id"].startswith("JIRA-")
        assert result["remediation_status"] == "TICKET_CREATED"

    def test_skips_ticket_low_score(self):
        """Should skip ticket when score < 8.5."""
        state = INITIAL_STATE.copy()
        state["final_priority_score"] = 3.6
        state["parsed_findings"] = [
            {"finding_id": "CWE-200", "tool_severity": 3.0, "message": "Info leak", "file_path": "log.py"}
        ]

        result = ticket_creator_node(state)

        assert result["jira_ticket_id"] == "SKIPPED"
        assert result["remediation_status"] == "LOW_PRIORITY_SKIPPED"


# ══════════════════════════════════════════════════════════════
# Tracking Pod Tests
# ══════════════════════════════════════════════════════════════

class TestTrackingPod:
    """Tests for the Tracking Pod."""

    def test_tracking_with_ticket(self):
        """Should report TRACKING_ACTIVE when ticket exists."""
        state = INITIAL_STATE.copy()
        state["jira_ticket_id"] = "JIRA-ABC123"
        state["final_priority_score"] = 10.8
        state["parsed_findings"] = [{"finding_id": "CWE-89"}]

        result = tracking_node(state)

        assert result["remediation_status"] == "TRACKING_ACTIVE"
        assert result["pod_name"] == "tracking_pod"

    def test_tracking_no_findings(self):
        """Should report CLEAN when no findings."""
        state = INITIAL_STATE.copy()
        state["parsed_findings"] = []

        result = tracking_node(state)

        assert result["remediation_status"] == "CLEAN"
