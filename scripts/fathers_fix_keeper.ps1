# Fathers heading-swallow fix keeper (Windows task KGL_Fathers_Fix, every 30 min).
# Relaunches fix_fathers_heading_swallow.py when no worker is alive. The job is
# idempotent and writes one book at a time, so a killed run loses nothing.
# ASCII-only on purpose: PS 5.1 on a zh-TW box misparses UTF-8-no-BOM scripts.
$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT
$log = "$ROOT\scripts\logs\fathers_fix_keeper.log"
function Note($m) { Add-Content $log ("[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m) }

$running = [bool](Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
    Where-Object { $_.CommandLine -match 'fix_fathers_heading_swallow' })
if ($running) { Note 'worker alive, skip'; exit 0 }

Note 'relaunch fathers heading fix (limit 3)'
Start-Process 'python.exe' -ArgumentList @('-X','utf8','scripts\fix_fathers_heading_swallow.py','--apply','--no-gemini','--limit','3') -WindowStyle Hidden -WorkingDirectory $ROOT
