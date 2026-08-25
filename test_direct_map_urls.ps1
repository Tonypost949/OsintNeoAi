$urls = @(
    "http://osintneoai.me/",
    "http://osintneoai.me/master_tactical_gis.html",
    "https://osintneoai.onhercules.app/",
    "http://57.152.82.43:10000/"
)

foreach ($u in $urls) {
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $r = Invoke-WebRequest -Uri $u -Method Get -TimeoutSec 10 -UseBasicParsing
        $sw.Stop()
        Write-Host "🟢 LIVE: $u (HTTP $($r.StatusCode) - $($sw.ElapsedMilliseconds)ms - $($r.RawContentLength) bytes)"
    } catch {
        Write-Host "🔴 FAIL: $u ($($_.Exception.Message))"
    }
}
