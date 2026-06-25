# Final pass for training album fill (G:-only, no D: needed).
# rename -> HEIC->JPG -> index -> transcode event videos -> index -> R2
$ErrorActionPreference = "Continue"
$py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }
$repo = "C:\Users\user\Desktop\know-graph-lab"
$log = "C:\tmp\final_pass.log"
Set-Location $repo
function Step($name, $exe, $argList) {
  "[$([DateTime]::Now.ToString('HH:mm:ss'))] >>> STEP: $name" | Out-File $log -Append -Encoding utf8
  & $exe @argList *>> $log
  $rc = $LASTEXITCODE
  "[$([DateTime]::Now.ToString('HH:mm:ss'))] <<< $name exit=$rc" | Out-File $log -Append -Encoding utf8
  return $rc
}
"=== FINAL_PASS START $([DateTime]::Now) ===" | Out-File $log -Encoding utf8

$rc = Step "rename auto training" $py @("-u","scripts\rename_photos.py","auto","training")
if ($rc -ne 0) { "=== FINAL_PASS FAILED at rename ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "convert HEIC->JPG" $py @("-u","scripts\convert_heic_to_jpg.py")
if ($rc -ne 0) { "=== FINAL_PASS FAILED at heic ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "build index (post-heic)" $py @("-u","scripts\build_photo_index.py")
if ($rc -ne 0) { "=== FINAL_PASS FAILED at index1 ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "transcode event videos" $py @("-u","scripts\transcode_videos.py")
if ($rc -ne 0) { "=== FINAL_PASS FAILED at transcode ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "build index (post-transcode)" $py @("-u","scripts\build_photo_index.py")
if ($rc -ne 0) { "=== FINAL_PASS FAILED at index2 ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "R2 sync training thumbs" "node" @("scripts\sync_photos_to_r2.mjs","training")
"[note] R2 training rc=$rc (non-fatal; local Drive is source of truth)" | Out-File $log -Append -Encoding utf8
$rc2 = Step "R2 index-only" "node" @("scripts\sync_photos_to_r2.mjs","--index-only")
"[note] R2 index rc=$rc2" | Out-File $log -Append -Encoding utf8

"=== FINAL_PASS DONE $([DateTime]::Now) ===" | Out-File $log -Append -Encoding utf8
