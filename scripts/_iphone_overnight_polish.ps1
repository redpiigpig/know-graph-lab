$ErrorActionPreference = "Continue"
$repo = "C:\Users\user\Desktop\know-graph-lab"
$py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
$logDir = "$repo\scripts\logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$log = "$logDir\iphone_polish_$stamp.log"

function Log($m) { "$((Get-Date).ToString('HH:mm:ss'))  $m" | Tee-Object -FilePath $log -Append }

Log "=== STEP 1: targeted rename ==="
& $py -u "$repo\scripts\_iphone_rename_targeted.py" 2>&1 | Tee-Object -FilePath $log -Append

Log "=== STEP 2: build_photo_index ==="
& $py -u "$repo\scripts\build_photo_index.py" 2>&1 | Tee-Object -FilePath $log -Append

Log "=== STEP 3: R2 thumbs (chenwei) ==="
node "$repo\scripts\sync_photos_to_r2.mjs" chenwei 2>&1 | Tee-Object -FilePath $log -Append

Log "=== STEP 4: R2 index-only ==="
node "$repo\scripts\sync_photos_to_r2.mjs" --index-only 2>&1 | Tee-Object -FilePath $log -Append

Log "=== IPHONE_POLISH DONE ==="
