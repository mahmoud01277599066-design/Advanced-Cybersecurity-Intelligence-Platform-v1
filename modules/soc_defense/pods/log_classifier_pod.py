import json
import time
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.utils import save_output_to_json
from modules.soc_defense.core.json_logger import SOCLogger

def log_classifier_node(state):
    data = state.get("current_node_output", {}).get("data payload", {})
    logs = data.get("logs", "")
    
    start_time = time.time()
    
    prompt = f"""Analyze these logs and classify them as True Positive or False Positive.
Logs: {logs}

📦 OUTPUT FORMAT (STRICT):
{{
  "module name": "soc defense",
  "pod name": "log_classifier_pod",
  "classification": "True Positive or False Positive",
  "ai thought process": "Detailed cybersecurity reasoning for this classification",
  "status": "success"
}}
IMPORTANT: Replace all placeholder text with actual security analysis. Return ONLY JSON.
"""
    response_str = query_llm(prompt)
    try:
        response_data = json.loads(response_str)
    except:
        response_data = {"status": "error"}

    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="log_classifier_pod")
    soc_logger.log(
        event_type="decision",
        input_data={"logs": logs},
        output_data=response_data,
        status=response_data.get("status", "error"),
        metadata={"execution_time_ms": exec_time_ms}
    )

    save_output_to_json(response_data, "log_classifier_pod")
    return {"current_node_output": response_data}
