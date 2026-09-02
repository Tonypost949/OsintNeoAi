# gods_eye monitor script
$urls = @(
  'https://osintneoai-app-949.azurewebsites.net/gods_eye_view.html',
  'https://osintneoai-app-949.azurewebsites.net/'
)
$ua = 'OSINTNeoAi-Monitor/1.0'
$cycleSeconds = 90
$requestTimeoutSeconds = 20
$maxDurationHours = 6
$start = Get-Date
$logDir = 'C:\OsintNeoAi\monitor_logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
$logFile = Join-Path $logDir 'gods_eye_monitor.log'
$reportFile = 'C:\OsintNeoAi\evidence\gods_eye_monitor_report.json'
if (-not (Test-Path 'C:\OsintNeoAi\evidence')) { New-Item -ItemType Directory -Force -Path 'C:\OsintNeoAi\evidence' | Out-Null }
Add-Content $logFile "Monitor START $start"

while ((Get-Date) -lt $start.AddHours($maxDurationHours)) {
  foreach ($url in $urls) {
    $ts = (Get-Date).ToString('o')
    try {
      $handler = New-Object System.Net.Http.HttpClientHandler
      $handler.AllowAutoRedirect = $true
      $client = New-Object System.Net.Http.HttpClient($handler)
      $client.Timeout = [System.TimeSpan]::FromSeconds($requestTimeoutSeconds)
      $req = New-Object System.Net.Http.HttpRequestMessage([System.Net.Http.HttpMethod]::Get, $url)
      $req.Headers.UserAgent.ParseAdd($ua)
      $resp = $client.SendAsync($req).GetAwaiter().GetResult()
      $status = [int]$resp.StatusCode
      $content = $resp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
      $line = "$ts $url $status"
      Add-Content $logFile $line
      if ($status -eq 200) {
        $headers = @{}
        foreach ($h in $resp.Headers.GetEnumerator()) { $headers[$h.Key] = ($h.Value -join ', ') }
        foreach ($h in $resp.Content.Headers.GetEnumerator()) { $headers[$h.Key] = ($h.Value -join ', ') }
        $snippet = if ($content) { $content.Substring(0,[Math]::Min(1500,$content.Length)) } else { $null }
        $report = @{ result='success'; timestamp=$ts; url=$url; headers=$headers; body_snippet=$snippet }
        $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8
        Add-Content $logFile "SUCCESS $ts $url returned 200"
        exit 0
      }
    } catch {
      $err = $_.Exception.Message.Replace("`n"," ").Replace("`r"," ")
      $line = "$ts $url ERROR $err"
      Add-Content $logFile $line
    } finally {
      if ($client) { $client.Dispose() }
    }
  }
  Start-Sleep -Seconds $cycleSeconds
}
# Timeout reached
$ts = (Get-Date).ToString('o')
$summary = @{ result='timeout'; timestamp=$ts; message='No HTTP 200 observed in the configured window' }
$summary | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportFile -Encoding UTF8
Add-Content $logFile "TIMEOUT $ts No HTTP 200 observed"
exit 0
