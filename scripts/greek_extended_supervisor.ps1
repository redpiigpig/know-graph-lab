param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('epicurus', 'epictetus', 'plotinus')]
    [string]$Pipeline,
    [int]$PollSeconds = 30,
    [int]$RetrySeconds = 300
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python -ErrorAction Stop).Source
$state = @{
    epicurus = @{
        Script = 'scripts\epicurus_build.py'
        Args = @('--all', '--engine', 'nvidia', '--resume', '--upload')
    }
    epictetus = @{
        Script = 'scripts\epictetus_build.py'
        Args = @('--all', '--engine', 'auto', '--upload')
    }
    plotinus = @{
        Script = 'scripts\plotinus_build.py'
        Args = @('all', '--engine', 'auto', '--upload')
    }
}[$Pipeline]
$scriptName = [IO.Path]::GetFileName($state.Script)
$pipelineArgs = $state.Args
$log = "C:\tmp\greek_${Pipeline}_supervisor.log"
$output = "C:\tmp\greek_${Pipeline}_supervisor.out.log"

function Write-SupervisorLog([string]$Message) {
    Add-Content -LiteralPath $log -Encoding utf8 -Value "$(Get-Date -Format o) $Message"
}

Set-Location -LiteralPath $repo
Write-SupervisorLog "supervisor started; script=$scriptName"

while ($true) {
    $active = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -match [regex]::Escape($scriptName) })
    if ($active.Count -gt 0) {
        Write-SupervisorLog "waiting for active pids=$($active.ProcessId -join ',')"
        Start-Sleep -Seconds $PollSeconds
        continue
    }

    Write-SupervisorLog "starting resumable verification run"
    & $python $state.Script @pipelineArgs *>> $output
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-SupervisorLog "pipeline complete and verified"
        exit 0
    }

    Write-SupervisorLog "pipeline exited code=$exitCode; retry in ${RetrySeconds}s"
    Start-Sleep -Seconds $RetrySeconds
}
