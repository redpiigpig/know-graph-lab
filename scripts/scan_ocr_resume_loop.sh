#!/usr/bin/env bash
# 掃描本 OCR 的續跑迴圈：Gemini 免費層是**日額度**，跑到一半撞牆是常態。
# 每 20 分鐘試一次 --resume，兩本都補滿就自己退出（不會像壞掉的排程那樣空轉，
# 見 [[feedback_disable_finished_schedules]]）。
#
#   bash scripts/scan_ocr_resume_loop.sh            # 前景
#   nohup bash scripts/scan_ocr_resume_loop.sh &    # 背景（過夜請改用工作排程器）
set -u
cd "$(dirname "$0")/.." || exit 1

MINDS_CACHE=c:/tmp/chaohwei/ocr2      # 《心靈的交會》v2 重跑（補註腳格式），目標 255
VJ_CACHE=c:/tmp/chaohwei_vijnapti/ocr # 《初期唯識思想》，目標 300
MINDS_TARGET=255
VJ_TARGET=300
LOG=c:/tmp/scan_ocr_resume.log
LOCK=c:/tmp/scan_ocr_resume.lock

# 防重入：兩份迴圈同時跑只會互搶同一批 key 的配額，看起來還「兩邊都在動」
if [ -e "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "已有一份迴圈在跑（pid $(cat "$LOCK")）"
  exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

count() { ls "$1" 2>/dev/null | wc -l | tr -d ' '; }

while true; do
  m=$(count "$MINDS_CACHE"); v=$(count "$VJ_CACHE")
  echo "$(date '+%m-%d %H:%M') 心靈的交會 $m/$MINDS_TARGET　初期唯識思想 $v/$VJ_TARGET" >> "$LOG"
  if [ "$m" -ge "$MINDS_TARGET" ] && [ "$v" -ge "$VJ_TARGET" ]; then
    echo "$(date '+%m-%d %H:%M') ✅ 兩本都補滿，收工" >> "$LOG"
    break
  fi
  # 一次跑一本，兩本同時跑只會互搶同一批 key 的配額。
  # 兩個模型都試：2.5-flash 對新申請的 key 一律 404，flash-latest 則常 503 overloaded，
  # 哪一個能通看當下，所以輪著試而不是挑一個。
  for MODEL in gemini-2.5-flash gemini-flash-latest; do
    if [ "$(count "$MINDS_CACHE")" -lt "$MINDS_TARGET" ]; then
      PYTHONIOENCODING=utf-8 python -u -X utf8 scripts/chaohwei_ocr.py \
        --work c:/tmp/chaohwei/work.pdf --cache "$MINDS_CACHE" --batch 6 --resume \
        --model "$MODEL" >> "$LOG" 2>&1
    fi
    if [ "$(count "$VJ_CACHE")" -lt "$VJ_TARGET" ]; then
      PYTHONIOENCODING=utf-8 python -u -X utf8 scripts/scan_ocr.py \
        --book chaohwei-vijnapti --batch 6 --resume --model "$MODEL" >> "$LOG" 2>&1
    fi
  done
  sleep 1200
done
