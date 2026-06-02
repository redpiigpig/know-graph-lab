#!/bin/bash
# Block until both Vol11 & Vol12 translate logs show completion marker.
L11=scripts/logs/translate_vol11.log
L12=scripts/logs/translate_vol12.log
while true; do
  d11=$(grep -c "ebooks row updated" "$L11" 2>/dev/null || echo 0)
  d12=$(grep -c "ebooks row updated" "$L12" 2>/dev/null || echo 0)
  if [ "$d11" -ge 1 ] && [ "$d12" -ge 1 ]; then
    echo "BOTH DONE: vol11+vol12 translation complete"
    break
  fi
  sleep 120
done
