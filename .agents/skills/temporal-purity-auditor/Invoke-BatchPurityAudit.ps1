<#
.SYNOPSIS
    Scheduled wrapper: auto-audit all dossier JSON files in the watch folder.
.DESCRIPTION
    Scans the watch folder for *.json dossiers (excluding purity_audit.json and
    files already audited), runs Invoke-TemporalPurityAudit.ps1 on each, writes
    results to the audits folder, and appends to batch_audit_log.jsonl.
    Non-interactive, batch safe (Law 13). Never blocks, never prompts.
#>
[CmdletBinding()]
param(
    [string]$WatchDir = 'C:\Amd949609_Antigravity_v1\dossiers\incoming',
    [string]$AuditDir = 'C:\Amd949609_Antigravity_v1\dossiers\audits',
    [string]$StateFile = 'C:\Amd949609_Antigravity_v1\dossiers\audit_state.json'
)

$ErrorActionPreference = 'Continue'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$auditor = Join-Path $scriptDir 'Invoke-TemporalPurityAudit.ps1'
$logFile = Join-Path $AuditDir 'batch_audit_log.jsonl'

if (-not (Test-Path -LiteralPath $WatchDir)) { New-Item -ItemType Directory -Force -Path $WatchDir | Out-Null; exit 0 }
if (-not (Test-Path -LiteralPath $AuditDir)) { New-Item -ItemType Directory -Force -Path $AuditDir | Out-Null }

$state = @{}
if (Test-Path -LiteralPath $StateFile) {
    try {
        $prev = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
        $prev.PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value }
    } catch { $state = @{} }
}

$files = Get-ChildItem -LiteralPath $WatchDir -Filter '*.json' -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne 'purity_audit.json' -and $_.Name -ne 'audit_state.json' }

$audited = 0
foreach ($f in $files) {
    $sig = "$($f.Name)|$($f.Length)|$($f.LastWriteTimeUtc.Ticks)"
    if ($state[$f.FullName] -eq $sig) { continue }

    $out = Join-Path $AuditDir $f.BaseName
    & powershell -ExecutionPolicy Bypass -File $auditor -DossierPath $f.FullName -OutDir $out -DossierId $f.BaseName | Out-Null
    $code = $LASTEXITCODE

    $verdict = 'UNKNOWN'
    $pf = Join-Path $out 'purity_audit.json'
    if (Test-Path -LiteralPath $pf) {
        try { $verdict = (Get-Content -LiteralPath $pf -Raw | ConvertFrom-Json).verdict } catch { }
    }

    $entry = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        dossier   = $f.FullName
        verdict   = $verdict
        exit_code = $code
        audit_out = $pf
    }
    Add-Content -LiteralPath $logFile -Value (($entry | ConvertTo-Json -Compress)) -Encoding UTF8

    $state[$f.FullName] = $sig
    $audited++
}

$state | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StateFile -Encoding UTF8
Write-Output "batch audit done: $audited dossier(s) processed"
exit 0
