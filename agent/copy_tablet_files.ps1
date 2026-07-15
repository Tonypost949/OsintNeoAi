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

$destDir = "c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_files"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir | Out-Null
}

function Copy-Files($folderItem) {
    $folder = $folderItem.GetFolder
    if (-not $folder) { return }
    
    foreach ($item in $folder.Items()) {
        if ($item.IsFolder) {
            Copy-Files $item
        } else {
            if ($item.Name -like "*.txt" -or $item.Name -like "*.json" -or $item.Name -like "*.md" -or $item.Name -like "*.html") {
                Write-Host "Copying $($item.Name)..."
                # Use shell namespace CopyHere
                $destFolder = $shell.NameSpace($destDir)
                $destFolder.CopyHere($item, 16) # 16 = Respond with Yes to All for any dialog box
            }
        }
    }
}

$deviceFolder = $tablet.GetFolder
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
        Copy-Files $item
    }
}
Write-Host "Copy complete!"
