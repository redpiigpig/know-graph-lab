# Daily z-library harvest: refresh the wanted list, then pull one day's quota.
#
# Free accounts cap daily downloads (~10), so this is a long-haul drip: 1,400+
# wanted titles get worked through a few per day. Files land in <repo>\z-lib\ and
# the 16:00 ingest_new_books.py picks them up from there.
#
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts.
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

function Note($m) {
    "[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m | Add-Content -Path $log -Encoding utf8
}

# Free tier tops out at 10 downloads a day (measured 2026-09-02); ask for a
# couple more and the extras just fail, which the fetcher now detects and stops on.
$limit = 12

# Spare accounts only. Leave the main account out on purpose.
$ACCOUNTS = @('2', '3', '4')
if ($args.Count -ge 1) { $limit = [int]$args[0] }

Note "start (limit=$limit)"
& 'C:\Users\user\AppData\Local\Python\bin\python.exe' -X utf8 scripts\zlib_wanted.py *>&1 |
    Out-File -FilePath $log -Append -Encoding utf8
Note "wanted list refreshed"

# The browser has to be visible - z-library's DiamWall rejects headless.
#
# The daily cap is per account (10 on the free tier, confirmed on the account
# page: 'Daily limit 0/10'). The user registered three spare accounts and asked
# to work all three, accepting that they may get banned; the main account is
# deliberately NOT in this list so a ban cannot cost the one that matters.
# Each account keeps its own session state file - sharing one would overwrite
# the previous account's cookies on every switch.
foreach ($acct in $ACCOUNTS) {
    Note "fetch start (account $acct)"
    & node scripts\zlib_fetch.mjs --list output\zlib_wanted_all.jsonl --account $acct --limit $limit *>&1 |
        Out-File -FilePath $log -Append -Encoding utf8
    Note "fetch exit=$LASTEXITCODE (account $acct)"
    Start-Sleep -Seconds 45
}

$drop = Get-ChildItem "$ROOT\z-lib" -File -ErrorAction SilentlyContinue
Note ("drop now holds {0} file(s)" -f $drop.Count)
