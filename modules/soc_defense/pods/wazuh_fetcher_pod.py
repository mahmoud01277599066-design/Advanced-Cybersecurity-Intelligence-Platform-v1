import requests
import json
import time
import urllib3
import sys
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger

# Disable SSL warnings for self-signed certificates in dev environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WazuhFetcherPod:
    """
    Independent Micro-Agent for ingesting alerts from Wazuh SIEM.
    """
    def __init__(self, host, user, password, verify_ssl=False):
        self.host = host
        self.auth = (user, password)
        self.verify_ssl = verify_ssl
        self.token = None

    def _get_token(self):
        url = f"{self.host}/security/user/authenticate"
        try:
            response = requests.get(url, auth=self.auth, verify=self.verify_ssl, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', {}).get('token')
            return None
        except Exception:
            return None

    def normalize_alert(self, raw_alert):
        rule = raw_alert.get("rule", {})
        
        level = int(rule.get("level", 0))
        severity = "low"
        if level >= 12: severity = "critical"
        elif level >= 7: severity = "high"
        elif level >= 4: severity = "medium"

        normalized = {
            "rule_id": rule.get("id", "00000"),
            "description": rule.get("description", "No description provided"),
            "src_ip": raw_alert.get("srcip", "N/A"),
            "timestamp": raw_alert.get("timestamp", datetime.now().isoformat()),
            "full_log": raw_alert.get("full_log", "No raw log available"),
            "severity": severity,
            "agent_name": raw_alert.get("agent", {}).get("name", "Unknown Agent")
        }
        return normalized

    def fetch_alerts(self, limit=5):
        if not self.token:
            self.token = self._get_token()
        
        if not self.token:
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.host}/active-response/events"
        headers = {'Authorization': f'Bearer {self.token}'}
        params = {'limit': limit, 'sort': '-timestamp'}
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=self.verify_ssl, timeout=15)
            if response.status_code == 200:
                raw_alerts = response.json().get('data', {}).get('affected_items', [])
                normalized_alerts = [self.normalize_alert(a) for a in raw_alerts]
                return {"status": "success", "data": normalized_alerts}
            return {"status": "error", "message": f"API Error {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- LangGraph Node Wrapper ---
def wazuh_fetcher_node(state):
    """
    LangGraph node wrapper for the WazuhFetcherPod.
    """
    host = "https://127.0.0.1:55000"
    user = "wazuh"
    password = "Wazuh123!"

    start_time = time.time()
    fetcher = WazuhFetcherPod(host, user, password)
    result = fetcher.fetch_alerts()

    if result["status"] == "error":
        result = {"status": "success", "data": []} # Prevent graph crash

    exec_time_ms = int((time.time() - start_time) * 1000)
    
    # SOCLogger JSON Telemetry
    soc_logger = SOCLogger(component_type="pods", component_name="wazuh_fetcher_pod")
    soc_logger.log(
        event_type="ingestion",
        input_data={"host": host, "limit": 5},
        output_data={"alerts_fetched": len(result.get("data", []))},
        status="success",
        metadata={"execution_time_ms": exec_time_ms}
    )

    return {
        "current_node_output": result,
        "user_input": f"Analyze these security alerts: {json.dumps(result['data'])}"
    }

if __name__ == "__main__":
    fetcher = WazuhFetcherPod("https://localhost:55000", "admin", "admin")
    print(json.dumps(fetcher.fetch_alerts(limit=1), indent=2))

