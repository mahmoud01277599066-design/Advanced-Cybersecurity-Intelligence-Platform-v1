import time
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger

def mitre_mapper_node(state):
    start_time = time.time()
    
    mapping_result = {
        "alert_id": "5716",
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "tactic": "Credential Access",
        "mitigation_recommendation": "Implement account lockout policies and enforce strong passwords or MFA."
    }
    
    current_node_output = {
        "module_name": "soc defense",
        "router_name": None,
        "pod_name": "mitre_mapper_pod",
        "status": "success",
        "ai_thought_process": "Mapped the provided SSH brute force alert to MITRE ATT&CK technique T1110.",
        "human_approval_required": False,
        "hitl_message": None,
        "data_payload": {
            "technical data": mapping_result
        }
    }

    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="mitre_mapper_pod")
    soc_logger.log(
        event_type="threat_mapping",
        input_data={"simulated_input": "SSH Brute Force alert"},
        output_data=mapping_result,
        status="success",
        metadata={"execution_time_ms": exec_time_ms}
    )
    
    return {"current_node_output": current_node_output}
