@echo off
REM 《内村鑑三全集》20 卷夜班 OCR（本機 MinerU）。
REM   1. 補下載還沒抓完的卷（archive.org，冪等、會續抓）
REM   2. 把下載完成的卷登記進 ebooks（冪等）
REM   3. 照卷序 OCR，最多跑 4 小時；GPU 被佔就安靜退出
REM   4. 20 卷全部有 chunks 了就把這個排程自己關掉（免得像 keeper 那樣空轉）
REM
REM 注意：python 一定要寫死路徑，裸 python 會中 _whisper_venv（沒有 fitz/requests）。

setlocal
cd /d "%~dp0\.."

set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set TODAY=%%I
set LOGFILE=%LOGDIR%\uchimura_zenshu_%TODAY%.log

set PY=C:\Users\user\AppData\Local\Python\bin\python.exe
if not exist "%PY%" set PY=python

echo === 全集夜班開始 %DATE% %TIME% === >> "%LOGFILE%"

echo --- fetch（補下載） --- >> "%LOGFILE%"
"%PY%" scripts\uchimura_zenshu_fetch.py >> "%LOGFILE%" 2>&1
echo fetch exit=%ERRORLEVEL% >> "%LOGFILE%"

echo --- register --- >> "%LOGFILE%"
"%PY%" scripts\uchimura_zenshu_register.py >> "%LOGFILE%" 2>&1
echo register exit=%ERRORLEVEL% >> "%LOGFILE%"

echo --- mineru ocr --- >> "%LOGFILE%"
"%PY%" scripts\uchimura_zenshu_ocr.py --max-minutes 240 >> "%LOGFILE%" 2>&1
set OCR_EXIT=%ERRORLEVEL%
echo ocr exit=%OCR_EXIT% >> "%LOGFILE%"

REM 全部轉完就自己收班：--status 回報「待轉錄 0 卷」時關閉排程。
"%PY%" scripts\uchimura_zenshu_ocr.py --status >> "%LOGFILE%" 2>&1
"%PY%" -c "import subprocess,sys,re;out=subprocess.run([r'%PY%',r'scripts\uchimura_zenshu_ocr.py','--status'],capture_output=True,text=True,encoding='utf-8').stdout;m=re.search(r'待轉錄 (\d+) 卷',out or '');sys.exit(0 if (m and m.group(1)=='0') else 1)"
if errorlevel 1 goto :keep_going
echo 20 卷全部轉錄完成，關閉排程 >> "%LOGFILE%"
schtasks /Change /TN "KGL_Uchimura_Zenshu_OCR" /DISABLE >> "%LOGFILE%" 2>&1
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0notify.ps1" -Title "內村全集 OCR 完工" -Body "20 卷全部轉錄完成，夜班排程已自動關閉" >nul 2>&1
goto :done

:keep_going
echo 還有卷沒轉完，排程保留 >> "%LOGFILE%"

:done
echo === 全集夜班結束 %DATE% %TIME% === >> "%LOGFILE%"
endlocal
