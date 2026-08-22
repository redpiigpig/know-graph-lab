# Keep the Greek reader's two language-model layers moving until they are done.
#
# The Chinese gloss layer (1,000 words) and the interlinear layer (2,021 units,
# ~50,000 words) both need the Claude Max account, which the overnight fleet and
# the interactive session share, so they spend most of their life rate-limited.
# A background shell started from a chat session dies with that session; only a
# scheduled task survives the night.
#
# The keeper is idempotent and sequential on purpose:
#   - it exits at once if either job is already running, so a short interval is safe;
#   - it finishes the small gloss layer before starting the large interlinear,
#     because two jobs racing for an exhausted quota just doubles the 429s;
#   - it rebuilds and revalidates the master only when both layers are complete,
#     so a half-glossed master never lands.
#
# The python jobs are run through Start-Process with their own redirected output
# files rather than piped with 2>&1.  PowerShell 5.1 wraps every stderr line of a
# native command in an ErrorRecord, which under ErrorActionPreference='Stop'
# turns the first "429 quota exhausted" notice into a terminating error and kills
# the pass - which is exactly how the first version of this keeper died.  Letting
# python write its own files also keeps the Traditional-Chinese progress lines in
# UTF-8 instead of the console code page.
#
# Pure ASCII on purpose: PowerShell 5.1 misparses this file otherwise.

$ErrorActionPreference = 'Stop'
$repo = 'c:\Users\user\Desktop\know-graph-lab'
$python = 'python'
$cache = Join-Path $repo 'output\source-cache\original-readers\greek-full'
$log = Join-Path $cache 'keeper.log'
$glossPath = Join-Path $cache 'greek-1000-gloss-zh-reviewed.json'
$interlinearPath = Join-Path $cache 'interlinear.json'
$masterPath = Join-Path $cache 'greek-reader-50-lessons.json'
$reportPath = Join-Path $cache 'validation-report.json'
$vocabTarget = 1000
$unitTarget = 2021

function Write-Log($message) {
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    Add-Content -Path $log -Value "$stamp  $message" -Encoding utf8
}

function Count-Entries($path, $property) {
    if (-not (Test-Path $path)) { return 0 }
    try {
        $payload = Get-Content $path -Raw -Encoding utf8 | ConvertFrom-Json
    } catch {
        Write-Log "cannot parse $path yet; treating as empty"
        return 0
    }
    $node = $payload.$property
    if ($null -eq $node) { return 0 }
    return @($node.PSObject.Properties).Count
}

function Invoke-Pass($label, $scriptArgs) {
    $out = Join-Path $cache "$label.out.log"
    $err = Join-Path $cache "$label.err.log"
    $process = Start-Process -FilePath $python -ArgumentList $scriptArgs `
        -WorkingDirectory $repo -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $out -RedirectStandardError $err
    Write-Log "$label exited with code $($process.ExitCode); output in $label.out.log"
}

Set-Location $repo
$env:PYTHONIOENCODING = 'utf-8'

$running = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object {
        $_.CommandLine -like '*build_greek_vocab_glosses*' -or
        $_.CommandLine -like '*build_greek_interlinear*'
    }
if ($running) {
    Write-Log 'a pass is already running; nothing to do'
    exit 0
}

$glossCount = Count-Entries $glossPath 'glosses'
if ($glossCount -lt $vocabTarget) {
    Write-Log "gloss layer at $glossCount/$vocabTarget; starting a pass"
    Invoke-Pass 'gloss' @('scripts/build_greek_vocab_glosses.py', '--model', 'auto')
    $glossCount = Count-Entries $glossPath 'glosses'
    Write-Log "gloss pass finished at $glossCount/$vocabTarget"
    exit 0
}

$unitCount = Count-Entries $interlinearPath 'units'
if ($unitCount -lt $unitTarget) {
    Write-Log "interlinear at $unitCount/$unitTarget units; starting a pass"
    Invoke-Pass 'interlinear' @('scripts/build_greek_interlinear.py', '--model', 'auto')
    $unitCount = Count-Entries $interlinearPath 'units'
    Write-Log "interlinear pass finished at $unitCount/$unitTarget units"
    exit 0
}

Write-Log 'both layers complete; rebuilding the master and revalidating'
Invoke-Pass 'master' @('scripts/build_greek_reader_data.py', '--write')
Invoke-Pass 'validate' @(
    'skills/build-original-language-reader/scripts/validate_reader_release.py',
    '--master', $masterPath, '--language', 'grc', '--scripture-lessons', '25',
    '--report', $reportPath
)
Write-Log 'done'
