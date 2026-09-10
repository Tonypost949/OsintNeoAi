@echo off
title OsintNeoAI Local Toolkit
color 0A
cls
echo ============================================================
echo   OsintNeoAI LOCAL OSINT TOOLKIT
echo   All tools running on your PC - no cloud needed
echo ============================================================
echo.
echo  [1] Full Domain Recon (DNS + WHOIS + SSL + Ports + Shodan)
echo  [2] Port Scanner (TCP connect scan)
echo  [3] WiFi Network Scanner
echo  [4] Bluetooth Device Scanner
echo  [5] Username OSINT (check 30+ platforms)
echo  [6] Email OSINT (MX + validation + social)
echo  [7] IP Reputation (AbuseIPDB + Shodan + GeoIP)
echo  [8] Phone Number OSINT
echo  [9] SSL Certificate Analyzer
echo [10] Subdomain Enumerator
echo [11] Technology Fingerprint (web)
echo [12] AI Analysis (ask Ollama anything)
echo [13] SpiderFoot Web UI (if available)
echo [14] Kali Tools (via WSL)
echo [15] OSINT Scripts (your 145 scripts)
echo  [0] Exit
echo.
echo ============================================================
set /p choice="Select tool (0-15): "

if "%choice%"=="1" goto recon
if "%choice%"=="2" goto portscan
if "%choice%"=="3" goto wifi
if "%choice%"=="4" goto bluetooth
if "%choice%"=="5" goto username
if "%choice%"=="6" goto email
if "%choice%"=="7" goto iprep
if "%choice%"=="8" goto phone
if "%choice%"=="9" goto ssl
if "%choice%"=="10" goto subdomain
if "%choice%"=="11" goto tech
if "%choice%"=="12" goto ai
if "%choice%"=="13" goto spiderfoot
if "%choice%"=="14" goto kali
if "%choice%"=="15" goto scripts
if "%choice%"=="0" exit
goto :eof

:recon
set /p target="Enter domain: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import recon; import json; print(json.dumps(recon('%target%'), indent=2, default=str))"
pause
goto :eof

:portscan
set /p target="Enter IP/hostname: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import port_scan; import json; print(json.dumps(port_scan('%target%'), indent=2))"
pause
goto :eof

:wifi
netsh wlan show networks mode=bssid
pause
goto :eof

:bluetooth
powershell -Command "Get-PnpDevice -Class Bluetooth | Select-Object Name,Status | Format-Table -AutoSize"
pause
goto :eof

:username
set /p target="Enter username: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import username_check; import json; print(json.dumps(username_check('%target%'), indent=2))"
pause
goto :eof

:email
set /p target="Enter email: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import email_check; import json; print(json.dumps(email_check('%target%'), indent=2))"
pause
goto :eof

:iprep
set /p target="Enter IP: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import ip_reputation; import json; print(json.dumps(ip_reputation('%target%'), indent=2))"
pause
goto :eof

:phone
set /p target="Enter phone number: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import phone_lookup; import json; print(json.dumps(phone_lookup('%target%'), indent=2))"
pause
goto :eof

:ssl
set /p target="Enter domain: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import ssl_check, cert_transparency; import json; print(json.dumps(ssl_check('%target%'), indent=2)); print(json.dumps(cert_transparency('%target%'), indent=2))"
pause
goto :eof

:subdomain
set /p target="Enter domain: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import subdomain_enum; import json; print(json.dumps(subdomain_enum('%target%'), indent=2))"
pause
goto :eof

:tech
set /p target="Enter URL: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import technology_fingerprint, http_headers; import json; print(json.dumps(http_headers('%target%'), indent=2)); print(json.dumps(technology_fingerprint('%target%'), indent=2))"
pause
goto :eof

:ai
set /p target="Ask AI anything: "
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "from osint_bridge import query_ollama; print(query_ollama('%target%'))"
pause
goto :eof

:spiderfoot
echo Starting SpiderFoot...
"C:\Users\Amd949609\AppData\Local\Python\bin\python.exe" -c "import spiderfoot; print('SpiderFoot module found')" 2>nul
if %errorlevel%==0 (
    echo SpiderFoot module available
    echo Access web UI at http://localhost:5001
) else (
    echo SpiderFoot not fully installed
    echo Use the local OSINT bridge instead
)
pause
goto :eof

:kali
echo Opening Kali Tools via WSL...
echo Available: nmap, whois, theHarvester, nikto
echo.
set /p target="Enter command (e.g. nmap -sV 192.168.1.1): "
wsl -d kali-linux -- %target%
pause
goto :eof

:scripts
echo Opening OSINT Scripts folder...
explorer "C:\Users\Amd949609\osint_scripts"
pause
goto :eof
