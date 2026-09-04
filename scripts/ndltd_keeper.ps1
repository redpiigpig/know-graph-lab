# NDLTD retry keeper. The site throws a CAPTCHA at this IP after a group or two;
# each run picks up where the last one stopped. Disables itself when all groups
# are done.
#
# ASCII only, on purpose. PowerShell 5.1 reads a .ps1 with no BOM as ANSI, so any
# Chinese in here gets mangled into a parse error -- the task then exits 1 and
# writes no log at all, which looks exactly like "never ran".
#
# cmd /c for the redirect, not PowerShell's *>>: PS 5.1 wraps every stderr line
# from a native exe in a NativeCommandError and writes the file as UTF-16.
$repo = "C:\Users\user\Desktop\know-graph-lab"
$log = "C:\tmp\ndltd_keeper.log"
$env:PYTHONIOENCODING = "utf-8"
Set-Location $repo
cmd /c "python -X utf8 scripts\thesis_ndltd.py --search >> $log 2>&1"
$state = & python -X utf8 scripts\thesis_ndltd.py --check-done
if ($state -match "ALL_DONE") {
  Disable-ScheduledTask -TaskName "KGL_NDLTD_Keeper" -ErrorAction SilentlyContinue
  cmd /c "echo ALL_DONE, task disabled. >> $log"
}
