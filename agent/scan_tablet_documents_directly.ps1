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

$deviceFolder = $tablet.GetFolder
$docFolder = $null
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
        $storage = $item.GetFolder
        foreach ($subItem in $storage.Items()) {
            if ($subItem.Name -eq "Documents") {
                $docFolder = $subItem.GetFolder
                break
            }
        }
    }
}

if ($docFolder) {
    Write-Host "Found Documents folder. Scanning files..."
    foreach ($file in $docFolder.Items()) {
        if ($file.Name -like "*.html" -or $file.Name -like "*.txt" -or $file.Name -like "*.csv" -or $file.Name -like "*.md") {
            $tempFile = [System.IO.Path]::GetTempFileName()
            $tempDir = [System.IO.Path]::GetDirectoryName($tempFile)
            
            $shellTemp = $shell.NameSpace($tempDir)
            $shellTemp.CopyHere($file, 16)
            
            $copiedPath = Join-Path $tempDir $file.Name
            if (Test-Path $copiedPath) {
                $content = Get-Content -Path $copiedPath -Raw
                $lines = $content -split "`n"
                for ($i=0; $i -lt $lines.Length; $i++) {
                    if ($lines[$i] -match "holes" -or $lines[$i] -match "disgrace") {
                        Write-Host "MATCH in Documents/$($file.Name) at Line $($i+1): $($lines[$i].Trim())"
                    }
                }
                Remove-Item $copiedPath -ErrorAction SilentlyContinue
            }
            Remove-Item $tempFile -ErrorAction SilentlyContinue
        }
    }
} else {
    Write-Host "Documents folder not found."
}
