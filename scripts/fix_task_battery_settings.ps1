<#
  補齊 KGL 系排程三件會讓工作「安靜地沒跑」的設定。這台是筆電（HP OMEN 16"，
  S0 Modern Standby），整天進出待機，所以這幾項在桌機上無所謂、在這裡很致命。

  🚨 兩個旗標的「好值」相反，別看到 False 就想改：
     電池那兩項 False = 好（不因電池中斷）
     StartWhenAvailable False = 壞（錯過排程就整輪蒸發）

  ① 電池殺手（$Battery）：工作排程器建立工作時**預設就勾著**「只有在電腦使用
     AC 電源時才啟動」與「切換到電池電源就停止」。沒人去設它，但跑到一半拔電源
     Windows 就直接砍掉整個工作，結束碼 3221225786（0xC000013A）。
     多數 KGL_* 早就是 False，這裡只補齊漏網那五支。

  ② 錯過排程（$StartWhenAvailable）：見該清單上方的註解。

  ③ z-lib 加重試：帳本（scripts/state/zlib_ledger.jsonl）逐筆即時寫入，斷在半路
     只損失手上那一筆，重跑會從斷點接下去——本來就能續跑，RestartCount=0 等於
     白白放棄這個特性。

  🚨 headless 不是解法。2026-09-08 實測：headless:true 被 DiamWall 直接
  「Access Denied」擋死（0 筆結果），headless:false 七秒過牆拿到 22 筆。
  那個看得見的 Chrome 視窗是必要之惡，只能讓工作本身別被砍。

  用法（一般權限即可，不需系統管理員）：
      powershell -ExecutionPolicy Bypass -File scripts\fix_task_battery_settings.ps1
      powershell -ExecutionPolicy Bypass -File scripts\fix_task_battery_settings.ps1 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Continue'

# 建立時被預設勾選、需要清掉的
$Battery = @(
    'KGLab-Quality-Sweep'
    'KGL_Dialogical_Write'
    'KGL_HBO_Reader_Keeper'
    'KGL_NDLTD_Keeper'
    'KGL_ZLib_Daily'
)

# 沒勾「錯過排程後盡快啟動」的——觸發時機器在睡就整輪蒸發，連 log 都不會有。
#
# 2026-09-08 實例：KGLab-OCR-Daily-18 的 18:00 那班沒跑，事件記錄 id=153 寫
# 「did not launch task as it missed its schedule. Consider using the
# configuration option to start the task when available」。那是當天最後一次
# OCR 機會，整天因此只完成 1 本。LastTaskResult 會是 2147946720，看起來像憑證
# 問題，其實是「這一輪沒有執行」。
#
# 全 repo 只有 KGLab-* 那四個與 Airiti 是 False，其餘 14 個 KGL_* 都是 True——
# 是建立時漏勾，不是刻意設計。這台是筆電、整天進出 Modern Standby，不補會一直漏。
$StartWhenAvailable = @(
    'KGLab-OCR-Daily-10'
    'KGLab-OCR-Daily-14'
    'KGLab-OCR-Daily-18'
    'KGLab-Quality-Sweep'
    'KGL_Airiti_Poll'
)

Write-Host '=== 修改前 ===' -ForegroundColor Cyan
Get-ScheduledTask | Where-Object { $_.TaskName -like 'KGL*' } | ForEach-Object {
    '{0,-34} stop={1,-5} disallow={2,-5} restart={3,-2} whenAvailable={4}' -f `
        $_.TaskName, $_.Settings.StopIfGoingOnBatteries,
        $_.Settings.DisallowStartIfOnBatteries, $_.Settings.RestartCount,
        $_.Settings.StartWhenAvailable
}

foreach ($n in $Battery) {
    try {
        $t = Get-ScheduledTask -TaskName $n -ErrorAction Stop
        $s = $t.Settings
        $s.StopIfGoingOnBatteries = $false
        $s.DisallowStartIfOnBatteries = $false
        # z-lib 專屬：斷了自己接回去。帳本已去重，重試不會重複抓。
        if ($n -eq 'KGL_ZLib_Daily') {
            $s.RestartCount = 2
            $s.RestartInterval = 'PT15M'
        }
        if ($PSCmdlet.ShouldProcess($n, 'clear battery-stop')) {
            Set-ScheduledTask -TaskName $n -Settings $s -ErrorAction Stop | Out-Null
            Write-Host "OK   $n" -ForegroundColor Green
        }
    } catch {
        Write-Host "FAIL $n : $($_.Exception.Message)" -ForegroundColor Red
    }
}

foreach ($n in $StartWhenAvailable) {
    try {
        $t = Get-ScheduledTask -TaskName $n -ErrorAction Stop
        $s = $t.Settings
        $s.StartWhenAvailable = $true
        if ($PSCmdlet.ShouldProcess($n, 'enable StartWhenAvailable')) {
            Set-ScheduledTask -TaskName $n -Settings $s -ErrorAction Stop | Out-Null
            Write-Host "OK   $n (StartWhenAvailable)" -ForegroundColor Green
        }
    } catch {
        Write-Host "FAIL $n : $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ''
Write-Host '=== 修改後 ===' -ForegroundColor Cyan
Get-ScheduledTask | Where-Object { $_.TaskName -like 'KGL*' } | ForEach-Object {
    '{0,-34} stop={1,-5} disallow={2,-5} restart={3,-2} whenAvailable={4}' -f `
        $_.TaskName, $_.Settings.StopIfGoingOnBatteries,
        $_.Settings.DisallowStartIfOnBatteries, $_.Settings.RestartCount,
        $_.Settings.StartWhenAvailable
}
Write-Host ''
Write-Host '提醒：日後用 Register-ScheduledTask 新建工作時，這兩個旗標又會預設為 True。' -ForegroundColor Yellow
Write-Host '      新增排程後回來跑一次這支，或建立時就帶 -Settings (New-ScheduledTaskSettingsSet' -ForegroundColor Yellow
Write-Host '      -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries)。' -ForegroundColor Yellow
