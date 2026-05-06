import time
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger


def wazuh_node(state):
    start_time = time.time()

    alert = {
        "rule_id": "5716",
        "description": "sshd: Invalid user login attempt.",
        "src_ip": "192.168.1.100",
        "failed_attempts": 15,
        "user": "admin",
        "timestamp": "2026-04-12T15:20:00Z"
    }
    
    current_node_output = {
        "module_name": "soc defense",
        "router_name": None,
        "pod_name": "wazuh_pod",
        "status": "success",
        "ai_thought_process": "Simulated extracting latest security alerts from Wazuh SIEM.",
        "human_approval_required": False,
        "hitl_message": None,
        "data_payload": {
            "technical data": alert
        }
    }

    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="wazuh_pod")
    soc_logger.log(
        event_type="ingestion",
        input_data={"source": "wazuh_siem_simulated"},
        output_data={"alerts_fetched": 1, "rule_id": alert["rule_id"]},
        status="success",
        metadata={"execution_time_ms": exec_time_ms}
    )
    
    return {"alert": alert, "current_node_output": current_node_output}
