# 整夜媒體優化序列：HEIC→JPG → index → 影片 HEVC 轉碼 → index
# 由 Start-Process detach 跑，可隨時重跑續傳（兩個 ledger 各自記錄進度）。
$ErrorActionPreference = "Continue"
$repo = "C:\Users\user\Desktop\know-graph-lab"
$py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
Set-Location $repo
$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
$log = "$repo\scripts\logs\media_optimize_$ts.log"

function Step($name, $scriptArgs) {
  "=== $name :: $(Get-Date -Format o) ===" | Out-File -FilePath $log -Append -Encoding utf8
  & $py @scriptArgs *>> $log
  "--- $name 完成 (exit $LASTEXITCODE) :: $(Get-Date -Format o) ---" | Out-File -FilePath $log -Append -Encoding utf8
}

Step "HEIC to JPG"        @("scripts\convert_heic_to_jpg.py")
Step "rebuild index (heic)" @("scripts\build_photo_index.py")
Step "transcode videos"   @("scripts\transcode_videos.py")
Step "rebuild index (video)" @("scripts\build_photo_index.py")

"=== ALL DONE :: $(Get-Date -Format o) ===" | Out-File -FilePath $log -Append -Encoding utf8
