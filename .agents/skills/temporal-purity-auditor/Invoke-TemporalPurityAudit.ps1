<#
.SYNOPSIS
    Temporal & Title Purity Auditor - automated pre-1960 archival dossier audit.
.DESCRIPTION
    Executes the four directives of the temporal-purity-auditor skill silently:
      1. Segregates post-1960 survey records into "modern_addendum".
      2. Flags/strips structures built after 1949 (built_year >= 1950).
      3. Applies CA State Plane Zone VI (EPSG:2227) mathematical offset corrections
         to Orange County plat coordinates (offsets from zone_vi_offsets.json).
      4. Zero prompting - non-interactive, batch safe.
    Emits purity_audit.json conforming to the skill's Output Schema.
.PARAMETER DossierPath
    Path to the dossier JSON file (object with "records" array, or a bare array).
.PARAMETER OutDir
    Directory for purity_audit.json. Defaults to the dossier's directory.
.PARAMETER DossierId
    Optional dossier identifier. Defaults to the dossier file base name.
.PARAMETER OffsetConfig
    Optional path to zone_vi_offsets.json. Defaults to a file beside this script.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File Invoke-TemporalPurityAudit.ps1 -DossierPath C:\case\dossier.json
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$DossierPath,

    [string]$OutDir,

    [string]$DossierId,

    [string]$OffsetConfig
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path -LiteralPath $DossierPath)) {
    Write-Error "Dossier not found: $DossierPath"
    exit 2
}
if (-not $OutDir) { $OutDir = Split-Path -Parent (Resolve-Path -LiteralPath $DossierPath) }
if (-not $DossierId) { $DossierId = [IO.Path]::GetFileNameWithoutExtension($DossierPath) }
if (-not $OffsetConfig) { $OffsetConfig = Join-Path $scriptDir 'zone_vi_offsets.json' }

# --- Zone VI offsets (feet). Applied as: corrected = original + offset ---
$offsetX = 0.0
$offsetY = 0.0
if (Test-Path -LiteralPath $OffsetConfig) {
    $cfg = Get-Content -LiteralPath $OffsetConfig -Raw | ConvertFrom-Json
    if ($null -ne $cfg.offset_x_ft) { $offsetX = [double]$cfg.offset_x_ft }
    if ($null -ne $cfg.offset_y_ft) { $offsetY = [double]$cfg.offset_y_ft }
    Write-Verbose "Loaded offsets: X=$offsetX ft, Y=$offsetY ft"
} else {
    Write-Warning "Offset config not found ($OffsetConfig) - using zero offsets."
}

# --- Load dossier (tolerant of wrapper objects) ---
$raw = Get-Content -LiteralPath $DossierPath -Raw
$doc = $raw | ConvertFrom-Json
$records = @()
if ($doc -is [Array]) { $records = $doc }
elseif ($doc.records) { $records = @($doc.records) }
elseif ($doc.dossier -and $doc.dossier.records) { $records = @($doc.dossier.records) }
elseif ($doc.PSObject.Properties.Name -contains 'items') { $records = @($doc.items) }
else {
    Write-Error "Unrecognized dossier structure: expected array or object with 'records'."
    exit 3
}

$modern = @()
$structures = @()
$corrections = @()
$kept = 0

foreach ($r in $records) {
    $kind = ''
    if ($r.PSObject.Properties.Name -contains 'kind') { $kind = [string]$r.kind }
    elseif ($r.PSObject.Properties.Name -contains 'type') { $kind = [string]$r.type }

    # --- Directive 3: plat coordinate correction (Zone VI) ---
    if (($r.PSObject.Properties.Name -contains 'easting') -and ($r.PSObject.Properties.Name -contains 'northing')) {
        $oe = [double]$r.easting
        $on = [double]$r.northing
        $ce = [math]::Round($oe + $offsetX, 4)
        $cn = [math]::Round($on + $offsetY, 4)
        $platId = $DossierId
        if ($r.PSObject.Properties.Name -contains 'plat_id') { $platId = [string]$r.plat_id }
        elseif ($r.PSObject.Properties.Name -contains 'record_id') { $platId = [string]$r.record_id }
        $corrections += [ordered]@{
            plat_id            = $platId
            original_easting   = $oe
            original_northing  = $on
            corrected_easting  = $ce
            corrected_northing = $cn
            offset_x_ft        = $offsetX
            offset_y_ft        = $offsetY
            grid_system        = 'CA_State_Plane_Zone_VI_ft_US'
            datum              = 'NAD83'
        }
    }

    # --- Directive 1: modern survey segregation (post-1960) ---
    $dateVal = $null
    foreach ($f in @('survey_date', 'date', 'recorded_date', 'record_date', 'filed_date')) {
        if ($r.PSObject.Properties.Name -contains $f -and $r.$f) {
            try { $dateVal = [datetime]::Parse([string]$r.$f) } catch { $dateVal = $null }
            break
        }
    }
    $isSurvey = ($kind -match 'survey') -or ($null -ne $dateVal -and $kind -notmatch 'structure|building|parcel')
    if ($isSurvey -and $dateVal -and $dateVal -gt [datetime]'1960-12-31') {
        $rid = $DossierId
        if ($r.PSObject.Properties.Name -contains 'record_id') { $rid = [string]$r.record_id }
        elseif ($r.PSObject.Properties.Name -contains 'id') { $rid = [string]$r.id }
        $modern += [ordered]@{
            record_id    = $rid
            survey_date  = $dateVal.ToString('yyyy-MM-dd')
            source       = if ($r.PSObject.Properties.Name -contains 'source') { [string]$r.source } else { 'unspecified' }
            reason       = 'post_1960_survey'
        }
        continue
    }

    # --- Directive 2: post-1949 structure filtering (built >= 1950) ---
    $builtYear = $null
    foreach ($f in @('built_year', 'year_built', 'construction_year', 'year')) {
        if ($r.PSObject.Properties.Name -contains $f -and $r.$f) {
            try { $builtYear = [int]$r.$f } catch { $builtYear = $null }
            break
        }
    }
    $isStructure = ($kind -match 'structure|building') -or ($null -ne $builtYear)
    if ($isStructure -and $null -ne $builtYear -and $builtYear -ge 1950) {
        $pid_ = $DossierId
        if ($r.PSObject.Properties.Name -contains 'parcel_id') { $pid_ = [string]$r.parcel_id }
        elseif ($r.PSObject.Properties.Name -contains 'record_id') { $pid_ = [string]$r.record_id }
        $structures += [ordered]@{
            parcel_id  = $pid_
            built_year = $builtYear
            action     = 'flagged'
            reason     = 'post_1949_structure'
        }
        continue
    }

    $kept++
}

# --- Verdict ---
$contaminated = $false
$hasAddendum = ($modern.Count -gt 0) -or ($structures.Count -gt 0) -or ($corrections.Count -gt 0)
if ($modern.Count -gt 0 -and $kept -eq 0) { $contaminated = $true }
if ($structures.Count -gt 0 -and $kept -eq 0) { $contaminated = $true }

if ($contaminated) { $verdict = 'CONTAMINATED' }
elseif ($hasAddendum) { $verdict = 'PURE_WITH_ADDENDUM' }
else { $verdict = 'PURE' }

$audit = [ordered]@{
    audit_timestamp    = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    dossier_id         = $DossierId
    modern_addendum    = [ordered]@{ count = $modern.Count; records = $modern }
    post_1949_flags    = [ordered]@{ count = $structures.Count; structures = $structures }
    zone_vi_corrections = [ordered]@{ count = $corrections.Count; corrections = $corrections }
    verdict            = $verdict
    kept_records       = $kept
}

if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$outFile = Join-Path $OutDir 'purity_audit.json'
$audit | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outFile -Encoding UTF8

Write-Output "AUDIT COMPLETE: $verdict"
Write-Output "  modern surveys segregated : $($modern.Count)"
Write-Output "  post-1949 structures     : $($structures.Count)"
Write-Output "  Zone VI corrections       : $($corrections.Count)"
Write-Output "  clean records retained    : $kept"
Write-Output "  output                    : $outFile"

if ($verdict -eq 'CONTAMINATED') { exit 1 }
exit 0
