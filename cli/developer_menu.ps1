function Show-DeveloperMenu {
    param([string[]]$ScriptArgs)
    Clear-Host
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "     OSINTNEOAI DEVELOPER CLI LAUNCHER   " -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  PRIMARY AI & AGENT CLIs:" -ForegroundColor Yellow
    Write-Host "   [1]  Antigravity (agy)"
    Write-Host "   [2]  OpenCode Pentest (Kali WSL + Auto-Installer)"
    Write-Host "   [3]  Gemini CLI (gemini)"
    Write-Host "   [4]  OSINTNEOAI Master Intelligence (osintneoai)"
    Write-Host "   [5]  Standard OpenCode (opencode)"
    Write-Host "   [6]  GitHub Copilot (gh copilot)"
    Write-Host "   [7]  Ollama (ollama)"
    Write-Host ""
    Write-Host "  DEVELOPMENT & RUNTIMES:" -ForegroundColor Yellow
    Write-Host "   [8]  Python 3 (python)"
    Write-Host "   [9]  Git (git)"
    Write-Host "   [10] VS Code (code .)"
    Write-Host "   [Q]  Quit / Cancel"
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""

    $choice = Read-Host "Select a CLI tool to launch [1-10, Q]"
    switch ($choice.ToString().Trim()) {
        "1" { agy $ScriptArgs }
        "2" {
            $tool_prompt = Read-Host "Paste target prompt, code snippet, or tool request"
            wsl -d kali-linux -- opencode-pentest "$tool_prompt"
        }
        "3" { gemini $ScriptArgs }
        "4" {
            python C:\OsintNeoAi\cli\cli.py report
            python C:\OsintNeoAi\cli\cli.py chat
        }
        "5" { opencode $ScriptArgs }
        "6" { gh copilot suggest }
        "7" { ollama run qwen2.5-coder:7b }
        "8" { python }
        "9" { git $ScriptArgs }
        "10" { code C:\OsintNeoAi }
        "Q" { return }
        "q" { return }
        Default { Write-Host "Invalid selection." -ForegroundColor Red }
    }
}

Set-Alias -Name cli -Value Show-DeveloperMenu -Option AllScope -Force -ErrorAction SilentlyContinue
Set-Alias -Name launch -Value Show-DeveloperMenu -Option AllScope -Force -ErrorAction SilentlyContinue
