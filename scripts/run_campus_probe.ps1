# Campus-gated probe runner for KGL_Campus_Probe.
#
# ASCII ONLY. PowerShell 5.1 mis-parses this file if it contains CJK comments:
# param() stops being recognised and you get "The assignment expression is not
# valid", with line numbers that do not match the file. Same trap as
# fleet_keeper.ps1 and run_airiti_batch.ps1. Chinese rationale lives in
# .claude/skills/research-data-theology/SKILL.md.
#
# What it does:
#   1. Cheap gate: campus_probe.py --check exits 0 only when Airiti recognises
#      the institution (i.e. we are on the Hsuan Chuang network). Off campus it
#      exits 1 and this script stops -- costs one HTTP request.
#   2. Once per day, when on campus, run the full probe so the harvest plan gets
#      real access results instead of "unknown".
#
# Why launch python through Start-Process with a hidden window:
#   CTRL_C_EVENT goes to every process attached to a console. A scheduled task
#   sharing a console with anything else can be taken down by someone else's
#   Ctrl+C, and Task Scheduler still reports success. Give python its own hidden
#   console. (2026-09-07, KGL_Airiti_Poll died this way for days.)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$py = 'python'
$log = 'C:\tmp\campus_probe.log'
$stamp = Join-Path $repo 'scripts\state\campus_probe_lastfull.txt'

function Write-Log([string]$msg) {
    $line = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -Path $log -Value $line -Encoding UTF8
}

function Invoke-Py([string[]]$pyArgs) {
    $out = [System.IO.Path]::GetTempFileName()
    $err = [System.IO.Path]::GetTempFileName()
    $p = Start-Process -FilePath $py -ArgumentList $pyArgs -WorkingDirectory $repo `
        -WindowStyle Hidden -PassThru -Wait `
        -RedirectStandardOutput $out -RedirectStandardError $err
    foreach ($f in @($out, $err)) {
        if ((Test-Path $f) -and (Get-Item $f).Length -gt 0) {
            # Read as UTF8 explicitly: python writes UTF-8, and Get-Content
            # without -Encoding uses the ANSI codepage (Big5 here), which
            # mangles the text twice on the way into a UTF-8 log.
            Get-Content $f -Encoding UTF8 | ForEach-Object { Write-Log $_ }
        }
        Remove-Item $f -ErrorAction SilentlyContinue
    }
    return $p.ExitCode
}

New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $stamp) | Out-Null

$code = Invoke-Py @('-X', 'utf8', 'scripts/campus_probe.py', '--check')
if ($code -ne 0) { exit 0 }   # not on campus: quiet no-op, this is the normal case

$today = Get-Date -Format 'yyyy-MM-dd'
$last = if (Test-Path $stamp) { (Get-Content $stamp -Encoding UTF8 -Raw).Trim() } else { '' }
if ($last -eq $today) {
    Write-Log 'on campus, full probe already done today'
    exit 0
}

Write-Log 'on campus: running full probe'
$code = Invoke-Py @('-X', 'utf8', 'scripts/campus_probe.py')
if ($code -eq 0) {
    Set-Content -Path $stamp -Value $today -Encoding UTF8
    Write-Log 'full probe finished'
} else {
    Write-Log ('full probe exited ' + $code)
}
exit 0
