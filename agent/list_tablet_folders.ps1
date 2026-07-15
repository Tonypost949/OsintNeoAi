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

function List-Folders($folderItem, $depth=0) {
    if ($depth -gt 4) { return }
    $folder = $folderItem.GetFolder
    if (-not $folder) { return }
    
    foreach ($item in $folder.Items()) {
        if ($item.IsFolder) {
            Write-Host ("  " * $depth) + $item.Name + " -> " + $item.Path
            List-Folders $item ($depth + 1)
        }
    }
}

$deviceFolder = $tablet.GetFolder
foreach ($item in $deviceFolder.Items()) {
    if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
        List-Folders $item
    }
}
