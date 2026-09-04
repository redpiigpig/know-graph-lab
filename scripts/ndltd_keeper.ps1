# NDLTD 續跑：站方對本 IP 掛驗證碼時整輪會中止，冷卻後再跑就能接續。
# 全部組別跑完（log 出現「待查 0 組」）就自己把排程停掉。
Set-Location "C:\Users\user\Desktop\know-graph-lab"
$log = "C:\tmp\ndltd_keeper.log"
& python -X utf8 scripts\thesis_ndltd.py --search *>> $log
if (Select-String -Path $log -Pattern "待查 0 組" -Quiet) {
  Disable-ScheduledTask -TaskName "KGL_NDLTD_Keeper" -ErrorAction SilentlyContinue
  Add-Content $log "全部組別已完成，排程自停。"
}
