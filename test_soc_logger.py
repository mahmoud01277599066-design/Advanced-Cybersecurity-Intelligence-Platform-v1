import os
import sys
import json
import time
from datetime import datetime

# Add root to sys.path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.json_logger import SOCLogger

def test_logger_standalone():
    print("Starting SOCLogger Standalone File Test...")
    
    # 1. Test Pod Logging
    pod_name = "test_pod"
    logger = SOCLogger(component_type="pods", component_name=pod_name)
    
    print(f"--- Testing {pod_name} ---")
    for i in range(3):
        logger.log(
            event_type="test_event",
            input_data={"run": i},
            output_data={"result": "success"},
            status="success",
            metadata={"index": i}
        )
        print(f"  Created log {i+1}/3")
        time.sleep(1.1)  # Ensure distinct timestamps for filename
        
    pod_log_dir = os.path.join(ROOT_DIR, "logs", "pods", pod_name)
    files = [f for f in os.listdir(pod_log_dir) if f.endswith(".json")]
    print(f"Found {len(files)} files in {pod_log_dir}")
    for f in files:
        print(f"  - {f}")
        
    if len(files) < 3:
        print(f"Error: Expected at least 3 files, found {len(files)}")
        return False

    # 2. Test Router Logging
    router_name = "test_router"
    logger = SOCLogger(component_type="router", component_name=router_name)
    print(f"\n--- Testing {router_name} ---")
    logger.log("routing", {"in": "data"}, {"out": "pod_x"}, "success")
    
    router_log_dir = os.path.join(ROOT_DIR, "logs", "router", router_name)
    files = os.listdir(router_log_dir)
    print(f"Created router log: {files[0]}")

    # 3. Test Script Logging
    script_name = "test_script"
    logger = SOCLogger(component_type="scripts", component_name=script_name)
    print(f"\n--- Testing {script_name} ---")
    logger.log("execution", {}, {"status": "finished"}, "success")
    
    script_log_dir = os.path.join(ROOT_DIR, "logs", "scripts", script_name)
    files = os.listdir(script_log_dir)
    print(f"Created script log: {files[0]}")

    # 4. Test Content Verification
    latest_file = os.path.join(script_log_dir, files[0])
    with open(latest_file, 'r') as f:
        data = json.load(f)
        
    required_keys = ["log_id", "schema_version", "timestamp", "component_type", "component_name", "event_type", "input", "output", "status", "metadata"]
    for key in required_keys:
        if key not in data:
            print(f"Missing key: {key}")
            return False
    
    print("\nLog Content Verification Passed")
    print(f"   Sample JSON Content:\n{json.dumps(data, indent=2)}")

    # 5. Test IPC (get_latest_event)
    print("\n--- Testing get_latest_event ---")
    latest = SOCLogger.get_latest_event("pods", pod_name)
    if latest and latest.get("input", {}).get("run") == 2:
        print("get_latest_event correctly retrieved the newest run (run 2)")
    else:
        print(f"get_latest_event failed or retrieved wrong run: {latest}")
        return False

    print("\nALL TESTS PASSED! SOC-Grade Logging is ACTIVE.")
    return True

if __name__ == "__main__":
    if test_logger_standalone():
        sys.exit(0)
    else:
        sys.exit(1)
