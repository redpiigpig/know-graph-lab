param(
  [int]$IntervalSeconds = 1800,
  [string]$LogPath = "scripts/logs/translation_progress_30min.log",
  [switch]$Once
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

function Add-ProgressLine {
  param([string]$Text)
  Add-Content -LiteralPath $logFullPath -Encoding UTF8 -Value $Text
}

function Add-CommandOutput {
  param(
    [string]$Label,
    [scriptblock]$Command
  )
  Add-ProgressLine "-- $Label --"
  try {
    $out = & $Command 2>&1
    if ($null -eq $out) {
      Add-ProgressLine "(no output)"
      return
    }
    foreach ($line in $out) {
      Add-ProgressLine ([string]$line)
    }
  } catch {
    Add-ProgressLine ("ERROR: {0}" -f $_.Exception.Message)
  }
}

function Add-ActiveJobs {
  Add-ProgressLine "-- active translation/transcription processes --"
  $procs = Get-CimInstance Win32_Process |
    Where-Object {
      $_.CommandLine -match 'panikkar|sbe_translate|jung_psychological_types|ingest_accs|accs_exo|ingest_lit_review|translate_ebook|ocr_pdf'
    } |
    Sort-Object ProcessId

  if (-not $procs) {
    Add-ProgressLine "(none matched)"
    return
  }

  foreach ($p in $procs) {
    $cmd = (($p.CommandLine -replace '\s+', ' ').Trim())
    if ($cmd.Length -gt 320) {
      $cmd = $cmd.Substring(0, 320) + "..."
    }
    Add-ProgressLine ("PID={0} NAME={1} CMD={2}" -f $p.ProcessId, $p.Name, $cmd)
  }
}

function Add-JungProgress {
  $path = Join-Path $root "scripts/logs/jung_psychological_types_monitor.log"
  Add-ProgressLine "-- jung psychological types --"
  if (-not (Test-Path $path)) {
    Add-ProgressLine "monitor log missing"
    return
  }
  $last = Get-Content -LiteralPath $path -Encoding UTF8 |
    Where-Object { $_.Trim().Length -gt 0 } |
    Select-Object -Last 1
  if (-not $last) {
    Add-ProgressLine "monitor log empty"
    return
  }
  try {
    $j = $last | ConvertFrom-Json
    $s = $j.status
    $latest = $j.latest
    Add-ProgressLine ("checked_at={0} done={1}/{2} current={3} error={4}" -f $j.checked_at, $s.done, $s.total, $s.current, $s.error)
    if ($latest) {
      Add-ProgressLine ("latest={0} heading={1} en_chars={2} zh_chars={3} ratio={4} bad_terms={5}" -f $latest.file, $latest.heading, $latest.en_chars, $latest.zh_chars, $latest.zh_en_ratio, (($latest.bad_terms -join ',') -replace '\s+', ' '))
    }
  } catch {
    Add-ProgressLine ("unparsed latest line: {0}" -f $last)
  }
}

function Add-AccsProgress {
  Add-ProgressLine "-- accs exodus/genesis ocr --"
  $paths = @(
    "scripts/logs/accs_exo.log",
    "scripts/logs/accs_gen_12-50_progress.log",
    "scripts/logs/accs_gen_12-50_direct.log"
  )
  foreach ($rel in $paths) {
    $path = Join-Path $root $rel
    if (-not (Test-Path $path)) { continue }
    Add-ProgressLine ("[{0}] last_write={1}" -f $rel, (Get-Item $path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"))
    $lines = Get-Content -LiteralPath $path -Encoding UTF8 -Tail 80 |
      Select-String -Pattern '\[[0-9]+|upserted|remaining|resume|bail|FAIL|DONE|raw entries|pages .* to do' |
      Select-Object -Last 12
    foreach ($m in $lines) {
      Add-ProgressLine ("  " + $m.Line)
    }
  }
}

function Add-SbeProgress {
  Add-ProgressLine "-- sacred books east translate --"
  $procs = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match 'sbe_translate.py' } |
    Sort-Object ProcessId
  if ($procs) {
    foreach ($p in $procs) {
      $cmd = (($p.CommandLine -replace '\s+', ' ').Trim())
      if ($cmd.Length -gt 280) { $cmd = $cmd.Substring(0, 280) + "..." }
      Add-ProgressLine ("PID={0} CMD={1}" -f $p.ProcessId, $cmd)
    }
  } else {
    Add-ProgressLine "no sbe_translate.py process matched"
  }
}

function Write-ProgressSnapshot {
  $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
  Add-ProgressLine ""
  Add-ProgressLine "===== $now ====="
  Add-ActiveJobs
  Add-CommandOutput "panikkar queue" { python -X utf8 scripts/panikkar_auto.py --list }
  Add-JungProgress
  Add-AccsProgress
  Add-SbeProgress
}

while ($true) {
  try {
    Write-ProgressSnapshot
  } catch {
    Add-ProgressLine ("ERROR {0}" -f $_.Exception.Message)
  }
  if ($Once) { break }
  Start-Sleep -Seconds $IntervalSeconds
}
