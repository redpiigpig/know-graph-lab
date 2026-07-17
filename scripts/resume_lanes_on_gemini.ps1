# 看門狗：Gemini 免費額度重置後自動放回暫停的翻譯線；ACCS 收官後放回 Sonnet 文獻。
# 分離式常駐（不依附 Claude session）。每 10 分一輪，兩條件都達成即收工。
#   條件 A：gemini_probe.py exit 0（額度恢復）→ 放回 plato / jung CW11 / panikkar vedic（皆 gemini-first，
#           回到 Gemini 後不再擠 Claude 帳號）
#   條件 B：ACCS 撒下(2sa) .done → 放回 Sonnet 文獻（純 sonnet，一直吃 Claude，故等 ACCS 全完才放）
$ErrorActionPreference = 'Continue'
Set-Location 'c:\Users\user\Desktop\know-graph-lab'
$log = 'scripts\logs\resume_watcher.log'
function Note($m) { Add-Content $log "[$(Get-Date -Format 'MM-dd HH:mm')] $m" }
function Running($pat) {
    [bool](Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
        Where-Object { $_.CommandLine -match $pat })
}
function Launch($cmd) {
    Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',
        "Set-Location 'c:\Users\user\Desktop\know-graph-lab'; $cmd"
}

# 單例保護：只認「-File …resume_lanes_on_gemini.ps1」啟動的真身，
# 避免把含此字串的臨時指令（git/grep/驗證）誤判成另一個 watcher。
$self = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
    Where-Object { $_.CommandLine -match '-[Ff]ile.*resume_lanes_on_gemini\.ps1' -and $_.ProcessId -ne $PID }
if ($self) { exit 0 }

Note "watcher start (Gemini 探測 + ACCS 收官偵測)"
$geminiDone = $false
$accsDone = $false
$done2sa = 'c:\tmp\accs_2sa_古代基督信仰聖經註釋叢書6-10 書士得撒.raw.done'

for ($i = 0; $i -lt 216; $i++) {   # 最多 ~36 小時
    if (-not $geminiDone) {
        python -X utf8 scripts\gemini_probe.py *> $null
        if ($LASTEXITCODE -eq 0) {
            Note "Gemini 額度已恢復 → 放回 plato / jung / panikkar"
            if (-not (Running 'plato_build')) {
                Launch 'foreach($w in "rhetoric","republic","philebus"){ python -X utf8 scripts\plato_build.py $w --engine auto --upload *>> scripts\logs\plato_resume.log }'
            }
            if (-not (Running 'jung_cw_translate')) {
                Launch 'python -X utf8 scripts\jung_cw_translate.py --vol 11 --engine auto *>> scripts\logs\jung_cw11.log'
            }
            if (-not (Running 'panikkar_auto')) {
                Launch 'python -X utf8 scripts\panikkar_auto.py --work vedic-experience --backend gemini-first --upload *>> scripts\logs\panikkar_bigtwo.log'
            }
            $geminiDone = $true
        }
    }
    if (-not $accsDone) {
        if (Test-Path $done2sa) {
            Note "ACCS 撒下已收官 → 放回 Sonnet 文獻"
            if (-not (Running 'ingest_lit_review')) {
                Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','c:\Users\user\Desktop\know-graph-lab\scripts\lit_review_sonnet_runner.ps1'
            }
            $accsDone = $true
        }
    }
    if ($geminiDone -and $accsDone) { Note "兩條件皆達成 → watcher 收工"; break }
    Start-Sleep -Seconds 600
}
Note "watcher end (gemini=$geminiDone accs=$accsDone)"
