# 每日自動續跑 ACCS 創世記 1-11 的 Gemini 批次 OCR（B：排程自動續跑）。
# Gemini 每日額度重置後（台灣約 15:00）跑此腳本，--resume 從 checkpoint 接續，
# --batch 4 省額度，空結果不清庫（ingest 內已 guard）。全頁完成寫 .done → 自動跳過。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'

# ingest 寫的是 ckpt.with_suffix('.done')＝<stem>.raw.done（不是 .done），路徑要對上才會 skip。
$done = 'c:\tmp\accs_gen_古代基督信仰聖經註釋叢書1 創1-11.raw.done'
if (Test-Path $done) { Write-Output "ACCS 創1-11 已完成（.done 存在）→ 跳過"; exit 0 }

$pdf = 'G:\我的雲端硬碟\資料\電子書\世界宗教\基督教\IVP - 古代基督信仰聖經註釋叢書 (27 冊)\古代基督信仰聖經註釋叢書1 創1-11.pdf'

# G: 是 Google Drive 串流碟，睡眠/Drive 當掉會卸載，導致整夜排程空跑（2026-06-14 踩過）。
# 自我修復：若 G: 未掛載，啟動 Google Drive 並等候最多 60 秒。
if (-not (Test-Path 'G:\')) {
    $launch = 'C:\Program Files\Google\Drive File Stream\launch.bat'
    if (Test-Path $launch) {
        Write-Output "G: 未掛載 → 啟動 Google Drive 並等候…"
        Start-Process $launch
        for ($i = 0; $i -lt 20; $i++) { Start-Sleep -Seconds 3; if (Test-Path 'G:\') { break } }
    }
}
if (-not (Test-Path $pdf)) { Write-Output "PDF 不在（G: 仍未掛載）→ 跳過本次"; exit 0 }

# G: 串流碟逐頁 on-demand 抓雲端，長跑時 render_page 會卡死（無 child、零 CPU；2026-06-14 踩過 2h）。
# → 一次性複製到本地 C:，OCR 全程只讀本地檔，徹底擺脫 G: I/O 脆弱性。
# 檔名須與 G: 原檔同 stem，否則 checkpoint 名（accs_gen_<stem>.raw.jsonl）對不上而從頭重跑。
$localPdf = 'c:\tmp\古代基督信仰聖經註釋叢書1 創1-11.pdf'
if (-not (Test-Path $localPdf)) {
    Write-Output "複製 PDF 到本地 $localPdf …"
    Copy-Item -LiteralPath $pdf -Destination $localPdf -Force
}
if (-not (Test-Path $localPdf)) { Write-Output "本地 PDF 複製失敗 → 跳過本次"; exit 0 }

# 引擎 = Sonnet（Haiku 掃描中文錯字率過高已確認；Sonnet 精度高 + Max 額度每 ~5h 滾動重置）。
# 每 2 小時跑一次：有 Max 額度就批次推進，沒額度就快速退出；.done 後自動跳過。
# --batch 1：多圖一次呼叫（batch≥2）會讓 claude CLI 卡死逾時（~2MB 單行 stream-json
# 撐爆 CLI parser；2026-06-15 實測 batch3 必逾時、batch1 秒回）。一頁一呼叫最穩。
python scripts\ingest_accs_genesis.py --pdf $localPdf --book gen --pages 1-316 `
  --source-vol 'ACCS OT I（創 1–11）' --engine sonnet --batch 1 --replace --resume --sleep 1 `
  *>> scripts\logs\accs_gen_1-11_sonnet.log
Write-Output "ACCS 創1-11 sonnet resume 跑完一輪 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
