# 印順學派與弘誓：兩批全文轉錄的背景續跑 keeper（排程 KGL_Yinshun_Fulltext，每 60 分鐘）。
#
#   A：scripts\yinshun_debate_fulltext.py        人間佛教論爭 74 檔（文字層／HTML／MD／OCR）
#   B：scripts\yinshun_japan_bilingual.py --auto 日本學者論印順 74 篇（OCR→切段→逐段中譯→R2）
#
# 每一輪：G: 在不在 → 各條工作若沒在跑、也還沒完成，就用明寫的解譯器背景重啟（兩條＝並行上限 2）；
# 工作本身可續跑（Drive 上的 _status.json／_對照\*.json），筆電休眠中斷後這裡會接回去。
# 兩條都印出 ALL_DONE → commit＋push 兩份索引 → 把自己這個排程註銷（不留空轉 keeper）。
# 同一個「本輪結束」摘要連續 36 輪沒變（卡死在永遠做不完的檔）→ 也註銷，並留 stalled 記錄待人處理。
#
# 🚨 本檔含中文，必須存 UTF-8 BOM（PS 5.1 無 BOM 會當 ANSI 解碼→語法錯、Start-Process 照樣回 pid 但秒死）。
# 🚨 python 一律寫完整路徑：裸 python 會中 _whisper_venv（缺套件、卡 import 不報錯）。
# 🚨 只管自己啟動的 PID（pid 檔），不 Stop-Process 別人的程序。

$ErrorActionPreference = 'Continue'
$Repo  = 'C:\Users\user\Desktop\know-graph-lab'
$PY    = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$State = Join-Path $Repo 'output\yinshun-fulltext'
$Task  = 'KGL_Yinshun_Fulltext'
New-Item -ItemType Directory -Force $State | Out-Null
$KLog = Join-Path $State 'keeper.log'
function Log($m) { Add-Content -Path $KLog -Encoding UTF8 -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }

if (-not (Test-Path 'G:\我的雲端硬碟')) { Log 'G: 不在（Drive 卡住），本輪跳過'; exit 0 }

$Jobs = @(
  @{ Name = 'debate'; Args = @('-X', 'utf8', 'scripts\yinshun_debate_fulltext.py') },
  @{ Name = 'japan';  Args = @('-X', 'utf8', 'scripts\yinshun_japan_bilingual.py', '--auto') }
)

function Is-Running($name) {
  $pf = Join-Path $State "$name.pid"
  if (-not (Test-Path $pf)) { return $false }
  $procId = [int](Get-Content $pf -TotalCount 1)
  $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
  return ($null -ne $p -and $p.ProcessName -like 'python*')
}

function Last-Log($name) {
  Get-ChildItem $State -Filter "$name-*.out.log" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
}

$allDone = $true
foreach ($j in $Jobs) {
  $n = $j.Name
  $doneFlag = Join-Path $State "$n.done"
  if (Test-Path $doneFlag) { continue }
  if (Is-Running $n) { $allDone = $false; Log "$n 還在跑"; continue }
  $last = Last-Log $n
  if ($last) {
    $txt = Get-Content $last.FullName -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($txt -match 'ALL_DONE') { New-Item -ItemType File $doneFlag -Force | Out-Null; Log "$n 完成"; continue }
    # 卡死偵測：本輪結束摘要與上一輪相同就累計
    $sum = ($txt | Select-String '本輪結束' | Select-Object -Last 1)
    if ($sum) {
      $sf = Join-Path $State "$n.summary"; $cf = Join-Path $State "$n.same"
      $prev = if (Test-Path $sf) { Get-Content $sf -Encoding UTF8 -TotalCount 1 } else { '' }
      if ("$sum" -eq $prev) { $c = 1 + [int](Get-Content $cf -ErrorAction SilentlyContinue | Select-Object -First 1) } else { $c = 0 }
      Set-Content $sf -Encoding UTF8 -Value "$sum"; Set-Content $cf -Value $c
      if ($c -ge 36) { New-Item -ItemType File (Join-Path $State "$n.stalled") -Force | Out-Null; New-Item -ItemType File $doneFlag -Force | Out-Null; Log "$n 連續 36 輪無進展，視為卡死：$sum"; continue }
    }
  }
  $allDone = $false
  $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
  $out = Join-Path $State "$n-$stamp.out.log"; $err = Join-Path $State "$n-$stamp.err.log"
  $p = Start-Process -FilePath $PY -ArgumentList $j.Args -WorkingDirectory $Repo -WindowStyle Hidden `
        -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
  Set-Content (Join-Path $State "$n.pid") -Value $p.Id
  Log "$n 啟動 PID $($p.Id)"
}

if ($allDone) {
  Set-Location $Repo
  $idx = @('public/content/research-data/yinshun-hongshi/debate-index.json',
           'public/content/research-data/yinshun-hongshi/japan-index.json')
  git diff --quiet -- $idx
  if ($LASTEXITCODE -ne 0) {
    git commit -m "chore(研究資料/印順弘誓): 全文轉錄背景工作完成，更新人間佛教論爭與日本學者論印順索引`n`nCo-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" -- $idx | Out-Null
    git push 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { git pull --no-rebase --no-edit 2>&1 | Out-Null; git push 2>&1 | Out-Null }
    $local = git rev-parse HEAD; git fetch origin master 2>&1 | Out-Null; $remote = git rev-parse origin/master
    Log "索引已 commit：local $local／origin $remote"
  }
  Log '兩條工作皆完成，註銷排程'
  Unregister-ScheduledTask -TaskName $Task -Confirm:$false -ErrorAction SilentlyContinue
}
