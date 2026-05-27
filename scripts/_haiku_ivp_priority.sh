#!/bin/bash
# IVP ACCS priority wrapper for Haiku OCR run.
# Runs the 22 IVP ACCS volumes first (--book ... --book ...), then falls back
# to standard FIFO autorestart for the rest of the queue.
#
# Usage:  bash scripts/_haiku_ivp_priority.sh
# Generated 2026-05-21 to fulfill user's IVP-first priority request.

set -u
LOG=scripts/logs/ocr_haiku_2026-05-21_ivp.log
PY="C:/Users/user/AppData/Local/Python/bin/python.exe"

# === Phase 1 — IVP ACCS priority pass ===
# Strip CRLF (Windows line endings) when reading ids file
mapfile -t IVP_IDS < <(tr -d '\r' < scripts/_ivp_priority_ids.txt)
if [ ${#IVP_IDS[@]} -eq 0 ]; then
  echo "ERR: scripts/_ivp_priority_ids.txt empty; nothing to prioritize" | tee -a "$LOG"
  exit 1
fi

BOOK_ARGS=()
for id in "${IVP_IDS[@]}"; do
  BOOK_ARGS+=(--book "$id")
done

echo "=== IVP-priority Phase 1 start at $(date) — ${#IVP_IDS[@]} books ===" | tee -a "$LOG"
for i in $(seq 1 6); do
  echo "--- IVP iteration $i / 6 at $(date) ---" | tee -a "$LOG"
  "$PY" -u scripts/ocr_with_gemini.py run --rpm 8 "${BOOK_ARGS[@]}" 2>&1 | tee -a "$LOG"
  exit_code=${PIPESTATUS[0]}
  echo "=== IVP iter $i exit=$exit_code ===" | tee -a "$LOG"

  # Check remaining IVP queue
  remaining_ivp=$("$PY" -X utf8 -c "
import os, sys
from pathlib import Path
env={}
for l in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in l and not l.startswith('#'):
        k,v=l.split('=',1); env[k.strip()]=v.strip().strip('\"').strip(\"'\")
import requests
url=env['SUPABASE_URL']; key=env['SUPABASE_SERVICE_ROLE_KEY']
H={'apikey':key,'Authorization':f'Bearer {key}'}
sys.stdout.reconfigure(encoding='utf-8')
ids = Path('scripts/_ivp_priority_ids.txt').read_text(encoding='utf-8').splitlines()
ids = [i.strip() for i in ids if i.strip()]
remaining = 0
for i in ids:
    r = requests.get(f'{url}/rest/v1/ebooks?select=parse_error&id=eq.{i}', headers=H)
    rows = r.json()
    if rows and rows[0].get('parse_error') and 'no extractable text' in (rows[0]['parse_error'] or ''):
        remaining += 1
print(remaining)
" 2>/dev/null)
  echo "  IVP remaining: $remaining_ivp" | tee -a "$LOG"
  if [ "$remaining_ivp" -le 0 ] 2>/dev/null; then
    echo "=== IVP complete, moving to Phase 2 ===" | tee -a "$LOG"
    break
  fi
done

# === Phase 2 — FIFO catch-all for rest ===
echo "=== Phase 2 catch-all start at $(date) ===" | tee -a "$LOG"
for i in $(seq 1 10); do
  echo "--- catch-all iteration $i / 10 at $(date) ---" | tee -a "$LOG"
  "$PY" -u scripts/ocr_with_gemini.py run --rpm 8 2>&1 | tee -a "$LOG"
  exit_code=${PIPESTATUS[0]}
  echo "=== catch-all iter $i exit=$exit_code ===" | tee -a "$LOG"

  remaining=$("$PY" -X utf8 -c "
import os, sys
from pathlib import Path
env={}
for l in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in l and not l.startswith('#'):
        k,v=l.split('=',1); env[k.strip()]=v.strip().strip('\"').strip(\"'\")
import requests
url=env['SUPABASE_URL']; key=env['SUPABASE_SERVICE_ROLE_KEY']
H={'apikey':key,'Authorization':f'Bearer {key}'}
sys.stdout.reconfigure(encoding='utf-8')
r=requests.get(f'{url}/rest/v1/ebooks?select=id,file_path&parse_error=ilike.*no extractable text*',
               headers={**H,'Range':'0-999'})
rows=r.json()
big=sum(1 for x in rows if Path(x['file_path']).exists() and Path(x['file_path']).stat().st_size > 50*1024*1024)
print(big)
" 2>/dev/null)
  echo "  big-file remaining: $remaining" | tee -a "$LOG"
  if [ "$remaining" -le 0 ] 2>/dev/null; then
    echo "=== Catch-all queue empty, exiting wrapper ===" | tee -a "$LOG"
    break
  fi
done
