# 語言教練字庫 gloss 自動重啟迴圈 — 對抗 OS 執行緒耗盡崩潰。
# gloss all 崩潰退出後自動再起（reentrant 接續），直到 en 達標或迴圈上限。
$ErrorActionPreference = 'Continue'
$log = 'C:/tmp/vocab_bank/overnight.log'
$py  = 'C:\Users\user\Desktop\know-graph-lab\_whisper_venv\Scripts\python.exe'
Set-Location 'C:\Users\user\Desktop\know-graph-lab'

for ($i = 1; $i -le 80; $i++) {
    $en = 0
    $line = (& $py scripts/coach_vocab_bank.py status 2>$null | Select-String '^en\s')
    if ($line) { $en = [int](($line.ToString().Trim() -split '\s+')[-1]) }
    if ($en -ge 29800) {
        "[loop] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') en=$en 達標，停止迴圈。" | Out-File -Append -Encoding utf8 $log
        break
    }
    "[loop $i] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 啟動 gloss all (en=$en)" | Out-File -Append -Encoding utf8 $log
    & $py scripts/coach_vocab_bank.py gloss all *>> $log 2>&1
    Start-Sleep -Seconds 8
}
"[loop] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 迴圈結束。" | Out-File -Append -Encoding utf8 $log
