# 排程 KGL_Footnote_Relink 每日 04:30：用模型補註號（scripts/relink_footnotes_daily.py；額度用完自停、隔天續）
$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\user\Desktop\know-graph-lab'
$py = 'C:\Users\user\Desktop\know-graph-lab\_whisper_venv\Scripts\python.exe'
$out = Join-Path $repo 'output\relink\daily_stdout.log'
Set-Location $repo
if (-not (Test-Path 'G:\我的雲端硬碟')) { "$(Get-Date -Format 'MM-dd HH:mm') G: 不在，略過" | Out-File (Join-Path $repo 'output\relink\daily.log') -Append -Encoding utf8; exit 0 }
& $py -X utf8 scripts\relink_footnotes_daily.py --max-calls 400 --hours 3 *> $out
