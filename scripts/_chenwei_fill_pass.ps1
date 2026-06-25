# Chenwei import pass: fill missing local files -> classify -> rename -> index -> R2.
# Run ONLY after training final pass is done (avoid index/rename conflict + disk contention).
$ErrorActionPreference = "Continue"
$py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }
$repo = "C:\Users\user\Desktop\know-graph-lab"
$log = "C:\tmp\chenwei_pass.log"
Set-Location $repo
function Step($name, $exe, $argList) {
  "[$([DateTime]::Now.ToString('HH:mm:ss'))] >>> STEP: $name" | Out-File $log -Append -Encoding utf8
  & $exe @argList *>> $log
  $rc = $LASTEXITCODE
  "[$([DateTime]::Now.ToString('HH:mm:ss'))] <<< $name exit=$rc" | Out-File $log -Append -Encoding utf8
  return $rc
}
"=== CHENWEI_PASS START $([DateTime]::Now) ===" | Out-File $log -Encoding utf8

$rc = Step "fill from local (copy + cr2 + heic->jpg)" $py @("-u","scripts\chenwei_fill_from_local.py")
if ($rc -ne 0) { "=== CHENWEI_PASS FAILED at fill ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "classify plan" $py @("-u","scripts\classify_photos.py","plan")
if ($rc -ne 0) { "=== CHENWEI_PASS FAILED at classify-plan ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "classify execute" $py @("-u","scripts\classify_photos.py","execute")
if ($rc -ne 0) { "=== CHENWEI_PASS FAILED at classify-exec ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "rename auto chenwei" $py @("-u","scripts\rename_photos.py","auto","chenwei")
if ($rc -ne 0) { "=== CHENWEI_PASS FAILED at rename ===" | Out-File $log -Append -Encoding utf8; exit 1 }

$rc = Step "build index" $py @("-u","scripts\build_photo_index.py")

$rc = Step "R2 sync chenwei thumbs" "node" @("scripts\sync_photos_to_r2.mjs","chenwei")
"[note] R2 chenwei rc=$rc (non-fatal)" | Out-File $log -Append -Encoding utf8
$rc2 = Step "R2 index-only" "node" @("scripts\sync_photos_to_r2.mjs","--index-only")

"=== CHENWEI_PASS DONE $([DateTime]::Now) ===" | Out-File $log -Append -Encoding utf8
