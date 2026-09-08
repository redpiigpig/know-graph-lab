@echo off
REM 《諸宗教的對話神學》七卷初稿的續跑器，給 Windows 排程用。
REM
REM 為什麼要走排程而不是背景程序：Claude session 一結束，背景 python 就被砍，
REM 84 章的工作被腰斬過三次。排程不受 session 生死影響。
REM 腳本本身可重入（已存在的章直接跳過），所以每次醒來就是接著跑。
REM
REM 🚨 python 要寫絕對路徑。Task Scheduler 的 PATH 跟互動 shell 不一樣，寫 "python"
REM    會找不到執行檔、任務立刻回 LastTaskResult=1，而且**log 一個字都不會寫**——
REM    看起來就像排程根本沒跑。2026-09-08 為此空轉了一整天。
REM
REM 🚨 跑完要 Disable-ScheduledTask，否則會無限空轉。判準看產出（84 章到齊）不看排程狀態。
cd /d C:\Users\user\Desktop\know-graph-lab
C:\Users\user\Desktop\know-graph-lab\_whisper_venv\Scripts\python.exe -X utf8 scripts\dialogical_theology_write.py >> output\dialogical_write.log 2>&1
