$shell = New-Object -ComObject Shell.Application
$thisPC = $shell.NameSpace(17)
$tablet = $null

foreach ($item in $thisPC.Items()) {
    if ($item.Name -like "*T-Mobile*" -or $item.Name -like "*REVVL*") {
        $tablet = $item
        break
    }
}

if (-not $tablet) {
    Write-Host "Tablet not found."
    exit
}

# Find target files in Download folder
$deviceFolder = $tablet.GetFolder
$downloadFolder = $null
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
        $storage = $item.GetFolder
        foreach ($subItem in $storage.Items()) {
            if ($subItem.Name -eq "Download") {
                $downloadFolder = $subItem.GetFolder
                break
            }
        }
    }
}

if ($downloadFolder) {
    Write-Host "Found Download folder. Scanning all text/markdown files directly on tablet..."
    foreach ($file in $downloadFolder.Items()) {
        if ($file.Name -like "*.txt" -or $file.Name -like "*.md" -or $file.Name -like "*.html" -or $file.Name -like "*.json") {
            # Copy to temp file to read since we cannot directly read streams via COM in simple powershell easily
            $tempFile = [System.IO.Path]::GetTempFileName()
            $tempDir = [System.IO.Path]::GetDirectoryName($tempFile)
            $tempBase = [System.IO.Path]::GetFileName($tempFile)
            
            $shellTemp = $shell.NameSpace($tempDir)
            $shellTemp.CopyHere($file, 16) # Copy to temp directory
            
            # The copied file will have the original name in the temp directory
            $copiedPath = Join-Path $tempDir $file.Name
            if (Test-Path $copiedPath) {
                $content = Get-Content -Path $copiedPath -Raw
                $lines = $content -split "`n"
                for ($i=0; $i -lt $lines.Length; $i++) {
                    if ($lines[$i] -match "holes" -or $lines[$i] -match "disgrace") {
                        Write-Host "MATCH in $($file.Name) at Line $($i+1): $($lines[$i].Trim())"
                    }
                }
                Remove-Item $copiedPath -ErrorAction SilentlyContinue
            }
            Remove-Item $tempFile -ErrorAction SilentlyContinue
        }
    }
} else {
    Write-Host "Download folder not found."
}
