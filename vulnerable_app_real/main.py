import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    # Demonstrating usage of outdated libraries
    try:
        res = requests.get("https://example.com", verify=False) # Insecure request
        status = res.status_code
    except Exception:
        status = "Error"
        
    template = f"""
    <h1>ACIP Vulnerable Real App Demo</h1>
    <p>Using Flask version: 1.1.2 (CVE-2023-30861)</p>
    <p>Using Requests version: 2.20.0 (CVE-2023-32681)</p>
    <p>External request status: {status}</p>
    """
    return render_template_string(template)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
