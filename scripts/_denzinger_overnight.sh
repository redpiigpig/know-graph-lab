#!/usr/bin/env bash
# Overnight Denzinger column-aware OCR resume.
#
# Behavior:
#   - Loop forever (no midnight stop, no max attempts)
#   - 30 min sleep between attempts
#   - Each attempt: run recolumn OCR until 2-strike pause or completion
#   - If new pages saved this attempt: ship inline (segment + relabel + creeds
#     + git commit + push) so reader benefits immediately
#   - Exit only when recolumn count == 967 (target met)
#
# Per user 2026-05-28: "用一整晚，誰說過半夜就停的" — no midnight cap.
# Per memory feedback_overnight_autonomous.md: this is the established pattern.

set -u

BOOK_ID="568726d3-967e-457a-ab69-7452b21d606f"
RECOLUMN="G:/我的雲端硬碟/資料/知識圖工作室/_chunks/${BOOK_ID}.recolumn.jsonl"
LOG="scripts/logs/denzinger_recolumn_2026-05-28.log"
TARGET=967

# Count non-empty lines (each attempt run appends; we count completions)
count_done() {
  wc -l < "${RECOLUMN}" | tr -d ' '
}

ship_increment() {
  # Run the downstream pipeline. Each step is idempotent so a mid-run crash
  # leaves the previous state intact.
  echo "[$(date '+%F %T')] shipping increment..."
  python -X utf8 -u scripts/segment_denzinger.py --apply \
    >> scripts/logs/denzinger_ship_overnight.log 2>&1 \
    && echo "[$(date '+%F %T')]   ✓ segment ok" \
    || echo "[$(date '+%F %T')]   ⚠ segment failed (ok, R2 has prev state)"
  python -X utf8 -u scripts/_denzinger_relabel.py --no-db \
    >> scripts/logs/denzinger_ship_overnight.log 2>&1 \
    && echo "[$(date '+%F %T')]   ✓ relabel ok" \
    || echo "[$(date '+%F %T')]   ⚠ relabel failed"
  python -X utf8 -u scripts/_denzinger_to_creeds.py --write --force \
    >> scripts/logs/denzinger_ship_overnight.log 2>&1 \
    && echo "[$(date '+%F %T')]   ✓ creeds ok" \
    || echo "[$(date '+%F %T')]   ⚠ creeds failed"
  # Commit + push (only if something changed)
  if [ -n "$(git status --porcelain data/creeds/)" ]; then
    git add data/creeds/ecumenical-councils/
    git commit -m "chore(denzinger): overnight resume ship — recolumn $(count_done)/${TARGET}

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>" \
      >> scripts/logs/denzinger_ship_overnight.log 2>&1
    git push >> scripts/logs/denzinger_ship_overnight.log 2>&1 \
      && echo "[$(date '+%F %T')]   ✓ git push ok" \
      || echo "[$(date '+%F %T')]   ⚠ git push failed"
  else
    echo "[$(date '+%F %T')]   (no creeds diff to commit)"
  fi
}

PREV=$(count_done)
START_TS=$(date '+%F %T')
echo "[${START_TS}] overnight-resume start; baseline = ${PREV} / ${TARGET}"

ATTEMPT=0
while true; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "[$(date '+%F %T')] attempt #${ATTEMPT} starting…"
  python -X utf8 -u scripts/_denzinger_recolumn_ocr.py \
    >> "${LOG}" 2>&1
  CUR=$(count_done)
  DELTA=$((CUR - PREV))
  echo "[$(date '+%F %T')] attempt #${ATTEMPT} done; new=${DELTA}, total=${CUR}/${TARGET}"

  if [ "${DELTA}" -gt 0 ]; then
    ship_increment
  fi

  PREV=${CUR}

  if [ "${CUR}" -ge "${TARGET}" ]; then
    echo "[$(date '+%F %T')] all ${TARGET} pages done — exiting overnight loop"
    break
  fi

  echo "[$(date '+%F %T')] sleeping 30 min before attempt #$((ATTEMPT + 1))…"
  sleep 1800
done

echo "[$(date '+%F %T')] overnight-resume finished; final = $(count_done) / ${TARGET}"
