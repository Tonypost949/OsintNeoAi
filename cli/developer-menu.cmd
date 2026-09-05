@echo off
setlocal enabledelayedexpansion
cls
echo =================================================
echo      OSINTNEOAI DEVELOPER CLI LAUNCHER (WINDOWS)
echo =================================================
echo   PRIMARY AI ^& AGENT CLIs:
echo    [1]  Antigravity (agy)
echo    [2]  OpenCode Pentest (Kali WSL + Auto-Installer)
echo    [3]  Gemini CLI (gemini)
echo    [4]  OSINTNEOAI Master Intelligence (osintneoai)
echo    [5]  Standard OpenCode (opencode)
echo    [6]  GitHub Copilot (gh copilot)
echo    [7]  Ollama (ollama)
echo.
echo   DEVELOPMENT ^& RUNTIMES:
echo    [8]  Python 3 (python)
echo    [9]  Git (git)
echo    [10] VS Code (code .)
echo    [Q]  Quit / Cancel
echo =================================================
echo.

set /p choice="Select a CLI tool to launch [1-10, Q]: "

if /i "%choice%"=="1" (
    agy %*
    goto end
)
if /i "%choice%"=="2" (
    set /p tool_prompt="Paste target prompt, code snippet, or tool request: "
    wsl -d kali-linux -- opencode-pentest "!tool_prompt!"
    goto end
)
if /i "%choice%"=="3" (
    gemini %*
    goto end
)
if /i "%choice%"=="4" (
    python C:\OsintNeoAi\cli\cli.py report
    python C:\OsintNeoAi\cli\cli.py chat
    goto end
)
if /i "%choice%"=="5" (
    opencode %*
    goto end
)
if /i "%choice%"=="6" (
    gh copilot suggest
    goto end
)
if /i "%choice%"=="7" (
    ollama run qwen2.5-coder:7b
    goto end
)
if /i "%choice%"=="8" (
    python
    goto end
)
if /i "%choice%"=="9" (
    git %*
    goto end
)
if /i "%choice%"=="10" (
    code C:\OsintNeoAi
    goto end
)
if /i "%choice%"=="Q" exit /b 0

:end
