param(
    [ValidateSet('auto', 'gemini', 'nvidia', 'haiku', 'sonnet')]
    [string]$Engine = 'auto',
    [int]$PollSeconds = 30
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python -ErrorAction Stop).Source
$log = 'C:\tmp\greek_translation_supervisor.log'

function Write-SupervisorLog([string]$Message) {
    $line = "$(Get-Date -Format o) $Message"
    Add-Content -LiteralPath $log -Encoding utf8 -Value $line
}

Set-Location -LiteralPath $repo
Write-SupervisorLog "waiting for direct plato_build workers"

do {
    $workers = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -match 'scripts[\\/]plato_build\.py' })
    if ($workers.Count -gt 0) {
        Write-SupervisorLog "active direct workers=$($workers.Count); pids=$($workers.ProcessId -join ',')"
        Start-Sleep -Seconds $PollSeconds
    }
} while ($workers.Count -gt 0)

while ($true) {
    Write-SupervisorLog "starting greek_overnight engine=$Engine"
    & $python scripts\greek_overnight.py --engine $Engine *>> C:\tmp\greek_translation_supervisor.out.log
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-SupervisorLog "greek_overnight complete"
        exit 0
    }
    Write-SupervisorLog "greek_overnight exited code=$exitCode; retry in 300s"
    Start-Sleep -Seconds 300
}
