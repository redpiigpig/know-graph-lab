# Fathers realign+fill keeper (Windows task KGL_Fathers_Fill, every 30 min).
#
# Relaunches scripts\fathers_lane.py --run when no worker is alive. The lane realigns each of
# the 37 Schaff volumes once and then translates the English rows that have no Chinese
# counterpart (Gemini -> NVIDIA only, never Haiku/Claude). It writes progress after every
# batch (apply_edits re-reads the file and only fills still-blank rows), so a run killed by
# sleep or by quota resumes where it stopped. The 30-min cadence IS the retry mechanism.
#
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts.
# It disables ITSELF when lane_state.json says all_done. Never set ExecutionTimeLimit to PT0S.

$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT

$py     = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$log    = "$ROOT\scripts\logs\fathers_fill_keeper.log"
$runlog = "$ROOT\output\fathers_gap\lane_run.log"
$task   = 'KGL_Fathers_Fill'

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

$running = @(Get-CimInstance Win32_Process -Filter "Name like '%python%'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*fathers_lane.py*--run*' })
if ($running.Count -gt 0) {
    Note "lane already running (pid $($running[0].ProcessId)) - skip"
    exit 0
}

$env:PYTHONIOENCODING = 'utf-8'
$status = ''
try {
    $script = Join-Path $ROOT ("scripts" + [char]92 + "fathers_lane.py")
    $status = (& $py -X utf8 $script --status 2>$null | Select-Object -Last 1)
} catch { Note "status failed: $($_.Exception.Message)" }

if ("$status".Trim() -eq 'DONE') {
    Note "all volumes realigned and filled; disabling $task"
    try { Disable-ScheduledTask -TaskName $task -ErrorAction Stop | Out-Null }
    catch { Note "disable failed: $($_.Exception.Message)" }
    exit 0
}

Note "status=$status; launching lane"
try {
    Start-Process -FilePath $py `
        -ArgumentList @('-X', 'utf8', "$ROOT\scripts\fathers_lane.py", '--run') `
        -WorkingDirectory $ROOT -WindowStyle Hidden `
        -RedirectStandardOutput $runlog -RedirectStandardError "$runlog.err"
} catch {
    Note "launch failed: $($_.Exception.Message)"
}
