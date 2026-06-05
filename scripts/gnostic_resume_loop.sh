#!/bin/bash
# Self-healing overnight loop for the /gnostic transcription.
# Re-runs `ingest_gnostic.py --all --resume` until the corpus is done or quota
# stays dead. Each pass aborts fast (4 consecutive failures) when Gemini+Haiku
# quota is exhausted; we then sleep 45min and retry, harvesting quota as it
# recovers overnight. Stops after 3 consecutive zero-progress cycles.
cd "c:/Users/user/Desktop/know-graph-lab" || exit 1
LOG=c:/tmp/gnostic_overnight.log

# Single-instance guard — refuse to start if another loop is already alive
# (prevents the zombie-accumulation that over-hammered the keys).
LOCK=c:/tmp/gnostic_loop.lock
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "### another gnostic loop already running (pid $(cat "$LOCK")) — exiting $(date)" >> "$LOG"
  exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

count() {
  python -X utf8 -c "import os,requests
from dotenv import load_dotenv; load_dotenv(os.path.join(os.getcwd(),'.env'))
ref=os.environ['SUPABASE_URL'].split('//')[1].split('.')[0]
r=requests.post(f'https://api.supabase.com/v1/projects/{ref}/database/query',headers={'Authorization':'Bearer '+os.environ['SUPABASE_ACCESS_TOKEN'],'Content-Type':'application/json'},json={'query':\"select count(distinct doc_slug) c from gnostic_sections\"})
print(r.json()[0]['c'])"
}

prev=$(count); zero=0
echo "### RESUME LOOP start (have $prev docs) $(date)" >> "$LOG"
for i in $(seq 1 20); do
  echo "### resume cycle $i $(date)" >> "$LOG"
  # Direct Haiku via Claude Max OAuth (user 2026-06-05: 「免費的沒有或被佔用了，就
  # 去開 Haiku，我有訂閱 max」). The free pools (Gemini / NVIDIA) were exhausted, so
  # rather than spin probing dead keys we pump straight through Max-Haiku. Patient
  # backoffs in haiku_translate ride out Max's rolling-window 429s.
  python -X utf8 -u scripts/ingest_gnostic.py --all --resume --engine haiku >> "$LOG" 2>&1
  cur=$(count); added=$((cur - prev)); prev=$cur
  echo "### cycle $i added $added (total $cur)" >> "$LOG"
  if [ "$added" -eq 0 ]; then zero=$((zero + 1)); else zero=0; fi
  if [ "$zero" -ge 3 ]; then echo "### 3 zero-progress cycles -> stop $(date)" >> "$LOG"; break; fi
  sleep 2700
done
echo "### RESUME LOOP done total=$prev $(date)" >> "$LOG"
