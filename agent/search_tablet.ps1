$shell = New-Object -ComObject Shell.Application
# 17 is ssfDRIVES (This PC)
$thisPC = $shell.NameSpace(17)
$tablet = $null

foreach ($item in $thisPC.Items()) {
    if ($item.Name -like "*T-Mobile*" -or $item.Name -like "*REVVL*") {
        $tablet = $item
        Write-Host "Found device: $($item.Name)"
        break
    }
}

if (-not $tablet) {
    Write-Host "Device not found under This PC. Listing all items under This PC:"
    foreach ($item in $thisPC.Items()) {
        Write-Host " - $($item.Name) (Type: $($item.Type))"
    }
    exit
}

# Recursively list folders/files to find text files
function Scan-Folder($folderItem, $depth=0) {
    if ($depth -gt 5) { return }
    $folder = $folderItem.GetFolder
    if (-not $folder) { return }
    
    foreach ($item in $folder.Items()) {
        if ($item.IsFolder) {
            Scan-Folder $item ($depth + 1)
        } else {
            if ($item.Name -like "*.txt" -or $item.Name -like "*.json" -or $item.Name -like "*.md" -or $item.Name -like "*.html") {
                Write-Host "$($item.Path) -> $($item.Name)"
            }
        }
    }
}

# Get the internal storage folder
$deviceFolder = $tablet.GetFolder
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
        Write-Host "Scanning storage: $($item.Name)"
        Scan-Folder $item
    }
}
