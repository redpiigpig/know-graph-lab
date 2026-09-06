@echo off
REM 華藝期刊全文的排程批次。引數：<這一批最多幾篇> <今天最多幾篇>。
REM 排程是每半小時跑一次「探一下」：人不在學校時，腳本驗完機構身分就收手
REM （一個請求），所以高頻並不等於高流量；人一到學校才真的開始下。
REM 一天的總量由 --daily-cap 守住，不是由排程的次數守住。
REM 腳本自己上鎖（c:\tmp\press_airiti_download.lock），所以兩個排程時段撞在一起、
REM 或是別的 session 也在跑的時候，後到的那一輪會直接跳過，不會把速率乘二。
REM 每篇之間固定間隔 6 秒 —— 下載額度綁的是玄奘的機構 IP，衝太快是停整個學校。
cd /d C:\Users\user\Desktop\know-graph-lab
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set N=%1
if "%N%"=="" set N=50
set CAP=%2
if "%CAP%"=="" set CAP=200
echo. >> c:\tmp\airiti_download.log
echo ===== %DATE% %TIME%  batch %N% ===== >> c:\tmp\airiti_download.log
python -X utf8 scripts\press_airiti.py --batch %N% --daily-cap %CAP% >> c:\tmp\airiti_download.log 2>&1
