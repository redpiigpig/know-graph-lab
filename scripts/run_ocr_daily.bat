@echo off
REM Daily OCR runner for Windows Task Scheduler.
REM Runs ingest -> parse -> ocr_with_gemini.py until daily quota is hit.
REM Idempotent: tomorrow's run picks up where today's left off.
REM
REM Logs to scripts/logs/ocr_YYYY-MM-DD.log (keeps history; review for failures).
REM
REM Hardening notes (2026-05-14):
REM   - Hardcode python to AppData\Local\Python so we don't accidentally hit
REM     _whisper_venv (which doesn't have ebooklib / fitz / google.genai).
REM   - Use PowerShell for ISO date instead of wmic (wmic deprecation + WMI
REM     service unreliability in Task Scheduler wake-from-sleep context).
REM   - Log per-step exit code so silent script failures are visible.

setlocal
cd /d "%~dp0\.."

set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM Robust ISO date via PowerShell (wmic is being deprecated + unreliable on wake)
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set TODAY=%%I
set LOGFILE=%LOGDIR%\ocr_%TODAY%.log

REM Pin python to the interpreter that actually has the pipeline deps installed.
REM (Falls back to PATH `python` if the explicit path is gone, so a fresh
REM install can still smoke-test by just running the bat.)
set PY=C:\Users\user\AppData\Local\Python\bin\python.exe
if not exist "%PY%" set PY=python

echo === Daily run started %DATE% %TIME% === >> "%LOGFILE%"
echo CWD=%CD%   PY=%PY%   LOGFILE=%LOGFILE% >> "%LOGFILE%"

REM Notify desktop that today's run is starting (toast notification).
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0notify.ps1" -Title "KGLab OCR daily" -Body "Run started %TIME% — ingest -> parse -> OCR" >nul 2>&1

REM Step 1: ingest any new ebooks dropped into z-lib/ at the project root
echo --- ingest_new_books --- >> "%LOGFILE%"
"%PY%" scripts\ingest_new_books.py run >> "%LOGFILE%" 2>&1
echo step1 exit=%ERRORLEVEL% >> "%LOGFILE%"

REM Step 2: parse newly-ingested (and any other unparsed) text-extractable books
echo --- parse_worker --- >> "%LOGFILE%"
"%PY%" scripts\parse_worker.py run --limit 30 >> "%LOGFILE%" 2>&1
echo step2 exit=%ERRORLEVEL% >> "%LOGFILE%"

REM Step 3a: pick a Gemini model that is actually alive right now.
REM   Every other Gemini consumer in this repo already probes first
REM   (fleet_keeper.ps1, accs_ocr_gemini_runner.ps1, resume_lanes_on_gemini.ps1,
REM   translation_cloud_supervisor.py). This bat was the only one hardcoded to
REM   ocr_with_gemini.py's DEFAULT_MODEL, and on 2026-08-30 that default
REM   (gemini-flash-latest) returned 503 "high demand" while gemini-3.6-flash
REM   worked fine -- the daily run was dying on the MODEL NAME, not on quota,
REM   and nothing said so. Free-tier quota is per-model, so "one model is dry"
REM   never means "Gemini is dry": probe, then use whatever still lives.
echo --- gemini_probe --- >> "%LOGFILE%"
"%PY%" scripts\gemini_probe.py >> "%LOGFILE%" 2>&1
if errorlevel 1 goto :gemini_dry
set /p GEMINI_MODEL=<scripts\state\gemini_live_model.txt
echo probe picked GEMINI_MODEL=%GEMINI_MODEL% >> "%LOGFILE%"

REM Step 3: OCR scanned PDFs until daily Gemini quota exhausted
echo --- ocr_with_gemini --- >> "%LOGFILE%"
"%PY%" scripts\ocr_with_gemini.py run --rpm 8 >> "%LOGFILE%" 2>&1
set GEMINI_EXIT=%ERRORLEVEL%
echo step3 exit=%GEMINI_EXIT% >> "%LOGFILE%"
goto :after_ocr

:gemini_dry
REM Probe swept every candidate model on every key and none could generate.
REM Reuse exit code 2 so the existing quota-notify branch below handles it.
echo step3 SKIPPED: gemini_probe found no live model on any key >> "%LOGFILE%"
set GEMINI_EXIT=2

:after_ocr

REM On Gemini daily-quota exhaustion (exit 2): notify desktop + skip fallback.
REM Qwen fallback DISABLED on this laptop (RTX 4050 Mobile, 6 GB VRAM):
REM qwen2.5vl:3b's vision compute graph needs ~6.7 GiB, drops to CPU at
REM ~1 tok/min, unusable. Plumbing kept (ocr_with_qwen.py exists) so
REM future hardware can re-enable by un-commenting the python line below.
if "%GEMINI_EXIT%"=="2" (
    powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0notify.ps1" -Title "KGLab OCR halted" -Body "Gemini daily quota hit at %TIME%. Resumes tomorrow 16:00." >nul 2>&1
    REM "%PY%" scripts\ocr_with_qwen.py run --limit 5 >> "%LOGFILE%" 2>&1
)

REM Step 4: auto-split fresh 套書 (idempotent — no-op when nothing pending).
REM detect_set_volumes finds 套書-titled books w/o volume metadata, runs Haiku
REM to decide multi/single-volume, writes volume field or NOT_A_SET marker.
REM split_ebook_set then breaks splittable ones into per-volume children.
echo --- detect_set_volumes --- >> "%LOGFILE%"
"%PY%" scripts\detect_set_volumes.py run --all >> "%LOGFILE%" 2>&1
echo step4a exit=%ERRORLEVEL% >> "%LOGFILE%"
echo --- split_ebook_set --- >> "%LOGFILE%"
"%PY%" scripts\split_ebook_set.py run --all >> "%LOGFILE%" 2>&1
echo step4b exit=%ERRORLEVEL% >> "%LOGFILE%"

REM Step 5: standardize freshly-parsed books (EPUB → markdown chapters,
REM PDF → Plan A polished pages). --only-fresh filters to standardized_at IS NULL
REM so it's a daily no-op once the catalogue is fully standardized.
echo --- standardize_ebook --- >> "%LOGFILE%"
"%PY%" scripts\standardize_ebook.py --all --only-fresh >> "%LOGFILE%" 2>&1
echo step5a exit=%ERRORLEVEL% >> "%LOGFILE%"
echo --- standardize_pdf_lite --- >> "%LOGFILE%"
"%PY%" scripts\standardize_pdf_lite.py --all --only-fresh >> "%LOGFILE%" 2>&1
echo step5b exit=%ERRORLEVEL% >> "%LOGFILE%"

REM Step 6: quality gate — 對當日動過的書重評分寫回 ebooks.quality_*（純規則零 LLM）。
REM 記 log 不擋 bat；全館掃描與 REOCR 重轉由 KGLab-Quality-Sweep 夜間任務負責。
echo --- quality_sweep (recent 1d) --- >> "%LOGFILE%"
"%PY%" scripts\quality_sweep.py --recent 1 >> "%LOGFILE%" 2>&1
echo step6 exit=%ERRORLEVEL% >> "%LOGFILE%"

REM Step 7: push transcription/translation progress JSON to c:/tmp + R2
REM (/transcription-progress monitoring page reads it).
echo --- push_transcription_progress --- >> "%LOGFILE%"
"%PY%" scripts\push_transcription_progress.py >> "%LOGFILE%" 2>&1
echo step7 exit=%ERRORLEVEL% >> "%LOGFILE%"

echo === Daily run ended %DATE% %TIME% (gemini-exit %GEMINI_EXIT%) === >> "%LOGFILE%"

endlocal
