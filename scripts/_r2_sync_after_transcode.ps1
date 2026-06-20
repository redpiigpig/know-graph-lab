# 等媒體優化序列（HEIC+影片+index 重建）跑完 → 自動 R2 同步
# 讓 217 張新 jpg 的縮圖上 R2，redpiigpig.com 雲端才看得到。
$ErrorActionPreference = "Continue"
$repo = "C:\Users\user\Desktop\know-graph-lab"
Set-Location $repo
$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
$log = "$repo\scripts\logs\r2_sync_$ts.log"

"等待影片轉碼序列 ALL DONE … $(Get-Date -Format o)" | Out-File $log -Append -Encoding utf8
while ($true) {
  $ml = Get-ChildItem "$repo\scripts\logs\media_optimize_*.log" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Desc | Select-Object -First 1
  if ($ml -and (Select-String -Path $ml.FullName -Pattern "ALL DONE" -Quiet -ErrorAction SilentlyContinue)) { break }
  Start-Sleep -Seconds 120
}
"序列完成，開始 R2 同步 $(Get-Date -Format o)" | Out-File $log -Append -Encoding utf8

node scripts\sync_photos_to_r2.mjs *>> $log

"=== R2 SYNC DONE :: $(Get-Date -Format o) ===" | Out-File $log -Append -Encoding utf8
