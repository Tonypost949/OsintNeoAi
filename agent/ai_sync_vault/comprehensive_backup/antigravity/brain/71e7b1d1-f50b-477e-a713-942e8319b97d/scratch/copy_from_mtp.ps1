# Powershell script to copy cityscan HTML files and PDF files from MTP device (T-Mobile REVVL TAB 2) to local scratch dir
$shell = New-Object -ComObject Shell.Application
$thisPC = $shell.NameSpace(17)
$outDir = "C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force
}

$device = $null
foreach ($item in $thisPC.Items()) {
    if ($item.Name -like "*REVVL*" -or $item.Name -like "*T-Mobile*") {
        $device = $item
    }
}

if ($null -eq $device) {
    Write-Host "Tablet not found."
    exit
}

$deviceFolder = $device.GetFolder
$destNamespace = $shell.NameSpace($outDir)

foreach ($storage in $deviceFolder.Items()) {
    if ($storage.Name -eq "Internal shared storage" -or $storage.Name -eq "Internal Storage" -or $storage.IsFolder) {
        $storageFolder = $storage.GetFolder
        foreach ($folder in $storageFolder.Items()) {
            if ($folder.Name -eq "Documents") {
                $docsFolder = $folder.GetFolder
                foreach ($file in $docsFolder.Items()) {
                    if ($file.Name -like "*city*") {
                        Write-Host "Copying $($file.Name) from Documents to scratch..."
                        $destNamespace.CopyHere($file, 16)
                    }
                }
            }
            if ($folder.Name -eq "Download") {
                $dlFolder = $folder.GetFolder
                foreach ($file in $dlFolder.Items()) {
                    if ($file.Name -like "*Jesse*" -or $file.Name -like "*city*") {
                        Write-Host "Copying $($file.Name) from Download to scratch..."
                        $destNamespace.CopyHere($file, 16)
                    }
                }
            }
        }
    }
}

Write-Host "Copy completed."
