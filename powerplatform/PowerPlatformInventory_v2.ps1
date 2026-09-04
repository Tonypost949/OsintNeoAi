<#
.SYNOPSIS
Enterprise Power Platform Inventory & Capability Discovery Tool

.DESCRIPTION
Dynamically discovers installed PAC CLI capabilities, handles authentication,
selects the target environment, runs supported solution/application/org inventory
commands, and exports structured JSON, CSV, and text reports with retry logic and full transcript logging.

.PARAMETER EnvironmentId
The target Power Platform Environment ID or URL.

.PARAMETER DryRun
Switch to simulate command execution without running mutating commands.

.PARAMETER MaxRetries
Maximum retry attempts for network/API calls (default: 3).

.EXAMPLE
.\PowerPlatformInventory_v2.ps1 -EnvironmentId "bd81f293-c879-f111-b27b-6045bd003333"
#>

[CmdletBinding()]
param(
    [string]$EnvironmentId = "bd81f293-c879-f111-b27b-6045bd003333",
    [switch]$DryRun,
    [int]$MaxRetries = 3
)

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------------
# Output & Transcript Setup
# ------------------------------------------------------------------
$OutputFolder = Join-Path $PSScriptRoot "Output"
New-Item -ItemType Directory -Force -Path $OutputFolder | Out-Null

$LogFile = Join-Path $OutputFolder "run.log"
$TranscriptFile = Join-Path $OutputFolder "transcript.log"

try { Stop-Transcript -ErrorAction SilentlyContinue } catch {}
Start-Transcript -Path $TranscriptFile -Force

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $Entry = "{0} [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Message
    Write-Host $Entry
    Add-Content -Path $LogFile -Value $Entry
}

function Invoke-WithRetry {
    param(
        [scriptblock]$Script,
        [string]$Operation
    )

    $Attempt = 1
    while ($Attempt -le $MaxRetries) {
        try {
            Write-Log "$Operation (Attempt $Attempt/$MaxRetries)"
            return & $Script
        }
        catch {
            Write-Log "$Operation failed: $_" "WARN"
            if ($Attempt -eq $MaxRetries) {
                throw
            }
            Start-Sleep -Seconds 3
            $Attempt++
        }
    }
}

function Invoke-Pac {
    param(
        [string]$Command
    )

    if ($DryRun) {
        Write-Log "[DRY RUN] pac $Command"
        return $null
    }

    Write-Log "Executing: pac $Command"
    $result = Invoke-Expression "pac $Command"
    return $result
}

function Export-StructuredData {
    param(
        $Object,
        [string]$Name
    )

    if ($null -eq $Object) { return }

    $JsonPath = Join-Path $OutputFolder "$Name.json"
    $CsvPath = Join-Path $OutputFolder "$Name.csv"

    # Export Raw Text / Standard Output
    $Object | Out-File (Join-Path $OutputFolder "$Name.txt") -Force

    # Try Converting to Structured JSON/CSV if object or valid JSON string
    try {
        if ($Object -is [string]) {
            $Parsed = $Object | ConvertFrom-Json -ErrorAction Stop
            $Parsed | ConvertTo-Json -Depth 20 | Out-File $JsonPath -Force
            $Parsed | Export-Csv $CsvPath -NoTypeInformation -ErrorAction SilentlyContinue
        } else {
            $Object | ConvertTo-Json -Depth 20 | Out-File $JsonPath -Force
            $Object | Export-Csv $CsvPath -NoTypeInformation -ErrorAction SilentlyContinue
        }
        Write-Log "Successfully exported structured data for $Name"
    } catch {
        Write-Log "Saved text output for $Name (Non-JSON stream)"
    }
}

# ------------------------------------------------------------------
# 1. Validate PAC CLI Installation
# ------------------------------------------------------------------
Write-Log "Validating Power Platform CLI (pac)"

try {
    $Version = pac version
    Write-Log "PAC CLI Installed Version: $Version"
} catch {
    Write-Log "PAC CLI is not installed or not available on PATH." "ERROR"
    Stop-Transcript
    exit 1
}

# ------------------------------------------------------------------
# 2. Authentication Check
# ------------------------------------------------------------------
Write-Log "Checking active PAC authentication profile..."

try {
    $Who = pac auth who 2>&1
    Write-Log "Authenticated profile active."
    $Who | Out-File (Join-Path $OutputFolder "AuthWho.txt")
} catch {
    Write-Log "No active PAC profile found. Triggering interactive auth..." "WARN"
    if (-not $DryRun) {
        pac auth create
    }
}

# ------------------------------------------------------------------
# 3. Environment Selection & Verification
# ------------------------------------------------------------------
if ($EnvironmentId) {
    try {
        Invoke-WithRetry {
            Invoke-Pac "env select --environment $EnvironmentId"
        } "Selecting Environment $EnvironmentId"
    } catch {
        Write-Log "Could not select environment $EnvironmentId. Proceeding with current profile." "WARN"
    }
}

# ------------------------------------------------------------------
# 4. Capability Discovery (Dynamic Help Scan)
# ------------------------------------------------------------------
Write-Log "Discovering installed PAC CLI command capabilities..."

$HelpText = pac help 2>&1
$HelpText | Out-File (Join-Path $OutputFolder "PacHelp.txt") -Force

$HasApplicationGroup = ($HelpText -match "application")
$HasSolutionGroup = ($HelpText -match "solution")
$HasAdminGroup = ($HelpText -match "admin")
$HasOrgGroup = ($HelpText -match "org")

Write-Log "Capability Scan Summary: [application: $HasApplicationGroup] [solution: $HasSolutionGroup] [admin: $HasAdminGroup] [org: $HasOrgGroup]"

# ------------------------------------------------------------------
# 5. Organization Details & User Permissions Verification
# ------------------------------------------------------------------
if ($HasOrgGroup) {
    try {
        $OrgWho = Invoke-WithRetry { Invoke-Pac "org who" } "Retrieve Org Who Details"
        Export-StructuredData -Object $OrgWho -Name "OrgWho"
    } catch {
        Write-Log "Unable to retrieve org details. User may lack Dataverse permissions." "WARN"
    }
}

# ------------------------------------------------------------------
# 6. Solutions Inventory
# ------------------------------------------------------------------
if ($HasSolutionGroup) {
    try {
        Write-Log "Querying installed solutions..."
        $Solutions = Invoke-WithRetry { Invoke-Pac "solution list" } "List Solutions"
        Export-StructuredData -Object $Solutions -Name "Solutions"
    } catch {
        Write-Log "Solution list failed. Check if user holds Dataverse System Customizer / System Administrator role." "WARN"
    }
}

# ------------------------------------------------------------------
# 7. Applications Inventory (Dynamic Check)
# ------------------------------------------------------------------
if ($HasApplicationGroup) {
    try {
        Write-Log "Querying installed environment applications..."
        $Apps = Invoke-WithRetry { Invoke-Pac "application list" } "List Applications"
        Export-StructuredData -Object $Apps -Name "Applications"
    } catch {
        Write-Log "Application list unavailable or not supported in current environment scope." "WARN"
    }
}

# ------------------------------------------------------------------
# 8. Profile & Environment Export
# ------------------------------------------------------------------
try {
    $AuthList = pac auth list 2>&1
    Export-StructuredData -Object $AuthList -Name "AuthProfiles"

    $EnvList = pac env list 2>&1
    Export-StructuredData -Object $EnvList -Name "Environments"
} catch {
    Write-Log "Failed to export profile list." "WARN"
}

Write-Log "Inventory and capability scan completed successfully!"
Stop-Transcript
