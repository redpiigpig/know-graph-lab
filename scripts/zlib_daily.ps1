# Daily z-library harvest: refresh the wanted list, then pull one day's quota.
#
# Free accounts cap daily downloads (~10), so this is a long-haul drip: 1,400+
# wanted titles get worked through a few per day. Files land in <repo>\z-lib\ and
# the 16:00 ingest_new_books.py picks them up from there.
#
# ASCII-only on purpose: PS 5.1 on a zh-TW box misreads UTF-8-no-BOM scripts.
$ErrorActionPreference = 'Continue'
$ROOT = 'c:\Users\user\Desktop\know-graph-lab'
Set-Location $ROOT
$log = "$ROOT\scripts\logs\zlib_daily.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null

function Note($m) {
    "[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm'), $m | Add-Content -Path $log -Encoding utf8
}

$limit = 10
if ($args.Count -ge 1) { $limit = [int]$args[0] }

Note "start (limit=$limit)"
& 'C:\Users\user\AppData\Local\Python\bin\python.exe' -X utf8 scripts\zlib_wanted.py *>> $log
Note "wanted list refreshed"

# The browser has to be visible - z-library's DiamWall rejects headless.
& node scripts\zlib_fetch.mjs --list output\zlib_wanted_all.jsonl --limit $limit *>> $log
Note "fetch exit=$LASTEXITCODE"

$drop = Get-ChildItem "$ROOT\z-lib" -File -ErrorAction SilentlyContinue
Note ("drop now holds {0} file(s)" -f $drop.Count)
