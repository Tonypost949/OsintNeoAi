<#
.SYNOPSIS
Power Platform Inventory Script

.DESCRIPTION
Authenticates to PAC, selects the target Power Platform environment, logs all operations,
and exports installed applications, solutions, and environment/auth profiles to text files.

.REQUIREMENTS
- Power Platform CLI (pac)
- Appropriate environment permissions (System Administrator / System Customizer)
#>

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

$EnvironmentId = "bd81f293-c879-f111-b27b-6045bd003333"

$OutputFolder = "$PSScriptRoot\Output"
$LogFile = "$OutputFolder\PowerPlatformInventory.log"

New-Item -ItemType Directory -Force -Path $OutputFolder | Out-Null

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Entry = "$Timestamp [$Level] $Message"

    Write-Host $Entry
    Add-Content -Path $LogFile -Value $Entry
}

# ---------------------------------------------------------------------
# PAC Validation
# ---------------------------------------------------------------------

try {
    Write-Log "Checking Power Platform CLI"
    $Version = pac version
    Write-Log "PAC Version: $Version"
}
catch {
    Write-Log "PAC CLI not installed or not in PATH" "ERROR"
    throw
}

# ---------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------

try {
    Write-Log "Checking authentication"
    $Who = pac auth who 2>$null

    if (-not $Who) {
        Write-Log "No active PAC profile found"
        pac auth create
        Write-Log "Authentication completed"
    }

    $Who = pac auth who
    Write-Log "Authenticated profile:"
    Write-Log $Who
}
catch {
    Write-Log "Authentication failed: $_" "ERROR"
    throw
}

# ---------------------------------------------------------------------
# Environment Selection
# ---------------------------------------------------------------------

try {
    Write-Log "Selecting environment"
    pac env select --environment $EnvironmentId
    Write-Log "Environment selected: $EnvironmentId"
}
catch {
    Write-Log "Unable to select environment" "ERROR"
    throw
}

# ---------------------------------------------------------------------
# List Applications
# ---------------------------------------------------------------------

try {
    Write-Log "Listing installed applications"
    $Apps = pac application list
    $Apps | Out-File "$OutputFolder\Applications.txt"
    Write-Log "Applications exported"
}
catch {
    Write-Log "Failed to retrieve applications" "ERROR"
}

# ---------------------------------------------------------------------
# List Solutions
# ---------------------------------------------------------------------

try {
    Write-Log "Listing solutions"
    $Solutions = pac solution list
    $Solutions | Out-File "$OutputFolder\Solutions.txt"
    Write-Log "Solutions exported"
}
catch {
    Write-Log "Failed to retrieve solutions" "ERROR"
}

# ---------------------------------------------------------------------
# Profile Information
# ---------------------------------------------------------------------

try {
    Write-Log "Gathering profile data"
    pac auth list | Out-File "$OutputFolder\AuthProfiles.txt"
    pac env list | Out-File "$OutputFolder\Environments.txt"
}
catch {
    Write-Log "Failed to export authentication data" "ERROR"
}

Write-Log "Script completed successfully"
