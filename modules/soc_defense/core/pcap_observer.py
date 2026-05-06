import os
import time
import re
import json
from collections import defaultdict
from modules.soc_defense.core.json_logger import SOCLogger

# Sliding window state
# Structure: { "src_ip": [{"timestamp": float, "port": int}] }
flow_state = defaultdict(list)

# Configuration
WINDOW_SIZE_SECONDS = 10  # 10s rolling window
FLOW_SUMMARY_THRESHOLD = 5 # Minimum connections in window to trigger analysis

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
HONEYPOT_LOG_PATH = os.path.join(ROOT_DIR, "logs", "honeypot_connections.log")

soc_logger = SOCLogger(component_type="router", component_name="pcap_observer")

def parse_line(line):
    # Example format: 2026-04-13 13:42:33,123 - HONEYPOT - CONNECTION ALARM - IP: 127.0.0.1 connected to Port: 22
    match = re.search(r"IP: ([\d\.]+) connected to Port: (\d+)", line)
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def clean_old_flows(current_time):
    """Remove connection records older than the sliding window."""
    for ip in list(flow_state.keys()):
        flow_state[ip] = [record for record in flow_state[ip] if current_time - record["timestamp"] <= WINDOW_SIZE_SECONDS]
        if not flow_state[ip]:
            del flow_state[ip]

def analyze_window(current_time, target_ip):
    """Calculates behavioral metrics for the given IP in the current window."""
    records = flow_state[target_ip]
    if len(records) < FLOW_SUMMARY_THRESHOLD:
        return None
        
    unique_ports = len(set(r["port"] for r in records))
    connection_rate = len(records) / WINDOW_SIZE_SECONDS
    
    # Simple pattern detection
    ports = [r["port"] for r in records]
    is_sequential = len(ports) >= 3 and ports == sorted(ports) and unique_ports == len(ports)
    pattern = "sequential" if is_sequential else ("random" if unique_ports > 1 else "targeted")
    
    flow_summary = {
        "src_ip": target_ip,
        "unique_ports": unique_ports,
        "connection_count": len(records),
        "connection_rate": round(connection_rate, 2),
        "pattern": pattern,
        "time_window": f"{WINDOW_SIZE_SECONDS}s"
    }
    
    return flow_summary

def run_pcap_observer(analysis_callback=None):
    """
    Acts as the SIEM network ingestor using a Fast-Flow Aggregator logic.
    Instead of full PCAP, we read connection streams and aggregate behaviors.
    """
    print("="*60)
    print("   ACIP Network Ingestor (Flow Aggregator) is ACTIVE")
    print("="*60)
    
    if not os.path.exists(HONEYPOT_LOG_PATH):
        print("[!] Waiting for Honeypot log file to be created...")
        # Create empty file if not exists yet
        os.makedirs(os.path.dirname(HONEYPOT_LOG_PATH), exist_ok=True)
        with open(HONEYPOT_LOG_PATH, 'a') as f:
            pass

    # Track reported flow fingerprints to avoid spamming the AI
    reported_flows = set()

    with open(HONEYPOT_LOG_PATH, 'r') as file:
        file.seek(0, os.SEEK_END)
        
        while True:
            line = file.readline()
            current_time = time.time()
            clean_old_flows(current_time)
            
            if not line:
                time.sleep(0.5)
                continue
                
            ip, port = parse_line(line)
            if ip and port:
                flow_state[ip].append({"timestamp": current_time, "port": port})
                
                # Check sliding window for behavior match
                summary = analyze_window(current_time, ip)
                if summary:
                    # Construct simple fingerprint (IP + Unique Ports) to prevent AI spam in the same window
                    fingerprint = f"{ip}_{summary['unique_ports']}"
                    if fingerprint not in reported_flows:
                        reported_flows.add(fingerprint)
                        print(f"\n[⚠️] FLOW ANOMALY DETECTED: {json.dumps(summary, indent=2)}")
                        
                        soc_logger.log(
                            event_type="ingestion",
                            input_data={"raw_line": line.strip()},
                            output_data=summary,
                            status="success"
                        )
                        
                        if analysis_callback:
                            analysis_callback(summary)
