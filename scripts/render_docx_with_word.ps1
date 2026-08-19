param(
  [Parameter(Mandatory = $true)][string]$Docx,
  [Parameter(Mandatory = $true)][string]$OutputDir,
  [int]$Dpi = 144,
  [int]$FromPage = 0,
  [int]$ToPage = 0
)

$ErrorActionPreference = 'Stop'
$docxPath = (Resolve-Path -LiteralPath $Docx).Path
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$outPath = (Resolve-Path -LiteralPath $OutputDir).Path
$baseName = [IO.Path]::GetFileNameWithoutExtension($docxPath)
$pdfPath = Join-Path $outPath ($baseName + '.pdf')

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.AutomationSecurity = 3
$word.Options.UpdateLinksAtOpen = $false
try {
  $document = $word.Documents.OpenNoRepairDialog($docxPath, $false, $true, $false)
  try {
    if ($FromPage -gt 0 -and $ToPage -ge $FromPage) {
      $document.ExportAsFixedFormat($pdfPath, 17, $false, 1, 3, $FromPage, $ToPage)
    }
    else {
      $document.ExportAsFixedFormat($pdfPath, 17, $false, 1)
    }
  }
  finally {
    $document.Close(0)
  }
}
finally {
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}

$poppler = 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\override\pdftoppm.cmd'
if (-not (Test-Path -LiteralPath $poppler)) { throw 'pdftoppm runtime not found' }
& $poppler -png -r $Dpi $pdfPath (Join-Path $outPath 'page')
if ($LASTEXITCODE -ne 0) { throw "pdftoppm failed: $LASTEXITCODE" }

$count = (Get-ChildItem -LiteralPath $outPath -Filter 'page-*.png').Count
Write-Output "${baseName}: $count pages rendered to $outPath"
