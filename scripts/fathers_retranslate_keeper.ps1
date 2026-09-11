# Fathers re-translation keeper (Windows task KGL_Fathers_Retranslate, every 20 min).
#
# Fills back the 1,677 chunks whose "Chinese" column is actually English
# (scripts/fathers_retranslate_untranslated.py). 90% of them sit in ANF Vol 2.
#
# Why a scheduled task: this laptop sleeps on the commute and a detached
# Start-Process dies with it; only the scheduler survives, and only with
# StartWhenAvailable does a slot missed while asleep get picked up afterwards.
# The 20-min cadence IS the retry mechanism -- the worker writes back every five
# chunks, so a run killed mid-way resumes where it stopped.
#
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts.
#
# It disables ITSELF once nothing is left to translate. A keeper with no work
# spins forever and the completion signal is the OUTPUT, not the task state.

$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT

$py     = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$log    = "$ROOT\scripts\logs\fathers_retranslate.log"
$runlog = "$ROOT\scripts\logs\fathers_retranslate_run.log"
$task   = 'KGL_Fathers_Retranslate'

function Note($m) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m
    for ($i = 0; $i -lt 3; $i++) {
        try {
            $fs = New-Object System.IO.FileStream($log, [System.IO.FileMode]::Append,
                [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite)
            $sw = New-Object System.IO.StreamWriter($fs)
            $sw.WriteLine($line); $sw.Flush(); $sw.Close(); $fs.Close()
            return
        } catch { Start-Sleep -Milliseconds 200 }
    }
}

$running = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*fathers_retranslate_untranslated*--apply*' })
if ($running.Count -gt 0) {
    Note "worker already running (pid $($running[0].ProcessId)) - skip"
    exit 0
}

# How much is left? --count prints a bare integer and makes no LLM calls.
$env:PYTHONIOENCODING = 'utf-8'
$left = -1
try {
    $script = Join-Path $ROOT ("scripts" + [char]92 + "fathers_retranslate_untranslated.py")
    $out = (& $py $script --count 2>$null | Select-Object -Last 1)
    if ("$out".Trim() -match '^\d+$') { $left = [int]"$out".Trim() }
} catch { Note "scan failed: $($_.Exception.Message)" }
if ($left -lt 0) { Note 'scan gave no number; leaving the task armed'; exit 0 }

if ($left -eq 0) {
    Note "nothing left to translate; disabling $task"
    try { Disable-ScheduledTask -TaskName $task -ErrorAction Stop | Out-Null }
    catch { Note "disable failed: $($_.Exception.Message)" }
    exit 0
}

Note "$left chunks left; launching worker"
try {
    Start-Process -FilePath $py `
        -ArgumentList @("$ROOT\scripts\fathers_retranslate_untranslated.py", '--all', '--apply', '--engine', 'auto') `
        -WorkingDirectory $ROOT -WindowStyle Hidden `
        -RedirectStandardOutput $runlog -RedirectStandardError "$runlog.err"
} catch {
    Note "launch failed: $($_.Exception.Message)"
}
