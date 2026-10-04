<# 
.SYNOPSIS
    Start a 24hr public Cloudflare tunnel to localhost:8080
.DESCRIPTION
    Downloads cloudflared if needed, kills existing tunnels, starts HTTP/2 tunnel
    Outputs the trycloudflare.com URL when ready
#>

param(
    [int]$Port = 8080,
    [string]$CloudflaredPath = "$env:TEMP\cloudflared.exe"
)

# Download cloudflared if missing
if (-not (Test-Path $CloudflaredPath)) {
    Write-Host "Downloading cloudflared..." -ForegroundColor Cyan
    $url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    try {
        Invoke-WebRequest -Uri $url -OutFile $CloudflaredPath -ErrorAction Stop
    } catch {
        Write-Error "Failed to download cloudflared: $_"
        exit 1
    }
}

# Kill existing tunnels
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "cf*" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*cloudflared*" } | Stop-Process -Force
Start-Sleep 2

# Start tunnel with HTTP/2 (bypasses QUIC/UDP issues on Windows)
Write-Host "Starting Cloudflare tunnel on http://localhost:$Port..." -ForegroundColor Green
Write-Host "Waiting for URL..." -ForegroundColor Yellow

# Run and capture output to extract URL
$proc = Start-Process -FilePath $CloudflaredPath -ArgumentList "tunnel --url http://localhost:$Port --protocol http2 --no-autoupdate" -PassThru -RedirectStandardOutput "$env:TEMP\cf_out.log" -RedirectStandardError "$env:TEMP\cf_err.log"

# Poll for URL in logs
$url = $null
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep 2
    if (Test-Path "$env:TEMP\cf_err.log") {
        $log = Get-Content "$env:TEMP\cf_err.log" -Raw
        if ($log -match 'https://[\w-]+\.trycloudflare\.com') {
            $url = $matches[0]
            break
        }
    }
}

if ($url) {
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "TUNNEL LIVE: $url/hbnc_rico_gis.html" -ForegroundColor Cyan
    Write-Host "============================================`n" -ForegroundColor Green
} else {
    Write-Warning "URL not detected yet. Check $env:TEMP\cf_err.log"
}

# Keep process alive
Write-Host "Tunnel running (PID: $($proc.Id)). Press Ctrl+C to stop."
try {
    $proc.WaitForExit()
} catch {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}