$repo = "C:\Users\user\Desktop\know-graph-lab"
$args = @("training","hongshi")
$maxRetries = 50
for ($i=1; $i -le $maxRetries; $i++) {
  $stamp = Get-Date -Format "MMdd_HHmmss"
  $out = "$repo\scripts\logs\prewarm_retry_${stamp}_try${i}.log"
  $err = "$repo\scripts\logs\prewarm_retry_${stamp}_try${i}.err"
  Write-Output ("[try {0}] starting at {1}" -f $i, (Get-Date -Format "HH:mm:ss"))
  $p = Start-Process -FilePath "node" `
    -ArgumentList (@("--max-old-space-size=4096","scripts\prewarm_thumbs.mjs") + $args) `
    -WorkingDirectory $repo -RedirectStandardOutput $out -RedirectStandardError $err `
    -WindowStyle Hidden -PassThru -Wait
  $exitCode = $p.ExitCode
  $lastLine = ((Get-Content $out -Tail 1) -join " ")
  Write-Output ("[try {0}] exit={1} last={2}" -f $i, $exitCode, $lastLine)
  if ($exitCode -eq 0 -and ((Get-Content $out -Raw) -match "=== Done")) {
    Write-Output "All done after $i tries."
    break
  }
  if ($exitCode -ne 0 -or -not (Get-Process node -ErrorAction SilentlyContinue)) {
    Start-Sleep -Seconds 3
  }
}
Write-Output ("Loop ended at {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
