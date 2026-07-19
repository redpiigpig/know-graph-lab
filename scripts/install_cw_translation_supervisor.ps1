<#
  Register scheduled task KGL_CW_Translation: wakes every N min, runs cw_translation_supervisor.ps1
  (single Haiku line, resumes modern classics + greek sequentially; guard prevents concurrency,
  MultipleInstances IgnoreNew prevents overlap).
  Usage: powershell -ExecutionPolicy Bypass -File scripts\install_cw_translation_supervisor.ps1 [-Engine haiku] [-IntervalMinutes 30]
#>
param(
    [int]$IntervalMinutes = 30
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ps = (Get-Command powershell.exe -ErrorAction Stop).Source
$script = Join-Path $root 'scripts\cw_translation_supervisor.ps1'
$taskName = 'KGL_CW_Translation'

if (-not (Test-Path -LiteralPath $script)) { throw "supervisor not found: $script" }

$arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""
$action = New-ScheduledTaskAction -Execute $ps -Argument $arguments -WorkingDirectory $root

# triggers: at logon + repeat every IntervalMinutes (periodic wake)
$atLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($atLogon, $repeat) `
    -Settings $settings -Principal $principal -Force `
    -Description "Collected-works modern-classics translation supervisor: wakes every $IntervalMinutes min, single Haiku line (lockfile-guarded), resumes modern_classics_auto." | Out-Null

Start-ScheduledTask -TaskName $taskName
Write-Output "installed_and_started=$taskName interval=${IntervalMinutes}min"
