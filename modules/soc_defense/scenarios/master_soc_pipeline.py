import os
import sys
import time
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.database import init_db
from modules.soc_defense.core.json_logger import SOCLogger

def run_live_soc():
    soc_logger = SOCLogger(component_type="scripts", component_name="master_pipeline")

    print("=" * 60)
    print("      ACIP - HYBRID SOC OPERATING ENVIRONMENT")
    print("             LangGraph Brain + JSON Telemetry")
    print("=" * 60)

    # Step 0: Initialize Infrastructure
    print("\n[0/4] Initializing Database and Services...")
    init_db()
    soc_logger.log(
        event_type="execute",
        input_data={"step": "init_db"},
        output_data={},
        status="success",
        metadata={"description": "Database initialized"}
    )

    # Step 1: Start Vulnerable Target (Background)
    print("\n[1/4] Starting Vulnerable Target (Flask)...")
    target_path = os.path.join(ROOT_DIR, "vulnerable_apps/flask_target.py")
    flask_process = subprocess.Popen(
        [sys.executable, target_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    print("[+] Flask target is live on port 5000.")
    soc_logger.log(
        event_type="execute",
        input_data={"step": "start_flask_target"},
        output_data={"pid": flask_process.pid, "port": 5000},
        status="success"
    )

    # Step 2: Start Log Observer + LangGraph Hybrid Engine (Background)
    print("\n[2/4] Starting Hybrid SOC Observer (LangGraph + JSON Telemetry)...")
    observer_path = os.path.join(ROOT_DIR, "modules/soc_defense/core/log_observer.py")
    observer_process = subprocess.Popen([sys.executable, observer_path])
    print("[+] Observer is watching for security events → routing via LangGraph engine.")
    soc_logger.log(
        event_type="execute",
        input_data={"step": "start_log_observer"},
        output_data={"pid": observer_process.pid},
        status="success"
    )

    # Step 3: Start Dashboard (Background)
    print("\n[3/4] Launching Professional SOC Dashboard...")
    dashboard_path = os.path.join(ROOT_DIR, "modules/soc_defense/ui/dashboard.py")
    dashboard_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", dashboard_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("[+] Dashboard launched. Open your browser for the Live View.")
    soc_logger.log(
        event_type="execute",
        input_data={"step": "start_dashboard"},
        output_data={"pid": dashboard_process.pid},
        status="success"
    )

    print("\n" + "-" * 60)
    print("      LIVE SOC ENVIRONMENT IS NOW OPERATIONAL")
    print("      • JSON Telemetry  →  /logs/")
    print("      • LangGraph Brain → executing decisions")
    print("-" * 60)
    print("\n[*] Press Ctrl+C to shut down all services.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[*] Shutting down ACIP Services...")
        flask_process.terminate()
        observer_process.terminate()
        dashboard_process.terminate()
        soc_logger.log(
            event_type="execute",
            input_data={"step": "shutdown"},
            output_data={},
            status="success",
            metadata={"description": "All services terminated cleanly"}
        )
        print("[*] All services terminated. Environment cleaned up.")

if __name__ == "__main__":
    run_live_soc()

