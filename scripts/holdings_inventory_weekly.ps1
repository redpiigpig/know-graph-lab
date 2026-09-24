# 每週重建資料總盤點 docs/holdings.md，只 commit 這一個檔（見 research-data-holdings skill §6）
$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\user\Desktop\know-graph-lab'
$py = 'C:\Users\user\Desktop\know-graph-lab\_whisper_venv\Scripts\python.exe'
$log = Join-Path $repo 'output\holdings\weekly.log'
New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null
Set-Location $repo
"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" | Out-File $log -Append -Encoding utf8
if (-not (Test-Path 'G:\我的雲端硬碟')) { 'G: 不在，略過（DriveFS 卡住？見 CLAUDE.md）' | Out-File $log -Append -Encoding utf8; exit 0 }
& $py -X utf8 scripts\holdings_inventory.py *>> $log
git add docs/holdings.md
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
  git commit -m "chore(盤點): 每週更新資料總盤點 docs/holdings.md`n`nCo-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" *>> $log
  git push *>> $log
}
