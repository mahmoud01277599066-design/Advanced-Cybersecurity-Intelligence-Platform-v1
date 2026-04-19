# SOC Defense Laboratory: Environment Setup Guide

This document describes how to transition from the **Simulation/Lab environment** to a **Real-World Security Environment**.

## 1. Prerequisites
- **Wazuh Manager:** Installed and running (Docker or VM).
- **Ollama:** Running as a background service (`ollama serve`).
- **Python 3.12+**: With `requests`, `urllib3`, and `langgraph` installed.

## 2. Real Wazuh Integration
To connect to your real Wazuh instance, modify the credentials in `modules/soc_defense/pods/wazuh_fetcher_pod.py`:

```python
# Replace these with your real Wazuh Manager details
fetcher = WazuhIngestor("https://YOUR_WAZUH_IP:55000", "admin_user", "admin_password")
```

> [!IMPORTANT]
> Ensure your network allows traffic on port **55000 (API)** and that the API user has permissions to read security events.

## 3. Persistent Dashboard Integration
The ACIP system saves all AI analysis results into the `outputs/` folder as standardized JSON.

### Recommended Dashboard Setup:
1.  **Direct File Monitoring**: Use a tool like **Datadog** or **Prometheus** to monitor the `outputs/` folder.
2.  **Custom Streamlit UI**: Create a simple Python script to read the latest JSON files and display:
    - AI Thought Process (Detailed Reasoning).
    - Status (Success/Error).
    - pod_name (Which specialized agent acted).

## 4. Active Response Safety
The `active_response_router` is configured with `"human approval required": true` by default. 

> [!WARNING]
> DO NOT disable human approval in production unless you have verified the AI classification accuracy for at least 30 days.

---
*Created as part of the ACIP Professional SOC Refining Process.*
