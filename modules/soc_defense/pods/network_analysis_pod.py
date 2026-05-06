import json
from collections import defaultdict
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.core.json_logger import SOCLogger

# Behavior Profiling tracker (In-memory simple state)
# Tracks history string per IP
attacker_profiles = defaultdict(list)

# Trusted Whitelist
TRUSTED_IPS = ["127.0.0.1_internal_scanner", "192.168.1.100"] 

class NetworkAnalysisPod:
    """
    Advanced NDR Detection Engine with Hybrid Logic (Rules + AI) and Behavior Profiling
    """
    
    def apply_rules(self, flow):
        """Rule-based Fast Detection Layer."""
        if flow["src_ip"] in TRUSTED_IPS:
            return {"classification": "False Positive", "confidence": 1.0, "reason": "Whitelisted internal scanner"}
            
        # Aggressive port scan > 20 ports in the window
        if flow["unique_ports"] > 20:
            return {"classification": "True Positive", "confidence": 0.98, "reason": f"Rule match: Aggressive scan ({flow['unique_ports']} ports) detected"}
            
        return None

    def query_ai_anomaly(self, flow, profile_history):
        """AI deep analysis of the flow and the attacker history."""
        prompt = f"""You are an Expert NDR Security Analyst. 
Analyze this network flow behavior and classify if it is a Reconnaissance/Port Scan attack.

Current Flow Window:
{json.dumps(flow, indent=2)}

Attacker History (Behavior Profile):
{profile_history}

STRICT OUTPUT FORMAT (JSON ONLY):
{{
  "classification": "True Positive | False Positive",
  "confidence": 0.0-1.0,
  "attack_type": "Reconnaissance - Port Scanning | Benign Traffic",
  "reason": "Explain based on connection rate, unique ports, pattern, and history."
}}
"""
        response_str = query_llm(prompt)
        try:
            return json.loads(response_str)
        except Exception as e:
            # Fallback
            if flow["unique_ports"] > 5 and flow["connection_rate"] > 1.0:
                return {"classification": "True Positive", "confidence": 0.8, "attack_type": "Reconnaissance - Port Scanning", "reason": "High unique ports / connection rate (AI Fallback)"}
            return {"classification": "False Positive", "confidence": 0.6, "attack_type": "Benign Traffic", "reason": "No deep anomaly detected (AI Fallback)"}

    def analyze_flow(self, flow):
        # 1. False Positive check / Quick Rules
        rule_decision = self.apply_rules(flow)
        if rule_decision:
            # Update history
            attacker_profiles[flow["src_ip"]].append({
                "window": flow["time_window"],
                "action": f"Rule-based flag: {rule_decision['reason']}"
            })
            return rule_decision
            
        # 2. Build History Profile string
        history = attacker_profiles.get(flow["src_ip"], [])
        history_str = "No previous history" if not history else json.dumps(history)
        
        # 3. Deep AI Analysis
        ai_decision = self.query_ai_anomaly(flow, history_str)
        
        # 4. Update Profile
        attacker_profiles[flow["src_ip"]].append({
            "window": flow["time_window"],
            "action": f"AI classified as {ai_decision['classification']}: {ai_decision['attack_type']}"
        })
        
        return ai_decision

import sys
import os
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger

# --- LangGraph Node Wrapper ---
def network_analysis_node(state):
    """
    Receives flow data via LangGraph, applies Advanced Anomaly Detection.
    """
    current_output = state.get("current_node_output", {})
    flow_data = current_output.get("data", {})
    
    if not flow_data:
        return {"current_node_output": {"status": "error", "message": "No flow data provided."}}
        
    start_time = time.time()
    pod = NetworkAnalysisPod()
    decision = pod.analyze_flow(flow_data)
    
    analysis_result = {**flow_data, **decision}
    
    exec_time_ms = int((time.time() - start_time) * 1000)
    
    soc_logger = SOCLogger(component_type="pods", component_name="network_analysis_pod")
    soc_logger.log(
        event_type="anomaly_detection",
        input_data={"flow_data": flow_data},
        output_data={"data": analysis_result},
        status="success",
        metadata={"execution_time_ms": exec_time_ms}
    )
    
    result = {
        "module_name": "soc defense",
        "pod_name": "network_analysis_pod",
        "status": "success",
        "ai_thought_process": "Executed Hybrid Detection (Rules + AI) with Behavior Profiling.",
        "data": [analysis_result] # Wrapped in list for consistency with other pods
    }
    
    return {"current_node_output": result, "user_input": f"Report on this network anomaly: {json.dumps(analysis_result)}"}

if __name__ == "__main__":
    pod = NetworkAnalysisPod()
    test_flow = {
        "src_ip": "1.2.3.4",
        "unique_ports": 50,
        "connection_count": 120,
        "connection_rate": 40.0,
        "pattern": "sequential",
        "time_window": "5s"
    }
    print(json.dumps(pod.analyze_flow(test_flow), indent=2))
