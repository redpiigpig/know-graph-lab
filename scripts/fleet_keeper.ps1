# Fleet keeper: every 30 min (Windows task KGL_Fleet_Keeper) self-heals translation/OCR lanes.
# If a lane's worker is not running, relaunch it. The 30-min cadence IS the retry mechanism.
# Direct Start-Process python.exe + arg array (avoids nested-string / redirect PS parse traps).
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts and breaks parsing.
$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT
$log = "$ROOT\scripts\logs\fleet_keeper.log"
$py = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
# Never let a reader silence the keeper. A `tail -f` on the log holds a Windows share
# lock that makes Add-Content throw, and with $ErrorActionPreference=Continue the keeper
# kept working while writing nothing for 5 hours (2026-08-18). Open the file ourselves
# with FileShare::ReadWrite, retry briefly, and fall back to a .alt file so the record
# always lands somewhere.
function Note($m) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m
    foreach ($target in @($log, "$log.alt")) {
        for ($i = 0; $i -lt 3; $i++) {
            try {
                $fs = New-Object System.IO.FileStream($target, [System.IO.FileMode]::Append,
                    [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite)
                $sw = New-Object System.IO.StreamWriter($fs)
                $sw.WriteLine($line); $sw.Flush(); $sw.Close(); $fs.Close()
                return
            } catch {
                Start-Sleep -Milliseconds 200
            }
        }
    }
}
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
#
# 2026-08-19: the threshold has to match how chatty the lane is, or the guard starts
# killing healthy work. plato_build prints one line per WORK, not per section, and each
# section is its own NVIDIA call (timeout 600s alone) - Critias has 76 of them, so an
# hour of silence is normal. A flat 45 min killed philo-queue five times in a day and it
# could never finish a work. ACCS logs every batch, so it keeps the tight threshold.
$STALL_DEFAULT = 45
$STALL_PER_LANE = @{
    'philo-queue'    = 180   # one log line per work; sections are individual LLM calls
    'jung-queue'     = 180   # same shape: whole-volume translate between log lines
    'panikkar-vedic' = 180
    'aquinas'        = 90    # prints every 20 articles, but a cold volume can be slow
}
function StallLimit($label) {
    if ($STALL_PER_LANE.ContainsKey($label)) { return $STALL_PER_LANE[$label] }
    return $STALL_DEFAULT
}
function WorkerAlive($label) {
    $lane = LaneName $label
    $pidFile = "$ROOT\scripts\state\fleet_$lane.pid"
    if (-not (Test-Path -LiteralPath $pidFile)) { return $false }
    $workerPid = (Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($workerPid -and (Get-Process -Id ([int]$workerPid) -ErrorAction SilentlyContinue)) {
        $out = "$ROOT\scripts\logs\fleet_$lane.out.log"
        if (Test-Path -LiteralPath $out) {
            $idle = ((Get-Date) - (Get-Item -LiteralPath $out).LastWriteTime).TotalMinutes
            if ($idle -gt (StallLimit $label)) {
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

# Batch size 2, not 4 (2026-08-19): four 1800px pages is a ~2.6 MB base64 payload and
# Gemini answered 504 DEADLINE_EXCEEDED on most of them - Romans managed 16 pages in an
# hour. Halving the batch doubles the request count but the daily ceiling (6 models x
# 7 keys x 20) is ~840 requests, far more than these volumes need.
# ACCS: DONE 2026-09-10 (user confirmed, incl. the deuterocanon). Verified three ways
# before removing the lane - the log line alone was not enough, since "本批全數完成"
# only ever covered volumes with status=ready:
#   - DB: 73 book_codes, i.e. the whole 66-book canon (39 OT + 27 NT) plus the seven
#     deuterocanonical codes tob/wis/sir/bar/sus/bel/aza. Judith and 1-2 Maccabees are
#     absent because ACCS vol XV does not cover them - publisher scope, not a gap
#     (see the BOOK_CODES comment in accs_epub.py).
#   - Config: all 23 volumes status=ready with ranges defined; 58 expected book x vol
#     items against 69 .raw.done markers in c:\tmp.
#   - Lane output: "本批 OCR 全數完成或無可跑項".
# It had been relaunched every 30 min doing nothing (16:00/16:31/17:00/17:30 on 09-10)
# - completion is judged by output, not by the schedule still being enabled
# ([[feedback_disable_finished_schedules]]). Re-add only if a new volume is licensed.
# Gemini Vision therefore now belongs to the scan-ocr lane below.

# Aquinas second (user 2026-08-17): Summa 17 vols, conservative OCR cleanup on the
# OpenRouter free pool (8 keys, own pool - does not touch Gemini/NVIDIA quota).
# clean_body caches per article under c:\tmp\aquinas_clean, so each pass only pays
# for what is still dirty; --upload is idempotent (upsert + replace chunks).
Ensure 'aquinas' 'aquinas_build' @('-X','utf8','scripts\aquinas_build.py','--all','--clean','--engine','openrouter','--upload')

# Scan-transcribe (2026-09-10): the two 昭慧法師 scanned books - 心靈的交會 (255 pages,
# v2 re-run for footnote markup) and 初期唯識思想 (300). Gemini Vision, which is free
# now that the ACCS lane has finished its batch ("本批 OCR 全數完成或無可跑項").
# This started as a nohup bash loop and DIED with the session, leaving a stale lock and
# both books frozen overnight at 90/255 and 162/300 - only scheduler-hosted work
# survives ([[feedback_laptop_sleeps_design_for_resume]]). scan_ocr_pass runs ONE pass
# and exits, so the keeper's 30-min cadence is the retry; when both books are full it
# prints one line and exits instead of spinning ([[feedback_disable_finished_schedules]]).
Ensure 'scan-ocr' 'scan_ocr_pass' @('-X','utf8','scripts\scan_ocr_pass.py','--batch','6')

# Jung: DONE 2026-09-02. All 16 translated volumes are on the site (the lane had been
# dead since the source EPUB moved to Drive, and file_path collisions were rejecting
# every volume but CW11 - see jung_collected_works.md). Nothing left to translate, and
# a lane that only re-assembles 16 volumes every 30 min is pure I/O waste. Re-add it
# only if a copyright-cleared volume shows up.
#
# Philo: the Plato/Aristotle queue (26 works) finished the same day and scanned clean,
# so the lane now runs the Hellenistic/Neoplatonic queue instead - Plotinus' six
# Enneads + Porphyry's Life, Epicurus' five letters/sayings, Epictetus' three works.
# Those 15 hub cards have existed with zero chunks because no lane ever ran the three
# builders. Haiku on Max: Gemini belongs to ACCS and NVIDIA has been 503-ing all day.
# Split in two so both halves move at once - the per-section caches do not overlap.
Ensure 'philo-queue' 'hellenistic_run_queue.py --group short' @('-X','utf8','scripts\hellenistic_run_queue.py','--group','short','--engine','haiku')
Ensure 'plotinus-queue' 'hellenistic_run_queue.py --group plotinus' @('-X','utf8','scripts\hellenistic_run_queue.py','--group','plotinus','--engine','haiku')
# Yanaihara's Taiwan book (Iwanami 1929, public domain worldwide): NDL scan pid 1191101,
# 201 images -> PDF -> Gemini Vision OCR. Both ends throttle us (NDL answers 429, Gemini
# answers 503), so the script never retries to death - it moves one step and exits, and
# this 30-min lane IS the retry. Slower page pause than a one-off run, on purpose.
Ensure 'yanaihara-ndl' 'yanaihara_ndl' @('-X','utf8','scripts\yanaihara_ndl.py','--auto','--pause','6','--batch','8')

# Yanaihara (Uchimura's disciple, 2nd-generation Mukyokai): the four Aozora Bunko texts,
# ja -> Traditional Chinese. The two short pieces are already up; this lane finishes the
# two long ones (Introduction to Christianity 490 paras, Life of Jesus 1017 paras).
# Same driver as Uchimura, --author switches the registry. Haiku for the same reason as
# the philo lane. Per-section checkpoints, so a restart resumes.
Ensure 'yanaihara' 'uchimura_auto' @('-X','utf8','scripts\uchimura_auto.py','--author','yanaihara','--run-queue','--backend','haiku')

# Panikkar last volume (vedic-experience, huge): on Haiku per user (idle Claude account).
# When it finishes, replace this lane with Max Weber (sociology) collected works.
# Moved off Gemini 2026-08-17 so ACCS owns the Gemini pool (see top of file).
Ensure 'panikkar-vedic' 'panikkar_auto' @('-X','utf8','scripts\panikkar_auto.py','--work','vedic-experience','--backend','nvidia')
# Uchimura first-wave cache is already complete; do not re-upload it on every wake.
# Dadaodao is a separate research-materials project, outside this collected-works restart.
# Sacred Books of the East: its five driver volumes are done locally; keep it off
# Gemini (ACCS owns that pool) and keep output local.
# 2026-08-25: the lane had been dead since it was set to '--backend nvidia',
# which sbe_translate.py does not accept (choices: cloud/gemini-first/haiku) -
# every keeper tick relaunched it and it exited on the argparse error. 'cloud'
# is the right free-first policy: Haiku on Max with a fast 20s fail, then Sonnet.
#
# 🚨 2026-09-08 STOPPED BY USER. '--backend cloud' means Haiku-first, and Haiku is
# what produced the meta-reply pollution this lane's own books are full of: when it
# judges the source "not English / garbled" it does not return empty, it returns a
# paragraph talking to you ("我需要指出，提供的英文原文…似乎不完整"), and the pipeline
# stores that as the translation. 2,554 such paragraphs were cleared today; four
# hours later this lane had refilled 35 of the blanks with fresh ones, and the lane
# log shows "uploaded (266 chunks)" twice despite --no-upload, so it was pushing
# them live. Cleaning while this runs is a treadmill.
#
# Before re-enabling: switch the backend off Haiku (see the engine policy in
# feedback_engine_nvidia_no_haiku / feedback_dialogue_rewrite_gemini_not_haiku),
# and confirm --no-upload is actually honoured. Audit with
#   python scripts/audit_llm_meta_replies.py --root mueller_data
# Ensure 'sbe-gemini' 'sbe_translate' @('-X','utf8','scripts\sbe_translate.py','--loop','--only','sbe-04-zend-avesta-1,sbe-06-quran-1,sbe-10-dhammapada,sbe-16-yi-king,sbe-22-jaina-1','--backend','cloud','--no-upload')
Note "keeper tick done"
