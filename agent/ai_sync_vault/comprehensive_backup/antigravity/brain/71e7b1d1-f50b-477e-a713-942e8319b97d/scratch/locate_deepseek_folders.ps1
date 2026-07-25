# This script searches for directories containing "deepseek" or "deeoseek" in:
# 1. PC's Downloads folder: C:\Users\HP\Downloads
# 2. Tablet's shared storage folders (including Downloads and Documents)

# 1. Search PC Downloads
$pcDownloads = "C:\Users\HP\Downloads"
Write-Host "Searching PC Downloads ($pcDownloads)..."
if (Test-Path $pcDownloads) {
    $folders = Get-ChildItem -Path $pcDownloads -Directory -Filter "*deep*" -ErrorAction SilentlyContinue
    foreach ($f in $folders) {
        if ($f.Name -like "*deepseek*" -or $f.Name -like "*deeoseek*") {
            Write-Host "  Found PC Folder: $($f.FullName)"
            # List files inside
            Get-ChildItem -Path $f.FullName -File | ForEach-Object {
                Write-Host "    [File] $($_.Name) ($($_.Length) bytes)"
            }
        }
    }
} else {
    Write-Host "PC Downloads folder not found."
}

# 2. Search Tablet
Write-Host "`nSearching connected tablet storage for 'deepseek' or 'deeoseek' folders..."
$shell = New-Object -ComObject Shell.Application
$thisPC = $shell.NameSpace(17) # 17 = My Computer

$device = $null
foreach ($item in $thisPC.Items()) {
    if ($item.Name -like "*REVVL*" -or $item.Name -like "*T-Mobile*") {
        $device = $item
    }
}

if ($null -eq $device) {
    Write-Host "Tablet device not found on PC."
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
    Write-Host "Tablet storage not found."
    exit
}

# Search both Download and Documents on tablet
$targets = @("Download", "Downloads", "Documents")
foreach ($t in $targets) {
    $folder = $null
    foreach ($item in $storage.Items()) {
        if ($item.Name -eq $t) {
            $folder = $item.GetFolder
        }
    }
    if ($folder) {
        Write-Host "Searching tablet '$t' folder..."
        foreach ($item in $folder.Items()) {
            if ($item.IsFolder -and ($item.Name -like "*deepseek*" -or $item.Name -like "*deeoseek*")) {
                Write-Host "  Found Tablet Folder: \Internal shared storage\$t\$($item.Name)"
                # List files in this tablet folder
                $sub = $item.GetFolder
                if ($sub) {
                    foreach ($subItem in $sub.Items()) {
                        if ($subItem.IsFolder) {
                            Write-Host "    [Sub-Folder] $($subItem.Name)"
                        } else {
                            Write-Host "    [File] $($subItem.Name) ($($subItem.Size) bytes)"
                        }
                    }
                }
            }
        }
    }
}

Write-Host "Search completed."
