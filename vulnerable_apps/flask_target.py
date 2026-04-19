from flask import Flask, request, jsonify
import logging
import os

app = Flask(__name__)

# Configure Logging to write to logs/access.log for Wazuh simulation
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
log_file = os.path.join(log_dir, "access.log")

# Setup a dedicated logger for security events
security_logger = logging.getLogger("SecurityLogger")
security_logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
security_logger.addHandler(handler)

@app.route('/')
def home():
    return "<h1>ACIP Vulnerable Target</h1><p>Welcome to the production-simulated environment.</p>"

@app.route('/search')
def search():
    user_id = request.args.get('id', '')
    
    # Log the incoming potentially malicious request
    # Real-world format: IP - [Date] "GET /search?id=PAYLOAD HTTP/1.1"
    ip = request.remote_addr
    security_logger.info(f"{ip} - GET /search?id={user_id} HTTP/1.1")
    
    # Intentional SQL Injection vulnerability simulation
    # (We don't actually need a DB, we just need to simulate the response logic)
    if "' OR '1'='1" in user_id or "UNION SELECT" in user_id:
        return jsonify({
            "status": "success",
            "results": [
                {"user": "admin", "pass": "admin_hashed_password_123"},
                {"user": "guest", "pass": "guest_pass"}
            ],
            "note": "SQL Query executed successfully (Vulnerable Mode)"
        })
    
    return jsonify({
        "status": "success",
        "results": [{"id": user_id, "name": "Generic User"}],
        "note": "Normal query executed."
    })

if __name__ == "__main__":
    print(f"[*] Starting vulnerable target on http://127.0.0.1:5000")
    print(f"[*] Logging security events to: {log_file}")
    app.run(port=5000, debug=False)
