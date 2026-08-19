param(
  [string]$Workspace = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$worksDir = Join-Path $Workspace 'public\content\works'
$sourceDir = Join-Path $Workspace 'public\content\interviews'
$statePath = Join-Path $Workspace 'scripts\state\dadaodao_pages_a5.json'
$qaDir = Join-Path $Workspace 'qa\dadaodao_pagination'
New-Item -ItemType Directory -Force -Path $qaDir | Out-Null

$titleToFile = @{}
Get-ChildItem -LiteralPath $sourceDir -Filter '*.txt' | ForEach-Object {
  $title = Get-Content -Encoding utf8 -LiteralPath $_.FullName |
    Where-Object { $_.Trim() } |
    Select-Object -First 1
  if ($title) { $titleToFile[$title.Trim()] = $_.BaseName }
}

$volumes = @(
  @{ Label = '一'; Name = 'mahaprajapati-interviews-vol1.docx'; Start = 1 },
  @{ Label = '二'; Name = 'mahaprajapati-interviews-vol2.docx'; Start = 189 },
  @{ Label = '三'; Name = 'mahaprajapati-interviews-vol3.docx'; Start = 414 }
)

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$pages = [ordered]@{}
$totals = [ordered]@{}

try {
  for ($volIndex = 0; $volIndex -lt $volumes.Count; $volIndex++) {
    $volume = $volumes[$volIndex]
    $sourcePath = Join-Path $worksDir $volume.Name
    $path = Join-Path $qaDir $volume.Name
    Copy-Item -LiteralPath $sourcePath -Destination $path -Force
    $doc = $word.Documents.OpenNoRepairDialog($path, $false, $false, $false)
    try {
      for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) {
        $doc.TablesOfContents.Item($i).Update()
      }
      $doc.Fields.Update() | Out-Null
      # Force Word to discard python-docx's cached layout before reading page
      # numbers.  PDF export revealed that ComputeStatistics can otherwise
      # return the previous pagination for a newly rebuilt document.
      $doc.Repaginate()

      $starts = @()
      foreach ($paragraph in $doc.Paragraphs) {
        if ($paragraph.OutlineLevel -eq 1) {
          $title = $paragraph.Range.Text.Trim([char]13, [char]7, ' ')
          if ($title) {
            $starts += [pscustomobject]@{
              Title = $title
              Page = [int]$paragraph.Range.Information(1)
            }
          }
        }
      }

      $physical = [int]$doc.ComputeStatistics(2)
      $endPos = [Math]::Max(0, $doc.Content.End - 1)
      $lastRange = $doc.Range($endPos, $endPos)
      $bodyLast = [int]$lastRange.Information(1)
      $totals[$volume.Name] = [ordered]@{
        physical = $physical
        body_start = $volume.Start
        body_last = $bodyLast
      }

      for ($i = 0; $i -lt $starts.Count; $i++) {
        $title = $starts[$i].Title
        if (-not $titleToFile.ContainsKey($title)) {
          throw "No source interview file for heading: $title"
        }
        $fileKey = $titleToFile[$title]
        $endPage = if ($i + 1 -lt $starts.Count) { $starts[$i + 1].Page - 1 } else { $bodyLast }
        $pages[$fileKey] = [ordered]@{
          vol = $volIndex + 1
          vol_label = $volume.Label
          start = $starts[$i].Page
          end = $endPage
          title = $title
        }
      }

      $doc.Save()
      Write-Output ("{0}: {1} physical pages; body pages {2}-{3}; TOC updated" -f $volume.Name, $physical, $volume.Start, $bodyLast)
    }
    finally {
      $doc.Close()
    }
    # 將 Word 更新後的目次與欄位寫回正式交付檔。
    Copy-Item -LiteralPath $path -Destination $sourcePath -Force
  }
}
finally {
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}

$state = [ordered]@{
  format = 'A5'
  pagination = 'cover unnumbered; contents lower-roman; interviews continuous decimal 1-564'
  pages = $pages
  totals = $totals
  quote_pages = [ordered]@{}
}
$state | ConvertTo-Json -Depth 7 | Set-Content -Encoding utf8 -LiteralPath $statePath
Write-Output "Page map: $statePath"
