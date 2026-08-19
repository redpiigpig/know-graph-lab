$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pythonw = 'C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe'
$script = Join-Path $root 'scripts\translation_cloud_supervisor.py'
$taskName = 'KGL_Cloud_Translation_Supervisor'
$arguments = "-X utf8 `"$script`" run --project genesis-philosophy --cooldown-seconds 1800"
$action = New-ScheduledTaskAction -Execute $pythonw -Argument $arguments -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
  -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 2) `
  -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
  -Settings $settings -Principal $principal `
  -Description 'KGL cloud pool: 7 pinned-key translators plus Gemini #4 full reviewer.' -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Output "installed_and_started=$taskName"
