# Sonnet 文獻翻譯 runner（genesis-philosophy shard 1）— 分離式，不依附 Claude session。
# 啟動前提：已用 translation_lane_claim.py 認領 gemini-2 lane（本 runner 每輪自動續租）。
# 結束（成功跑完 shard 或重試耗盡）自動 release lane 讓雲端池收回。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'
$log = 'scripts\logs\lit_review_sonnet.log'

# 防重複：已有 sonnet shard-1 worker 就跳過
$running = Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
    Where-Object { $_.CommandLine -match 'ingest_lit_review\.py' -and $_.CommandLine -match 'sonnet' }
if ($running) { Add-Content $log "[runner] 已有 sonnet worker (PID $($running[0].ProcessId)) → 退出"; exit 0 }

$n = 0
while ($true) {
    python -X utf8 scripts\translation_lane_claim.py acquire --lane gemini-2 --owner claude --minutes 1440 --note "sonnet runner 自動續租" *>> $log
    python -X utf8 scripts\ingest_lit_review.py --fetch-fulltext --project genesis-philosophy --resume --engine sonnet --pace 1 --shard-index 1 --shard-count 7 *>> $log
    if ($LASTEXITCODE -eq 0) { Add-Content $log "[runner] worker 正常結束（shard 完成）"; break }
    $n++
    Add-Content $log "[runner] worker exit=$LASTEXITCODE (retry #$n) $(Get-Date -Format 'MM-dd HH:mm')"
    if ($n -ge 40) { Add-Content $log "[runner] 40 次重試耗盡 → 放棄"; break }
    Start-Sleep -Seconds 300
}
python -X utf8 scripts\translation_lane_claim.py release --lane gemini-2 *>> $log
Add-Content $log "[runner] 收工，lane 已釋放 $(Get-Date -Format 'MM-dd HH:mm')"
