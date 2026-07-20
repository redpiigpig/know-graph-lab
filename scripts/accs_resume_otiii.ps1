# ACCS OT III（出埃及記/利未記/民數記/申命記）合卷 resume，給排程 ACCS_OTIII_Resume 每 30 分跑。
# 四書共用一個掃描 PDF（2-5 出利民申），但 ref 無書名 → 必須每書各自 --book + 頁界分開跑。
# 頁界（人工核定，offset PDF=書頁+44）：exo 45-272 / lev 273-332 / num 333-428 / deu 429-522（523=附錄）。
# 🚨 絕不可 --replace（清光該 book_code）。🚨 各書頁界絕不可越界（跨書 1:1 會誤掛）。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'

$pdf = 'c:\tmp\古代基督信仰聖經註釋叢書2-5 出利民申.pdf'
$src = 'G:\我的雲端硬碟\資料\知識圖工作室\教父著作\基督教 - IVP - 古代基督信仰聖經註釋叢書\古代基督信仰聖經註釋叢書2-5 出 利 民 申.pdf'
$stem = '古代基督信仰聖經註釋叢書2-5 出利民申'

if (-not (Test-Path 'G:\')) {
    $launch = 'C:\Program Files\Google\Drive File Stream\launch.bat'
    if (Test-Path $launch) { Start-Process $launch; for ($i=0; $i -lt 20; $i++){ Start-Sleep -Seconds 3; if (Test-Path 'G:\'){break} } }
}
if (-not (Test-Path $pdf) -and (Test-Path $src)) { Copy-Item -LiteralPath $src -Destination $pdf -Force }
if (-not (Test-Path $pdf)) { Write-Output "OT III 本地 PDF 不在 → 跳過本次"; exit 0 }

$books = @(
  @{ code='exo'; pages='45-272';  vol='ACCS OT III（出埃及記）' },
  @{ code='lev'; pages='273-332'; vol='ACCS OT III（利未記）' },
  @{ code='num'; pages='333-428'; vol='ACCS OT III（民數記）' },
  @{ code='deu'; pages='429-522'; vol='ACCS OT III（申命記）' }
)

foreach ($b in $books) {
  $done = "c:\tmp\accs_$($b.code)_$stem.raw.done"
  if (Test-Path $done) { Write-Output "$($b.code) 已完成 → 跳過"; continue }
  Write-Output "=== 跑 $($b.code) pages $($b.pages) $(Get-Date -Format 'HH:mm') ==="
  python scripts\ingest_accs_genesis.py --pdf $pdf --book $b.code --pages $b.pages `
    --source-vol $b.vol --engine sonnet --batch 1 --resume --sleep 1 `
    *>> scripts\logs\accs_otiii.log
  # 這本沒寫 .done（rate-limit 中途退）→ 別接下一本，等下一次觸發續傳本書。
  if (-not (Test-Path $done)) { Write-Output "$($b.code) 本輪未完（多半 rate-limit）→ 停本輪"; break }
}
Write-Output "ACCS OT III resume 跑完一輪 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
