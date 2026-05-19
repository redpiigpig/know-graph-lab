#!/bin/bash
# Auto-restart wrapper for Haiku OCR run.
# Python process tends to die silently after some hours — this wrapper restarts it
# until OCR queue is empty (script naturally exits or "OCR candidates: 0").
#
# Usage: bash scripts/_haiku_autorestart.sh

LOG=scripts/logs/ocr_haiku_2026-05-19_v2.log
PY="C:/Users/user/AppData/Local/Python/bin/python.exe"
MAX_RESTARTS=15

for i in $(seq 1 $MAX_RESTARTS); do
  echo "=== autorestart iteration $i / $MAX_RESTARTS at $(date) ===" >> "$LOG"
  "$PY" -u scripts/ocr_with_gemini.py run --engine haiku 2>&1 | tee -a "$LOG"
  exit_code=${PIPESTATUS[0]}
  echo "=== iteration $i exit=$exit_code ===" >> "$LOG"

  # Check remaining queue
  remaining=$("$PY" -X utf8 -c "
import os, sys
from dotenv import load_dotenv
load_dotenv()
import requests
sys.stdout.reconfigure(encoding='utf-8')
url=os.environ['SUPABASE_URL']
key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
H={'apikey':key,'Authorization':f'Bearer {key}'}
import pathlib
r=requests.get(f'{url}/rest/v1/ebooks?select=id,file_path&parse_error=ilike.*no extractable text*',
               headers={**H,'Range':'0-999'})
rows=r.json()
# Count >50MB ones in queue (Haiku candidates)
big=sum(1 for x in rows if pathlib.Path(x['file_path']).exists() and pathlib.Path(x['file_path']).stat().st_size > 50*1024*1024)
print(big)
" 2>/dev/null)

  echo "  remaining big-file queue: $remaining" | tee -a "$LOG"
  if [ "$remaining" -le 0 ] 2>/dev/null; then
    echo "=== Queue empty, exiting wrapper ===" | tee -a "$LOG"
    break
  fi
  echo "=== Waiting 30s before restart ===" | tee -a "$LOG"
  sleep 30
done
