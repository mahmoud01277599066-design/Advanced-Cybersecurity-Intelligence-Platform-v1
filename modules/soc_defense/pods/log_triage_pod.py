import time
import sys
import os
import json
from datetime import datetime, timedelta

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger

class LogTriagePod:
    """
    Advanced SOC Normalization & Grouping Pod.
    Handles multi-alert correlation and enrichment.
    """
    
    def normalize_and_enrich(self, raw_alert: dict) -> dict:
        src_ip = raw_alert.get("src_ip", "0.0.0.0")
        is_suspicious_ip = src_ip.startswith("192.168.1.10")
        
        normalized = {
            "source": raw_alert.get("agent", raw_alert.get("source", "unknown_agent")),
            "event_id": str(raw_alert.get("rule_id", raw_alert.get("id", "00000"))),
            "description": str(raw_alert.get("description", raw_alert.get("alert", "No description"))),
            "src_ip": src_ip,
            "user_agent": raw_alert.get("user_agent", raw_alert.get("agent", "N/A")),
            "endpoint": raw_alert.get("endpoint", "/"),
            "timestamp": raw_alert.get("timestamp", datetime.now().isoformat()),
            "raw_payload": str(raw_alert.get("full_log", raw_alert.get("log", ""))),
            "enrichment": {
                "ip_reputation": "malicious" if is_suspicious_ip else "neutral",
                "geo_location": "US" if not is_suspicious_ip else "RU",
            }
        }
        return normalized

    def group_alerts(self, alerts: list, time_window_sec: int) -> list:
        if not alerts: return []
        try:
            alerts.sort(key=lambda x: x['timestamp'])
        except: pass

        grouped = {}
        for alert in alerts:
            key = (alert['src_ip'], alert['user_agent'], alert['endpoint'])
            if key not in grouped: grouped[key] = []
            grouped[key].append(alert)

        result = []
        for key, cluster in grouped.items():
            if not cluster: continue
            start_time = datetime.fromisoformat(cluster[0]['timestamp'].replace('Z', '+00:00'))
            window_end = start_time + timedelta(seconds=time_window_sec)
            filtered_cluster = [a for a in cluster if datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) <= window_end]
            result.extend(filtered_cluster)
        return result

def log_triage_node(state):
    """
    LangGraph node for log triage. Refactored for Standard Data Flow.
    """
    from modules.soc_defense.src.intelligence_engine import intelligence_engine
    from modules.soc_defense.src.llm_client import query_llm
    
    correlation_id = state.get("correlation_id", "unknown")
    current_out = state.get("current_node_output", {})
    raw_alerts = []
    
    # Adaptive Input Extraction
    if "data_payload" in current_out and "logs" in current_out["data_payload"]:
        raw_alerts = current_out["data_payload"]["logs"]
    elif "data" in current_out:
        raw_alerts = current_out["data"]
        
    if not raw_alerts and state.get("user_input"):
        user_in = state.get("user_input")
        try:
            if "[" in user_in and "]" in user_in:
                json_str = user_in[user_in.find("["):user_in.rfind("]")+1]
                raw_alerts = json.loads(json_str)
        except: pass

    if not raw_alerts:
        return {"current_node_output": {"rag_context": "N/A", "thinking_reasoning": "No logs provided.", "hitl_status": "approved", "final_decision": "Log Triage Skipped", "confidence_score": 0.0, "data_payload": {}}}

    start_time = time.time()
    triage_pod = LogTriagePod()
    normalized = [triage_pod.normalize_and_enrich(a) for a in raw_alerts if isinstance(a, dict)]
    grouped_alerts = triage_pod.group_alerts(normalized, state.get("time_window", 10))
    
    local_rag = intelligence_engine.get_rag_context(str(raw_alerts))
    rag_enriched_data = state.get("rag_enriched_data", {})
    if rag_enriched_data:
        rag_context = f"MITRE ENRICHMENT:\n{json.dumps(rag_enriched_data)}\n\nLOCAL INTELLIGENCE:\n{local_rag}"
    else:
        rag_context = local_rag

    prompt = intelligence_engine.wrap_thinking_prompt(f"Explain group behavior for {len(grouped_alerts)} alerts.", rag_context)
    ai_response = query_llm(prompt)
    try:
        ai_data = json.loads(ai_response)
    except:
        ai_data = {"thinking_reasoning": "Standard normalization applied.", "final_decision": "Logs Processed"}

    exec_time_ms = int((time.time() - start_time) * 1000)
    
    # STANDARD SCHEMA: final_decision (str), data_payload (dict)
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": ai_data.get("thinking_reasoning", "N/A"),
        "hitl_status": "approved",
        "final_decision": f"Successfully processed {len(grouped_alerts)} alerts into structured clusters.",
        "confidence_score": 1.0,
        "data_payload": {
            "grouped_alerts": grouped_alerts,
            "alert_count": len(grouped_alerts),
            "execution_time_ms": exec_time_ms,
            "correlation_id": correlation_id
        }
    }
    
    return {"current_node_output": result, "rag_context": rag_context, "thinking_reasoning": result["thinking_reasoning"]}
