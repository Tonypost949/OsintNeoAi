$shell = New-Object -ComObject Shell.Application
$thisPC = $shell.NameSpace(17) # 17 = My Computer

$device = $null
foreach ($item in $thisPC.Items()) {
    if ($item.Name -like "*REVVL*" -or $item.Name -like "*T-Mobile*") {
        $device = $item
    }
}

if ($null -eq $device) {
    Write-Host "Device not found."
    exit
}

$deviceFolder = $device.GetFolder
$storage = $null
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -eq "Internal shared storage" -or $item.Name -eq "Internal Storage" -or $item.IsFolder) {
        $storage = $item.GetFolder
    }
}

if ($null -eq $storage) {
    Write-Host "Storage not found."
    exit
}

# Locate Documents folder
$documents = $null
foreach ($item in $storage.Items()) {
    if ($item.Name -eq "Documents") {
        $documents = $item.GetFolder
    }
}

if ($null -eq $documents) {
    Write-Host "Documents folder not found."
    exit
}

Write-Host "Listing ALL files inside tablet's 'Documents' folder:"
foreach ($item in $documents.Items()) {
    if ($item.IsFolder) {
        Write-Host "  [Folder] $($item.Name)"
    } else {
        Write-Host "  [File] $($item.Name) ($($item.Size) bytes) Path: $($item.Path)"
    }
}
