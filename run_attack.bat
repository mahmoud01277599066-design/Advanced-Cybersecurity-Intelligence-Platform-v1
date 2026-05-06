@echo off
echo ========================================================
echo Executing Threat Simulation (SQL Injection)
echo ========================================================
set PYTHONPATH=%cd%
python threat_sim\sql_attacker.py
pause
