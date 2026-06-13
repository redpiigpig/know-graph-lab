# 每日自動續跑 ACCS 創世記 1-11 的 Gemini 批次 OCR（B：排程自動續跑）。
# Gemini 每日額度重置後（台灣約 15:00）跑此腳本，--resume 從 checkpoint 接續，
# --batch 4 省額度，空結果不清庫（ingest 內已 guard）。全頁完成寫 .done → 自動跳過。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'

$done = 'c:\tmp\accs_gen_古代基督信仰聖經註釋叢書1 創1-11.done'
if (Test-Path $done) { Write-Output "ACCS 創1-11 已完成（.done 存在）→ 跳過"; exit 0 }

$pdf = 'G:\我的雲端硬碟\資料\電子書\世界宗教\基督教\IVP - 古代基督信仰聖經註釋叢書 (27 冊)\古代基督信仰聖經註釋叢書1 創1-11.pdf'
if (-not (Test-Path $pdf)) { Write-Output "PDF 不在（G: 未掛載？）→ 跳過本次"; exit 0 }

python scripts\ingest_accs_genesis.py --pdf $pdf --book gen --pages 1-316 `
  --source-vol 'ACCS OT I（創 1–11）' --engine gemini --batch 4 --replace --resume --sleep 2 `
  *>> scripts\logs\accs_gen_1-11_gemini.log
Write-Output "ACCS 創1-11 resume 跑完一輪 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
