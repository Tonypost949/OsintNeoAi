$urls = @(
    "https://gemini.google.com/app",
    "https://mail.google.com/mail/u/0/#inbox",
    "https://drive.google.com/drive/my-drive",
    "https://www.esri.com/en-us/arcgis/products/arcgis-for-microsoft/overview",
    "https://www.esri.com/en-us/arcgis/products/arcgis-for-microsoft/get-started",
    "https://www.arcgis.com/apps/mapviewer/index.html",
    "https://www.arcgis.com/home/index.html",
    "https://my.esri.com/#/my-profile/overview",
    "https://my.esri.com/#/my-profile/purchases",
    "https://my.esri.com/#/my-profile/organizations",
    "https://my.esri.com/#/my-profile/personal-info"
)

$targetDir = "C:\OsintNeoAi\scraped_tabs"
if (!(Test-Path $targetDir)) { New-Item -ItemType Directory -Force -Path $targetDir }

foreach ($u in $urls) {
    $cleanName = ($u -replace '[^a-zA-Z0-9]', '_').Trim('_') + ".html"
    $outFile = Join-Path $targetDir $cleanName
    try {
        Write-Host "[+] Fetching HTML for: $u"
        $res = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
        $res.Content | Out-File -FilePath $outFile -Encoding utf8
        Write-Host "    --> Saved to $outFile ($(($res.Content).Length) bytes)"
    } catch {
        Write-Host "    [-] Could not directly fetch $u ($($_.Exception.Message))"
    }
}
