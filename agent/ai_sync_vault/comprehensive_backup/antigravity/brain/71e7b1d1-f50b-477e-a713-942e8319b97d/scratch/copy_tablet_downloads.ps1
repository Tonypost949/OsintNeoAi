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

$destDir = "C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_downloads"
if (!(Test-Path $destDir)) {
    New-Item -ItemType Directory -Force -Path $destDir
}

# We want to find files matching names or content. Since reading content directly from MTP objects is not possible,
# we can first copy files of interest (like .txt, .html, .md, .csv, .docx, .xlsx, .pdf) to the local folder and then search.
# Let's copy text-based files from the tablet Download folder to local PC for searching.
Write-Host "Copying text-based and sheet files from tablet's Download folder..."
$destFolderObject = $shell.NameSpace($destDir)

$exts = @(".txt", ".html", ".md", ".csv", ".docx", ".xlsx", ".json")

foreach ($item in $download.Items()) {
    if ($item.IsFolder) {
        continue
    }
    $ext = [System.IO.Path]::GetExtension($item.Name).ToLower()
    # Also check files containing 'report' or 'summary' or 'scan'
    $name = $item.Name.ToLower()
    if ($exts -contains $ext -or $name -like "*report*" -or $name -like "*scan*" -or $name -like "*mx*") {
        Write-Host "  Copying $($item.Name)..."
        $destFolderObject.CopyHere($item, 16)
        Start-Sleep -Milliseconds 200
    }
}

Write-Host "Copy process completed."
