$desktop = [Environment]::GetFolderPath('Desktop')
$envId = "d5b42781-da97-e29a-a5bc-d88f977ebd01"

$agents = @(
    @{ Name = "OsintNeoAi Sentinel Agent"; Id = "e6781ec6-79e6-4868-90be-60e88d51435b" },
    @{ Name = "OsintNeoAi Master Agent"; Id = "3bda9cdd-4646-47bf-8e7a-4d02547f01bf" },
    @{ Name = "Truth & Fact Audit Agent"; Id = "af9caeaa-991a-4dbc-9a48-ad2ebb8d60f2" },
    @{ Name = "HUD Housing Verifier Agent"; Id = "7450e379-710b-404f-923d-9ac7150384e9" }
)

$ws = New-Object -ComObject WScript.Shell
foreach ($agent in $agents) {
    $path = Join-Path $desktop "$($agent.Name).url"
    $s = $ws.CreateShortcut($path)
    $s.TargetPath = "https://copilotstudio.microsoft.com/environments/$envId/bots/$($agent.Id)/canvas"
    $s.Save()
    Write-Host "[+] Created desktop shortcut: $path"
}
