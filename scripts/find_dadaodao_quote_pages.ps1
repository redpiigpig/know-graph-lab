param(
  [string]$Workspace = (Split-Path -Parent $PSScriptRoot),
  [string]$NeedlesPath = (Join-Path $PSScriptRoot 'data\dadaodao_quote_needles.json'),
  [string]$OutputPath = (Join-Path $PSScriptRoot 'state\dadaodao_quote_pages_a5.json')
)

$ErrorActionPreference = 'Stop'
$items = Get-Content -LiteralPath $NeedlesPath -Raw -Encoding utf8 | ConvertFrom-Json
$works = Join-Path $Workspace 'qa\dadaodao_pagination'
$results = [ordered]@{}
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.AutomationSecurity = 3
$word.Options.UpdateLinksAtOpen = $false
try {
  foreach ($volume in 1, 2, 3) {
    $selected = @($items | Where-Object { $_.volume -eq $volume })
    if ($selected.Count -eq 0) { continue }
    $path = Join-Path $works ("mahaprajapati-interviews-vol{0}.docx" -f $volume)
    $doc = $word.Documents.OpenNoRepairDialog($path, $false, $true, $false)
    try {
      $doc.Repaginate()
      foreach ($item in $selected) {
        $range = $doc.Content.Duplicate
        $range.Find.ClearFormatting()
        $found = $range.Find.Execute($item.needle)
        if (-not $found) { throw "Quote needle not found: $($item.id)" }
        $results[$item.id] = [ordered]@{
          volume = $volume
          adjusted_page = [int]$range.Information(1)
          physical_page = [int]$range.Information(3)
          needle = $item.needle
        }
      }
    }
    finally {
      $doc.Close(0)
    }
  }
}
finally {
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}

$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputPath -Encoding utf8
$results | ConvertTo-Json -Depth 5
