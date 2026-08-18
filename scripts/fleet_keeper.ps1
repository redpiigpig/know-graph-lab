# Fleet keeper: every 30 min (Windows task KGL_Fleet_Keeper) self-heals translation/OCR lanes.
# If a lane's worker is not running, relaunch it. The 30-min cadence IS the retry mechanism.
# Direct Start-Process python.exe + arg array (avoids nested-string / redirect PS parse traps).
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts and breaks parsing.
$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT
$log = "$ROOT\scripts\logs\fleet_keeper.log"
$py = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
function Note($m) { Add-Content $log ("[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m) }
if (Test-Path "$ROOT\scripts\state\fleet_keeper.pause") {
    Note 'keeper paused by monitor; no lanes relaunched'
    exit 0
}
$slotFile = "$ROOT\scripts\state\gemini_live_slot.txt"
if (Test-Path -LiteralPath $slotFile) {
    $slot = (Get-Content -LiteralPath $slotFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($slot -match '^[1-9][0-9]*$') {
        $env:KGL_GEMINI_SLOT = $slot
        Note "Gemini pinned to validated slot $slot"
    }
}
function LaneName($label) {
    ($label -replace '[^A-Za-z0-9_-]', '_')
}
function LanePaused($label) {
    $lane = LaneName $label
    Test-Path -LiteralPath "$ROOT\scripts\state\fleet_$lane.pause"
}
# A lane whose log has not advanced in this long is wedged, not working. 2026-08-18:
# the ACCS worker sat on one Gemini call for 49 min (24h alive, 76s CPU) because the
# SDK had no request timeout - and the keeper never relaunched it, since the process
# was still technically alive. Liveness must mean progress, not just a live pid.
$STALL_MINUTES = 45
function WorkerAlive($label) {
    $lane = LaneName $label
    $pidFile = "$ROOT\scripts\state\fleet_$lane.pid"
    if (-not (Test-Path -LiteralPath $pidFile)) { return $false }
    $workerPid = (Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($workerPid -and (Get-Process -Id ([int]$workerPid) -ErrorAction SilentlyContinue)) {
        $out = "$ROOT\scripts\logs\fleet_$lane.out.log"
        if (Test-Path -LiteralPath $out) {
            $idle = ((Get-Date) - (Get-Item -LiteralPath $out).LastWriteTime).TotalMinutes
            if ($idle -gt $STALL_MINUTES) {
                Note ("wedged {0}: log idle {1:N0} min -> kill pid {2} and relaunch" -f $label, $idle, $workerPid)
                # /T so the ingest/build grandchild dies too, else it keeps the pipe open.
                & taskkill /F /T /PID $workerPid *> $null
                Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
                return $false
            }
        }
        return $true
    }
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    return $false
}
function Launch($label, $argv) {
    $lane = LaneName $label
    $out = "$ROOT\scripts\logs\fleet_$lane.out.log"
    $err = "$ROOT\scripts\logs\fleet_$lane.err.log"
    $proc = Start-Process $py -ArgumentList $argv -WindowStyle Hidden -WorkingDirectory $ROOT `
        -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
    Set-Content -LiteralPath "$ROOT\scripts\state\fleet_$lane.pid" -Value $proc.Id -Encoding ascii
    Note "started $label pid=$($proc.Id)"
}
function Ensure($label, $pat, $argv) {
    if (LanePaused $label) {
        Note "lane paused: $label"
        return
    }
    if (WorkerAlive $label) { return }
    Note "relaunch $label"
    Launch $label $argv
}

# ACCS FIRST (user 2026-08-17): campus ACCS OCR is the top priority and OWNS the
# Gemini pool - every other lane is on NVIDIA/OpenRouter/local so nothing competes
# for Gemini Vision quota. Gemini-gated: only launch when a key has quota.
if (LanePaused 'accs-gemini') {
    Note 'lane paused: accs-gemini'
} elseif (-not (WorkerAlive 'accs-gemini')) {
    Remove-Item -LiteralPath "$ROOT\scripts\state\gemini_live_model.txt" -Force -ErrorAction SilentlyContinue
    & $py -X utf8 scripts\gemini_probe.py *> $null
    if ($LASTEXITCODE -eq 0) {
        # Free-tier daily quota is per MODEL (20/day/key/model as of 2026-08), so the
        # probe reports which model still has room; pin the lane to it for this pass.
        $liveModel = ''
        $mf = "$ROOT\scripts\state\gemini_live_model.txt"
        if (Test-Path -LiteralPath $mf) {
            $liveModel = (Get-Content -LiteralPath $mf -ErrorAction SilentlyContinue | Select-Object -First 1)
        }
        if ($liveModel) { $env:GEMINI_MODEL = $liveModel.Trim() }
        Note "Gemini has quota on $($env:GEMINI_MODEL) -> ACCS OCR queue (batch-4, NT first)"
        Launch 'accs-gemini' @('-X','utf8','scripts\accs_ocr_run.py','--engine','gemini','--batch','4')
    } else {
        # Gemini dry on every key x every model -> fall back to Sonnet (user 2026-08-17).
        # Sonnet runs on the Claude Max OAuth token, so this costs no extra spend; ACCS
        # keeps moving overnight instead of idling until the daily quota resets.
        Note 'Gemini dry on all keys x all models -> ACCS OCR queue on Sonnet'
        Launch 'accs-gemini' @('-X','utf8','scripts\accs_ocr_run.py','--engine','sonnet','--batch','4')
    }
}

# Aquinas second (user 2026-08-17): Summa 17 vols, conservative OCR cleanup on the
# OpenRouter free pool (8 keys, own pool - does not touch Gemini/NVIDIA quota).
# clean_body caches per article under c:\tmp\aquinas_clean, so each pass only pays
# for what is still dirty; --upload is idempotent (upsert + replace chunks).
Ensure 'aquinas' 'aquinas_build' @('-X','utf8','scripts\aquinas_build.py','--all','--clean','--engine','openrouter','--upload')

# Overnight ACCS priority (user 2026-07-22): ACCS OCR owns Gemini; jung + philo on NVIDIA.
# jung: full 19-vol CW queue (9ii/11/12 done, resume skips them); NVIDIA keeps Gemini for ACCS.
Ensure 'jung-queue' 'jung_cw_translate|jung_run_queue' @('-X','utf8','scripts\jung_run_queue.py','--engine','nvidia','--no-upload')
Ensure 'philo-queue' 'plato_build|plato_run_queue' @('-X','utf8','scripts\plato_run_queue.py','--engine','nvidia','--no-upload')
# Panikkar last volume (vedic-experience, huge): on Haiku per user (idle Claude account).
# When it finishes, replace this lane with Max Weber (sociology) collected works.
# Moved off Gemini 2026-08-17 so ACCS owns the Gemini pool (see top of file).
Ensure 'panikkar-vedic' 'panikkar_auto' @('-X','utf8','scripts\panikkar_auto.py','--work','vedic-experience','--backend','nvidia')
# Uchimura first-wave cache is already complete; do not re-upload it on every wake.
# Dadaodao is a separate research-materials project, outside this collected-works restart.
# Sacred Books of the East: its five driver volumes are done locally; keep it off
# Gemini (ACCS owns that pool) and keep output local.
Ensure 'sbe-gemini' 'sbe_translate' @('-X','utf8','scripts\sbe_translate.py','--loop','--only','sbe-04-zend-avesta-1,sbe-06-quran-1,sbe-10-dhammapada,sbe-16-yi-king,sbe-22-jaina-1','--backend','nvidia','--no-upload')
Note "keeper tick done"
