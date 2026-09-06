@ECHO OFF

if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit /b)

set /p what_to_do=enable or disable windows defender?:
if "%what_to_do%"=="disable" (
	set state=1
) else (
	if "%what_to_do%"=="enable" (
		set state=0
	) else (
		echo choice isn't recognized
		goto end
	)
)

reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableScanOnRealtimeEnable /t REG_DWORD /d %state% /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d %state% /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableBehaviorMonitoring /t REG_DWORD /d %state% /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableOnAccessProtection /t REG_DWORD /d %state% /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v DisableRealtimeMonitoring /t REG_DWORD /d %state% /f
echo ok

:end
pause