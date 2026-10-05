<#
.SYNOPSIS
    Corpus runner: normalizes every dossier (MD/JSON) into audit records and
    runs Invoke-TemporalPurityAudit.ps1 on each, non-interactively.
.DESCRIPTION
    - Scans primary locations for *dossier*.{md,json} (skips backups, worktrees,
      mirrors, and .bak files).
    - Extracts audit-relevant records via heuristic normalization:
        * surveys   -> "survey" + date, or survey_date/date fields
        * structures-> "built|constructed" + year, or built_year/year fields
        * plats     -> easting/northing coordinate pairs (JSON only)
        * plain text dates post-1960 -> modern record candidates
    - Writes normalized records to staging, runs the purity auditor, and appends
      verdicts to corpus_audit_log.jsonl.
    Zero prompting; batch safe; reversible (staging only, sources untouched).
#>
[CmdletBinding()]
param(
    [string[]]$Roots = @('C:\OsintNeoAi', 'C:\Amd949609_Antigravity_v1'),
    [string]$StagingDir = 'C:\Amd949609_Antigravity_v1\dossiers\incoming',
    [string]$ReportDir = 'C:\Amd949609_Antigravity_v1\dossiers\corpus'
)

$ErrorActionPreference = 'Continue'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$auditor = Join-Path $scriptDir 'Invoke-TemporalPurityAudit.ps1'
$logFile = Join-Path $ReportDir 'corpus_audit_log.jsonl'

New-Item -ItemType Directory -Force -Path $StagingDir, $ReportDir | Out-Null

$excludeDirs = 'backup_repo', 'copilot-worktrees', 'gdrive_shared_export', 'tasklet_export', 'ai_sync_vault', 'dossiers\audits', 'dossiers\corpus', 'dossiers\incoming', 'public\evidence\full_downloads_hartest'

function Get-DossierFiles {
    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Name -match 'dossier' -and ($_.Extension -eq '.md' -or $_.Extension -eq '.json') -and
                $_.Name -notmatch '\.bak|\.pre_|_backup' -and
                ($_.FullName -notmatch '\\\.backup_repo\\|\\copilot-worktrees\\|\\gdrive_shared_export\\|\\tasklet_export\\|\\ai_sync_vault\\|\\dossiers\\')
            }
    }
}

function ConvertTo-AuditRecords {
    param([string]$Path)
    $records = New-Object System.Collections.Generic.List[object]
    $ext = [IO.Path]::GetExtension($Path).ToLower()

    if ($ext -eq '.json') {
        try { $doc = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json } catch { return $null }
        $i = 0
        function Walk($node) {
            if ($null -eq $node) { return }
            if ($node -is [Array]) { foreach ($n in $node) { Walk $n }; return }
            if ($node -isnot [PSObject]) { return }
            $props = $node.PSObject.Properties.Name
            $rec = $null
            $surveyDate = $null
            foreach ($f in @('survey_date', 'date', 'recorded_date', 'record_date', 'filed_date', 'extracted_at', 'incident_date')) {
                if ($props -contains $f -and $node.$f) {
                    try { $surveyDate = ([datetime]::Parse([string]$node.$f)).ToString('yyyy-MM-dd') } catch { }
                    break
                }
            }
            $builtYear = $null
            foreach ($f in @('built_year', 'year_built', 'construction_year')) {
                if ($props -contains $f -and $node.$f) { try { $builtYear = [int]$node.$f } catch { }; break }
            }
            $hasCoords = ($props -contains 'easting') -and ($props -contains 'northing')
            if ($surveyDate -or $builtYear -or $hasCoords) {
                $script:seq++
                $rec = [ordered]@{
                    record_id = if ($props -contains 'record_id') { [string]$node.record_id } else { "R-$($script:seq)" }
                }
                if ($hasCoords) {
                    $rec.kind = 'plat'
                    $rec.easting = [double]$node.easting
                    $rec.northing = [double]$node.northing
                    if ($props -contains 'plat_id') { $rec.plat_id = [string]$node.plat_id }
                }
                if ($builtYear) {
                    $rec.kind = 'structure'
                    $rec.built_year = $builtYear
                    if ($props -contains 'parcel_id') { $rec.parcel_id = [string]$node.parcel_id }
                }
                if ($surveyDate) {
                    if (-not $rec.kind) { $rec.kind = 'survey' }
                    $rec.survey_date = $surveyDate
                    if ($props -contains 'source') { $rec.source = [string]$node.source }
                }
                $records.Add([pscustomobject]$rec)
            }
            foreach ($p in $node.PSObject.Properties) {
                if ($p.Value -is [Array] -or ($p.Value -is [PSObject] -and $p.Value -isnot [string])) { Walk $p.Value }
            }
        }
        $script:seq = 0
        Walk $doc
        return $records
    }

    # Markdown: heuristic line extraction
    $lines = Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue
    $n = 0
    foreach ($line in $lines) {
        $n++
        $rec = $null
        if ($line -match '(?i)\bsurvey\b.*\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|(?:1[5-9]\d{2}|20[0-2]\d))\b') {
            $raw = $Matches[1]
            $dt = $null
            try { $dt = [datetime]::Parse($raw) } catch { try { $dt = [datetime]::ParseExact($raw, 'yyyy', $null) } catch { $dt = $null } }
            if ($dt -and $dt.Year -ge 1500 -and $dt.Year -le (Get-Date).Year) {
                $rec = [ordered]@{ record_id = "L$n"; kind = 'survey'; survey_date = $dt.ToString('yyyy-MM-dd'); source = [IO.Path]::GetFileName($Path) }
            }
        }
        elseif ($line -match '(?i)\b(?:built|constructed|erected|built in)\b.*\b(1[6-9]\d{2}|20[0-3]\d)\b') {
            $by = [int]$Matches[1]
            if ($by -ge 1600 -and $by -le (Get-Date).Year) {
                $rec = [ordered]@{ record_id = "L$n"; kind = 'structure'; built_year = $by }
            }
        }
        elseif ($line -match '(?i)\bstructure.*\b(?:19(?:5\d|6\d|7\d|8\d|9\d)|20\d\d)\b|\b(?:19[5-9]\d|20\d\d)\s+(?:structure|building|residence|home)\b') {
            if ($line -match '\b(1[6-9]\d{2}|20[0-3]\d)\b') {
                $by = [int]$Matches[1]
                if ($by -ge 1600 -and $by -le (Get-Date).Year) {
                    $rec = [ordered]@{ record_id = "L$n"; kind = 'structure'; built_year = $by }
                }
            }
        }
        if ($rec) { $records.Add([pscustomobject]$rec) }
    }
    return $records
}

$files = @(Get-DossierFiles)
$summary = @()
$idx = 0
foreach ($f in $files) {
    $idx++
    $recs = ConvertTo-AuditRecords -Path $f.FullName
    $verdict = 'NO_RECORDS'
    $staged = $null
    if ($null -ne $recs -and $recs.Count -gt 0) {
        $staged = Join-Path $StagingDir ("corpus_" + $f.BaseName + "_" + [IO.Path]::GetFileName($f.DirectoryName) + ".json")
        [pscustomobject]@{ records = @($recs) } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $staged -Encoding UTF8
        $out = Join-Path $ReportDir ([IO.Path]::GetFileNameWithoutExtension($staged))
        & powershell -ExecutionPolicy Bypass -File $auditor -DossierPath $staged -OutDir $out -DossierId ([IO.Path]::GetFileNameWithoutExtension($staged)) | Out-Null
        $pf = Join-Path $out 'purity_audit.json'
        if (Test-Path -LiteralPath $pf) {
            try { $verdict = (Get-Content -LiteralPath $pf -Raw | ConvertFrom-Json).verdict } catch { $verdict = 'ERROR' }
        } else { $verdict = 'ERROR' }
        Remove-Item -LiteralPath $staged -Force -ErrorAction SilentlyContinue
    }
    $entry = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        dossier   = $f.FullName
        records   = if ($null -ne $recs) { $recs.Count } else { 0 }
        verdict   = $verdict
    }
    Add-Content -LiteralPath $logFile -Value ($entry | ConvertTo-Json -Compress) -Encoding UTF8
    $summary += [pscustomobject]$entry
    Write-Output "[$idx/$($files.Count)] $verdict  $($f.FullName)"
}

Write-Output ""
Write-Output "=== CORPUS AUDIT SUMMARY ==="
$summary | Group-Object verdict | Sort-Object Name | ForEach-Object { Write-Output ("  {0,-22} {1}" -f $_.Name, $_.Count) }
Write-Output "log: $logFile"
exit 0
