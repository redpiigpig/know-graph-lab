@echo off
REM Overnight transcription chain. Idempotent and resumable at every step, so a
REM kill mid-run costs only the book in flight.
REM
REM Order matters: parse first (costs no LLM quota, and it is what decides which
REM PDFs actually need OCR), then OCR, then the structure passes over what landed.
REM
REM Sleep must be off for this to finish (powercfg standby-timeout-ac 0). This is
REM an S0 Modern Standby machine, so closing the lid still suspends it.
REM
REM ASCII-only and CRLF on purpose: a zh-TW box mis-decodes UTF-8-without-BOM in
REM shell scripts, and an LF-only .bat makes cmd's parser desync and execute
REM fragments of comment lines (2026-09-04, killed the whole daily pipeline).

setlocal
cd /d "%~dp0\.."

set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set STAMP=%%I
set LOGFILE=%LOGDIR%\overnight_%STAMP%.log

set PY=C:\Users\user\AppData\Local\Python\bin\python.exe
if not exist "%PY%" set PY=python

echo === Overnight run started %DATE% %TIME% === >> "%LOGFILE%"

REM 1. Pull anything sitting in the z-lib drop folder into Drive first.
echo --- ingest_new_books --- >> "%LOGFILE%"
"%PY%" scripts\ingest_new_books.py run >> "%LOGFILE%" 2>&1
echo step1 exit=%ERRORLEVEL% >> "%LOGFILE%"

REM 2. Parse the whole queue -- deliberately no --limit. Books with no text layer
REM    get flagged here and fall through to OCR below.
echo --- parse_worker (whole queue) --- >> "%LOGFILE%"
"%PY%" scripts\parse_worker.py run >> "%LOGFILE%" 2>&1
echo step2 exit=%ERRORLEVEL% >> "%LOGFILE%"

REM 3. OCR. Probe first: free-tier quota is per-model, so one dead model never
REM    means Gemini as a whole is dry.
echo --- gemini_probe --- >> "%LOGFILE%"
"%PY%" scripts\gemini_probe.py >> "%LOGFILE%" 2>&1
if errorlevel 1 goto :no_gemini
echo --- ocr_with_gemini --- >> "%LOGFILE%"
"%PY%" scripts\ocr_with_gemini.py run --rpm 8 >> "%LOGFILE%" 2>&1
echo step3 exit=%ERRORLEVEL% >> "%LOGFILE%"
goto :structure
:no_gemini
echo step3 SKIPPED: gemini_probe found no live model >> "%LOGFILE%"

:structure
REM 4. Split freshly-landed multi-volume sets before anything reads them as books.
echo --- detect_set_volumes / split_ebook_set --- >> "%LOGFILE%"
"%PY%" scripts\detect_set_volumes.py run --all >> "%LOGFILE%" 2>&1
"%PY%" scripts\split_ebook_set.py run --all >> "%LOGFILE%" 2>&1

REM 5. Standardize whatever is newly parsed.
echo --- standardize --- >> "%LOGFILE%"
"%PY%" scripts\standardize_ebook.py --all --only-fresh >> "%LOGFILE%" 2>&1
"%PY%" scripts\standardize_pdf_lite.py --all --only-fresh >> "%LOGFILE%" 2>&1

REM 6. Split giant chunks. standardize merges, it never splits, so a book can come
REM    out of step 5 as one 200k-char blob. Selection is by chunk size, not score:
REM    a 2.4M-char blob still scored 82 and sat on the shelf looking fine.
echo --- resegment --- >> "%LOGFILE%"
"%PY%" scripts\resegment_ebook.py --all >> "%LOGFILE%" 2>&1

REM 7. Rescore. Pure rules, no LLM.
echo --- quality_sweep --- >> "%LOGFILE%"
"%PY%" scripts\quality_sweep.py --all >> "%LOGFILE%" 2>&1

echo === Overnight run ended %DATE% %TIME% === >> "%LOGFILE%"
endlocal
