# Wait for the running _denzinger_gaps_ocr.py process to exit, then
# auto-chain: consolidate → segment dry-run+write-jsonl.
#
# Intentionally does NOT call segment --apply (that needs DB migration first).
# Outputs all stdout/stderr to a single log so caller can grep for outcome.
#
# Usage:
#   pwsh -File scripts/_denzinger_wait_then_pipeline.ps1
#
# Designed to run via Bash run_in_background — harness notifies on completion.

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyy-MM-dd_HH-mm"
$logDir = Join-Path $PSScriptRoot "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "_denzinger_pipeline_$ts.log"

function Log($msg) {
    $line = "[$(Get-Date -Format HH:mm:ss)] $msg"
    Write-Output $line
    Add-Content -Path $log -Value $line -Encoding utf8
}

Log "Pipeline wrapper start — watching for python processes matching '_denzinger_gaps_ocr'."

# Poll every 60s; exit loop when no matching python process remains.
$pollCount = 0
while ($true) {
    $procs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*_denzinger_gaps_ocr*' }
    if (-not $procs) { break }
    $pollCount++
    if ($pollCount % 5 -eq 0) {
        $pidsStr = ($procs | ForEach-Object { $_.ProcessId }) -join ','
        Log "Still running: PIDs=$pidsStr (poll #$pollCount)"
    }
    Start-Sleep -Seconds 60
}

Log "OCR process exited. Starting consolidate."

# Consolidate
& python -X utf8 -u (Join-Path $PSScriptRoot "_denzinger_consolidate.py") 2>&1 |
    ForEach-Object { Log "consolidate> $_" }

if ($LASTEXITCODE -ne 0) {
    Log "consolidate FAILED with exit $LASTEXITCODE — STOP."
    exit 1
}

Log "consolidate done. Running segment dry-run + write-jsonl."

# Segment (dry-run report + write JSONL; NO --apply because DB migration not yet done)
& python -X utf8 -u (Join-Path $PSScriptRoot "segment_denzinger.py") --dry-run --report --write-jsonl 2>&1 |
    ForEach-Object { Log "segment> $_" }

if ($LASTEXITCODE -ne 0) {
    Log "segment FAILED with exit $LASTEXITCODE."
    exit 2
}

Log "ALL DONE — consolidate + segment write-jsonl complete. .bilingual.jsonl written."
Log "Next manual steps: DB migration, then segment --apply."
exit 0
