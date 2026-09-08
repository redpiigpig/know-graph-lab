#!/usr/bin/env bash
# 華藝「見縫插針」接力下載：只在沒有別的 press_airiti 在跑時才補一批。
#
# 為什麼需要這支
# --------------
# KGL_Airiti_Poll 每 30 分鐘跑一輪 100 篇，中間有空檔；人在學校的時間有限（下載綁
# 機構 IP，離開就抓不了），所以想把空檔填滿。但**兩個行程同時抓＝間隔砍半**，而
# press_airiti.py 沒有跨行程鎖、排程的 IgnoreNew 也只擋同一工作的第二個實例、擋不住
# 另外開的行程。2026-09-08 就差點這樣重疊。
#
# 6 秒間隔是對機構 IP 的承諾（見 run_airiti_batch.ps1 檔頭），這支不碰它——它只決定
# 「什麼時候可以開始下一批」，不決定「下多快」。實測含篇目讀取約 12 秒／篇。
#
#   bash scripts/airiti_opportunistic.sh 1000        # 今天上限 1000
#   touch c:/tmp/airiti_stop                         # 要它收工
#
# 收工條件：達到上限、出現 stop 檔、或連續空轉 20 分鐘（多半是離開學校斷網了）。
set -u

CAP="${1:-1000}"
# 批次可以放大：press_airiti.py 自己有跨行程鎖（c:/tmp/press_airiti_download.lock，
# 見該檔 LOCK），排程撞上正在跑的批次會自動印「另一輪下載還在跑；這次跳過」。
# 所以不需要靠批次大小去閃 :00/:30，反而該放大——每批開頭都要重讀一輪篇目，
# 批次太小那個固定開銷佔比過高。
# 🚨 鎖的 stale 期限是 3 小時：批次若被 Modern Standby 砍掉，鎖會卡住最多 3 小時，
#    期間所有排程都跳過。看到「這次跳過」但沒有行程在跑，就是這個。
BATCH=60
ROOT="C:/Users/user/Desktop/know-graph-lab"
DAILY="c:/tmp/press_airiti_daily.json"
STOP="c:/tmp/airiti_stop"
LOG="c:/tmp/airiti_opportunistic.log"

cd "$ROOT" || exit 1
say() { echo "[$(date +%H:%M:%S)] $*" >> "$LOG"; }
say "=== 接力啟動，上限 $CAP，每批 $BATCH ==="

# 有沒有 press_airiti 在跑。本腳本是「跑完一批才回來檢查」的同步流程，所以檢查的
# 當下自己一定沒有子批次在跑——不需要排除自己，看到任何一個就是別人（排程）。
others_running() {
  powershell.exe -NoProfile -Command "
    \$p = Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" |
         Where-Object { \$_.CommandLine -match 'press_airiti' }
    if (\$p) { 'BUSY' } else { 'FREE' }
  " 2>/dev/null | tr -d '\r\n'
}

count_now() { python -c "import json;print(json.load(open(r'$DAILY'))['count'])" 2>/dev/null || echo 0; }

idle=0
while :; do
  [ -f "$STOP" ] && { say "偵測到 stop 檔，收工"; break; }

  used="$(count_now)"
  if [ "$used" -ge "$CAP" ] 2>/dev/null; then
    say "已達上限 $used/$CAP，收工"; break
  fi

  if [ "$(others_running)" = "BUSY" ]; then
    idle=$((idle + 1))
    if [ "$idle" -ge 40 ]; then say "連續 20 分鐘都有別人在跑，收工避免打架"; break; fi
    sleep 30
    continue
  fi

  idle=0
  left=$((CAP - used))
  n=$(( left < BATCH ? left : BATCH ))
  say "空檔，補 $n 篇（目前 $used/$CAP）"
  python -X utf8 scripts/press_airiti.py --batch "$n" --daily-cap "$CAP" >> "$LOG" 2>&1
  rc=$?
  after="$(count_now)"
  say "本批結束 rc=$rc，$used → $after"
  # 一篇都沒增加多半是斷網或權限掉了（華藝權限掉會回 200 的 JSON 不是 PDF）
  if [ "$after" = "$used" ]; then
    idle=$((idle + 4))
    if [ "$idle" -ge 12 ]; then say "連續數批零進度，多半已離開機構網路，收工"; break; fi
  fi
  sleep 5
done
say "=== 接力結束，最終 $(count_now)/$CAP ==="
