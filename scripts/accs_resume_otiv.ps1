# ACCS OT IV（約書亞/士師/路得/撒上/撒下）合卷 resume，給排程 ACCS_OTIV_Resume 每 30 分跑。
# 五書共用一個掃描 PDF（6-10 書士得撒），ref 無書名 → 必須每書各自 --book + 頁界分開跑。
# 頁界（人工核定 5 個標題頁，offset PDF=書頁+42）：jos 43-184 / jdg 185-298 / rut 299-318 / 1sa 319-512 / 2sa 513-612（613=附錄）。
# 🚨 絕不可 --replace（清光該 book_code）。🚨 各書頁界絕不可越界（跨書 1:1 會誤掛）。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'

# 防重複：已有 ingest_accs_genesis worker 在跑（排程/手動皆算）就跳過本輪
$running = Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
    Where-Object { $_.CommandLine -match 'ingest_accs_genesis\.py' }
if ($running) { Write-Output "已有 ACCS worker (PID $($running[0].ProcessId)) → 跳過本輪"; exit 0 }

$pdf = 'c:\tmp\古代基督信仰聖經註釋叢書6-10 書士得撒.pdf'
$src = 'G:\我的雲端硬碟\資料\知識圖工作室\教父著作\基督教 - IVP - 古代基督信仰聖經註釋叢書\古代基督信仰聖經註釋叢書6-10 書 士 得 撒.pdf'
$stem = '古代基督信仰聖經註釋叢書6-10 書士得撒'

if (-not (Test-Path 'G:\')) {
    $launch = 'C:\Program Files\Google\Drive File Stream\launch.bat'
    if (Test-Path $launch) { Start-Process $launch; for ($i=0; $i -lt 20; $i++){ Start-Sleep -Seconds 3; if (Test-Path 'G:\'){break} } }
}
if (-not (Test-Path $pdf) -and (Test-Path $src)) { Copy-Item -LiteralPath $src -Destination $pdf -Force }
if (-not (Test-Path $pdf)) { Write-Output "OT IV 本地 PDF 不在 → 跳過本次"; exit 0 }

$books = @(
  @{ code='jos'; pages='43-184';  vol='ACCS OT IV（約書亞記）' },
  @{ code='jdg'; pages='185-298'; vol='ACCS OT IV（士師記）' },
  @{ code='rut'; pages='299-318'; vol='ACCS OT IV（路得記）' },
  @{ code='1sa'; pages='319-512'; vol='ACCS OT IV（撒母耳記上）' },
  @{ code='2sa'; pages='513-612'; vol='ACCS OT IV（撒母耳記下）' }
)

foreach ($b in $books) {
  $done = "c:\tmp\accs_$($b.code)_$stem.raw.done"
  if (Test-Path $done) { Write-Output "$($b.code) 已完成 → 跳過"; continue }
  Write-Output "=== 跑 $($b.code) pages $($b.pages) $(Get-Date -Format 'HH:mm') ==="
  python scripts\ingest_accs_genesis.py --pdf $pdf --book $b.code --pages $b.pages `
    --source-vol $b.vol --engine sonnet --batch 1 --resume --sleep 1 `
    *>> scripts\logs\accs_otiv.log
  if (-not (Test-Path $done)) { Write-Output "$($b.code) 本輪未完（多半 rate-limit）→ 停本輪"; break }
}
Write-Output "ACCS OT IV resume 跑完一輪 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
