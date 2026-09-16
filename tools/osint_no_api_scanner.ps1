param (
    [Parameter(Mandatory=$false)]
    [string]$KeywordFile = "C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\my_search_targets.txt",
    
    [Parameter(Mandatory=$false)]
    [string]$EvidenceDir = "C:\Users\Amd949609\StudioProjects\OsintNeoAi\evidence",

    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\local_scan_results.json"
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   OSINT NEO AI - ZERO-API LOCAL EVIDENCE SCANNER" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Ensure the keyword file exists so the user can edit it
if (-not (Test-Path $KeywordFile)) {
    Set-Content -Path $KeywordFile -Value ""
    Write-Host "[!] Created empty keyword file: $KeywordFile" -ForegroundColor Yellow
}

# 2. Prompt user to add their keywords
Write-Host "`n[+] Opening Notepad so you can paste your exact keyword list..." -ForegroundColor Green
Write-Host "    --> PASTE YOUR LIST, HIT CTRL+S TO SAVE, THEN CLOSE NOTEPAD <--" -ForegroundColor Red
Start-Process -FilePath "notepad.exe" -ArgumentList $KeywordFile -Wait

# 3. Read the targets
$targets = Get-Content -Path $KeywordFile | Where-Object { $_.Trim() -ne "" -and $_ -notmatch "^Paste your" } | ForEach-Object { $_.Trim().ToLower() }

if ($targets.Count -eq 0) {
    Write-Host "`n[-] No valid targets found in file. Aborting." -ForegroundColor Red
    exit
}

Write-Host "`n[+] Loaded $($targets.Count) target keywords. Scanning locally (No APIs)..." -ForegroundColor Cyan

# 4. Do the scan locally via PowerShell (No Python, No APIs)
$results = @{}
foreach ($t in $targets) { $results[$t] = @() }

$filesScanned = 0
$hitsFound = 0

# Limit to readable files to prevent hanging
$files = Get-ChildItem -Path $EvidenceDir -Recurse -File -Include *.txt,*.md,*.csv,*.json,*.html

foreach ($file in $files) {
    $filesScanned++
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        if ($null -ne $content) {
            $content = $content.ToLower()
            foreach ($t in $targets) {
                if ($content.Contains($t)) {
                    $relPath = $file.FullName.Replace($EvidenceDir + "\", "")
                    $results[$t] += $relPath
                    $hitsFound++
                }
            }
        }
    } catch {
        # Skip unreadable files
    }
    
    # Progress indicator
    if ($filesScanned % 100 -eq 0) {
        Write-Host "    Scanned $filesScanned files..." -ForegroundColor DarkGray
    }
}

Write-Host "`n[✓] Scan Complete!" -ForegroundColor Green
Write-Host "    Files Scanned: $filesScanned"
Write-Host "    Total Hits: $hitsFound"

# 5. Format and Output JSON manually
$jsonOut = "{`n  `"scan_metadata`": {`n    `"files_scanned`": $filesScanned,`n    `"total_hits`": $hitsFound,`n    `"targets`": ["
$targetList = $targets | ForEach-Object { "`"$_`"" }
$jsonOut += ($targetList -join ", ") + "]`n  },`n  `"findings`": {`n"

$keys = $results.Keys | Sort-Object
for ($i=0; $i -lt $keys.Count; $i++) {
    $k = $keys[$i]
    $jsonOut += "    `"$k`": ["
    $paths = $results[$k] | ForEach-Object { "`"$_`"" }
    $jsonOut += ($paths -join ", ") + "]"
    if ($i -lt $keys.Count - 1) { $jsonOut += ",`n" } else { $jsonOut += "`n" }
}
$jsonOut += "  }`n}"

Set-Content -Path $OutputFile -Value $jsonOut -Encoding UTF8
Write-Host "[✓] Results saved to: $OutputFile" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
