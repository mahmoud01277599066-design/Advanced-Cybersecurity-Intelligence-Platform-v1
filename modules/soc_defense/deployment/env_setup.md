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

### Real-Time Forwarding to SOC API
For direct Wazuh -> ACIP SOC forwarding, use:

- `modules/soc_defense/integrations/wazuh_forwarder.py`
- `modules/soc_defense/integrations/WAZUH_INTEGRATION.md`

Default SOC ingest endpoint used by forwarder:

- `http://127.0.0.1:8001/api/v1/soc/ingest`

You can override it with:

```bash
export SOC_INGEST_URL="http://<soc-host>:8001/api/v1/soc/ingest"
```

## 3. Real-Time Host Monitor (Auto Alerts)
You can also generate real host alerts from the machine itself using:

- `modules/soc_defense/integrations/real_time_monitor.py`

Example:

```bash
python modules/soc_defense/integrations/real_time_monitor.py --endpoint http://127.0.0.1:8001/api/v1/soc/ingest --cpu-threshold 90 --mem-threshold 90
```

> [!NOTE]
> This monitor requires `psutil`. Install with `pip install psutil`.

## 4. Persistent Dashboard Integration
The ACIP system saves all AI analysis results into the `outputs/` folder as standardized JSON.

### Recommended Dashboard Setup:
1.  **Direct File Monitoring**: Use a tool like **Datadog** or **Prometheus** to monitor the `outputs/` folder.
2.  **Custom Streamlit UI**: Create a simple Python script to read the latest JSON files and display:
    - AI Thought Process (Detailed Reasoning).
    - Status (Success/Error).
    - pod_name (Which specialized agent acted).

## 5. Active Response Safety
The `active_response_router` is configured with `"human approval required": true` by default. 

> [!WARNING]
> DO NOT disable human approval in production unless you have verified the AI classification accuracy for at least 30 days.

---
*Created as part of the ACIP Professional SOC Refining Process.*
