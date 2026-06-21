# 收尾：把剩餘影片轉碼跑乾 → 重建 index → R2 sync 跑到完整一輪
# 兩段都用 retry-loop 扛 Drive 冷讀 native crash（SKILL prewarm 同模式）。
$ErrorActionPreference = "Continue"
$repo = "C:\Users\user\Desktop\know-graph-lab"
$py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
Set-Location $repo
$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
$log = "$repo\scripts\logs\finalize_$ts.log"
function Log($m) { "[$([DateTime]::Now.ToString('HH:mm:ss'))] $m" | Out-File $log -Append -Encoding utf8 }

# 1) 影片轉碼跑到 --count 為 0（或 12 次保險）
Log "=== 影片 retry-loop 開始 ==="
for ($i = 1; $i -le 12; $i++) {
  $rem = (& $py scripts\transcode_videos.py --count 2>$null | Select-Object -Last 1).Trim()
  Log "try $i：尚餘 $rem 支"
  if ($rem -eq "0") { break }
  & $py scripts\transcode_videos.py *>> $log
}

# 2) 重建 index（影片大小變了 + 收尾旋轉影片）
Log "=== 重建 index ==="
& $py scripts\build_photo_index.py *>> $log

# 3) R2 sync 跑到 node 自己印 '=== Done in'（完整一輪），最多 50 次
Log "=== R2 sync retry-loop 開始 ==="
for ($i = 1; $i -le 50; $i++) {
  Log "r2 sync try $i"
  $out = & node scripts\sync_photos_to_r2.mjs 2>&1
  $out | Out-File $log -Append -Encoding utf8
  if ($out | Select-String -Pattern "=== Done in" -Quiet) { Log "R2 sync 完整完成"; break }
  Log "r2 sync try $i 中斷，續跑"
  Start-Sleep -Seconds 5
}
Log "=== FINALIZE ALL DONE ==="
