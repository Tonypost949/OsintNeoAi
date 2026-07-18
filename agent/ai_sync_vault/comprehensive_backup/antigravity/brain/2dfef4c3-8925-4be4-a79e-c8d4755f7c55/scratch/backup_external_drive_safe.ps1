$source = "G:\"
$destRoot = "C:\Users\HP\OneDrive\External_Backup"
$batchLimitBytes = 200MB
$batchLimitFiles = 500

# Create destination root
New-Item -ItemType Directory -Path $destRoot -Force | Out-Null

# List of items to copy
$items = Get-ChildItem -Path $source -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -ne '$RECYCLE.BIN' -and 
    $_.Name -ne 'System Volume Information' -and 
    $_.Name -ne '.gemini' -and
    $_.Name -ne '.dropbox.device'
}

Write-Output "Found $($items.Count) top-level items to back up."

$currentBatchSizeBytes = 0
$currentBatchFileCount = 0

function Wait-For-Sync {
    Write-Output "[SYNC] Batch limit reached ($([math]::Round($currentBatchSizeBytes / 1MB, 2)) MB, $currentBatchFileCount files). Requesting dehydration..."
    
    # Run attrib to ensure Windows knows to offload
    attrib +U -P "$destRoot\*.*" /S /D 2>$null
    
    $syncing = $true
    $loopCount = 0
    while ($syncing) {
        $loopCount++
        
        # Check C: drive free space
        $freeGB = (Get-PSDrive C).Free / 1GB
        
        # Count files that are still local (not offline/sparse)
        $localFilesCount = 0
        $files = Get-ChildItem -Path $destRoot -Recurse -File -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            if ($f.Attributes -notmatch "Offline" -and $f.Attributes -notmatch "SparseFile") {
                $localFilesCount++
            }
        }
        
        Write-Output "[SYNC STATUS] C: Free: $([math]::Round($freeGB, 2)) GB | Files still local: $localFilesCount"
        
        # If all files are dehydrated OR C: drive space is healthy (> 12GB) and local files are very low
        if ($localFilesCount -eq 0 -or ($freeGB -ge 13.0 -and $localFilesCount -lt 5)) {
            $syncing = $false
            Write-Output "[SYNC] Space recovered. Resuming backup."
        } else {
            # Periodically re-trigger attrib in case OneDrive needs a nudge
            if ($loopCount % 5 -eq 0) {
                attrib +U -P "$destRoot\*.*" /S /D 2>$null
            }
            Start-Sleep -Seconds 30
        }
    }
}

function Copy-GranularStrict {
    param (
        [string]$sourcePath,
        [string]$destPath
    )
    
    if (Test-Path $sourcePath -PathType Container) {
        if (-not (Test-Path $destPath)) {
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            attrib +U -P $destPath 2>$null
        }
        
        $children = Get-ChildItem -Path $sourcePath -ErrorAction SilentlyContinue
        foreach ($child in $children) {
            $childDest = Join-Path $destPath $child.Name
            Copy-GranularStrict -sourcePath $child.FullName -destPath $childDest
        }
    } else {
        # Check if already exists in destination
        if (Test-Path $destPath) {
            return
        }
        
        # Check batch limits before copying
        $fileSize = (Get-Item $sourcePath).Length
        if (($script:currentBatchSizeBytes + $fileSize -ge $batchLimitBytes) -or ($script:currentBatchFileCount + 1 -ge $batchLimitFiles)) {
            Wait-For-Sync
            $script:currentBatchSizeBytes = 0
            $script:currentBatchFileCount = 0
        }
        
        # Copy file
        Copy-Item -Path $sourcePath -Destination $destPath -Force -ErrorAction SilentlyContinue
        $script:currentBatchSizeBytes += $fileSize
        $script:currentBatchFileCount++
        
        # Instantly request dehydration on the file
        attrib +U -P $destPath 2>$null
    }
}

foreach ($item in $items) {
    $targetPath = Join-Path $destRoot $item.Name
    Write-Output "=== Starting safe backup of: $($item.Name) ==="
    Copy-GranularStrict -sourcePath $item.FullName -destPath $targetPath
    Write-Output "=== Finished safe backup of: $($item.Name) ==="
}

# Final dehydration pass
Wait-For-Sync
Write-Output "=== ALL EXTERNAL DRIVE FILES BACKED UP AND DEHYDRATED ==="
