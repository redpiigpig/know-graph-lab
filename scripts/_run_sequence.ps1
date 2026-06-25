# Sequencer: wait for training final pass to finish, then run chenwei fill pass.
$ErrorActionPreference = "Continue"
$seqlog = "C:\tmp\sequencer.log"
$fp = "C:\tmp\final_pass.log"
"=== SEQUENCER START $([DateTime]::Now) ===" | Out-File $seqlog -Encoding utf8
$ok = $false
for ($i = 0; $i -lt 720; $i++) {
  if (Test-Path $fp) {
    $c = Get-Content $fp -Raw
    if ($c -match "FINAL_PASS DONE") { "[$([DateTime]::Now.ToString('HH:mm'))] final pass DONE -> launching chenwei" | Out-File $seqlog -Append -Encoding utf8; $ok = $true; break }
    if ($c -match "FINAL_PASS FAILED") { "SEQUENCER_STOP final_pass_failed $([DateTime]::Now)" | Out-File $seqlog -Append -Encoding utf8; exit 1 }
  }
  Start-Sleep -Seconds 60
}
if (-not $ok) { "SEQUENCER_STOP timeout_waiting_final_pass $([DateTime]::Now)" | Out-File $seqlog -Append -Encoding utf8; exit 1 }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\user\Desktop\know-graph-lab\scripts\_chenwei_fill_pass.ps1"
"SEQUENCER_DONE $([DateTime]::Now)" | Out-File $seqlog -Append -Encoding utf8
