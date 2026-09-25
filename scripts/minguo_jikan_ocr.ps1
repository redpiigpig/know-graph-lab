# 《民國佛教期刊文獻集成》OCR 排程班（KGL_Minguo_Jikan_OCR，每 30 分鐘一班）
# 一班做三件事：(1) G: 在不在 (2) 補下載缺的冊（最多 2 冊，別占掉整班）(3) OCR 25 分鐘。
# 引擎由 minguo_jikan_ocr.py 自己決定：GPU 鎖沒人握就用 GPU，否則 --device cpu。
# 🚨 檔案要存 UTF-8 BOM（含中文的 .ps1 沒 BOM 會被 PS5.1 當 ANSI 解碼、語法錯）。
# 🚨 裸 python 會中 _whisper_venv，解譯器路徑寫死。
$ErrorActionPreference = 'Continue'
# python 用 -X utf8 吐 UTF-8，PS5.1 預設用主控台碼頁（950）解，log 會變亂碼；兩邊都講明 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$repo = 'C:\Users\user\Desktop\know-graph-lab'
$py = 'C:\Users\user\AppData\Local\Python\bin\python.exe'
$logDir = Join-Path $repo 'output\minguo_jikan'
$log = Join-Path $logDir ('ocr_' + (Get-Date -Format 'yyyy-MM-dd') + '.log')
New-Item -ItemType Directory -Force $logDir | Out-Null
Set-Location $repo
"=== 班 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
if (-not (Test-Path 'G:\我的雲端硬碟')) {
  'G: 不在，略過這班（DriveFS 卡住？見 CLAUDE.md）' | Out-File $log -Append -Encoding utf8
  exit 0
}
# 補下載（優先冊先）；一班最多 2 冊，Commons 每檔間隔 5 秒由腳本自己控制
$tsv = 'G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成\_篇目_太虛相關_全集.tsv'
$fetching = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*haichaoyin_commons_fetch*' }
if ($fetching) {
  '另一個下載程序在跑（手動整批），這班不補下載' | Out-File $log -Append -Encoding utf8
} elseif (Test-Path $tsv) {
  & $py -X utf8 -u scripts\haichaoyin_commons_fetch.py --series all --priority-tsv $tsv --max-files 2 2>&1 |
    Select-Object -Last 12 | Out-File $log -Append -Encoding utf8
}
# DILA 篇目快取有新頁（整庫 crawl 還在跑、或有人補抓）就重建 _篇目_全集.tsv，切單篇才切得到
$full = 'G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成\_篇目_全集.tsv'
$cache = Join-Path $repo 'output\minguo_jikan\dila_pages'
if (Test-Path $cache) {
  $newest = (Get-ChildItem $cache -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
  if (-not (Test-Path $full) -or ((Get-Item $full).LastWriteTime -lt $newest)) {
    & $py -X utf8 -u scripts\minguo_jikan_dila_catalog.py build 2>&1 | Select-Object -First 3 | Out-File $log -Append -Encoding utf8
  }
}
& $py -X utf8 -u scripts\minguo_jikan_ocr.py run --max-minutes 25 2>&1 | Out-File $log -Append -Encoding utf8
"--- 班結束 exit=$LASTEXITCODE $(Get-Date -Format 'HH:mm:ss')" | Out-File $log -Append -Encoding utf8
exit 0
