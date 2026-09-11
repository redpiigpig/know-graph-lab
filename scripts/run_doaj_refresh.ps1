# Weekly DOAJ refresh for KGL_DOAJ_Weekly.
#
# ASCII ONLY. PowerShell 5.1 mis-parses this file if it contains CJK comments:
# param() stops being recognised and the error messages point at the wrong
# lines. Same trap as fleet_keeper.ps1 and run_airiti_batch.ps1. The Chinese
# rationale lives in .claude/skills/research-data-theology/SKILL.md.
#
# Weekly, not daily: DOAJ journals publish by issue, so a daily run would spend
# ~300 HTTP requests to find nothing. The harvester skips journals whose jsonl
# already exists, so a refresh only costs new journals unless --force is given.
#
# Step 1 re-reads the journal list (new titles get added to DOAJ constantly).
# Step 2 fetches articles for journals that have no file yet.
# Step 3 rebuilds the site index so the page reflects the new totals.
#
# python goes through Start-Process so it gets its own hidden console:
# CTRL_C_EVENT reaches every process sharing a console, and a scheduled task
# that shares one can be killed by someone else's Ctrl+C while Task Scheduler
# still reports success (KGL_Airiti_Poll died that way for days in 2026-09).

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$py = 'python'
$log = 'C:\tmp\doaj_refresh.log'

function Write-Log([string]$msg) {
    Add-Content -Path $log -Encoding UTF8 `
        -Value ('{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
}

function Invoke-Py([string[]]$pyArgs) {
    $out = [System.IO.Path]::GetTempFileName()
    $err = [System.IO.Path]::GetTempFileName()
    $p = Start-Process -FilePath $py -ArgumentList $pyArgs -WorkingDirectory $repo `
        -WindowStyle Hidden -PassThru -Wait `
        -RedirectStandardOutput $out -RedirectStandardError $err
    foreach ($f in @($out, $err)) {
        if ((Test-Path $f) -and (Get-Item $f).Length -gt 0) {
            # Read as UTF8 explicitly. python writes UTF-8; Get-Content without
            # -Encoding uses the ANSI codepage (Big5 here) and mangles it twice.
            Get-Content $f -Encoding UTF8 | ForEach-Object { Write-Log $_ }
        }
        Remove-Item $f -ErrorAction SilentlyContinue
    }
    return $p.ExitCode
}

# Drive must be mounted: article jsonl lives under G:\...\_corpus\doaj.
# A stalled DriveFS unmounts the volume and never remounts itself, so check
# rather than write into a path that silently is not there.
if (-not (Test-Path 'G:\我的雲端硬碟')) {
    Write-Log 'G: not mounted, skipping (see CLAUDE.md for the restart recipe)'
    exit 0
}

New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
Write-Log 'refresh start'
Invoke-Py @('-X', 'utf8', 'scripts/doaj_harvest.py', '--journals') | Out-Null
Invoke-Py @('-X', 'utf8', 'scripts/doaj_harvest.py', '--articles') | Out-Null
Invoke-Py @('-X', 'utf8', 'scripts/doaj_harvest.py', '--index') | Out-Null
Write-Log 'refresh done'
exit 0
