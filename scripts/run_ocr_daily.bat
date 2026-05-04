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

echo === OCR run started %DATE% %TIME% === >> "%LOGFILE%"
python scripts\ocr_with_gemini.py run --rpm 8 >> "%LOGFILE%" 2>&1
echo === OCR run ended %DATE% %TIME% (exit %ERRORLEVEL%) === >> "%LOGFILE%"

endlocal
