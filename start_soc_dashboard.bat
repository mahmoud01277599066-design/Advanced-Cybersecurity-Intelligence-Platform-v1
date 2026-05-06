@echo off
echo ========================================================
echo Starting ACIP SOC Dynamic Dashboard...
echo ========================================================
set PYTHONPATH=%cd%
python -m uvicorn modules.soc_defense.main:app --host 127.0.0.1 --port 8080 --reload
pause
