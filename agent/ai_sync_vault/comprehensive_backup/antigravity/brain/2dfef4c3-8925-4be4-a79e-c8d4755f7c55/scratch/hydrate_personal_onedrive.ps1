$paths = @("C:\Users\HP\OneDrive")
Write-Output "Scanning OneDrive folders for cloud-only files..."
$files = Get-ChildItem -Path $paths -Recurse -File -ErrorAction SilentlyContinue

$total = 0
$hydrated = 0
$failed = 0

Write-Output "Starting hydration loop for offline files..."
foreach ($file in $files) {
    if ($file.Attributes -match "Offline" -or $file.Attributes -match "SparseFile") {
        $total++
        try {
            $stream = [System.IO.File]::OpenRead($file.FullName)
            $stream.Close()
            $hydrated++
            if ($hydrated % 100 -eq 0) {
                Write-Output "[PROGRESS] Hydrated $hydrated files..."
            }
        } catch {
            $failed++
        }
    }
}
Write-Output "=== HYDRATION FINISHED ==="
Write-Output "Total processed: $total"
Write-Output "Successfully hydrated: $hydrated"
Write-Output "Failed: $failed"
