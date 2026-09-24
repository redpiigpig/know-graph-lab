# Fleet keeper: every 30 min (Windows task KGL_Fleet_Keeper) self-heals translation/OCR lanes.
# If a lane's worker is not running, relaunch it. The 30-min cadence IS the retry mechanism.
#
# 2026-09-12 - THE KEEPER ITSELF NEEDS A KEEPER. One tick wedged at 01:34 (single thread,
# kernel Executive wait, unkillable by Stop-Process AND taskkill) and every trigger from
# 02:00 to 09:30 was silently dropped: the task is MultipleInstances=IgnoreNew, so a live
# instance makes the scheduler skip the next one, and ExecutionTimeLimit was PT0S = no
# limit, so nothing ever killed the wedged one. Ten hours with State=Running, LastRunTime
# advancing, and NOT ONE LINE in this log - every lane sat dead meanwhile.
# Fixed by giving the task a limit (a healthy tick takes seconds):
#   $t = Get-ScheduledTask -TaskName 'KGL_Fleet_Keeper'
#   $t.Settings.ExecutionTimeLimit = 'PT10M'
#   Set-ScheduledTask -TaskName 'KGL_Fleet_Keeper' -Settings $t.Settings
# Diagnosis rule: this log going quiet is the symptom to watch, NOT the task's State
# (which says Running) and NOT LastRunTime (which keeps advancing).
# KGL_Fathers_Retranslate and KGL_Translation_Supervisor are still PT0S - same trap.
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
    'husserl'        = 240   # one log line per SECTION, and the biggest is 355 paragraphs
    'jbungo-s0'     = 60    # one log line per chapter
    'jbungo-s1'     = 60    # one log line per chapter
    'jbungo-s2'     = 60    # one log line per chapter
    'kjv-s0'        = 60    # one log line per chapter
    'kjv-s1'        = 60    # one log line per chapter
    'kjv-s2'        = 60    # one log line per chapter
    'asv-s0'        = 60    # one log line per chapter
    'asv-s1'        = 60    # one log line per chapter
    'asv-s2'        = 60    # one log line per chapter
    'niv-s0'        = 60    # one log line per chapter
    'niv-s1'        = 60    # one log line per chapter
    'niv-s2'        = 60    # one log line per chapter
    'sekine-s0'      = 240   # one log line per article; the longest has ~230 paragraphs
    'sekine-s1'      = 240   # one log line per article; the longest has ~230 paragraphs
    'sekine-s2'      = 240   # one log line per article; the longest has ~230 paragraphs
    'sbe-b2-s0'      = 90    # one line per section; a 30-paragraph Manu section is slow
    'sbe-b2-s1'      = 90
    'sbe-b2-s2'      = 90
    'sbe-b2-s3'      = 90
    'sbe-b2-s4'      = 90
    'sbe-b2-s5'      = 90
    'mineru-queue'   = 180   # one log line per BOOK; a 500-page scan runs 30+ min on the GPU
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
function LaunchExe($label, $exe, $argv, $hidden = $true) {
    $lane = LaneName $label
    $out = "$ROOT\scripts\logs\fleet_$lane.out.log"
    $err = "$ROOT\scripts\logs\fleet_$lane.err.log"
    # z-lib needs a VISIBLE Chrome (DiamWall refuses headless), so that lane passes
    # $hidden=$false. Hiding the launcher does not hide Chrome, but keep it explicit.
    $style = if ($hidden) { 'Hidden' } else { 'Normal' }
    $proc = Start-Process $exe -ArgumentList $argv -WindowStyle $style -WorkingDirectory $ROOT `
        -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
    Set-Content -LiteralPath "$ROOT\scripts\state\fleet_$lane.pid" -Value $proc.Id -Encoding ascii
    Note "started $label pid=$($proc.Id)"
}
function Launch($label, $argv) {
    LaunchExe $label $py $argv
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
# A lane for a FINITE job must be able to retire itself, or it spins forever
# ([[feedback_disable_finished_schedules]] - the ACCS lane above was relaunched every
# 30 min doing nothing). The worker prints an ASCII marker when there is nothing left;
# seeing it, we drop the pause file so later ticks skip the lane, and say so in the log.
# The marker is the worker's own verdict - do NOT re-derive "is it done" here, or the
# keeper and the worker can disagree and neither is obviously wrong.
function EnsureUntil($label, $exe, $argv, $marker, $hidden = $true) {
    $lane = LaneName $label
    if (LanePaused $label) { return }
    $out = "$ROOT\scripts\logs\fleet_$lane.out.log"
    if ((Test-Path -LiteralPath $out) -and (Select-String -LiteralPath $out -SimpleMatch $marker -Quiet)) {
        Set-Content -LiteralPath "$ROOT\scripts\state\fleet_$lane.pause" -Value $marker -Encoding ascii
        Note "lane finished, retiring: $label ($marker)"
        return
    }
    if (WorkerAlive $label) { return }
    Note "relaunch $label"
    LaunchExe $label $exe $argv $hidden
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

# Library OCR backlog (user 2026-09-23, "scan them now"): 272 scanned PDFs had been
# "parsed" off a cover-page text layer and never OCR'd (~100k pages), requeued that day.
# The three daily OCR runs (8 books / 90 min each) would need over a month, so MinerU
# eats the whole queue here. The GPU lock in mineru_ocr keeps it from colliding with the
# daily runs; a halt (env failure) just ends the process and the next tick relaunches.
# Retires itself on MINERU_QUEUE_EMPTY.
# -u is required: redirected stdout is block-buffered, so on 09-23 the out log sat idle
# 166 min while books were being published, and the stall guard killed a healthy worker.
EnsureUntil 'mineru-queue' $py @('-X','utf8','-u','scripts\mineru_ocr.py','queue','--limit','1000') 'MINERU_QUEUE_EMPTY'

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
EnsureUntil 'philo-queue' $py @('-X','utf8','scripts\hellenistic_run_queue.py','--group','short','--engine','haiku') 'HELLENISTIC_QUEUE_COMPLETE'
EnsureUntil 'plotinus-queue' $py @('-X','utf8','scripts\hellenistic_run_queue.py','--group','plotinus','--engine','haiku') 'HELLENISTIC_QUEUE_COMPLETE'
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
EnsureUntil 'yanaihara' $py @('-X','utf8','scripts\uchimura_auto.py','--author','yanaihara','--run-queue','--backend','auto') 'QUEUE_COMPLETE'

# Husserl, Ideas I (Boyce Gibson 1931, public domain): Gemini Vision OCR finished
# 2026-09-11 (59/59 batches, KGL_Husserl_OCR then disabled itself), and the section
# splitting was repaired 2026-09-12 - 21 sections, 1547 body paragraphs, en + zh.
# Backend 'auto' = Gemini first, NVIDIA on fallback; NOT haiku (it answers refusals as
# if they were translations - see feedback_haiku_meta_reply_pollution).
# Checkpoints are per section under .claude/skills/ebook-collected-works/husserl_data,
# so a commute-sleep restart resumes where it stopped.
EnsureUntil 'husserl' $py @('-X','utf8','scripts\uchimura_auto.py','--author','husserl','--run-queue') 'QUEUE_COMPLETE'

# Sekine Masao (2026-09-23): 43 J-STAGE papers + 5 Western papers, ja/de/fr -> zh.
# NVIDIA only (Gemini answered 503 on every key that day). sekine_build declares
# STRICT_COMPLETE, so uchimura_auto prints QUEUE_COMPLETE only when every paragraph is
# filled, or a pass made no progress with zero engine errors - engine outages keep the lane alive.
# Three shards (user OK'd 2026-09-23): latency-bound (~1 paragraph/min per lane), not
# RPM-bound. --shard assigns whole sections greedily by size, so lanes never share a secN.json.
EnsureUntil 'sekine-s0' $py @('-X','utf8','scripts\uchimura_auto.py','--author','sekine','--run-queue','--backend','nvidia','--shard','0/3') 'QUEUE_COMPLETE'
EnsureUntil 'sekine-s1' $py @('-X','utf8','scripts\uchimura_auto.py','--author','sekine','--run-queue','--backend','nvidia','--shard','1/3') 'QUEUE_COMPLETE'
EnsureUntil 'sekine-s2' $py @('-X','utf8','scripts\uchimura_auto.py','--author','sekine','--run-queue','--backend','nvidia','--shard','2/3') 'QUEUE_COMPLETE'

# Uchimura, Kyuanroku (2026-09-23): only in the Iwanami zenshu vol.1, not on Aozora. Source
# text is the MinerU transcription corrected page-by-page (uchimura_zenshu_works.py).
EnsureUntil 'kyuanroku' $py @('-X','utf8','scripts\uchimura_auto.py','--author','uchimura-zenshu','--run-queue','--backend','nvidia') 'QUEUE_COMPLETE'
# Bible versions -> Chinese direct translation, chapter by chapter (2026-09-24). Bungo-yaku (Japanese),
# KJV incl. Apocrypha, ASV: archaic -> classical Chinese (user: thee/thou -> ru); NIV -> vernacular.
EnsureUntil 'jbungo-s0' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','jbungo_zh','--shard','0/3') 'QUEUE_COMPLETE'
EnsureUntil 'jbungo-s1' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','jbungo_zh','--shard','1/3') 'QUEUE_COMPLETE'
EnsureUntil 'jbungo-s2' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','jbungo_zh','--shard','2/3') 'QUEUE_COMPLETE'
EnsureUntil 'kjv-s0' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','kjv_zh','--shard','0/3') 'QUEUE_COMPLETE'
EnsureUntil 'kjv-s1' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','kjv_zh','--shard','1/3') 'QUEUE_COMPLETE'
EnsureUntil 'kjv-s2' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','kjv_zh','--shard','2/3') 'QUEUE_COMPLETE'
EnsureUntil 'asv-s0' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','asv_zh','--shard','0/3') 'QUEUE_COMPLETE'
EnsureUntil 'asv-s1' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','asv_zh','--shard','1/3') 'QUEUE_COMPLETE'
EnsureUntil 'asv-s2' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','asv_zh','--shard','2/3') 'QUEUE_COMPLETE'
EnsureUntil 'niv-s0' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','niv_zh','--shard','0/3') 'QUEUE_COMPLETE'
EnsureUntil 'niv-s1' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','niv_zh','--shard','1/3') 'QUEUE_COMPLETE'
EnsureUntil 'niv-s2' $py @('-X','utf8','scripts\japanese_bible.py','translate','--ver','niv_zh','--shard','2/3') 'QUEUE_COMPLETE'

# Collected works -> one Word reader per book on Drive (user 2026-09-23: "Drive needs a Word
# for every book"). Incremental: only books whose JSONL is newer than the .docx are rebuilt,
# so this keeps the Word copies in step with lanes that are still translating (sekine etc.).
# Exits after one pass; Ensure relaunches it next tick = a 30-min refresh.
Ensure 'cw-word' 'collected_works_word' @('-X','utf8','scripts\collected_works_word.py')

# Panikkar last volume (vedic-experience, huge): on Haiku per user (idle Claude account).
# When it finishes, replace this lane with Max Weber (sociology) collected works.
# Moved off Gemini 2026-08-17 so ACCS owns the Gemini pool (see top of file).
EnsureUntil 'panikkar-vedic' $py @('-X','utf8','scripts\panikkar_auto.py','--work','vedic-experience','--backend','nvidia') 'PANIKKAR_WORK_COMPLETE'
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
#
# SBE batch 2 (2026-09-19). The two conditions the note above set for re-enabling are met:
#   (a) backend is 'nvidia', not cloud/haiku - the meta-reply pollution came from Haiku.
#   (b) the '--no-upload despite uploads' mystery is solved: --no-upload only skips the
#       FINAL assemble of a pass. translate_work() still re-uploads every N sections, and
#       ingest_work() calls assemble_and_upload() unconditionally at its end. That is why
#       the old lane logged "uploaded (266 chunks)" while asked not to upload. Nothing is
#       broken - but with six shards on one volume the whole-volume write count gets
#       multiplied by the process count, so --reupload-every 60 replaces the default 12.
#
# Six volumes are split across six shards: each lane takes every 6th section of EVERY
# unfinished volume, so load balances itself and no lane runs out of work early. Binding
# one lane to one volume made the finish time the biggest volume's (Manu alone was 37h)
# and left finished slots being relaunched into empty passes every 5 min.
#
# 2026-09-18 this ran as a bare Start-Process watchdog and died with the machine at the
# 09-18 shutdown, at left=8397, with nothing to restart it - only scheduler-hosted work
# survives a reboot ([[feedback_laptop_sleeps_design_for_resume]]). Hence this lane.
#
# The marker is NOT the driver's own "sbe done": is_done() counts segments that failed
# MAX_FAIL times as complete, so it fires while work remains. sbe_batch2_lane.py prints
# SBE_BATCH2_COMPLETE only when sbe_progress's real counts say left=0 AND dead=0, and the
# shard that wins a lock also runs the per-volume assemble the --no-upload lanes skipped.
EnsureUntil 'sbe-b2-s0' $py @('-X','utf8','scripts\sbe_batch2_lane.py','--shard','0/6') 'SBE_BATCH2_COMPLETE'
EnsureUntil 'sbe-b2-s1' $py @('-X','utf8','scripts\sbe_batch2_lane.py','--shard','1/6') 'SBE_BATCH2_COMPLETE'
EnsureUntil 'sbe-b2-s2' $py @('-X','utf8','scripts\sbe_batch2_lane.py','--shard','2/6') 'SBE_BATCH2_COMPLETE'
EnsureUntil 'sbe-b2-s3' $py @('-X','utf8','scripts\sbe_batch2_lane.py','--shard','3/6') 'SBE_BATCH2_COMPLETE'
EnsureUntil 'sbe-b2-s4' $py @('-X','utf8','scripts\sbe_batch2_lane.py','--shard','4/6') 'SBE_BATCH2_COMPLETE'
EnsureUntil 'sbe-b2-s5' $py @('-X','utf8','scripts\sbe_batch2_lane.py','--shard','5/6') 'SBE_BATCH2_COMPLETE'
# z-lib probe: verify the WHOLE wanted list against the site (user asked 2026-09-16).
# Finite job - measured 4 titles/min, ~1,600 left, so roughly 7 hours. Too long to
# survive in one run: this laptop sleeps on the commute, and the #1 failure mode is
# the VISIBLE Chrome window being closed (DiamWall refuses headless), which kills the
# run with "Target page, context or browser has been closed". The 30-min tick is the
# retry. Retires itself on ZLIB-PROBE-COMPLETE.
#
# --max-tries 6000 covers the remainder in one go; the worker skips anything already
# in the ledger (probe mode counts even 'dry' as seen), so relaunching never redoes work.
$node = 'C:\Program Files\nodejs\node.exe'
EnsureUntil 'zlib-probe' $node @('scripts\zlib_fetch.mjs','--probe','--list','output\zlib_wanted_all.jsonl','--max-tries','6000') 'ZLIB-PROBE-COMPLETE' $false

# The three foreign-database lines (added 2026-09-17). They had been started by hand,
# so they stayed dead whenever a run ended - CyberLeninka died on HTTP 521 and nobody
# relaunched it. All three are resumable and cheap on memory (18-30 MB each; the RAM
# hogs on this box are the LLM/OCR lanes), so the 30-min tick is the right mechanism.
#
# No completion marker yet on purpose: all three are nowhere near done (Unpaywall 12.2%,
# CyberLeninka 4.8%, J-Stage text 18.1%), so a plain Ensure is right. When one gets
# close, give it a marker and switch to EnsureUntil - do NOT leave a finished lane
# relaunching every 30 min doing nothing ([[feedback_disable_finished_schedules]]).
Ensure 'unpaywall-resolve' 'unpaywall_resolve' @('scripts\unpaywall_resolve.py','--resolve')
# ...and the half nobody was running (2026-09-19). --resolve only ASKS Unpaywall
# which DOIs are open access; --fetch is what actually downloads the PDFs, and no
# lane ever called it: 149,574 DOIs resolved, 52,153 with a direct PDF link, 0 files
# on disk. Sampling 25 of them: 52% give a real PDF, 24% answer 403 (bepress-style
# repositories refusing scripted access), 20% hand back an HTML landing page (the
# fetcher checks the %PDF magic, so those are correctly refused rather than saved as
# fake PDFs), 4% have a broken TLS certificate.
#
# --limit keeps each run bounded so Drive can drain between ticks. The fetcher also
# keeps fetch-failed.jsonl now: todo is computed from which .pdf files exist, so
# without it the permanently-dead 40% pile up at the FRONT of the queue and every
# later run spends its whole limit re-trying them. Delete that file to retry (a 403
# can be temporary).
Ensure 'unpaywall-fetch' 'unpaywall_resolve --fetch' @('scripts\unpaywall_resolve.py','--fetch','--limit','400')
Ensure 'cyberleninka-fetch' 'cyberleninka_harvest' @('scripts\cyberleninka_harvest.py','--fetch')
# J-Stage PDFs are DONE (14,731/14,747 = 99.9%, finished 2026-09-17), so no fetch lane.
# What is left is text extraction: 12,060 PDFs downloaded but not extracted. This is the
# one line that needs NO network - the PDFs are on Drive - so it also runs on the commute.
Ensure 'jstage-text' 'jstage_ibk_harvest --text' @('scripts\jstage_ibk_harvest.py','--text')
Note "keeper tick done"
