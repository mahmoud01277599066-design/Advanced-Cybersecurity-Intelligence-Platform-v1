@echo off
echo ========================================================
echo Starting ACIP Live SOC Environment...
echo ========================================================
set PYTHONPATH=%cd%
python modules\soc_defense\scenarios\master_soc_pipeline.py
pause
