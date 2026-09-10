# Daily z-library harvest: refresh the wanted list, then pull one day's quota.
#
# The list holds 5,600+ titles. At 10 books a day it would take a decade, so the
# user asked (2026-09-10) for 40 a day and for the main account to join the
# rotation -- 4 accounts x 10 = 40. See the -Target switch below.
#
# Files land in <repo>\z-lib\ and the 16:00 ingest_new_books.py picks them up.
#
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts.
param(
    # Books to have downloaded TODAY by the time this run ends -- not per run.
    # A run that finds 25 already in the ledger only goes after the last 15, so
    # a top-up run costs nothing when the morning run already hit the number.
    [int]$Target = 40,
    # Free tier caps each account at 10 a day (account page: 'Daily limit 0/10').
    [int]$PerAccount = 10
)
$ErrorActionPreference = 'Continue'
# Two separate encoding bugs used to make this log unreadable, which meant a
# failed run left no usable evidence (2026-09-04: the run died at the DiamWall
# and the log said nothing readable about it).
#   1. PS 5.1 decodes a child process's stdout with Console::OutputEncoding,
#      which is cp950 on this zh-TW box -- python's UTF-8 output was already
#      mangled before it reached the file.
#   2. `*>>` writes UTF-16LE while Add-Content -Encoding utf8 writes UTF-8,
#      so the file ended up with both encodings interleaved.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT
$log = "$ROOT\scripts\logs\zlib_daily.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
$PY = 'C:\Users\user\AppData\Local\Python\bin\python.exe'

function Note($m) {
    "[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m | Add-Content -Path $log -Encoding utf8
}

function TodayCount {
    # Source of truth is the ledger, not this script's own tally: the day's 40
    # can be spread over the morning run and two top-ups, and a run that was
    # killed mid-way (commuting laptop goes to sleep) still banked its books.
    $n = & $PY -X utf8 "$ROOT\scripts\zlib_today.py" 2>$null
    if ($n -match '^\d+$') { return [int]$n }
    return 0
}

# '1' means the main account (.env has ZLIB_EMAIL with no suffix; an empty
# string will not survive the PowerShell -> cmd -> node hop, so the fetcher
# maps '1' back to ''). The user accepted the ban risk on the main account
# 2026-09-10 in exchange for the 4th slot -- 30 a day was not enough.
$ACCOUNTS = @('1', '2', '3', '4')

Note "start (target=$Target/day, $PerAccount per account)"
& $PY -X utf8 scripts\zlib_wanted.py *>&1 | Out-File -FilePath $log -Append -Encoding utf8
Note "wanted list refreshed"

$before = TodayCount
if ($before -ge $Target) {
    Note "already at $before/$Target today -- nothing to do"
    exit 0
}
Note "today so far: $before/$Target"

# The browser has to be visible - z-library's DiamWall rejects headless.
#
# Each account keeps its own session state file - sharing one would overwrite
# the previous account's cookies on every switch.
foreach ($acct in $ACCOUNTS) {
    $have = TodayCount
    if ($have -ge $Target) {
        Note "target reached ($have/$Target) -- skipping remaining accounts"
        break
    }
    # Never ask one account for more than its daily cap, and never for more
    # than what is still missing.
    $want = [Math]::Min($PerAccount, $Target - $have)
    Note "fetch start (account $acct, want $want)"

    # Let the child write to the log itself instead of piping into Out-File.
    #
    # `& node ... | Out-File` buffers in the PowerShell pipeline and only flushes
    # when the pipeline does. If this process dies mid-fetch, everything node had
    # said is lost -- and that is exactly the case worth diagnosing. 2026-09-07:
    # the 10:17 run died 4 seconds in, and the log ended at "fetch start
    # (account 2)" with not one line from node, so there was nothing to go on.
    # cmd's redirect appends as node writes, so a kill keeps whatever came before it.
    #
    # It also sidesteps the stdout decoding bug noted above: PowerShell never
    # decodes the bytes, so node's UTF-8 lands in the UTF-8 log unmangled.
    & cmd /c "node scripts\zlib_fetch.mjs --list output\zlib_wanted_all.jsonl --account $acct --limit $want >> ""$log"" 2>&1"
    Note "fetch exit=$LASTEXITCODE (account $acct, now $(TodayCount)/$Target)"
    Start-Sleep -Seconds 45
}

$after = TodayCount
$drop = Get-ChildItem "$ROOT\z-lib" -File -ErrorAction SilentlyContinue
Note ("done: {0}/{1} today (+{2} this run); drop holds {3} file(s)" -f $after, $Target, ($after - $before), $drop.Count)
if ($after -lt $Target) {
    # Not an error -- the top-up runs later in the day exist for exactly this.
    Note "short by $($Target - $after); a later top-up run will pick it up"
}
