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

# Find the Documents folder
$deviceFolder = $tablet.GetFolder
$docFolder = $null
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
        $storage = $item.GetFolder
        foreach ($subItem in $storage.Items()) {
            if ($subItem.Name -eq "Documents") {
                $docFolder = $subItem.GetFolder
                Write-Host "Found Documents folder: $($subItem.Path)"
                break
            }
        }
    }
}

if ($docFolder) {
    foreach ($file in $docFolder.Items()) {
        Write-Host "File: $($file.Name) | Path: $($file.Path)"
    }
} else {
    Write-Host "Documents folder not found under Internal storage."
}
