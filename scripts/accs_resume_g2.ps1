# ACCS 創 12-50（OT II）單次 resume pass，給排程 ACCS_Gen2_Resume 每 2h 跑。
# 仿 accs_resume.ps1，但：① 不同 PDF/checkpoint/.done（創12-50）。
# ② **絕不可 --replace**（會刪光 book_code=gen 含已完成的創1-11 698 列）。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'

# ingest 寫的 .done＝<stem>.raw.done
$done = 'c:\tmp\accs_gen_古代基督信仰聖經註釋叢書1 創12-50.raw.done'
if (Test-Path $done) { Write-Output "ACCS 創12-50 已完成（.done 存在）→ 跳過"; exit 0 }

$pdf = 'c:\tmp\古代基督信仰聖經註釋叢書1 創12-50.pdf'
$src = 'G:\我的雲端硬碟\資料\知識圖工作室\教父著作\基督教 - IVP - 古代基督信仰聖經註釋叢書\古代基督信仰聖經註釋叢書1 創12-50.pdf'

# G: 串流碟睡眠/當掉會卸載；未掛載先啟動 Google Drive 等候。
if (-not (Test-Path 'G:\')) {
    $launch = 'C:\Program Files\Google\Drive File Stream\launch.bat'
    if (Test-Path $launch) { Start-Process $launch; for ($i=0; $i -lt 20; $i++){ Start-Sleep -Seconds 3; if (Test-Path 'G:\'){break} } }
}
# 本地 PDF 不在就複製（OCR 全程只讀本地，避免 G: 串流長跑卡死 render_page）。
if (-not (Test-Path $pdf) -and (Test-Path $src)) { Copy-Item -LiteralPath $src -Destination $pdf -Force }
if (-not (Test-Path $pdf)) { Write-Output "創12-50 本地 PDF 不在 → 跳過本次"; exit 0 }

# 必 --batch 1（多圖一次呼叫會卡死 CLI）；**無 --replace**（章號 12-50 不重疊 1-11，直接 upsert 累加）。
python scripts\ingest_accs_genesis.py --pdf $pdf --book gen --pages 1-654 `
  --source-vol 'ACCS OT II（創 12–50）' --engine sonnet --batch 1 --resume --sleep 1 `
  *>> scripts\logs\accs_gen_12-50.log
Write-Output "ACCS 創12-50 resume 跑完一輪 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
