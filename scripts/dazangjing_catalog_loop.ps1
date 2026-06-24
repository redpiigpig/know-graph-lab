param(
  [ValidateSet("start", "stop", "health", "once")]
  [string]$Command = "health",
  [int]$IntervalSeconds = 3600,
  [int]$MaxRecords = 0,
  [string]$InputPath = "",
  [string]$LedgerPath = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$CatalogDir = Join-Path $Root "data\dazangjing\source-catalog"
$PidFile = Join-Path $CatalogDir "catalog-loop.pid"
$Heartbeat = Join-Path $CatalogDir "catalog-loop-heartbeat.json"
$Log = Join-Path $CatalogDir "catalog-loop.log"
$Script = Join-Path $Root "scripts\dazangjing_catalog_ai.py"

function Ensure-CatalogDir {
  if (-not (Test-Path $CatalogDir)) {
    New-Item -ItemType Directory -Force -Path $CatalogDir | Out-Null
  }
}

function Get-LoopProcess {
  if (-not (Test-Path $PidFile)) { return $null }
  $pidText = (Get-Content -Raw -Path $PidFile).Trim()
  if (-not $pidText) { return $null }
  try {
    return Get-Process -Id ([int]$pidText) -ErrorAction Stop
  } catch {
    return $null
  }
}

Ensure-CatalogDir

if ($Command -eq "start") {
  $existing = Get-LoopProcess
  if ($existing) {
    Write-Output "already running pid=$($existing.Id)"
    exit 0
  }

  $argsList = @(
    $Script,
    "loop",
    "--interval", "$IntervalSeconds"
  )
  if ($InputPath) {
    $argsList += @("--input", $InputPath)
  }
  if ($LedgerPath) {
    $argsList += @("--ledger", $LedgerPath)
  }
  if ($MaxRecords -gt 0) {
    $argsList += @("--max-records", "$MaxRecords")
  }

  $proc = Start-Process -FilePath "python" -ArgumentList $argsList -WorkingDirectory $Root -WindowStyle Hidden -PassThru
  Set-Content -Path $PidFile -Value $proc.Id -Encoding ASCII
  Write-Output "started pid=$($proc.Id)"
  exit 0
}

if ($Command -eq "stop") {
  $existing = Get-LoopProcess
  if (-not $existing) {
    Write-Output "not running"
    Remove-Item -Path $PidFile -ErrorAction SilentlyContinue
    exit 0
  }
  Stop-Process -Id $existing.Id
  Remove-Item -Path $PidFile -ErrorAction SilentlyContinue
  Write-Output "stopped pid=$($existing.Id)"
  exit 0
}

if ($Command -eq "once") {
  $argsList = @($Script, "once")
  if ($InputPath) {
    $argsList += @("--input", $InputPath)
  }
  if ($LedgerPath) {
    $argsList += @("--ledger", $LedgerPath)
  }
  if ($MaxRecords -gt 0) {
    $argsList += @("--max-records", "$MaxRecords")
  }
  & python @argsList
  exit $LASTEXITCODE
}

$existing = Get-LoopProcess
if ($existing) {
  Write-Output "process=running pid=$($existing.Id)"
} else {
  Write-Output "process=not-running"
}

if (Test-Path $Heartbeat) {
  Get-Content -Raw -Path $Heartbeat
} else {
  Write-Output "heartbeat=missing"
}

if (Test-Path $Log) {
  Write-Output "last-log-lines:"
  Get-Content -Path $Log -Tail 8
}
