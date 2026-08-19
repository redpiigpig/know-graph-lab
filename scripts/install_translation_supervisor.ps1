param(
  [int]$IdleSeconds = 0,
  [int]$StepParagraphs = 3
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pythonw = 'C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe'
$script = Join-Path $root 'scripts\translation_supervisor.py'
$taskName = 'KGL_Translation_Supervisor'

if (-not (Test-Path -LiteralPath $pythonw)) {
  throw "pythonw not found: $pythonw"
}

$arguments = "-X utf8 `"$script`" run --interval 60 --idle-seconds $IdleSeconds --step-paras $StepParagraphs"
$action = New-ScheduledTaskAction -Execute $pythonw -Argument $arguments -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -RestartCount 3 `
  -RestartInterval (New-TimeSpan -Minutes 2) `
  -ExecutionTimeLimit ([TimeSpan]::Zero) `
  -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
  -Settings $settings -Principal $principal -Description `
  'KGL deterministic local-first translation supervisor; runs whenever Windows is awake.' `
  -Force | Out-Null

Start-ScheduledTask -TaskName $taskName
Write-Output "installed_and_started=$taskName"
