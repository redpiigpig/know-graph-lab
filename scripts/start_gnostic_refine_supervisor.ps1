param(
  [int]$ApiLimit = 20,
  [int]$LocalLimit = 3,
  [int]$SleepSeconds = 1800,
  [string]$LocalModel = "qwen3-coder:30b"
)

$ErrorActionPreference = "Continue"
$Repo = "C:\Users\user\Desktop\know-graph-lab"
$Log = "C:\tmp\gnostic_refine_supervisor.log"
$PidFile = "C:\tmp\gnostic_refine_supervisor.pid"
$Ledger = "C:\tmp\gnostic_refine.done"

Set-Location $Repo
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Log([string]$Message) {
  $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
  "$stamp $Message" | Tee-Object -FilePath $Log -Append
}

function Get-LedgerCount {
  if (Test-Path $Ledger) {
    return @((Get-Content $Ledger -ErrorAction SilentlyContinue)).Count
  }
  return 0
}

function Test-ExistingSupervisor {
  if (-not (Test-Path $PidFile)) { return $false }
  $oldPid = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
  if (-not $oldPid) { return $false }
  try {
    $proc = Get-Process -Id ([int]$oldPid) -ErrorAction Stop
    return ($null -ne $proc)
  } catch {
    return $false
  }
}

function Invoke-RefineBatch([string]$Engine, [int]$Limit) {
  $before = Get-LedgerCount
  Write-Log "batch start engine=$Engine limit=$Limit ledger_before=$before"
  if ($Engine -eq "ollama") {
    $env:OLLAMA_MODEL = $LocalModel
  }

  $args = @(
    "-X", "utf8",
    "scripts\fix_gnostic_quality.py",
    "--retranslate",
    "--exclude-apocrypha",
    "--exclude-category", "manichaean",
    "--resume",
    "--engine", $Engine,
    "--limit", "$Limit",
    "--pace", "0.2"
  )

  & python @args 2>&1 | Tee-Object -FilePath $Log -Append
  $exit = $LASTEXITCODE
  $after = Get-LedgerCount
  $added = $after - $before
  Write-Log "batch end engine=$Engine exit=$exit ledger_after=$after added=$added"
  return [pscustomobject]@{ Exit = $exit; Before = $before; After = $after; Added = $added }
}

if (Test-ExistingSupervisor) {
  Write-Log "already running; pid=$(Get-Content $PidFile | Select-Object -First 1)"
  exit 0
}

"$PID" | Set-Content -Path $PidFile -Encoding ascii
Write-Log "supervisor start pid=$PID api_limit=$ApiLimit local_limit=$LocalLimit local_model=$LocalModel"

try {
  while ($true) {
    $api = Invoke-RefineBatch "haiku" $ApiLimit
    if ($api.Added -gt 0) {
      Write-Log "api made progress; continuing next cycle"
      continue
    }

    Write-Log "api made no progress; falling back to local ollama"
    $local = Invoke-RefineBatch "ollama" $LocalLimit
    if ($local.Added -gt 0) {
      Write-Log "local ollama made progress; continuing next cycle"
      continue
    }

    Write-Log "no progress from api or local; sleeping $SleepSeconds seconds"
    Start-Sleep -Seconds $SleepSeconds
  }
} finally {
  Remove-Item $PidFile -ErrorAction SilentlyContinue
  Write-Log "supervisor stop pid=$PID"
}
