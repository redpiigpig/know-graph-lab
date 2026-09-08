<#
  把 KGL 系排程的「電池殺手」設定關掉，並讓 z-lib 那支失敗後會自己重試。

  為什麼需要這支：Windows 工作排程器**建立工作時預設就勾著**
  「只有在電腦使用 AC 電源時才啟動工作」與「如果電腦切換到電池電源就停止」。
  沒有人去設它，但這台是筆電（HP OMEN 16"）——跑到一半拔電源，Windows 就直接
  砍掉整個工作，結束碼 3221225786（0xC000013A）。KGL_ZLib_Daily 昨天就是這樣死的。

  三個 OCR 排程與 Airiti 早就是 False，所以這裡只補齊漏網的那幾支，設定一致。

  z-lib 另外加重試：帳本（scripts/state/zlib_ledger.jsonl）是逐筆即時寫入的，
  斷在半路只損失手上那一筆，重跑會從斷點接下去——本來就能續跑，RestartCount=0
  等於白白放棄這個特性。

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

Write-Host '=== 修改前 ===' -ForegroundColor Cyan
Get-ScheduledTask | Where-Object { $_.TaskName -like 'KGL*' } | ForEach-Object {
    '{0,-34} stop={1,-5} disallow={2,-5} restart={3}' -f `
        $_.TaskName, $_.Settings.StopIfGoingOnBatteries,
        $_.Settings.DisallowStartIfOnBatteries, $_.Settings.RestartCount
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

Write-Host ''
Write-Host '=== 修改後 ===' -ForegroundColor Cyan
Get-ScheduledTask | Where-Object { $_.TaskName -like 'KGL*' } | ForEach-Object {
    '{0,-34} stop={1,-5} disallow={2,-5} restart={3}' -f `
        $_.TaskName, $_.Settings.StopIfGoingOnBatteries,
        $_.Settings.DisallowStartIfOnBatteries, $_.Settings.RestartCount
}
Write-Host ''
Write-Host '提醒：日後用 Register-ScheduledTask 新建工作時，這兩個旗標又會預設為 True。' -ForegroundColor Yellow
Write-Host '      新增排程後回來跑一次這支，或建立時就帶 -Settings (New-ScheduledTaskSettingsSet' -ForegroundColor Yellow
Write-Host '      -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries)。' -ForegroundColor Yellow
