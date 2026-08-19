$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'

$report = 'scripts\logs\accs_gen_12-50_progress.log'
$checkpoint = Get-ChildItem 'c:\tmp' -Filter 'accs_gen_*創12-50.raw.jsonl' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
$done = Get-ChildItem 'c:\tmp' -Filter 'accs_gen_*創12-50.raw.done' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
$log = Get-Item 'scripts\logs\accs_gen_12-50.log' -ErrorAction SilentlyContinue

$checkpointLines = $null
if ($checkpoint) {
    $checkpointLines = (Get-Content -LiteralPath $checkpoint.FullName -Encoding UTF8 | Measure-Object -Line).Lines
}

$taskInfo = Get-ScheduledTaskInfo -TaskName 'ACCS_Gen2_Resume' -ErrorAction SilentlyContinue
$task = Get-ScheduledTask -TaskName 'ACCS_Gen2_Resume' -ErrorAction SilentlyContinue

$db = 'C:\tmp\q_accs.mjs not found'
if (Test-Path 'C:\tmp\q_accs.mjs') {
    $db = (& node 'C:\tmp\q_accs.mjs' 2>&1) -join "`n"
}

$now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$lines = @(
    "=== ACCS Gen 12-50 progress $now ===",
    "task_state=$($task.State) last_run=$($taskInfo.LastRunTime) last_result=$($taskInfo.LastTaskResult) next_run=$($taskInfo.NextRunTime)",
    "db=$db",
    "checkpoint_lines=$checkpointLines checkpoint_write=$($checkpoint.LastWriteTime) checkpoint_bytes=$($checkpoint.Length)",
    "main_log_write=$($log.LastWriteTime) main_log_bytes=$($log.Length)",
    "done_exists=$([bool]$done) done_file=$($done.FullName)",
    ""
)

$lines | Add-Content -LiteralPath $report -Encoding UTF8
