import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Ensure project root is in path
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.pods.wazuh_fetcher_pod import WazuhFetcherPod
from modules.soc_defense.pods.enrichment_pod import EnrichmentPod
from modules.soc_defense.pods.ai_triage_pod import AITriagePod
from modules.soc_defense.pods.pro_reporting_pod import ProReportingPod
from modules.soc_defense.core.database import log_incident, init_db

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LiveObserver")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, log_path):
        self.log_path = log_path
        self._last_position = os.path.getsize(log_path) if os.path.exists(log_path) else 0
        
        # Initialize Analytics Engine (Pods)
        self.fetcher = WazuhFetcherPod("http://localhost:55000", "admin", "admin")
        self.enricher = EnrichmentPod()
        self.triage = AITriagePod()
        self.reporter = ProReportingPod(output_dir=os.path.join(ROOT_DIR, "reports"))
        
        init_db()

    def on_modified(self, event):
        if event.src_path.endswith("access.log"):
            self.process_new_lines()

    def process_new_lines(self):
        try:
            with open(self.log_path, "r") as f:
                f.seek(self._last_position)
                new_lines = f.readlines()
                self._last_position = f.tell()
                
                for line in new_lines:
                    if line.strip():
                        self.analyze_line(line.strip())
        except Exception as e:
            logger.error(f"Error reading log file: {e}")

    def analyze_line(self, log_line):
        logger.info(f"Detected new log entry: {log_line[:50]}...")
        
        # Real Parsing: 2026-04-13 13:49:43,105 - INFO - 127.0.0.1 - GET /search...
        import re
        ip_match = re.search(r' - (\d+\.\d+\.\d+\.\d+) - ', log_line)
        real_ip = ip_match.group(1) if ip_match else "Unknown"
        
        # 1. Pipeline: Normalize & Push to IPC Bus
        raw_alert = {
            "srcip": real_ip,
            "full_log": log_line,
            "rule": {"id": "100200", "level": 10, "description": "Suspicious Web Request"},
            "timestamp": time.ctime()
        }
        
        rule = raw_alert.get("rule", {})
        normalized = {
            "rule_id": rule.get("id"),
            "description": rule.get("description"),
            "src_ip": real_ip,
            "timestamp": raw_alert.get("timestamp"),
            "full_log": log_line,
            "severity": "high" if "UNION" in log_line else "medium",
            "agent_name": "Web Server"
        }
        
        from modules.soc_defense.core.json_logger import SOCLogger
        soc_logger = SOCLogger(component_type="router", component_name="log_observer")
        soc_logger.log(
            event_type="web_log",
            input_data={"raw": log_line},
            output_data={"data": [normalized]},
            status="success"
        )
        
        # 2. Trigger Hybrid LangGraph Orchestrator Brain
        from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph
        app = build_soc_graph()
        
        # We explicitly target the 'log_triage' scenario via the master router
        user_req = f"[log_triage] Analyze this suspicious web log: {log_line}"
        res = app.invoke({"user_input": user_req})
        
        # 3. Log extracted incidents if applicable
        final_output = res.get("current_node_output", {})
        logger.info(f"LangGraph execution completed. Status: {final_output.get('status', 'Unknown')}")
        
        # The true results are preserved safely and permanently inside logs/router/ and logs/pods/ via SOCLogger

def start_observer():
    log_dir = os.path.join(ROOT_DIR, "logs")
    log_file = os.path.join(log_dir, "access.log")
    
    if not os.path.exists(log_file):
        with open(log_file, "w") as f: pass
        
    event_handler = LogFileHandler(log_file)
    observer = Observer()
    observer.schedule(event_handler, path=log_dir, recursive=False)
    observer.start()
    
    logger.info(f"Live SOC Observer started. Watching {log_file}")
    
    try:
        while True:
            event_handler.process_new_lines()
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_observer()
