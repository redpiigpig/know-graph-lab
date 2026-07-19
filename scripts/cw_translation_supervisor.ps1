<#
  Collected-works "modern classics" translation supervisor (single pass; the KGL_CW_Translation
  scheduled task re-triggers it periodically).

  Scope: modern_classics_auto only (English-first Haiku, .done books skipped, resumable).
  Greek (Plato/Aristotle) is handled by the pre-existing KGL_Translation_Supervisor on
  --engine auto (NVIDIA), so it is NOT run here (avoids double work; different engine pool).

  Guard: a PID lock file (robust under a Limited-rights scheduled task, where
  Get-CimInstance CommandLine can come back null). If a live pass holds the lock, skip.

  Note: Haiku uses ~/.claude/.credentials.json Max OAuth token; needs an unexpired token
  (Claude Code refreshes it) or the pass 401s and resumes on the next wake.
#>
$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python -ErrorAction Stop).Source
$log = 'C:\tmp\cw_translation_supervisor.log'
$lock = 'C:\tmp\cw_translation.lock'

function Log([string]$m) { Add-Content -LiteralPath $log -Encoding utf8 -Value "$(Get-Date -Format o) $m" }

# --- PID lock guard ---
if (Test-Path -LiteralPath $lock) {
    $old = (Get-Content -LiteralPath $lock -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($old -and (Get-Process -Id ([int]$old) -ErrorAction SilentlyContinue)) {
        Log "locked by pid=$old - skip this pass"; exit 0
    }
    Log "stale lock (pid=$old dead) - clearing"
}
Set-Content -LiteralPath $lock -Value $PID -Encoding ascii

try {
    Set-Location -LiteralPath $repo
    Log "=== modern classics pass start (pid=$PID) ==="
    & $python scripts\modern_classics_auto.py *>> C:\tmp\modern_haiku.out.log
    Log "modern_classics_auto exit=$LASTEXITCODE"
    Log "=== modern classics pass end ==="
}
finally {
    Remove-Item -LiteralPath $lock -Force -ErrorAction SilentlyContinue
}
exit 0
