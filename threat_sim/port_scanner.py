import socket
import time
import argparse
import random
from concurrent.futures import ThreadPoolExecutor

import sys
import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(ROOT_DIR)
from modules.soc_defense.core.json_logger import SOCLogger

print(r"""
    ___   ___________    __         __  __             
   /   | / ____/  _/ |  / /   ___  / /_/ /____  _  __  
  / /| |/ /    / / | | / /   / _ \/ __/ __/ _ \| |/_/  
 / ___ / /____/ /  | |/ /___/  __/ /_/ /_/  __/>  <    
/_/  |_\____/___/  |___/____/\___/\__/\__/\___/_/|_|   
     --- Advanced Network Threat Simulator ---
""")

def scan_port(ip, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            return port, True
        return port, False
    except Exception:
        return port, False
    finally:
        sock.close()

def run_aggressive_scan(target_ip, ports):
    print(f"[*] Mode: AGGRESSIVE (Fast Scan)")
    print(f"[*] Scanning {len(ports)} ports simultaneously...\n")
    start_time = time.time()
    
    open_ports = []
    # Dump 100 threads to scan as fast as possible
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(lambda p: scan_port(target_ip, p, timeout=0.5), ports)
        for port, is_open in results:
            if is_open:
                open_ports.append(port)
                
    end_time = time.time()
    print(f"\n[+] Scan completed in {end_time - start_time:.2f} seconds.")
    print(f"[+] Open Ports: {open_ports}")
    return open_ports

def run_stealth_scan(target_ip, ports):
    print(f"[*] Mode: STEALTH (Slow Scan)")
    print(f"[*] Scanning {len(ports)} ports with 2-second delays...\n")
    start_time = time.time()
    
    open_ports = []
    # Scan sequentially with sleep
    for port in ports:
        print(f"    [-] Probing port {port}...")
        _, is_open = scan_port(target_ip, port, timeout=1.0)
        if is_open:
            open_ports.append(port)
        time.sleep(2.0)
        
    end_time = time.time()
    print(f"\n[+] Stealth scan completed in {end_time - start_time:.2f} seconds.")
    print(f"[+] Open Ports: {open_ports}")
    return open_ports

def run_random_scan(target_ip, ports):
    print(f"[*] Mode: RANDOMIZED (Evasion Scan)")
    print(f"[*] Scanning {len(ports)} ports in random order with random delays...\n")
    start_time = time.time()
    
    shuffled_ports = list(ports)
    random.shuffle(shuffled_ports)
    
    open_ports = []
    for port in shuffled_ports:
        delay = random.uniform(0.1, 1.5)
        print(f"    [-] Deep probe on port {port} (delay: {delay:.2f}s)...")
        _, is_open = scan_port(target_ip, port, timeout=1.0)
        if is_open:
            open_ports.append(port)
        time.sleep(delay)
        
    end_time = time.time()
    print(f"\n[+] Randomized scan completed in {end_time - start_time:.2f} seconds.")
    print(f"[+] Open Ports: {open_ports}")
    return open_ports

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ACIP Threat Simulator - Port Scanner")
    parser.add_argument("--target", type=str, default="127.0.0.1", help="Target IP address")
    parser.add_argument("--mode", type=str, choices=["aggressive", "stealth", "random"], default="aggressive", help="Scan mode")
    
    args = parser.parse_args()
    
    # Common ports + some random high ports for noise
    target_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 3306, 3389, 5000, 8080]
    # Add 20 random noise ports
    target_ports.extend(random.sample(range(1024, 65535), 20))
    target_ports = list(set(target_ports)) # Unique
    
    print(f"[*] Target: {args.target}")
    
    t_start = time.time()
    open_ports_found = []
    
    if args.mode == "aggressive":
        open_ports_found = run_aggressive_scan(args.target, target_ports)
    elif args.mode == "stealth":
        open_ports_found = run_stealth_scan(args.target, target_ports)
    elif args.mode == "random":
        open_ports_found = run_random_scan(args.target, target_ports)
        
    # JSON Time-Partitioned Logging for Scripts
    soc_logger = SOCLogger(component_type="scripts", component_name="attack_simulation_pcap")
    soc_logger.log(
        event_type="simulation",
        input_data={"target": args.target, "mode": args.mode, "ports_scanned": len(target_ports)},
        output_data={"open_ports_found": open_ports_found, "count_open": len(open_ports_found)},
        status="success",
        metadata={"execution_time_ms": int((time.time() - t_start) * 1000)}
    )


