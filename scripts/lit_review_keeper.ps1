# 研究回顧全文翻譯看門狗的「自我修復」keeper（仿 KGL_Fleet_Keeper）
# 排程每 30 分跑一次：若看門狗沒在跑就重啟它（Start-Process 分離會在 session teardown 死掉，
# 只有排程能撐過整夜／session 重啟）。引擎讀 state 檔（預設 haiku），切引擎＝改該檔即可、免重註冊。
# 純 ASCII，避免 PS5.1 中文解析崩（見 [[project_fleet_keeper]]）。
$repo = 'C:\Users\user\Desktop\know-graph-lab'
$sup  = Join-Path $repo 'scripts\lit_review_sonnet_supervisor.ps1'
$state = Join-Path $repo 'scripts\state\lit_review_engine.txt'
$engine = 'haiku'
if (Test-Path $state) { $e = (Get-Content $state -Raw).Trim(); if ($e) { $engine = $e } }
if ($engine -eq 'off') { return }   # 寫 'off' 到 state 檔即停用 keeper 重啟

$me = $PID
$running = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
  Where-Object { $_.ProcessId -ne $me -and $_.CommandLine -like '*-File*lit_review_sonnet_supervisor.ps1*' })
if ($running.Count -eq 0) {
  Start-Process -FilePath 'powershell.exe' `
    -ArgumentList '-ExecutionPolicy','Bypass','-File',$sup,'-Engine',$engine `
    -WindowStyle Hidden -WorkingDirectory $repo
  Add-Content -Path 'C:\tmp\lit_review_keeper.log' -Value ("[{0}] relaunched supervisor (engine={1})" -f (Get-Date -Format 'MM-dd HH:mm:ss'), $engine) -Encoding utf8
}
