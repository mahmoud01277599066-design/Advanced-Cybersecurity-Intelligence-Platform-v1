import os
import sys
import time
import json
import threading
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core.pcap_observer import run_pcap_observer
from modules.soc_defense.pods.network_analysis_pod import NetworkAnalysisPod
from modules.soc_defense.pods.pro_reporting_pod import ProReportingPod
from modules.soc_defense.core.database import log_incident

def start_dashboard():
    dashboard_path = os.path.join(ROOT_DIR, "modules", "soc_defense", "ui", "dashboard.py")
    # Using sys.executable ensures we use the correct python env on Windows
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", dashboard_path], stdout=subprocess.DEVNULL)
    print("[*] Streamlit Dashboard launched in background.")

def handle_flow_anomaly(flow_summary):
    # 1. Log the Anomaly to the Router Bus
    from modules.soc_defense.core.json_logger import SOCLogger
    soc_logger = SOCLogger(component_type="router", component_name="pcap_observer")
    soc_logger.log(
        event_type="pcap_flow",
        input_data={"source": "honeypot"},
        output_data={"data": [flow_summary]},
        status="success"
    )
    
    print(f"\n[AI] Routing PCAP Anomaly via LangGraph Hybrid Engine: {flow_summary['src_ip']}...")
    
    # 2. Trigger Hybrid LangGraph Orchestrator Brain
    from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph
    app = build_soc_graph()
    
    app.invoke({"user_input": f"[anomaly_detection] Analyze this network flow anomaly: {json.dumps(flow_summary)}"})
    
    print("[+] LangGraph Hybrid Pipeline executed. Telemetry captured in /logs/ JSON Bus.")

def start_ndr_pipeline():
    print("="*60)
    print("   ACIP MASTER PCAP PIPELINE (NDR) INITIALIZING")
    print("="*60)
    
    start_dashboard()
    
    print("[*] Starting PCAP Flow Observer...")
    try:
        run_pcap_observer(analysis_callback=handle_flow_anomaly)
    except KeyboardInterrupt:
        print("\n[*] Shutting down NDR Master Pipeline...")

if __name__ == "__main__":
    start_ndr_pipeline()
