# Gemini CLI Vertex AI Fix Script
# Run after `npm install -g @google/gemini-cli` or updates
# Patches the JS bundle to use gemini-2.5-flash on Vertex AI

$ErrorActionPreference = "Stop"

$geminiPath = "$env:APPDATA\npm\node_modules\@google\gemini-cli"
if (!(Test-Path $geminiPath)) {
    $geminiPath = "$env:LOCALAPPDATA\Programs\nodejs\node_modules\@google\gemini-cli"
}
if (!(Test-Path $geminiPath)) {
    Write-Host "ERROR: Gemini CLI not found" -ForegroundColor Red
    exit 1
}

$bundleDir = "$geminiPath\bundle"
Write-Host "Patching Gemini CLI in: $bundleDir" -ForegroundColor Cyan

# Patch: Change gemini-3.5-flash to gemini-2.5-flash in setFlashModels calls
# This fixes the Vertex AI model resolution bug where hasGemini35FlashGAAccess()
# returns true for Vertex AI, causing the wrong model ID to be used.

$patchCount = 0
Get-ChildItem "$bundleDir\chunk-*.js" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match 'setFlashModels\("gemini-3\.5-flash",\s*"gemini-3\.5-flash"\)') {
        $newContent = $content -replace 'setFlashModels\("gemini-3\.5-flash",\s*"gemini-3\.5-flash"\)', 'setFlashModels("gemini-2.5-flash", "gemini-2.5-flash")'
        Set-Content $_.FullName -Value $newContent -NoNewline
        Write-Host "  Patched: $($_.Name)" -ForegroundColor Green
        $patchCount++
    }
}

if ($patchCount -eq 0) {
    Write-Host "  No files needed patching (already patched or new version)" -ForegroundColor Yellow
} else {
    Write-Host "  Patched $patchCount file(s)" -ForegroundColor Green
}

# Copy settings
$settingsSrc = "$PSScriptRoot\gemini-settings.json"
$settingsDst = "$env:USERPROFILE\.gemini\settings.json"
if (Test-Path $settingsSrc) {
    Copy-Item $settingsSrc $settingsDst -Force
    Write-Host "  Copied settings.json" -ForegroundColor Green
}

# Ensure env vars
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_PROJECT", "blah-905ad", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_LOCATION", "us-central1", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", "", "User")
Write-Host "  Environment variables set" -ForegroundColor Green

Write-Host "`nDone! Gemini CLI is configured for Vertex AI." -ForegroundColor Cyan
