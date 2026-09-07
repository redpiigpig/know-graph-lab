# Airiti full-text scheduled batch. Args: <articles this run> <articles today>.
#
# ASCII ONLY. PowerShell 5.1 mis-parses this file if it contains CJK comments:
# the param() block stops being recognised and you get
#   "The assignment expression is not valid" at [int]$Batch = 100
# with line numbers that do not match the file. Same trap as fleet_keeper.ps1.
# The Chinese rationale lives in .claude/skills/research-data-airiti/SKILL.md.
#
# Why not call run_airiti_batch.bat directly:
#   2026-09-07: the scheduled runs died after ~1 minute with a bare `^C`, having
#   downloaded only 2-3 articles, while Task Scheduler reported "successfully
#   completed". Fleet Keeper was ruled out (it only kills pids in its own state
#   files, and it killed nothing that day) and so was Task Scheduler itself.
#   The remaining difference is the CONSOLE: the failing task was cmd.exe ->
#   python.exe (has a console), while KGL_Translation_Supervisor, which polls on
#   the same 30-minute cadence and never dies, runs pythonw.exe (no console).
#   CTRL_C_EVENT goes to every process attached to a console, so sharing one is
#   enough to get taken down by someone else's Ctrl+C.
#
#   So: launch python through Start-Process so it gets its own hidden console,
#   mirroring fleet_keeper.ps1. Output goes to temp files and is appended to the
#   main log afterwards (Start-Process can only truncate, never append).
#
# The 6-second gap between downloads is a promise to the institution IP, not a
# tuning knob. Raise the daily total (second arg) instead of lowering DELAY_DL.
param(
    [int]$Batch = 100,
    [int]$DailyCap = 500
)

$ErrorActionPreference = 'Stop'
$root = 'C:\Users\user\Desktop\know-graph-lab'
$log = 'C:\tmp\airiti_download.log'
$py = 'C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$tmpOut = 'C:\tmp\airiti_batch.out.tmp'
$tmpErr = 'C:\tmp\airiti_batch.err.tmp'

$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

# Header is written as UTF-8. The old .bat used cmd's echo, which lands as Big5
# and leaves the log needing two decoders to read one file.
$header = "`r`n===== {0}  batch {1} (cap {2}) =====" -f `
    (Get-Date -Format 'yyyy/MM/dd HH:mm:ss'), $Batch, $DailyCap
Add-Content -LiteralPath $log -Value $header -Encoding UTF8

$argv = @('-X', 'utf8', '-u', 'scripts\press_airiti.py',
          '--batch', "$Batch", '--daily-cap', "$DailyCap")
$proc = Start-Process $py -ArgumentList $argv -WorkingDirectory $root `
    -WindowStyle Hidden -RedirectStandardOutput $tmpOut -RedirectStandardError $tmpErr `
    -PassThru -Wait

# Read the temp files back AS UTF-8. Python writes UTF-8 (PYTHONIOENCODING), but
# Get-Content without -Encoding uses the ANSI codepage (Big5 here), so the text is
# mangled on the way in and then re-encoded as UTF-8 on the way out - wrecked
# twice, while the script still exits 0 and the log still looks populated.
foreach ($f in @($tmpOut, $tmpErr)) {
    if ((Test-Path -LiteralPath $f) -and (Get-Item -LiteralPath $f).Length -gt 0) {
        Add-Content -LiteralPath $log -Encoding UTF8 `
            -Value (Get-Content -LiteralPath $f -Raw -Encoding UTF8)
    }
    Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue
}
Add-Content -LiteralPath $log -Value ("----- exit {0}" -f $proc.ExitCode) -Encoding UTF8
exit $proc.ExitCode
