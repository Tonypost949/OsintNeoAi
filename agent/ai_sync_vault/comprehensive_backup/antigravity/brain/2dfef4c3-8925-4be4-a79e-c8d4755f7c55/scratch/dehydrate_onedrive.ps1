$paths = @("C:\Users\HP\OneDrive", "C:\Users\HP\OneDrive - Post University,inc")
Write-Output "Scanning for local files to unpin..."
$files = Get-ChildItem -Path $paths -Recurse -File -Force -ErrorAction SilentlyContinue

$total = 0
$dehydrated = 0
$failed = 0

Write-Output "Starting unpinning loop with attribute override..."
foreach ($file in $files) {
    if ($file.Attributes -match "Offline" -eq $false) {
        $total++
        try {
            $is_hidden = $file.Attributes -match "Hidden"
            $is_system = $file.Attributes -match "System"
            
            if ($is_hidden -or $is_system) {
                attrib.exe -h -s $file.FullName
            }
            
            attrib.exe +U -P $file.FullName
            
            if ($is_hidden) { attrib.exe +h $file.FullName }
            if ($is_system) { attrib.exe +s $file.FullName }
            
            $dehydrated++
            if ($dehydrated % 1000 -eq 0) {
                Write-Output "[PROGRESS] Freed up $dehydrated files..."
            }
        } catch {
            $failed++
        }
    }
}
Write-Output "=== UNPINNING FINISHED ==="
Write-Output "Total processed: $total"
Write-Output "Successfully freed up: $dehydrated"
Write-Output "Failed: $failed"
