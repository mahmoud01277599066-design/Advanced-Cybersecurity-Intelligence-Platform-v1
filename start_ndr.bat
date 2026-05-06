@echo off
echo ========================================================
echo Starting ACIP Live NDR Anomaly Detection Environment...
echo ========================================================
set PYTHONPATH=%cd%
python modules\soc_defense\scenarios\master_pcap_pipeline.py
pause
