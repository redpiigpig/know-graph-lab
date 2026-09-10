# Husserl Ideen I Vision-OCR keeper (Windows task KGL_Husserl_OCR, every 20 min).
#
# Why a scheduled task and not a background process: this laptop sleeps on the commute,
# and a detached Start-Process dies with it. Only the scheduler survives, and only with
# StartWhenAvailable does a slot missed while asleep get picked up afterwards.
# See memory feedback_laptop_sleeps_design_for_resume.
#
# The 20-min cadence IS the retry mechanism: husserl_build.py --ocr is resumable
# (one cache file per 8-page batch), so a run that dies on a Gemini quota wall simply
# resumes at the next tick. Nothing to reset by hand.
#
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts and breaks
# parsing (memory project_fleet_keeper).
#
# It disables ITSELF once every batch is cached. A keeper with no work left spins forever
# and the completion signal is the OUTPUT, not the task state
# (memory feedback_disable_finished_schedules).

$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT

$py       = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$log      = "$ROOT\scripts\logs\husserl_ocr.log"
$runlog   = "$ROOT\scripts\logs\husserl_ocr_run.log"
$ocrDir   = 'c:\tmp\husserl_cache\ocr'
$expected = 59          # 472 scanned pages / 8 per batch
$taskName = 'KGL_Husserl_OCR'

function Note($m) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m
    # A `tail -f` on the log holds a Windows share lock that makes Add-Content throw.
    # Open it ourselves with FileShare::ReadWrite so a reader can never silence us.
    for ($i = 0; $i -lt 3; $i++) {
        try {
            $fs = New-Object System.IO.FileStream($log, [System.IO.FileMode]::Append,
                [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite)
            $sw = New-Object System.IO.StreamWriter($fs)
            $sw.WriteLine($line); $sw.Flush(); $sw.Close(); $fs.Close()
            return
        } catch {
            Start-Sleep -Milliseconds 200
        }
    }
}

$done = 0
if (Test-Path -LiteralPath $ocrDir) {
    $done = @(Get-ChildItem -LiteralPath $ocrDir -Filter 'b*.json' -ErrorAction SilentlyContinue).Count
}

if ($done -ge $expected) {
    Note "all $done/$expected batches cached; disabling $taskName"
    try { Disable-ScheduledTask -TaskName $taskName -ErrorAction Stop | Out-Null }
    catch { Note "disable failed: $($_.Exception.Message)" }
    exit 0
}

$running = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*husserl_build*--ocr*' })
if ($running.Count -gt 0) {
    Note "$done/$expected cached; worker already running (pid $($running[0].ProcessId)) - skip"
    exit 0
}

Note "$done/$expected cached; relaunching OCR worker"
$env:PYTHONIOENCODING = 'utf-8'
try {
    Start-Process -FilePath $py -ArgumentList @('scripts/husserl_build.py', '--ocr') `
        -WorkingDirectory $ROOT -WindowStyle Hidden `
        -RedirectStandardOutput $runlog -RedirectStandardError "$runlog.err"
} catch {
    Note "launch failed: $($_.Exception.Message)"
}
