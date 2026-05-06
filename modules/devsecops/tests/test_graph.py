"""
Tests for DevSecOps Module - Full Graph Integration
Tests the complete LangGraph pipeline end-to-end.
"""

import pytest
from modules.devsecops.core_orchestrator.main_graph import build_devsecops_graph
from modules.devsecops.core_orchestrator.state_schema import INITIAL_STATE


class TestDevSecOpsGraph:
    """Integration tests for the full DevSecOps pipeline."""

    @pytest.fixture
    def graph(self):
        """Build a fresh graph for each test."""
        return build_devsecops_graph()

    def test_high_severity_full_pipeline(self, graph):
        """
        High severity finding should go through the full pipeline:
        Parser → Router → Prioritization → Auto-Patcher → Ticket → Tracking
        """
        initial_input = INITIAL_STATE.copy()
        initial_input["sarif_input"] = [
            {
                "finding_id": "CWE-89-SQL-INJECTION",
                "tool_severity": 9.5,
                "file_path": "src/api/auth.py",
                "message": "SQL Injection vulnerability detected",
                "level": "error",
            }
        ]
        initial_input["commit_id"] = "test_commit_high"

        final_state = graph.invoke(initial_input)

        # Should have created a ticket
        assert final_state.get("jira_ticket_id") is not None
        assert final_state["jira_ticket_id"].startswith("JIRA-")

        # Should have a high priority score
        assert final_state["final_priority_score"] >= 8.5

        # Should have generated a patch
        assert final_state.get("patch_suggestion") is not None

        # Should end in tracking status
        assert final_state["remediation_status"] in ("TRACKING_ACTIVE", "CLEAN")

    def test_low_severity_quick_report(self, graph):
        """
        Low severity finding should skip deep analysis:
        Parser → Router → Tracking (quick report)
        """
        initial_input = INITIAL_STATE.copy()
        initial_input["sarif_input"] = [
            {
                "finding_id": "CWE-200-INFO-EXPOSURE",
                "tool_severity": 3.0,
                "file_path": "src/utils/log.py",
                "message": "Information exposure through log output",
                "level": "note",
            }
        ]
        initial_input["commit_id"] = "test_commit_low"

        final_state = graph.invoke(initial_input)

        # Should NOT have created a ticket
        assert final_state.get("jira_ticket_id") is None or final_state.get("jira_ticket_id") == "SKIPPED"

        # Should end in monitoring or clean status
        assert final_state["remediation_status"] in ("MONITORING", "CLEAN", "TRACKING_ACTIVE")

    def test_no_findings_ends_workflow(self, graph):
        """
        No findings should end the workflow early:
        Parser → Router → END
        """
        initial_input = INITIAL_STATE.copy()
        initial_input["sarif_input"] = []
        initial_input["commit_id"] = "test_commit_empty"

        final_state = graph.invoke(initial_input)

        # Should have no ticket
        assert final_state.get("jira_ticket_id") is None

        # Should have no priority score
        assert final_state.get("final_priority_score") is None

    def test_sarif_format_input(self, graph):
        """
        Full SARIF format input should be parsed and processed correctly.
        """
        sarif_input = {
            "runs": [
                {
                    "tool": {"driver": {"name": "Semgrep"}},
                    "results": [
                        {
                            "ruleId": "CWE-79-XSS",
                            "message": {"text": "Cross-site scripting vulnerability"},
                            "level": "error",
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": "src/web/template.py"},
                                        "region": {"startLine": 15},
                                    }
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        initial_input = INITIAL_STATE.copy()
        initial_input["sarif_input"] = sarif_input
        initial_input["commit_id"] = "test_sarif_commit"

        final_state = graph.invoke(initial_input)

        # Should have processed findings
        findings = final_state.get("parsed_findings", [])
        assert len(findings) >= 1

        # Remediation status should not be START
        assert final_state["remediation_status"] != "START_PROCESSING"

    def test_standardized_output_protocol(self, graph):
        """
        Final state should contain all ACIP Standardized Output Protocol fields.
        """
        initial_input = INITIAL_STATE.copy()
        initial_input["sarif_input"] = [
            {
                "finding_id": "CWE-89",
                "tool_severity": 9.5,
                "file_path": "auth.py",
                "message": "SQL Injection",
                "level": "error",
            }
        ]
        initial_input["commit_id"] = "test_protocol"

        final_state = graph.invoke(initial_input)

        # Check ACIP required fields
        assert final_state.get("module_name") == "devsecops"
        assert "ai_thought_process" in final_state
        assert "data_payload" in final_state
        assert isinstance(final_state.get("messages"), list)
