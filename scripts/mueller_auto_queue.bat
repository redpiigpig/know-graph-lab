@echo off
REM Continuous Max Müller collected-works auto-transcription queue.
REM Registered as a Windows scheduled task (every few hours). The runner holds a
REM lock so a re-fire while a run is still active just exits — no double-run. It
REM resumes from the per-section cache, so reboots/crashes lose nothing.
cd /d C:\Users\user\Desktop\know-graph-lab
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python scripts\mueller_auto.py --run-queue >> c:\tmp\mueller_queue_scheduled.log 2>&1
