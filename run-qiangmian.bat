@echo off
cd /d "%~dp0"
echo ========================================
echo  宗教史讀書會 YouTube 下載與轉錄流水線
echo ========================================
echo.
python -u scripts\transcribe-qiangmian.py
echo.
echo ========================================
echo  完成！按任意鍵關閉
echo ========================================
pause
