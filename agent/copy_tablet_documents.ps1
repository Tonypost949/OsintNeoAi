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

$destDir = "c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_documents"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir | Out-Null
}

# Documents folder path on tablet:
$docPath = "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}\\\?\usb#vid_1bbb&pid_0167&mi_00#6&2907d613&0&0000#{6ac27878-a6fa-4155-ba85-f98f491d4f33}\SID-{10001,,48296329216}\{6A42C48B-46FE-4833-0000-000000000000}"
$docFolder = $shell.NameSpace($docPath)

if ($docFolder) {
    Write-Host "Found Documents folder. Copying files..."
    foreach ($file in $docFolder.Items()) {
        Write-Host "Copying: $($file.Name)"
        $destFolder = $shell.NameSpace($destDir)
        $destFolder.CopyHere($file, 16)
    }
    Write-Host "Done copying documents!"
} else {
    Write-Host "Could not bind to the Documents folder path directly. Finding recursively..."
    $deviceFolder = $tablet.GetFolder
    foreach ($item in $deviceFolder.Items()) {
        if ($item.Name -like "*storage*" -or $item.Name -like "*Internal*") {
            $storage = $item.GetFolder
            foreach ($subItem in $storage.Items()) {
                if ($subItem.Name -eq "Documents") {
                    Write-Host "Found Documents folder at $($subItem.Path)"
                    $docFolder2 = $subItem.GetFolder
                    foreach ($file in $docFolder2.Items()) {
                        Write-Host "Copying: $($file.Name)"
                        $destFolder = $shell.NameSpace($destDir)
                        $destFolder.CopyHere($file, 16)
                    }
                }
            }
        }
    }
}
