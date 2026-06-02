#!/bin/bash
L=scripts/logs/proofread_vol12.log
while true; do
  if grep -q "wrote report" "$L" 2>/dev/null; then
    echo "VOL12 PROOFREAD DONE"; break
  fi
  sleep 60
done
