# ============================================================
# Import script for stores data via Management API
# Run: cd "c:\Users\user\Desktop\know-graph-lab"
#      .\scripts\import-thousands.ps1
# ============================================================

$envLines     = Get-Content ".env"
$ACCESS_TOKEN = ($envLines | Where-Object { $_ -match "^SUPABASE_ACCESS_TOKEN=" }) -replace "SUPABASE_ACCESS_TOKEN=",""
$API_BASE     = "https://api.supabase.com/v1/projects/vloqgautkahgmqcwgfuo/database/query"

function Invoke-SQL([string]$sql) {
  $bodyObj  = [ordered]@{ query = $sql }
  $bodyJson = $bodyObj | ConvertTo-Json -Compress -Depth 2
  $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyJson)

  $req = [System.Net.HttpWebRequest]::Create($API_BASE)
  $req.Method      = "POST"
  $req.ContentType = "application/json; charset=utf-8"
  $req.Headers.Add("Authorization", "Bearer $ACCESS_TOKEN")
  $req.ContentLength = $bodyBytes.Length
  $s = $req.GetRequestStream(); $s.Write($bodyBytes, 0, $bodyBytes.Length); $s.Close()
  $resp   = $req.GetResponse()
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream(), [System.Text.Encoding]::UTF8)
  $json   = $reader.ReadToEnd(); $resp.Close()
  return $json | ConvertFrom-Json
}

function Esc([string]$s) {
  if ($null -eq $s -or $s.Trim() -eq "") { return "NULL" }
  $escaped = $s.Trim() -replace "'","''"
  return "'$escaped'"
}

# Unicode chars to avoid encoding issues in source
$COMMA  = [char]0xFF0C   # full-width comma ，
$PAGE   = [char]0x9801   # page char 頁
$LBR    = [char]0x300A   # left book bracket 《
$RBR    = [char]0x300B   # right book bracket 》
$CH1    = "$([char]0x7B2C)$([char]0x4E00)$([char]0x7AE0)"   # 第一章
$CH2    = "$([char]0x7B2C)$([char]0x4E8C)$([char]0x7AE0)"   # 第二章
$CH3    = "$([char]0x7B2C)$([char]0x4E09)$([char]0x7AE0)"   # 第三章
$PROJ_T = "$([char]0x5F85)$([char]0x5BEB)$([char]0x8457)$([char]0x4F5C)"  # 待寫著作

function Parse-Citation($raw) {
  if ($null -eq $raw) { return @{ author=$null; bookTitle=$null; page=$null } }
  $s = $raw.ToString() -replace "`r","" -replace "`n",""
  $parts = $s.Split($COMMA)
  if ($parts.Count -ge 3) {
    $author    = $parts[0].Trim()
    $bookTitle = $parts[1].Trim() -replace [string]$LBR,"" -replace [string]$RBR,""
    $pageStr   = ($parts[-1] -replace [string]$PAGE,"").Trim()
    return @{ author=$author; bookTitle=$bookTitle; page=$pageStr }
  } elseif ($parts.Count -eq 2) {
    $author    = $parts[0].Trim()
    $bookTitle = ($parts[1] -replace [string]$LBR,"" -replace [string]$RBR,"").Trim()
    return @{ author=$author; bookTitle=$bookTitle; page=$null }
  }
  return @{ author=$null; bookTitle=$null; page=$null }
}

# 待寫著作 ID (hardcoded - verified via hex e5be85e5afabe89197e4bd9c)
$bookProjectId = "2d950579-0358-477a-8d12-978e8cc8e3a5"
Write-Host "book_project id (待寫著作): $bookProjectId"

# Add unique constraint on books.title (ignore if exists)
try { Invoke-SQL "ALTER TABLE books ADD CONSTRAINT books_title_unique UNIQUE (title)" | Out-Null } catch {}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$totalOK = 0; $totalFail = 0

foreach ($chKey in @("ch11","ch12","ch13","ch14","ch15","ch16","ch17","ch18","ch19","ch20")) {
  $filePath = "c:\Users\user\Desktop\know-graph-lab\stores\$([char]0x5343)$([char]0x9762)$([char]0x4E0A)$([char]0x5E1D)\$chKey.csv"
  Write-Host "`n=== $chKey ==="

  if (-not (Test-Path $filePath)) { Write-Host "  File not found: $filePath"; continue }
  $wb = $excel.Workbooks.Open($filePath)
  $ws = $wb.Sheets.Item(1)
  $lastRow = $ws.UsedRange.Rows.Count
  Write-Host "  Rows: $lastRow"

  # Collect unique books first and upsert
  $bookMap = @{}
  for ($r = 1; $r -le $lastRow; $r++) {
    $c3 = $ws.Cells.Item($r, 3).Value2
    if ($null -ne $c3) {
      $p = Parse-Citation $c3
      if ($p.bookTitle -and $p.bookTitle.Trim() -ne "") {
        $bookMap[$p.bookTitle] = if ($p.author) { $p.author } else { "?" }
      }
    }
  }
  foreach ($bt in $bookMap.Keys) {
    $sql = "INSERT INTO books (title, author) VALUES ($(Esc $bt), $(Esc $bookMap[$bt])) ON CONFLICT (title) DO NOTHING"
    try { Invoke-SQL $sql | Out-Null } catch {}
  }
  Write-Host "  Books upserted: $($bookMap.Count)"

  # Build rows array
  $rows = @()
  for ($r = 1; $r -le $lastRow; $r++) {
    $c1 = $ws.Cells.Item($r, 1).Value2
    $c2 = $ws.Cells.Item($r, 2).Value2
    $c3 = $ws.Cells.Item($r, 3).Value2
    if ($null -eq $c2 -or $c2.ToString().Trim() -eq "") { continue }
    if ($null -eq $c1 -or $c1.ToString().Trim() -eq "") { continue }
    $title   = $c1.ToString().Trim() -replace "`r","" -replace "`n"," "
    $content = $c2.ToString().Trim()
    $p       = Parse-Citation $c3
    $rows += @{ title=$title; content=$content; page=$p.page; bookTitle=$p.bookTitle }
  }
  $wb.Close($false)
  Write-Host "  Valid rows: $($rows.Count)"

  if ($rows.Count -eq 0) { continue }

  # Chapter as chr() — 第=31532,章=31456,十=21313; 一=19968,二=20108,三=19977,四=22235,五=20116,六=20845,七=19971,八=20843,九=20061
  $TEN = 21313
  $chExprMap = @{
    "ch1"  = "chr(31532)||chr(19968)||chr(31456)"
    "ch2"  = "chr(31532)||chr(20108)||chr(31456)"
    "ch3"  = "chr(31532)||chr(19977)||chr(31456)"
    "ch4"  = "chr(31532)||chr(22235)||chr(31456)"
    "ch5"  = "chr(31532)||chr(20116)||chr(31456)"
    "ch6"  = "chr(31532)||chr(20845)||chr(31456)"
    "ch7"  = "chr(31532)||chr(19971)||chr(31456)"
    "ch8"  = "chr(31532)||chr(20843)||chr(31456)"
    "ch9"  = "chr(31532)||chr(20061)||chr(31456)"
    "ch10" = "chr(31532)||chr($TEN)||chr(31456)"
    "ch11" = "chr(31532)||chr($TEN)||chr(19968)||chr(31456)"
    "ch12" = "chr(31532)||chr($TEN)||chr(20108)||chr(31456)"
    "ch13" = "chr(31532)||chr($TEN)||chr(19977)||chr(31456)"
    "ch14" = "chr(31532)||chr($TEN)||chr(22235)||chr(31456)"
    "ch15" = "chr(31532)||chr($TEN)||chr(20116)||chr(31456)"
    "ch16" = "chr(31532)||chr($TEN)||chr(20845)||chr(31456)"
    "ch17" = "chr(31532)||chr($TEN)||chr(19971)||chr(31456)"
    "ch18" = "chr(31532)||chr($TEN)||chr(20843)||chr(31456)"
    "ch19" = "chr(31532)||chr($TEN)||chr(20061)||chr(31456)"
    "ch20" = "chr(31532)||chr(20108)||chr($TEN)||chr(31456)"
  }
  $chapterChrExpr = $chExprMap[$chKey]

  # Build one batch CTE SQL for all rows in this chapter
  $valueRows = $rows | ForEach-Object {
    $bt = if ($_.bookTitle -and $_.bookTitle.Trim() -ne "") { Esc $_.bookTitle } else { "NULL" }
    $pg = if ($_.page -and $_.page.Trim() -ne "")           { Esc $_.page }      else { "NULL" }
    "($(Esc $_.title), $(Esc $_.content), $pg, $bt)"
  }
  $valuesClause = $valueRows -join ",`n    "

  $batchSql = @"
WITH vals AS (
  SELECT v.title, v.content, $chapterChrExpr AS chapter, v.page_number,
         b.id AS book_id
  FROM (VALUES
    $valuesClause
  ) AS v(title, content, page_number, book_title)
  LEFT JOIN books b ON b.title = v.book_title
),
ins AS (
  INSERT INTO excerpts (title, content, chapter, page_number, book_id)
  SELECT title, content, chapter, page_number, book_id FROM vals
  RETURNING id
)
INSERT INTO excerpt_book_projects (excerpt_id, book_project_id)
SELECT id, '$bookProjectId' FROM ins
"@

  try {
    Invoke-SQL $batchSql | Out-Null
    $totalOK += $rows.Count
    Write-Host "  Batch insert OK: $($rows.Count) rows"
  } catch {
    $msg = $_.Exception.Message
    Write-Host "  Batch FAIL: $($msg.Substring(0,[Math]::Min(300,$msg.Length)))"
    $totalFail += $rows.Count
  }
  # Rate limit protection: wait between chapters
  Start-Sleep -Seconds 8
}

$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

Write-Host "`nDone! OK=$totalOK  FAIL=$totalFail"
