# ACCS 創 12-50（OT II）batch-1 OCR 自動續跑迴圈。仿 accs_loop.ps1，但：
#  ① 不同 PDF / checkpoint / .done（stem=創12-50，與創1-11 分開、不互相覆蓋）。
#  ② **不可 --replace**：--replace 會刪光整個 book_code=gen（含已完成的創1-11 698 列）！
#     12-50 章號與 1-11 不重疊，直接 upsert(merge-duplicates) 累加即可。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'
$done = 'c:\tmp\accs_gen_古代基督信仰聖經註釋叢書1 創12-50.raw.done'
$pdf  = 'c:\tmp\古代基督信仰聖經註釋叢書1 創12-50.pdf'
$src  = 'G:\我的雲端硬碟\資料\電子書\世界宗教\基督教\IVP - 古代基督信仰聖經註釋叢書 (27 冊)\古代基督信仰聖經註釋叢書1 創12-50.pdf'
$log  = 'scripts\logs\accs_gen_12-50.log'
# 本地 PDF 不在就從 G: 複製（G: 串流長跑會卡，故只讀本地）。
if (-not (Test-Path $pdf)) {
    if (-not (Test-Path 'G:\')) {
        $launch = 'C:\Program Files\Google\Drive File Stream\launch.bat'
        if (Test-Path $launch) { Start-Process $launch; for ($i=0; $i -lt 20; $i++){ Start-Sleep -Seconds 3; if (Test-Path 'G:\'){break} } }
    }
    if (Test-Path $src) { Copy-Item -LiteralPath $src -Destination $pdf -Force }
}
if (-not (Test-Path $pdf)) { Write-Output "創12-50 本地 PDF 不在且無法複製 → 退出"; exit 0 }
$round = 0
while (-not (Test-Path $done)) {
    $round++
    Write-Output "=== g2 loop round $round  $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" *>> $log
    python scripts\ingest_accs_genesis.py --pdf $pdf --book gen --pages 1-654 `
      --source-vol 'ACCS OT II（創 12–50）' --engine sonnet --batch 1 --resume --sleep 1 *>> $log
    if (Test-Path $done) { break }
    Start-Sleep -Seconds 30
}
Write-Output "ACCS 創12-50 全本完成（.done）loop 結束 $(Get-Date -Format 'yyyy-MM-dd HH:mm')" *>> $log
