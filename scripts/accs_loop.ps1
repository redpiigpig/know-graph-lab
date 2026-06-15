# ACCS 創1-11 batch-1 OCR 自動續跑迴圈：每次 run 結束（完成/bail/被系統資源耗盡殺掉）
# 都從 checkpoint resume 重跑，直到 .done 出現。survives crash / 「OS can't spawn worker thread」。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'
$done = 'c:\tmp\accs_gen_古代基督信仰聖經註釋叢書1 創1-11.done'
$pdf  = 'c:\tmp\古代基督信仰聖經註釋叢書1 創1-11.pdf'
$log  = 'scripts\logs\accs_gen_1-11_batch1.log'
$round = 0
while (-not (Test-Path $done)) {
    $round++
    Write-Output "=== loop round $round  $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" *>> $log
    python scripts\ingest_accs_genesis.py --pdf $pdf --book gen --pages 1-316 `
      --source-vol 'ACCS OT I（創 1–11）' --engine sonnet --batch 1 --replace --resume --sleep 1 *>> $log
    if (Test-Path $done) { break }
    Start-Sleep -Seconds 30   # 給系統喘息（資源耗盡時別狂 spawn）
}
Write-Output "ACCS 創1-11 全本完成（.done）loop 結束 $(Get-Date -Format 'yyyy-MM-dd HH:mm')" *>> $log
