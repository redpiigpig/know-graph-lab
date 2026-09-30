# 異譯對讀第二棒：等第一棒（run_tripitaka_compare_batch.ps1）跑完，
# 重試失敗的組（增一阿含經號撞名那批已修）、補跑分品，再只提交對讀產出。
param([int]$WaitPid = 0)
$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\user\Desktop\know-graph-lab'
$py = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$log = 'C:\tmp\cbeta\compare_auto2.log'
Set-Location $repo
if ($WaitPid -gt 0) { Wait-Process -Id $WaitPid -ErrorAction SilentlyContinue }
"=== $(Get-Date -Format s) 重試失敗組" | Out-File -Append -Encoding utf8 $log
& $py -X utf8 scripts\tripitaka_compare_auto.py --retry-failed *>> $log
"=== $(Get-Date -Format s) 分品補跑" | Out-File -Append -Encoding utf8 $log
& $py -X utf8 scripts\tripitaka_compare_auto.py --chapters *>> $log
"=== $(Get-Date -Format s) 提交" | Out-File -Append -Encoding utf8 $log
git add public/content/tripitaka/compare *>> $log
git commit -m "data(大藏經): 異譯對讀自動對齊（重試與分品）`n`nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" *>> $log
git push *>> $log
"=== $(Get-Date -Format s) ALL DONE" | Out-File -Append -Encoding utf8 $log
