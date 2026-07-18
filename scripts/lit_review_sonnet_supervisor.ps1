# 研究回顧全文翻譯 — 過夜看門狗（resumable）
# 三個計畫輪流：大愛道革命 / 世界宗教文化導論(WR1) / 宗教系國文講義(SL1)
# fetch_fulltext 連續 4 次失敗會自 abort（429/網路）→ 本 loop 睡一段再重試 --resume。
# 每翻完一段即持久化，斷點續傳不重做。
# 引擎預設 gemini（內含 gemini→nvidia→haiku 免費鏈；Sonnet 週期額度耗盡時改用此鏈）。
# 用法：powershell -ExecutionPolicy Bypass -File scripts\lit_review_sonnet_supervisor.ps1 [-Engine gemini]
param([string]$Engine = 'gemini')
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot\..
$log = "C:\tmp\lit_review_${Engine}_supervisor.log"
$rounds = 80
$sleepSec = 600   # 每輪之間睡 10 分鐘

$jobs = @(
  @{ name = 'dadaodao';  args = @('--project','mahaprajapati-revolution') },
  @{ name = 'world-rel'; args = @('--project','world-religions-intro','--book-id','WR1') },
  @{ name = 'sinograph'; args = @('--project','sinographic-literature','--book-id','SL1') }
)

function Log($m) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'MM-dd HH:mm:ss'), $m
  Write-Host $line
  Add-Content -Path $log -Value $line -Encoding utf8
}

Log "=== supervisor start (rounds=$rounds, sleep=${sleepSec}s, engine=$Engine) ==="
for ($i = 1; $i -le $rounds; $i++) {
  foreach ($j in $jobs) {
    Log "round $i/$rounds → $($j.name) fetch-fulltext --engine $Engine --resume"
    $a = @('-X','utf8','scripts/ingest_lit_review.py','--fetch-fulltext') + $j.args + @('--engine',$Engine,'--resume','--pace','1')
    & python @a *>> $log
    Log "round $i/$rounds → $($j.name) done (exit=$LASTEXITCODE)"
  }
  if ($i -lt $rounds) {
    Log "sleeping ${sleepSec}s before round $($i+1)"
    Start-Sleep -Seconds $sleepSec
  }
}
Log "=== supervisor finished all rounds ==="
