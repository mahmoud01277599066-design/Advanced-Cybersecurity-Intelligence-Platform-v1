import socket
import threading
import time
import logging
import os

# Configure logging specifically for the honeypot to feed the PCAP Observer (if needed as a fallback)
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
os.makedirs(log_dir, exist_ok=True)
honeypot_log = os.path.join(log_dir, "honeypot_connections.log")

logging.basicConfig(
    filename=honeypot_log,
    level=logging.INFO,
    format='%(asctime)s - HONEYPOT - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

SERVICES = {
    21: b"220 (vsFTPd 3.0.3)\r\n",
    22: b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n",
    80: b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\n\r\n<html><body><h1>It works!</h1></body></html>\n",
    3306: b"J\x00\x00\x00\x0a8.0.26\x00\x01\x00\x00\x00x\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00mysql_native_password\x00",
    8080: b"HTTP/1.1 401 Unauthorized\r\nServer: nginx/1.18.0\r\n\r\n",
}

class HoneypotService(threading.Thread):
    def __init__(self, port, banner):
        super().__init__()
        self.port = port
        self.banner = banner
        self.host = '0.0.0.0'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True

    def run(self):
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            logging.info(f"[*] Smart Honeypot listening on port {self.port}")
            
            while self.running:
                try:
                    self.sock.settimeout(1.0) # Allows checking self.running
                    client_sock, addr = self.sock.accept()
                    logging.info(f"CONNECTION ALARM - IP: {addr[0]} connected to Port: {self.port}")
                    
                    # Send realistic banner
                    client_sock.sendall(self.banner)
                    
                    # Receive data if attacker sends payloads (optional reading)
                    try:
                        client_sock.settimeout(2.0)
                        data = client_sock.recv(1024)
                        if data:
                            logging.info(f"PAYLOAD - IP: {addr[0]} Port: {self.port} Data: {data.decode(errors='ignore').strip()}")
                    except socket.timeout:
                        pass
                        
                    client_sock.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logging.error(f"Error on port {self.port}: {e}")
        except PermissionError:
            logging.error(f"[!] Access Denied: Cannot bind to port {self.port}. Administrator privileges required.")
        except Exception as e:
            logging.error(f"Failed to start service on port {self.port}: {e}")

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass

def start_honeypot():
    print("="*60)
    print("   ACIP Smart Honeypot (NDR Target Surface) is ACTIVE")
    print("="*60)
    
    threads = []
    for port, banner in SERVICES.items():
        t = HoneypotService(port, banner)
        t.daemon = True
        t.start()
        threads.append(t)
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down smart honeypot...")
        for t in threads:
            t.stop()
        print("[*] All services stopped.")

if __name__ == "__main__":
    start_honeypot()
