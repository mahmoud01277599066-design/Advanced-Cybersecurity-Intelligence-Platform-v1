import time
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger


def firewall_node(state):
    # Simulate a generic confirmed attack response
    ip_to_block = state.get("user_input", "192.168.1.100") 
    
    start_time = time.time()
    
    firewall_response = f"Successfully generated block rule on perimeter firewall for context: {ip_to_block[:50]}"
        
    current_node_output = {
        "module name": "soc defense",
        "router name": None,
        "pod name": "firewall_pod",
        "status": "success",
        "ai thought process": "Executing perimeter defense strategy to isolate the threat.",
        "human approval required": True, # High risk action requires True as per standard
        "hitl message": "A firewall block rule has been drafted. Please authorize deployment.",
        "data payload": {
            "technical data": {
                "firewall_response": firewall_response
            }
        }
    }

    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="firewall_pod")
    soc_logger.log(
        event_type="decision",
        input_data={"ip_to_block": ip_to_block[:50]},
        output_data={"firewall_response": firewall_response},
        status="success",
        metadata={
            "execution_time_ms": exec_time_ms,
            "human_approval_required": True
        }
    )
    
    return {"current_node_output": current_node_output}
