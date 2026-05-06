"""
Tests for DevSecOps Module - Routers
Tests router decision logic in isolation.
"""

import pytest
from modules.devsecops.routers.sast_router import sast_router_node, route_after_sast
from modules.devsecops.routers.pipeline_router import pipeline_router_node, route_after_pipeline
from modules.devsecops.core_orchestrator.state_schema import INITIAL_STATE


# ══════════════════════════════════════════════════════════════
# SAST Router Tests
# ══════════════════════════════════════════════════════════════

class TestSASTRouter:
    """Tests for SAST Router decision logic."""

    def test_routes_high_severity_to_deep_analysis(self):
        """High severity findings should route to DEEP_ANALYSIS."""
        state = INITIAL_STATE.copy()
        state["parsed_findings"] = [
            {"finding_id": "CWE-89", "tool_severity": 9.5},
        ]

        result = sast_router_node(state)

        assert result["routing_decision"] == "DEEP_ANALYSIS"
        assert result["router_name"] == "sast_router"

    def test_routes_low_severity_to_quick_report(self):
        """Low severity findings should route to QUICK_REPORT."""
        state = INITIAL_STATE.copy()
        state["parsed_findings"] = [
            {"finding_id": "CWE-200", "tool_severity": 3.0},
        ]

        result = sast_router_node(state)

        assert result["routing_decision"] == "QUICK_REPORT"

    def test_routes_no_findings_to_end(self):
        """No findings should route to END_WORKFLOW."""
        state = INITIAL_STATE.copy()
        state["parsed_findings"] = []

        result = sast_router_node(state)

        assert result["routing_decision"] == "END_WORKFLOW"

    def test_conditional_edge_function(self):
        """route_after_sast should read decision from state."""
        state = INITIAL_STATE.copy()
        state["routing_decision"] = "DEEP_ANALYSIS"

        assert route_after_sast(state) == "DEEP_ANALYSIS"

    def test_standardized_output_fields(self):
        """Router output should contain all ACIP standardized fields."""
        state = INITIAL_STATE.copy()
        state["parsed_findings"] = [
            {"finding_id": "CWE-89", "tool_severity": 9.5},
        ]

        result = sast_router_node(state)

        # Check all required ACIP fields are present
        assert "routing_decision" in result
        assert "router_name" in result
        assert "ai_thought_process" in result
        assert "human_approval_required" in result
        assert "data_payload" in result
        assert result["human_approval_required"] is False


# ══════════════════════════════════════════════════════════════
# Pipeline Router Tests
# ══════════════════════════════════════════════════════════════

class TestPipelineRouter:
    """Tests for Pipeline Router decision logic."""

    def test_routes_sarif_to_scan_results(self):
        """SARIF format input should route to SCAN_RESULTS."""
        state = INITIAL_STATE.copy()
        state["sarif_input"] = {"runs": [{"results": []}]}

        result = pipeline_router_node(state)

        assert result["routing_decision"] == "SCAN_RESULTS"
        assert result["router_name"] == "pipeline_router"

    def test_routes_findings_list_to_scan_results(self):
        """Pre-parsed findings should route to SCAN_RESULTS."""
        state = INITIAL_STATE.copy()
        state["sarif_input"] = [
            {"finding_id": "CWE-89", "tool_severity": 9.0}
        ]

        result = pipeline_router_node(state)

        assert result["routing_decision"] == "SCAN_RESULTS"

    def test_routes_empty_to_default(self):
        """Empty input should default to SCAN_RESULTS."""
        state = INITIAL_STATE.copy()
        state["sarif_input"] = []

        result = pipeline_router_node(state)

        assert result["routing_decision"] == "SCAN_RESULTS"
