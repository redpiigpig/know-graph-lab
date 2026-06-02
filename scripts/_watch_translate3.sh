#!/bin/bash
while true; do
  d16=$(grep -c "ebooks row updated" scripts/logs/translate_vol16.log 2>/dev/null || echo 0)
  d17=$(grep -c "ebooks row updated" scripts/logs/translate_vol17.log 2>/dev/null || echo 0)
  d18=$(grep -c "ebooks row updated" scripts/logs/translate_vol18.log 2>/dev/null || echo 0)
  if [ "$d16" -ge 1 ] && [ "$d17" -ge 1 ] && [ "$d18" -ge 1 ]; then
    echo "BATCH 16-18 DONE"; break
  fi
  sleep 180
done
