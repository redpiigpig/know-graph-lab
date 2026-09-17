@echo off
REM Nightly OCR for Uchimura Kanzo zenshu (20 vols, local MinerU).
REM   1. fetch  - resume any volume not fully downloaded (idempotent)
REM   2. register - upsert downloaded volumes into ebooks (idempotent)
REM   3. ocr    - transcribe volume by volume, 4 hours max; exits quietly if GPU busy
REM   4. self-disable once all 20 volumes have chunks (so it stops spinning)
REM
REM ASCII ONLY. 2026-09-18: the first version had Chinese comments/echo and
REM cmd.exe chopped lines mid-token ("'s' is not recognized", "'" mkdir ""'"),
REM so the 01:00 run died with code 255 and never wrote a single log line.
REM Keep Chinese inside the Python scripts, which set their own utf-8 stdout.
REM
REM Python path is hardcoded: bare `python` resolves to _whisper_venv, which
REM lacks requests/fitz and hangs on import without an error.

setlocal
cd /d "%~dp0.."

set "LOGDIR=%~dp0logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "TODAY=%%I"
if "%TODAY%"=="" set "TODAY=undated"
set "LOGFILE=%LOGDIR%\uchimura_zenshu_%TODAY%.log"

set "PY=C:\Users\user\AppData\Local\Python\bin\python.exe"
if not exist "%PY%" set "PY=python"

echo === run started %DATE% %TIME% === >> "%LOGFILE%"

echo --- fetch --- >> "%LOGFILE%"
"%PY%" scripts\uchimura_zenshu_fetch.py >> "%LOGFILE%" 2>&1
echo fetch exit=%ERRORLEVEL% >> "%LOGFILE%"

echo --- register --- >> "%LOGFILE%"
"%PY%" scripts\uchimura_zenshu_register.py >> "%LOGFILE%" 2>&1
echo register exit=%ERRORLEVEL% >> "%LOGFILE%"

echo --- mineru ocr --- >> "%LOGFILE%"
"%PY%" scripts\uchimura_zenshu_ocr.py --max-minutes 240 >> "%LOGFILE%" 2>&1
echo ocr exit=%ERRORLEVEL% >> "%LOGFILE%"

echo --- status --- >> "%LOGFILE%"
"%PY%" scripts\uchimura_zenshu_ocr.py --status >> "%LOGFILE%" 2>&1

REM Disable this task once nothing is pending (exit 0 = all done).
"%PY%" scripts\uchimura_zenshu_done.py
if errorlevel 1 goto :keep_going
echo all 20 volumes transcribed, disabling task >> "%LOGFILE%"
schtasks /Change /TN "KGL_Uchimura_Zenshu_OCR" /DISABLE >> "%LOGFILE%" 2>&1
goto :done

:keep_going
echo volumes still pending, task stays enabled >> "%LOGFILE%"

:done
echo === run ended %DATE% %TIME% === >> "%LOGFILE%"
endlocal
