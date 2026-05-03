@echo off
cd /d "%~dp0"
echo ========================================
echo  轉錄流水線（faster-whisper medium）
echo ========================================
echo.
_whisper_venv\Scripts\python.exe -u scripts\transcribe-interviews.py
echo.
echo ========================================
echo  完成！按任意鍵關閉
echo ========================================
pause
