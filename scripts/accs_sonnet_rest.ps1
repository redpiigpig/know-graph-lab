# ACCS 舊約 ready 單書卷 → Sonnet Vision OCR（Claude Max 車道）。
# 與 Gemini 車道分流：Gemini 只跑新約（accs_ocr_gemini_runner.ps1 --testament NT），
# 本腳本只跑舊約 ready 單書卷（伯 / 詩×2 / 賽×2）。每 30 分由排程 ACCS_OT_Sonnet 觸發。
# 設計沿用 accs_resume_otiv.ps1：① 逐卷 .done 跳過 ② G:→c:\tmp 本地複製（避開串流碟 render 卡死）
#   ③ --engine sonnet --batch 1（sonnet 多圖會卡死 CLI）④ 本輪未完（rate-limit）即停、下輪續。
# 🚨 一律 **無 --replace**：詩/賽各有「同 book_code 兩半 PDF」，--replace 會互相清光。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'
$log = 'scripts\logs\accs_ot_sonnet.log'

# --- PID 鎖：同時只准一個本車道實例（Max 額度共用；防 30 分排程自我重疊 / 手動重跑撞車）。---
# 原子 CreateNew 建鎖並寫入本進程 PID；已存在則看記錄的 PID 是否還活著（活＝跳過；死＝陳舊、接管）。
$lock = 'c:\tmp\accs_ot_sonnet.lock'
function Get-Lock {
    try {
        $fs = [System.IO.File]::Open($lock, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
        $sw = New-Object System.IO.StreamWriter($fs); $sw.Write($PID); $sw.Close(); return $true
    } catch { return $false }
}
if (-not (Get-Lock)) {
    $old = (Get-Content $lock -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($old -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) {
        Write-Output "另一實例 PID $old 在跑 → 跳過本輪"; exit 0
    }
    Remove-Item $lock -Force -ErrorAction SilentlyContinue    # 陳舊鎖 → 接管
    if (-not (Get-Lock)) { Write-Output "搶鎖失敗（另一實例同時啟動）→ 跳過"; exit 0 }
}

try {
    # G: 串流碟睡眠/當掉會卸載；未掛載先啟動 Google Drive 等候。
    if (-not (Test-Path 'G:\')) {
        $launch = 'C:\Program Files\Google\Drive File Stream\launch.bat'
        if (Test-Path $launch) { Start-Process $launch; for ($i=0; $i -lt 20; $i++){ Start-Sleep -Seconds 3; if (Test-Path 'G:\'){break} } }
    }

    $base = 'G:\我的雲端硬碟\資料\知識圖工作室\教父著作\基督教 - IVP - 古代基督信仰聖經註釋叢書'
    # 舊約 ready 單書卷；code/pages 對齊 accs_volume_config.json。
    $vols = @(
      @{ code='job'; file='古代基督信仰聖經註釋叢書18 伯.pdf';       pages='1-412'; vol='ACCS（約伯記）' },
      @{ code='psa'; file='古代基督信仰聖經註釋叢書19 詩1-50.pdf';   pages='1-708'; vol='ACCS（詩篇）' },
      @{ code='psa'; file='古代基督信仰聖經註釋叢書19 詩51-150.pdf'; pages='1-760'; vol='ACCS（詩篇）' },
      @{ code='isa'; file='古代基督信仰聖經註釋叢書23 賽1-39.pdf';   pages='1-534'; vol='ACCS（以賽亞書）' },
      @{ code='isa'; file='古代基督信仰聖經註釋叢書23 賽40-66.pdf';  pages='1-584'; vol='ACCS（以賽亞書）' }
    )

    foreach ($v in $vols) {
      $stem = [System.IO.Path]::GetFileNameWithoutExtension($v.file)
      $done = "c:\tmp\accs_$($v.code)_$stem.raw.done"
      if (Test-Path $done) { Write-Output "$($v.code) [$stem] 已完成 → 跳過"; continue }

      $src = Join-Path $base $v.file
      $pdf = Join-Path 'c:\tmp' $v.file    # 同檔名 → checkpoint stem 對得上，續接 Gemini 已跑的頁
      if (-not (Test-Path $pdf) -and (Test-Path $src)) { Copy-Item -LiteralPath $src -Destination $pdf -Force }
      if (-not (Test-Path $pdf)) { Write-Output "$($v.code) 本地 PDF 不在（G: 未掛載？）→ 跳過本輪"; continue }

      Write-Output "=== 跑 $($v.code) [$stem] pages $($v.pages) sonnet $(Get-Date -Format 'MM-dd HH:mm') ==="
      python scripts\ingest_accs_genesis.py --pdf $pdf --book $v.code --pages $v.pages `
        --source-vol $v.vol --engine sonnet --batch 1 --resume --sleep 1 `
        *>> $log
      # 本卷未寫 .done（多半 rate-limit 中途退）→ 別接下一卷，等下輪續傳本卷。
      if (-not (Test-Path $done)) { Write-Output "$($v.code) 本輪未完（多半 rate-limit / 額度乾）→ 停本輪"; break }
    }
    Write-Output "ACCS OT sonnet 跑完一輪 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}
finally { Remove-Item $lock -Force -ErrorAction SilentlyContinue }
