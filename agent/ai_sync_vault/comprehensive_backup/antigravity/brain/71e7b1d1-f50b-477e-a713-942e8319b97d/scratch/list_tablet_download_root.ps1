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

# Locate Download folder
$download = $null
foreach ($item in $storage.Items()) {
    if ($item.Name -eq "Download" -or $item.Name -eq "Downloads") {
        $download = $item.GetFolder
    }
}

if ($null -eq $download) {
    Write-Host "Download folder not found."
    exit
}

Write-Host "Listing ALL files/folders in tablet's 'Download' root folder:"
foreach ($item in $download.Items()) {
    if ($item.IsFolder) {
        Write-Host "  [Folder] $($item.Name)"
    } else {
        Write-Host "  [File] $($item.Name) ($($item.Size) bytes)"
    }
}
