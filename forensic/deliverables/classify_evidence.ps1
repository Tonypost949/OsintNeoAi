# PowerShell Forensic Classification Sorter
# Ingests forensic evidence files and classifies into CLEAN, HOLD, MANUAL, and MIXED queues.

param (
    [string]$SourcePath = "C:\osintneoai\forensic\raw_evidence",
    [string]$OutputPath = "C:\osintneoai\forensic\classified"
)

$Keywords = @{
    HOLD   = @("sidhu", "ament", "rafiei", "surplus land", "default judgment", "void", "quid pro quo", "plea", "indictment")
    MANUAL = @("mercy house", "homi", "ruzicka", "cameron ln", "quantum auto", "flint", "chamber", "hoang", "sontag", "drissen")
    MIXED  = @("grant", "hud", "ochca", "1601 dove", "lakeview", "cedar ln", "wire transfer", "appraisal", "nonprofit", "tax-exempt")
}

foreach ($q in @("CLEAN", "HOLD", "MANUAL", "MIXED")) {
    $dir = Join-Path $OutputPath $q
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}

Write-Host "[*] Starting Forensic Document Classification..." -ForegroundColor Cyan

Get-ChildItem -Path $SourcePath -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    $searchTarget = ($_.Name + " " + $content).ToLower()

    $holdMatches   = $Keywords.HOLD   | Where-Object { $searchTarget -match [regex]::Escape($_) }
    $manualMatches = $Keywords.MANUAL | Where-Object { $searchTarget -match [regex]::Escape($_) }
    $mixedMatches  = $Keywords.MIXED  | Where-Object { $searchTarget -match [regex]::Escape($_) }

    $total = $holdMatches.Count + $manualMatches.Count + $mixedMatches.Count
    $targetCategory = "CLEAN"

    if ($total -eq 0) {
        $targetCategory = "CLEAN"
    } elseif ($holdMatches.Count -gt 0 -and ($manualMatches.Count -gt 0 -or $mixedMatches.Count -gt 0)) {
        $targetCategory = "MIXED"
    } elseif ($manualMatches.Count -ge 2 -or $total -ge 3) {
        $targetCategory = "MANUAL"
    } else {
        $targetCategory = "HOLD"
    }

    $dest = Join-Path $OutputPath $targetCategory $_.Name
    Copy-Item $_.FullName $dest -Force
    Write-Host "[+] Classified: $($_.Name) -> [$targetCategory] (Hits: $total)" -ForegroundColor Green
}

Write-Host "[✓] Classification Completed." -ForegroundColor Green