@echo off
TITLE OSINT NeoAI PSA Launcher
echo ========================================================
echo Starting OSINT NeoAI PSA System...
echo ========================================================

REM Ensure Node.js and Python are in PATH
set PATH=%PATH%;C:\Program Files\nodejs\;C:\Users\Amd949609\AppData\Roaming\npm

echo Checking Python environment...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo Launching OSINT NeoAI PSA Server on http://localhost:8080 ...
start "" http://localhost:8080
python C:\OsintNeoAi\osint_psa_server.py
pause
