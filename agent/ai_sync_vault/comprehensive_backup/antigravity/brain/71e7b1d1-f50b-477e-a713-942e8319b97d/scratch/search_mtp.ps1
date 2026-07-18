# Powershell script to search for the connected MTP device (T-Mobile REVVL TAB 2)
# and try to locate any files containing "disgrace" or "cities" or listing text.

$shell = New-Object -ComObject Shell.Application
$thisPC = $shell.NameSpace(17) # 17 = My Computer / This PC

if ($null -eq $thisPC) {
    Write-Host "Could not bind to This PC."
    exit
}

Write-Host "Listing devices under 'This PC':"
$device = $null
foreach ($item in $thisPC.Items()) {
    Write-Host "  Found device/folder: $($item.Name)"
    if ($item.Name -like "*REVVL*" -or $item.Name -like "*T-Mobile*") {
        $device = $item
    }
}

if ($null -eq $device) {
    Write-Host "No connected MTP device matching 'T-Mobile' or 'REVVL' found under This PC."
    exit
}

Write-Host "Found device: $($device.Name)"
# Get folder object for the device
$deviceFolder = $device.GetFolder
if ($null -eq $deviceFolder) {
    Write-Host "Could not get folder object for $($device.Name)"
    exit
}

# Recursively list folders/files in MTP storage (Internal shared storage)
# Because MTP is slow, we will write a limited search helper
function Search-MTPFolder($folder, $depth) {
    if ($depth -gt 4) { return } # limit depth to prevent endless loops
    try {
        foreach ($item in $folder.Items()) {
            if ($item.IsFolder) {
                # Skip massive system directories on android like Android/data or Android/obb
                if ($item.Name -eq "Android") { continue }
                Write-Host ("  " * $depth + "[Folder] " + $item.Name)
                $subFolder = $item.GetFolder
                if ($subFolder) {
                    Search-MTPFolder $subFolder ($depth + 1)
                }
            } else {
                # Print file name
                $name = $item.Name
                # Check if it matches search terms or seems relevant
                if ($name -like "*disgrace*" -or $name -like "*city*" -or $name -like "*cities*" -or $name -like "*search*") {
                    Write-Host ("  " * $depth + "[MATCHING FILE] " + $name + " Path: " + $item.Path)
                }
            }
        }
    } catch {
        Write-Host "Error scanning folder: $_"
    }
}

Write-Host "Starting search of Internal shared storage..."
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -eq "Internal shared storage" -or $item.Name -eq "Internal Storage" -or $item.IsFolder) {
        Write-Host "Entering folder: $($item.Name)"
        $storageFolder = $item.GetFolder
        if ($storageFolder) {
            Search-MTPFolder $storageFolder 1
        }
    }
}

Write-Host "Search finished."
