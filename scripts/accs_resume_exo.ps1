# ACCS 出埃及記（OT III）單次 resume pass，給排程 ACCS_Exo_Resume 每 2h 跑。
# 仿 accs_resume_g2.ps1：① exo PDF/checkpoint/.done。② **絕不可 --replace**（會刪光 book_code=exo）。
# Exodus 內容＝PDF 45-272（出埃及記 book 1-228；273=利未記 標題頁，絕不可越界否則 Lev 1:1 誤掛 exo）。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'

$done = 'c:\tmp\accs_exo_古代基督信仰聖經註釋叢書2-5 出利民申.raw.done'
if (Test-Path $done) { Write-Output "ACCS 出埃及記 已完成（.done 存在）→ 跳過"; exit 0 }

$pdf = 'c:\tmp\古代基督信仰聖經註釋叢書2-5 出利民申.pdf'
$src = 'G:\我的雲端硬碟\資料\電子書\世界宗教\基督教\IVP - 古代基督信仰聖經註釋叢書 (27 冊)\古代基督信仰聖經註釋叢書2-5 出 利 民 申.pdf'

# G: 串流碟睡眠/當掉會卸載；未掛載先啟動 Google Drive 等候。
if (-not (Test-Path 'G:\')) {
    $launch = 'C:\Program Files\Google\Drive File Stream\launch.bat'
    if (Test-Path $launch) { Start-Process $launch; for ($i=0; $i -lt 20; $i++){ Start-Sleep -Seconds 3; if (Test-Path 'G:\'){break} } }
}
# 本地 PDF 不在就複製（OCR 全程只讀本地，避免 G: 串流長跑卡死 render_page）。
if (-not (Test-Path $pdf) -and (Test-Path $src)) { Copy-Item -LiteralPath $src -Destination $pdf -Force }
if (-not (Test-Path $pdf)) { Write-Output "出埃及記 本地 PDF 不在 → 跳過本次"; exit 0 }

# 必 --batch 1（多圖一次呼叫會卡死 CLI）；**無 --replace**；只跑 Exodus 頁 45-272。
python scripts\ingest_accs_genesis.py --pdf $pdf --book exo --pages 45-272 `
  --source-vol 'ACCS OT III（出埃及記）' --engine sonnet --batch 1 --resume --sleep 1 `
  *>> scripts\logs\accs_exo.log
Write-Output "ACCS 出埃及記 resume 跑完一輪 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
