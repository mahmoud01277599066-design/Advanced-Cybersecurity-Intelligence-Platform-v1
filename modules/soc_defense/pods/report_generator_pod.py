import json
import time
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.utils import save_output_to_json
from modules.soc_defense.core.json_logger import SOCLogger

def report_generator_node(state):
    data = state.get("current_node_output", {}).get("data payload", {})
    activities = data.get("activities", "")
    
    start_time = time.time()
    
    prompt = f"""Generate an executive SOC summary based on these activities.
Activities: {activities}

📦 OUTPUT FORMAT (STRICT):
{{
  "module name": "soc defense",
  "pod name": "report_generator_pod",
  "summary_report": "Extensive executive summary of findings",
  "ai_thought_process": "The focus and key insights of this report",
  "status": "success"
}}
IMPORTANT: Replace all placeholders with the actual summarized report. Return ONLY JSON.
"""
    response_str = query_llm(prompt)
    try:
        response_data = json.loads(response_str)
    except:
        response_data = {"status": "error"}

    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="report_generator_pod")
    soc_logger.log(
        event_type="reporting",
        input_data={"activities": activities},
        output_data=response_data,
        status=response_data.get("status", "error"),
        metadata={"execution_time_ms": exec_time_ms}
    )

    save_output_to_json(response_data, "report_generator_pod")
    return {"current_node_output": response_data}
