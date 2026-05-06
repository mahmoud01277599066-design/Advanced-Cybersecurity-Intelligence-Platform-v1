import time
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger


def reporting_node(state):
    start_time = time.time()

    summary_result = {
        "report_title": "Executive Summary: Recent SOC Activity",
        "incidents_analyzed": 5,
        "critical_threats": 1,
        "actions_taken": ["Blocked IP 10.0.0.55 on Edge Firewall"],
        "summary": "The SOC processed 5 alerts in the last hour. One critical SQL injection was confirmed and automatically blocked. Other alerts were related to generic scanning and were logged for further correlation."
    }
    
    current_node_output = {
        "module_name": "soc defense",
        "router_name": None,
        "pod_name": "reporting_pod",
        "status": "success",
        "ai_thought_process": "Generated an executive summary of recent SOC incidents and actions.",
        "human_approval_required": False,
        "hitl_message": None,
        "data_payload": {
            "technical data": summary_result
        }
    }

    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="reporting_pod")
    soc_logger.log(
        event_type="processing",
        input_data={"incidents_analyzed": summary_result["incidents_analyzed"]},
        output_data={"report_title": summary_result["report_title"]},
        status="success",
        metadata={"execution_time_ms": exec_time_ms}
    )
    
    return {"current_node_output": current_node_output}
