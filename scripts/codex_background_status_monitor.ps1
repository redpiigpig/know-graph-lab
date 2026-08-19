param(
  [int]$IntervalSeconds = 1800,
  [string]$LogPath = "scripts/logs/codex_background_status.log"
)

$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$logFullPath = Join-Path $root $LogPath
$logDir = Split-Path -Parent $logFullPath
if (-not (Test-Path $logDir)) {
  New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

function Write-Status {
  $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
  Add-Content -LiteralPath $logFullPath -Encoding UTF8 -Value ""
  Add-Content -LiteralPath $logFullPath -Encoding UTF8 -Value "===== $now ====="

  $procs = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match 'python|node|bash|powershell|pwsh' } |
    Sort-Object ProcessId

  foreach ($p in $procs) {
    $cmd = ($p.CommandLine -replace '\s+', ' ').Trim()
    Add-Content -LiteralPath $logFullPath -Encoding UTF8 -Value ("PID={0} NAME={1} CMD={2}" -f $p.ProcessId, $p.Name, $cmd)
  }

  $gnostic = $procs | Where-Object {
    $_.CommandLine -match 'gnostic|fix_gnostic|ingest_gnostic|gnostic_refine|gnostic_resume'
  }
  if ($gnostic) {
    Add-Content -LiteralPath $logFullPath -Encoding UTF8 -Value ("GNOSTIC_RUNNING=yes count={0}" -f $gnostic.Count)
  } else {
    Add-Content -LiteralPath $logFullPath -Encoding UTF8 -Value "GNOSTIC_RUNNING=no"
  }
}

while ($true) {
  try {
    Write-Status
  } catch {
    Add-Content -LiteralPath $logFullPath -Encoding UTF8 -Value ("ERROR {0}" -f $_.Exception.Message)
  }
  Start-Sleep -Seconds $IntervalSeconds
}
