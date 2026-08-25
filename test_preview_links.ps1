# Test HTML Preview and direct live rendered map URLs
$urls = @(
    "https://htmlpreview.github.io/?https://github.com/Tonypost949/OsintNeoAi/blob/main/index.html",
    "https://htmlpreview.github.io/?https://github.com/Tonypost949/OsintNeoAi/blob/main/badass_osint_map.html",
    "https://htmlpreview.github.io/?https://github.com/Tonypost949/OsintNeoAi/blob/main/hbnc_rico_gis.html",
    "https://htmlpreview.github.io/?https://github.com/Tonypost949/OsintNeoAi/blob/main/nationwide_coc_map.html",
    "https://htmlpreview.github.io/?https://github.com/Tonypost949/OsintNeoAi/blob/main/arcgis_teams_dashboard.html"
)

foreach ($u in $urls) {
    try {
        $r = Invoke-WebRequest -Uri $u -Method Head -TimeoutSec 5 -UseBasicParsing
        Write-Host "🟢 LIVE: $u (HTTP $($r.StatusCode))"
    } catch {
        Write-Host "🔴 ERR: $u"
    }
}
