@echo off
REM 《諸宗教的對話神學》七卷初稿的續跑器，給 Windows 排程用。
REM
REM 為什麼要走排程而不是背景程序：Claude session 一結束，背景 python 就被砍，
REM 84 章的工作被腰斬過三次。排程不受 session 生死影響。
REM 腳本本身可重入（已存在的章直接跳過），所以每次醒來就是接著跑。
REM 防重入靠排程的 -MultipleInstances IgnoreNew，不另外做鎖。
REM
REM 🚨 跑完要 Disable-ScheduledTask，否則會無限空轉。判準看產出（84 章到齊）不看排程狀態。
cd /d C:\Users\user\Desktop\know-graph-lab
python -X utf8 scripts\dialogical_theology_write.py >> output\dialogical_write.log 2>&1
