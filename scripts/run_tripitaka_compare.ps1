# 異譯對讀接力（取代前兩棒）：等短經批次那個 python 結束 → 重試失敗短經 → 提交推送
# → 長經分品一次一部、每部做完就提交推送（一部要好幾小時，別等全部做完才上線）。
# 可重跑：已完成的組與已做完的部都會跳過。
param([int]$WaitPid = 0)
$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\user\Desktop\know-graph-lab'
$py = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$log = 'C:\tmp\cbeta\compare_relay.log'
Set-Location $repo

function Log($m) { "=== $(Get-Date -Format s) $m" | Out-File -Append -Encoding utf8 $log }
function Publish($msg) {
    # 只加對讀產出，別的 session 未提交的東西一律不碰
    git add public/content/tripitaka/compare *>> $log
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -m "$msg`n`nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" *>> $log
        git push *>> $log
    }
}

if ($WaitPid -gt 0) { Log "等短經批次 PID $WaitPid"; Wait-Process -Id $WaitPid -ErrorAction SilentlyContinue }
Log '重試失敗的短經'
& $py -X utf8 scripts\tripitaka_compare_auto.py --retry-failed *>> $log
Publish 'data(大藏經): 異譯對讀自動對齊・短經'

for ($i = 1; $i -le 200; $i++) {
    Log "分品第 $i 部"
    $out = & $py -X utf8 scripts\tripitaka_compare_auto.py --chapters --limit 1 2>&1
    $out | Out-File -Append -Encoding utf8 $log
    if (($out -join "`n") -match '分品：0 部') { break }
    if (($out -join "`n") -match '引擎不可用') { Log '引擎不可用，停'; break }
    Publish "data(大藏經): 異譯對讀自動對齊・長經分品（第 $i 部）"
}
Log 'ALL DONE'
