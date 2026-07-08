@echo off
REM 夜間品質維護（KGLab-Quality-Sweep，02:30）：
REM   1. 全館品質評分寫回 ebooks.quality_*（純規則零 LLM，~5 分鐘）
REM   2. REOCR tier 重轉錄（staging + gate，一晚最多 5 本，quota 撞牆自動停）
REM 手動跑：scripts\run_quality_sweep.bat
setlocal
set "PY=C:\Users\user\AppData\Local\Python\bin\python.exe"
cd /d "%~dp0.."
set "LOGFILE=%~dp0logs\quality_%DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2%.log"
if not exist "%~dp0logs" mkdir "%~dp0logs"

echo === Quality sweep started %DATE% %TIME% === >> "%LOGFILE%"

echo --- quality_sweep --all --- >> "%LOGFILE%"
"%PY%" scripts\quality_sweep.py --all >> "%LOGFILE%" 2>&1
echo sweep exit=%ERRORLEVEL% >> "%LOGFILE%"

echo --- requeue_reocr run --limit 5 --- >> "%LOGFILE%"
"%PY%" scripts\requeue_reocr.py run --limit 5 >> "%LOGFILE%" 2>&1
echo requeue exit=%ERRORLEVEL% >> "%LOGFILE%"

echo --- push_transcription_progress --- >> "%LOGFILE%"
"%PY%" scripts\push_transcription_progress.py >> "%LOGFILE%" 2>&1
echo push exit=%ERRORLEVEL% >> "%LOGFILE%"

echo === Quality sweep ended %DATE% %TIME% === >> "%LOGFILE%"
endlocal
