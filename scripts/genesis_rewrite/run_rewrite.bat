@echo off
REM Genesis 15-volume rewrite. Scheduled every 30 min; script holds a PID lock so overlaps skip.
REM ASCII only on purpose: cmd.exe reads .bat in the ANSI codepage, so UTF-8 Chinese in REM
REM lines gets mis-decoded and executed as commands.
REM When all 124 sections are done: Disable-ScheduledTask KGL_Genesis_Rewrite
cd /d C:\Users\user\Desktop\know-graph-lab
python -X utf8 -u scripts\genesis_rewrite\rewrite.py --all >> C:\tmp\genesis_rewrite\run.log 2>&1
