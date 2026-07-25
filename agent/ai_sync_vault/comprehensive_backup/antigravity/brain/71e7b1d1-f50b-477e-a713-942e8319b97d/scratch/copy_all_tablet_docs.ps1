$shell = New-Object -ComObject Shell.Application
$thisPC = $shell.NameSpace(17) # This PC

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

$destDir = "C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
if (!(Test-Path $destDir)) {
    New-Item -ItemType Directory -Force -Path $destDir
}

Write-Host "Copying all files from tablet's 'Documents' folder to PC scratch..."
foreach ($item in $documents.Items()) {
    if (!$item.IsFolder) {
        $destPath = Join-Path $destDir $item.Name
        Write-Host "  Copying $($item.Name) to $destPath"
        # Copy file using the Shell COM copy engine to avoid MTP issues
        $destFolderObject = $shell.NameSpace($destDir)
        $destFolderObject.CopyHere($item, 16) # 16 = Respond "Yes to All" to any dialogs
    }
}

Write-Host "Copy process completed."
