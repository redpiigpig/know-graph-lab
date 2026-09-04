@echo off
REM 華藝期刊全文的排程批次。第一個引數是這一批要下幾篇（整批總數，不是每刊）。
REM 腳本自己上鎖（c:\tmp\press_airiti_download.lock），所以兩個排程時段撞在一起、
REM 或是別的 session 也在跑的時候，後到的那一輪會直接跳過，不會把速率乘二。
REM 每篇之間固定間隔 6 秒 —— 下載額度綁的是玄奘的機構 IP，衝太快是停整個學校。
cd /d C:\Users\user\Desktop\know-graph-lab
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set N=%1
if "%N%"=="" set N=25
echo. >> c:\tmp\airiti_download.log
echo ===== %DATE% %TIME%  batch %N% ===== >> c:\tmp\airiti_download.log
python -X utf8 scripts\press_airiti.py --batch %N% >> c:\tmp\airiti_download.log 2>&1
