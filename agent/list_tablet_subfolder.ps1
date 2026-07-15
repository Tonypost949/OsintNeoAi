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

# Targeted folder: osintneoai 1_20260526_010006
$targetPath = "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}\\\?\usb#vid_1bbb&pid_0167&mi_00#6&2907d613&0&0000#{6ac27878-a6fa-4155-ba85-f98f491d4f33}\SID-{10001,,48296329216}\{6A44DE02-3382-2412-0000-000000000000}\{6A155325-344F-5A6E-0000-000000000000}"
$folder = $shell.NameSpace($targetPath)

if ($folder) {
    Write-Host "Listing files in target subfolder:"
    foreach ($file in $folder.Items()) {
        Write-Host "File: $($file.Name) | Path: $($file.Path)"
    }
} else {
    Write-Host "Subfolder not found directly. Finding recursively..."
    
    function Find-Subfolder($folderItem) {
        $f = $folderItem.GetFolder
        if (-not $f) { return }
        foreach ($sub in $f.Items()) {
            if ($sub.IsFolder) {
                if ($sub.Name -like "*osintneoai*") {
                    Write-Host "Found subfolder at $($sub.Path)"
                    $sf = $sub.GetFolder
                    foreach ($file in $sf.Items()) {
                        Write-Host "File: $($file.Name) | Path: $($file.Path)"
                    }
                } else {
                    Find-Subfolder $sub
                }
            }
        }
    }
    
    $deviceFolder = $tablet.GetFolder
    foreach ($item in $deviceFolder.Items()) {
        if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
            Find-Subfolder $item
        }
    }
}
