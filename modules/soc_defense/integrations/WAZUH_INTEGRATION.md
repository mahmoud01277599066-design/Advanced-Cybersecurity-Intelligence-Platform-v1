# Wazuh -> ACIP SOC Integration (Quick Setup)

This setup forwards real Wazuh alerts to ACIP SOC API in real-time.

## 1) Ensure APIs are running
- DevSecOps API: `http://127.0.0.1:8000`
- SOC API: `http://127.0.0.1:8001`

## 2) Place forwarder script on Wazuh manager
Copy this file to your Wazuh integrations scripts path:
- `modules/soc_defense/integrations/wazuh_forwarder.py`

Typical path on Wazuh manager:
- `/var/ossec/integrations/custom-acip-soc.py`

Make executable:
```bash
chmod +x /var/ossec/integrations/custom-acip-soc.py
```

## 3) Add integration block in `ossec.conf`
Use this block inside `<ossec_config>`:

```xml
<integration>
  <name>custom-acip-soc</name>
  <hook_url>http://127.0.0.1:8001/api/v1/soc/ingest</hook_url>
  <level>3</level>
  <alert_format>json</alert_format>
</integration>
```

If you use script mode instead of `hook_url`, configure custom integration execution according to your Wazuh version, and call the script with the alert json file.

## 4) Restart Wazuh manager
```bash
systemctl restart wazuh-manager
```

## 5) Verify in ACIP
- SOC list endpoint: `GET http://127.0.0.1:8001/api/v1/soc/alerts`
- SOC dashboard: `http://127.0.0.1:8001/dashboard`
- DevSecOps received alerts: `GET http://127.0.0.1:8000/api/v1/soc/alerts`
