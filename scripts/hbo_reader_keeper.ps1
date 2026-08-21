# Keep the Hebrew reader's interlinear upgrade running until it is done.
#
# Sonnet stayed rate-limited for three days straight while the fleet and the
# interactive session shared one Claude Max account, so the upgrade engine was
# switched to Gemini, whose quota is separate and per-model. A background shell
# started from a chat session also dies with that session.  This keeper is idempotent:
# it exits immediately when a pass is already running or when every unit is
# already on the target engine, so it can be scheduled on a short interval.
#
# Pure ASCII on purpose: PowerShell 5.1 misparses this file otherwise.

$ErrorActionPreference = 'Stop'
$repo = 'c:\Users\user\Desktop\know-graph-lab'
$python = 'python'
$log = Join-Path $repo 'output\qa\original-readers\hebrew-full\keeper.log'
$target = 'gemini-3.5-flash'

function Write-Log($message) {
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    Add-Content -Path $log -Value "$stamp  $message" -Encoding utf8
}

Set-Location $repo
$env:PYTHONIOENCODING = 'utf-8'

$running = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like '*build_hebrew_interlinear*' }
if ($running) {
    Write-Log 'pass already running; nothing to do'
    exit 0
}

$masterPath = Join-Path $repo 'output\source-cache\original-readers\hebrew-full\interlinear.json'
if (-not (Test-Path $masterPath)) {
    Write-Log 'no interlinear master yet; nothing to do'
    exit 0
}
$master = Get-Content $masterPath -Raw -Encoding utf8 | ConvertFrom-Json
$stale = @($master.units.PSObject.Properties | Where-Object { $_.Value.engine -ne $target })
if ($stale.Count -eq 0) {
    Write-Log 'every unit is already on the target engine; keeper idle'
    exit 0
}

Write-Log "$($stale.Count) units still below $target; starting an upgrade pass"
& $python 'scripts/build_hebrew_interlinear.py' '--model' 'gemini' '--upgrade' '--workers' '3' '--rounds' '6' '--probe-attempts' '20' 2>&1 |
    ForEach-Object { Write-Log $_ }

$master = Get-Content $masterPath -Raw -Encoding utf8 | ConvertFrom-Json
$stale = @($master.units.PSObject.Properties | Where-Object { $_.Value.engine -ne $target })
Write-Log "pass finished; $($stale.Count) units still below $target"

# Rebuild the printed artifacts only once the whole book is on the target engine,
# so a half-upgraded PDF never lands in output/.
if ($stale.Count -eq 0) {
    Write-Log 'rebuilding DOCX/PDF and running the release gate'
    & $python 'scripts/build_hebrew_full_reader.py' 2>&1 | ForEach-Object { Write-Log $_ }
    & 'C:\Program Files\LibreOffice\program\soffice.com' --headless --norestore --convert-to pdf `
        --outdir "$repo\output\original-readers" `
        "$repo\output\original-readers\hebrew-original-reader-50-lessons.docx" 2>&1 | Out-Null
    & $python 'scripts/qa_hebrew_full_reader.py' 2>&1 | ForEach-Object { Write-Log $_ }
    Write-Log 'done'
}
