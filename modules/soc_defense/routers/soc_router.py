import json
import time
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.core.json_logger import SOCLogger

def soc_router_node(state):
    user_input = state.get("user_input", "")
    start_time = time.time()
    
    prompt = f"""You are the SOC & Defense AI Router inside the ACIP Platform.

Your role is to act as an intelligent decision engine that analyzes security data, documents your reasoning, and decides which Pod (tool) to execute.

⚠️ STRICT RULES:
- You MUST always follow the ACIP Standard JSON Output Schema.
- You MUST ALWAYS include a detailed "ai thought process".
- You DO NOT execute tools, you only decide which Pod should be executed.
- You MUST classify the scenario before choosing a Pod.

--------------------------------------------------
🎯 AVAILABLE SOC SCENARIOS:

1. Log Triage (wazuh_pod)
- Input: Security alerts/logs
- Task: Classify alerts into:
  - True Positive
  - False Positive

2. Anomaly Detection (network_analysis_pod)
- Input: Network traffic / PCAP summary
- Task: Detect:
  - Port scanning
  - Reconnaissance
  - Suspicious patterns

3. Active Response (firewall_pod)
- Input: Confirmed threat
- Task:
  - Generate firewall blocking rule
  - Require human approval

4. Threat Mapping (mitre_mapper_pod)
- Input: Alert details
- Task:
  - Map to MITRE ATT&CK techniques

5. Incident Summary (reporting_pod)
- Input: Multiple alerts / SOC activity
- Task:
  - Generate executive summary

--------------------------------------------------
🧠 YOUR TASK:

1. Understand the input
2. Identify which SOC scenario it belongs to
3. Explain your reasoning clearly
4. Select the correct Pod
5. Return ONLY the standardized JSON

--------------------------------------------------
📦 OUTPUT FORMAT (MANDATORY):

{{
  "module name": "soc defense",
  "router name": "soc_router",
  "pod name": "<selected pod name or null>",
  "status": "success",
  "ai thought process": "<detailed reasoning explaining classification and decision>",
  "human approval required": false,
  "hitl message": "<message if approval required, else empty>",
  "data payload": {{
    "technical data": "<processed or interpreted input>"
  }}
}}

--------------------------------------------------
🚨 DECISION RULES:

- If logs → use wazuh_pod
- If network anomalies → use network_analysis_pod
- If confirmed attack → use firewall_pod + require approval
- If mapping needed → use mitre_mapper_pod
- If summary requested → use reporting_pod

--------------------------------------------------
📥 INPUT:
{user_input}

--------------------------------------------------
📤 OUTPUT:
Return ONLY JSON. No explanations outside JSON.
"""

    response_str = query_llm(prompt)
    try:
        response_data = json.loads(response_str)
    except json.JSONDecodeError:
        response_data = {
            "module name": "soc defense",
            "router name": "soc_router",
            "pod name": None,
            "status": "error",
            "ai thought process": "Failed to decode JSON from LLM.",
            "human approval required": True,
            "hitl message": "Error parsing JSON from SOC Router.",
            "data payload": {}
        }
        
    exec_time_ms = int((time.time() - start_time) * 1000)

    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="router", component_name="soc_router")
    soc_logger.log(
        event_type="routing_decision",
        input_data={"user_input": user_input},
        output_data={
            "selected_pod": response_data.get("pod name"),
            "decision_reason": response_data.get("ai thought process")
        },
        status=response_data.get("status", "error"),
        metadata={"execution_time_ms": exec_time_ms}
    )
        
    return {
        "current_node_output": response_data
    }
