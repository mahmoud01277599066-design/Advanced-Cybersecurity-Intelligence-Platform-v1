@echo off
set SOC_ENDPOINT=%1
if "%SOC_ENDPOINT%"=="" set SOC_ENDPOINT=http://127.0.0.1:8080/api/v1/soc/ingest

echo Starting ACIP real-time monitor...
echo Endpoint: %SOC_ENDPOINT%
python modules\soc_defense\integrations\real_time_monitor.py --endpoint %SOC_ENDPOINT%
