# 語言教練預備字庫「第二遍補做」— 補做第一輪全引擎失敗被跳過的 batch。
# 守門：若已有 gloss 程序在跑就跳過（不與整夜 run 衝突）。
# 可重入：gloss all 自動略過 ledger 已完成詞，只補缺口；全滿時為快速 no-op。
$ErrorActionPreference = 'Continue'
$log = 'C:/tmp/vocab_bank/secondpass.log'
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

$running = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*coach_vocab*gloss*' }
if ($running) {
    "[$stamp] gloss 仍在跑（PID $($running.ProcessId -join ',')），本次跳過。" | Out-File -Append -Encoding utf8 $log
    exit 0
}

"[$stamp] 開始第二遍 gloss all 補做。" | Out-File -Append -Encoding utf8 $log
Set-Location 'C:\Users\user\Desktop\know-graph-lab'
& 'C:\Users\user\Desktop\know-graph-lab\_whisper_venv\Scripts\python.exe' scripts/coach_vocab_bank.py gloss all *>> $log
"[$((Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))] 第二遍結束（exit $LASTEXITCODE）。" | Out-File -Append -Encoding utf8 $log
