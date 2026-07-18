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
    if ($item.Name -eq "Download") {
        $download = $item.GetFolder
    }
}

if ($null -eq $download) {
    Write-Host "Download folder not found."
    exit
}

# Locate osintneoai folder
$osintFolder = $null
foreach ($item in $download.Items()) {
    if ($item.Name -eq "osintneoai 1_20260526_010006") {
        $osintFolder = $item.GetFolder
    }
}

if ($null -eq $osintFolder) {
    Write-Host "osintneoai folder not found."
    exit
}

Write-Host "Listing files inside 'osintneoai 1_20260526_010006':"
function List-Folder($folder, $depth) {
    foreach ($item in $folder.Items()) {
        if ($item.IsFolder) {
            Write-Host ("  " * $depth + "[Folder] " + $item.Name)
            $sub = $item.GetFolder
            if ($sub) { List-Folder $sub ($depth + 1) }
        } else {
            Write-Host ("  " * $depth + "[File] " + $item.Name + " (" + $item.Size + " bytes)")
        }
    }
}

List-Folder $osintFolder 1
