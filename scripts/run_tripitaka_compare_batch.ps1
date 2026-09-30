# 異譯對讀全量批次（tripitaka_compare_auto.py）。可重跑：已完成與已判失敗的組會跳過。
# 🚨 解譯器寫全路徑：裸 python 會中 _whisper_venv（見記憶 feedback_powershell_python_whisper_venv）
$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\user\Desktop\know-graph-lab'
$py = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$log = 'C:\tmp\cbeta\compare_auto.log'
Set-Location $repo
"=== $(Get-Date -Format s) 開始：短經" | Out-File -Append -Encoding utf8 $log
& $py -X utf8 scripts\tripitaka_compare_auto.py *>> $log
"=== $(Get-Date -Format s) 分品（長經）" | Out-File -Append -Encoding utf8 $log
& $py -X utf8 scripts\tripitaka_compare_auto.py --chapters *>> $log
"=== $(Get-Date -Format s) 提交" | Out-File -Append -Encoding utf8 $log
# 只加對讀產出，別的 session 未提交的東西一律不碰
git add public/content/tripitaka/compare *>> $log
git commit -m "data(大藏經): 異譯對讀自動對齊批次產出`n`nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" *>> $log
git push *>> $log
"=== $(Get-Date -Format s) ALL DONE" | Out-File -Append -Encoding utf8 $log
