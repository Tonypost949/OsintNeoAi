$source = "G:\"
$destRoot = "C:\Users\HP\OneDrive\External_Backup"

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

# Helper function to check space and wait for hydration/sync
function Protect-DiskSpace {
    $cDrive = Get-PSDrive C
    $freeGB = $cDrive.Free / 1GB
    
    if ($freeGB -lt 8.0) {
        Write-Output "[WARNING] C: drive free space is critically low ($([math]::Round($freeGB, 2)) GB)!"
        Write-Output "Dehydrating existing backups to free up space..."
        attrib +U -P "$destRoot\*.*" /S /D 2>$null
        
        while ($freeGB -lt 15.0) {
            Write-Output "Waiting for OneDrive to upload and free up space... Current C: Free: $([math]::Round($freeGB, 2)) GB"
            Start-Sleep -Seconds 45
            $cDrive = Get-PSDrive C
            $freeGB = $cDrive.Free / 1GB
        }
        Write-Output "C: drive space recovered: $([math]::Round($freeGB, 2)) GB. Resuming backup."
    }
}

# Granular recursive copy function
function Copy-Granular {
    param (
        [string]$sourcePath,
        [string]$destPath
    )
    
    if (Test-Path $sourcePath -PathType Container) {
        # Create directory
        if (-not (Test-Path $destPath)) {
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            # Dehydrate directory container
            attrib +U -P $destPath 2>$null
        }
        
        # Recurse children
        $children = Get-ChildItem -Path $sourcePath -ErrorAction SilentlyContinue
        foreach ($child in $children) {
            $childDest = Join-Path $destPath $child.Name
            Copy-Granular -sourcePath $child.FullName -destPath $childDest
        }
    } else {
        # File copy
        Protect-DiskSpace
        
        # Check if file already exists and is offline
        if (Test-Path $destPath) {
            # Skip if file already copied
            return
        }
        
        # Copy file
        Copy-Item -Path $sourcePath -Destination $destPath -Force -ErrorAction SilentlyContinue
        
        # Instantly dehydrate the file
        attrib +U -P $destPath 2>$null
    }
}

foreach ($item in $items) {
    $targetPath = Join-Path $destRoot $item.Name
    Write-Output "=== Starting backup of top-level item: $($item.Name) ==="
    Copy-Granular -sourcePath $item.FullName -destPath $targetPath
    Write-Output "=== Finished backup of top-level item: $($item.Name) ==="
}

Write-Output "=== ALL EXTERNAL DRIVE FILES BACKED UP AND DEHYDRATED ==="
