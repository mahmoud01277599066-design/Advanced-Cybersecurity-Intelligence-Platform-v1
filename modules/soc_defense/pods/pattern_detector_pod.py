import json
import time
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.utils import save_output_to_json
from modules.soc_defense.core.json_logger import SOCLogger

def pattern_detector_node(state):
    data = state.get("current_node_output", {}).get("data payload", {})
    traffic = data.get("network_traffic", "")
    
    start_time = time.time()
    
    prompt = f"""Analyze network traffic for anomalies.
Traffic: {traffic}

📦 OUTPUT FORMAT (STRICT):
{{
  "module name": "soc defense",
  "pod name": "pattern_detector_pod",
  "anomalies_detected": ["List of specific technical anomalies"],
  "ai_thought_process": "Detailed reasoning for anomaly classification",
  "status": "success"
}}
IMPORTANT: Replace all placeholders with actual technical analysis. Return ONLY JSON.
"""
    response_str = query_llm(prompt)
    try:
        response_data = json.loads(response_str)
    except:
        response_data = {"status": "error"}

    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="pattern_detector_pod")
    soc_logger.log(
        event_type="anomaly_detection",
        input_data={"network_traffic": traffic},
        output_data=response_data,
        status=response_data.get("status", "error"),
        metadata={"execution_time_ms": exec_time_ms}
    )

    save_output_to_json(response_data, "pattern_detector_pod")
    return {"current_node_output": response_data}
