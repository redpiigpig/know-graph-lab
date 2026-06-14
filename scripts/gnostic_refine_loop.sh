#!/usr/bin/env bash
# Self-healing loop for the full-corpus 白話/和合本 精修 (re-translate every section
# except Manichaean (done) and the 23 apocrypha_slug docs (await 黃根春 backfill)).
#
# Each pass is `fix_gnostic_quality.py --retranslate --resume`: the ledger
# (c:/tmp/gnostic_refine.done) skips finished sections, so a death / quota wall
# never restarts from zero. We loop until a pass makes no further progress (all
# done, or only permanent failures remain — then we stop instead of spinning).
#
#   bash scripts/gnostic_refine_loop.sh
set -u
LOCK=c:/tmp/gnostic_refine.lock
LEDGER=c:/tmp/gnostic_refine.done
TOTAL=15563                      # sections in scope (see --dry)
ARGS="--retranslate --exclude-apocrypha --exclude-category manichaean --resume --engine haiku"

if [ -f "$LOCK" ]; then echo "already running (lock $LOCK) — abort"; exit 1; fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

stuck=0
while true; do
  before=$( [ -f "$LEDGER" ] && wc -l < "$LEDGER" || echo 0 )
  echo "=== pass start: ledger=$before/$TOTAL @ $(date '+%H:%M') ==="
  python -X utf8 scripts/fix_gnostic_quality.py $ARGS
  after=$( [ -f "$LEDGER" ] && wc -l < "$LEDGER" || echo 0 )
  echo "=== pass end: ledger=$after/$TOTAL ==="

  if [ "$after" -ge "$TOTAL" ]; then echo "ALL DONE ($after)"; break; fi
  if [ "$after" -le "$before" ]; then
    stuck=$((stuck + 1))
    echo "no progress ($before→$after) — strike $stuck/3"
    if [ "$stuck" -ge 3 ]; then echo "GIVING UP — $((TOTAL - after)) left (permanent fails?)"; break; fi
    echo "sleeping 30min for quota reset…"; sleep 1800
  else
    stuck=0   # progress made; loop straight into the next pass
  fi
done
