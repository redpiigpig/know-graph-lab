@echo off
REM Daily OCR runner for Windows Task Scheduler.
REM Runs ocr_with_gemini.py until daily quota is hit, then exits cleanly.
REM Idempotent: tomorrow's run picks up where today's left off.
REM
REM Logs to scripts/logs/ocr_YYYY-MM-DD.log (keeps history; review for failures).

setlocal
cd /d "%~dp0\.."

set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value ^| find "="') do set DT=%%I
set TODAY=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%
set LOGFILE=%LOGDIR%\ocr_%TODAY%.log

echo === Daily run started %DATE% %TIME% === >> "%LOGFILE%"

REM Notify desktop that today's run is starting (toast notification).
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0notify.ps1" -Title "KGLab OCR daily" -Body "Run started %TIME% — ingest -> parse -> OCR" >nul 2>&1

REM Step 1: ingest any new ebooks dropped into z-lib/ at the project root
echo --- ingest_new_books --- >> "%LOGFILE%"
python scripts\ingest_new_books.py run >> "%LOGFILE%" 2>&1

REM Step 2: parse newly-ingested (and any other unparsed) text-extractable books
echo --- parse_worker --- >> "%LOGFILE%"
python scripts\parse_worker.py run --limit 30 >> "%LOGFILE%" 2>&1

REM Step 3: OCR scanned PDFs until daily Gemini quota exhausted
echo --- ocr_with_gemini --- >> "%LOGFILE%"
python scripts\ocr_with_gemini.py run --rpm 8 >> "%LOGFILE%" 2>&1
set GEMINI_EXIT=%ERRORLEVEL%

REM On Gemini daily-quota exhaustion (exit 2): notify desktop + skip fallback.
REM Qwen fallback DISABLED on this laptop (RTX 4050 Mobile, 6 GB VRAM):
REM qwen2.5vl:3b's vision compute graph needs ~6.7 GiB, drops to CPU at
REM ~1 tok/min, unusable. Plumbing kept (ocr_with_qwen.py exists) so
REM future hardware can re-enable by un-commenting the python line below.
if "%GEMINI_EXIT%"=="2" (
    powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0notify.ps1" -Title "KGLab OCR halted" -Body "Gemini daily quota hit at %TIME%. Resumes tomorrow 16:00." >nul 2>&1
    REM python scripts\ocr_with_qwen.py run --limit 5 >> "%LOGFILE%" 2>&1
)

echo === Daily run ended %DATE% %TIME% (gemini-exit %GEMINI_EXIT%) === >> "%LOGFILE%"

endlocal
