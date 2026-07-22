# Fleet keeper: every 30 min (Windows task KGL_Fleet_Keeper) self-heals translation/OCR lanes.
# If a lane's worker is not running, relaunch it. The 30-min cadence IS the retry mechanism.
# Direct Start-Process python.exe + arg array (avoids nested-string / redirect PS parse traps).
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts and breaks parsing.
$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT
$log = "$ROOT\scripts\logs\fleet_keeper.log"
$py = 'python.exe'
function Note($m) { Add-Content $log ("[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m) }
function Running($pat) {
    [bool](Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
        Where-Object { $_.CommandLine -match $pat })
}
function Ensure($label, $pat, $argv) {
    if (Running $pat) { return }
    Note "relaunch $label"
    Start-Process $py -ArgumentList $argv -WindowStyle Hidden -WorkingDirectory $ROOT
}

# Overnight ACCS priority (user 2026-07-22): ACCS OCR owns Gemini; jung + philo on NVIDIA.
# jung: full 19-vol CW queue (9ii/11/12 done, resume skips them); NVIDIA keeps Gemini for ACCS.
Ensure 'jung-queue' 'jung_cw_translate|jung_run_queue' @('-X','utf8','scripts\jung_run_queue.py','--engine','nvidia')
Ensure 'philo-queue' 'plato_build|plato_run_queue' @('-X','utf8','scripts\plato_run_queue.py','--engine','nvidia')
# Panikkar last volume (vedic-experience, huge): on Haiku per user (idle Claude account).
# When it finishes, replace this lane with Max Weber (sociology) collected works.
Ensure 'panikkar-vedic' 'panikkar_auto' @('-X','utf8','scripts\panikkar_auto.py','--work','vedic-experience','--backend','haiku','--upload')
Ensure 'uchimura' 'uchimura_auto' @('-X','utf8','scripts\uchimura_auto.py','--run-queue')
# dadaodao research-materials fulltext translation (NVIDIA, 7 keys, off Claude/Gemini)
Ensure 'dadaodao' 'dadaodao_translate' @('-X','utf8','scripts\dadaodao_translate.py','--engine','nvidia')
# Sacred Books of the East: dedicate the (now-idle) Claude account via Haiku to remaining 5 volumes
Ensure 'sbe-haiku' 'sbe_translate' @('-X','utf8','scripts\sbe_translate.py','--loop','--only','sbe-04-zend-avesta-1,sbe-06-quran-1,sbe-10-dhammapada,sbe-16-yi-king,sbe-22-jaina-1','--backend','haiku')

# ACCS campus OCR — overnight priority (user 2026-07-22): Matthew done → full Gemini
# batch-4 queue for mrk/luk/... . jung+philo moved to NVIDIA so ACCS owns Gemini.
# Gemini-gated: only launch when a key has quota (else the driver just bails).
if (-not (Running 'accs_ocr_run|ingest_accs_genesis')) {
    python -X utf8 scripts\gemini_probe.py *> $null
    if ($LASTEXITCODE -eq 0) {
        Note "Gemini has quota -> ACCS OCR queue (gemini batch-4, NT first)"
        Start-Process $py -ArgumentList @('-X','utf8','scripts\accs_ocr_run.py','--engine','gemini','--batch','4') -WindowStyle Hidden -WorkingDirectory $ROOT
    }
}
Note "keeper tick done"
