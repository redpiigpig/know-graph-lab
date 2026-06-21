# 收尾：影片轉碼跑乾 → 重建 index → R2 sync 跑到完整一輪
# 兩段都 retry-loop 扛偶發 native crash / Drive 冷讀。
$ErrorActionPreference = "Continue"
$repo = "C:\Users\user\Desktop\know-graph-lab"
$py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
Set-Location $repo
$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
$log = "$repo\scripts\logs\finalize_$ts.log"
function Log($m) { "[$([DateTime]::Now.ToString('HH:mm:ss'))] $m" | Out-File $log -Append -Encoding utf8 }

# 1) 影片：transcode 一次處理所有 todo；retry 扛偶發 crash（count 純 ASCII，強制轉字串比較）
for ($i = 1; $i -le 8; $i++) {
  $n = ("$(& $py scripts\transcode_videos.py --count 2>$null)").Trim()
  Log "影片 try $i：尚餘 $n 支"
  if ($n -eq "0") { break }
  & $py scripts\transcode_videos.py 2>&1 | Out-File $log -Append -Encoding utf8
}

# 2) 重建 index（影片大小變了）
Log "重建 index"
& $py scripts\build_photo_index.py 2>&1 | Out-File $log -Append -Encoding utf8

# 3) R2 sync：跑到 node 自己印 '=== Done in'（完整一輪未崩），最多 50 次
for ($i = 1; $i -le 50; $i++) {
  Log "R2 sync try $i"
  & node scripts\sync_photos_to_r2.mjs 2>&1 | Out-File $log -Append -Encoding utf8
  if (Select-String -Path $log -Pattern "=== Done in" -Quiet) { Log "R2 sync 完整完成"; break }
  Log "R2 sync try $i 中斷，續跑"
  Start-Sleep -Seconds 5
}
Log "=== FINALIZE ALL DONE ==="
