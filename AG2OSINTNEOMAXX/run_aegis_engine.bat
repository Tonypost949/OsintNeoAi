@echo off
title AEGIS CONTINUOUS OSINT CORRELATION ENGINE
echo ==========================================================
echo STARTING AEGIS THREAT MODEL IN CONTINUOUS DAEMON MODE
echo ==========================================================
echo [INFO] Press Ctrl+C at any time to exit the background loop.
echo [INFO] Polling cycle: every 60 seconds.
echo ==========================================================
python aegis_correlation_engine.py --daemon
pause
