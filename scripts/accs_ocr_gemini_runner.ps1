# 看門狗：Gemini 免費額度一恢復就 OCR 校園版 ACCS 單書卷（NT 優先，Gemini Vision batch-4）。
# 分離式常駐，不依附 Claude session。多書卷（needs_boundaries）不在此批，待定界後另跑。
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'
$log = 'scripts\logs\accs_ocr_gemini.log'
function Note($m) { Add-Content $log "[$(Get-Date -Format 'MM-dd HH:mm')] $m" }

# 單例保護：只認 -File 啟動的真身
$self = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
    Where-Object { $_.CommandLine -match '-[Ff]ile.*accs_ocr_gemini_runner\.ps1' -and $_.ProcessId -ne $PID }
if ($self) { exit 0 }

Note "runner start：等 Gemini 復活後 OCR 校園版單書卷（batch-4，NT 先）"
for ($i = 0; $i -lt 288; $i++) {   # 最多 ~48 小時（每 10 分一輪）
    python -X utf8 scripts\gemini_probe.py *> $null
    if ($LASTEXITCODE -eq 0) {
        Note "Gemini 有額度 → 跑 accs_ocr_run（ready 單書卷，NT 先）"
        python -X utf8 scripts\accs_ocr_run.py --engine gemini --batch 4 *>> $log
        if ($LASTEXITCODE -eq 0) { Note "單書卷全批完成 → runner 收工"; break }
        Note "本輪中止（多半 Gemini 當輪額度乾）→ 10 分後重探續傳"
    }
    Start-Sleep -Seconds 600
}
Note "runner end"
