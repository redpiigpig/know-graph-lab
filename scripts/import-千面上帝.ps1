# ============================================================
# 千面上帝 書摘匯入腳本
# 執行：cd "c:\Users\user\Desktop\know-graph-lab"
#       .\scripts\import-千面上帝.ps1
# ============================================================

$envLines     = Get-Content ".env"
$ACCESS_TOKEN = ($envLines | Where-Object { $_ -match "^SUPABASE_ACCESS_TOKEN=" }) -replace "SUPABASE_ACCESS_TOKEN=",""
$API_BASE     = "https://api.supabase.com/v1/projects/vloqgautkahgmqcwgfuo/database/query"

function Invoke-SQL([string]$sql) {
  $body = [System.Text.Encoding]::UTF8.GetBytes((@{ query = $sql } | ConvertTo-Json -Compress -Depth 2))
  $req  = [System.Net.WebRequest]::Create($API_BASE)
  $req.Method        = "POST"
  $req.ContentType   = "application/json; charset=utf-8"
  $req.Headers["Authorization"] = "Bearer $ACCESS_TOKEN"
  $req.ContentLength = $body.Length
  $stream = $req.GetRequestStream()
  $stream.Write($body, 0, $body.Length)
  $stream.Close()
  $resp   = $req.GetResponse()
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream(), [System.Text.Encoding]::UTF8)
  $json   = $reader.ReadToEnd()
  $resp.Close()
  return $json | ConvertFrom-Json
}

# 跳脫 SQL 字串：' → ''，控制字元清理
function Esc([string]$s) {
  if ($null -eq $s -or $s.Trim() -eq "") { return "NULL" }
  $s = $s.Trim() -replace "'","''"
  return "'$s'"
}

# 解析 C3 引用：作者，書名，頁XX
function Parse-Citation($raw) {
  if ($null -eq $raw) { return @{ author=$null; bookTitle=$null; page=$null } }
  $s = $raw.ToString() -replace "`r","" -replace "`n",""
  if ($s -match "^(.+?)，(.+?)，頁\s*(.+)$") {
    return @{ author=$Matches[1].Trim(); bookTitle=($Matches[2].Trim() -replace "^《","" -replace "》$",""); page=$Matches[3].Trim() }
  } elseif ($s -match "^(.+?)，(.+)$") {
    return @{ author=$Matches[1].Trim(); bookTitle=($Matches[2].Trim() -replace "^《","" -replace "》$","" -replace "，頁.*",""); page=$null }
  }
  return @{ author=$null; bookTitle=$null; page=$null }
}

# 取得「待寫著作」project id
$projRes = Invoke-SQL "SELECT id FROM book_projects WHERE type = '待寫著作' LIMIT 1"
$bookProjectId = $projRes[0].id
Write-Host "book_project id: $bookProjectId"

# 加 unique constraint（若已存在會拋錯忽略）
try { Invoke-SQL "ALTER TABLE books ADD CONSTRAINT books_title_unique UNIQUE (title)" | Out-Null } catch {}

$chapterMap = @{ "ch1"="第一章"; "ch2"="第二章"; "ch3"="第三章" }
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$totalOK = 0; $totalFail = 0

foreach ($chKey in @("ch1","ch2","ch3")) {
  $filePath = "c:\Users\user\Desktop\know-graph-lab\stores\千面上帝\$chKey.csv"
  $chapter  = $chapterMap[$chKey]
  Write-Host "`n=== $chKey ($chapter) ==="

  $wb = $excel.Workbooks.Open($filePath)
  $ws = $wb.Sheets.Item(1)

  # 先收集並 upsert 所有書籍
  $bookMap = @{}
  for ($r = 1; $r -le $ws.UsedRange.Rows.Count; $r++) {
    $c3 = $ws.Cells.Item($r, 3).Value2
    $p  = Parse-Citation $c3
    if ($p.bookTitle) { $bookMap[$p.bookTitle] = $p.author }
  }

  foreach ($bt in $bookMap.Keys) {
    $au = if ($bookMap[$bt]) { $bookMap[$bt] } else { "不詳" }
    $sql = "INSERT INTO books (title, author) VALUES ($(Esc $bt), $(Esc $au)) ON CONFLICT (title) DO NOTHING"
    try { Invoke-SQL $sql | Out-Null } catch {}
  }
  Write-Host "  書籍 upsert: $($bookMap.Count) 本"

  # 逐列插入摘文
  for ($r = 1; $r -le $ws.UsedRange.Rows.Count; $r++) {
    $c1 = $ws.Cells.Item($r, 1).Value2
    $c2 = $ws.Cells.Item($r, 2).Value2
    $c3 = $ws.Cells.Item($r, 3).Value2
    if ($null -eq $c2 -or $c2.ToString().Trim() -eq "") { continue }
    if ($null -eq $c1 -or $c1.ToString().Trim() -eq "") { continue }

    $title   = ($c1.ToString().Trim() -replace "`r","" -replace "`n"," ")
    $content = $c2.ToString().Trim()
    $p       = Parse-Citation $c3

    $bookIdExpr = if ($p.bookTitle) { "(SELECT id FROM books WHERE title = $(Esc $p.bookTitle) LIMIT 1)" } else { "NULL" }
    $pageExpr   = if ($p.page)      { Esc $p.page } else { "NULL" }

    $sql = @"
WITH new_e AS (
  INSERT INTO excerpts (title, content, chapter, page_number, book_id)
  VALUES ($(Esc $title), $(Esc $content), $(Esc $chapter), $pageExpr, $bookIdExpr)
  RETURNING id
)
INSERT INTO excerpt_book_projects (excerpt_id, book_project_id)
SELECT id, '$bookProjectId' FROM new_e
"@
    try {
      Invoke-SQL $sql | Out-Null
      $totalOK++
      if ($totalOK % 20 -eq 0) { Write-Host "  已匯入 $totalOK 筆..." }
    } catch {
      $msg = $_.Exception.Message
      Write-Host "  FAIL row$r : $($msg.Substring(0,[Math]::Min(120,$msg.Length)))"
      $totalFail++
    }
  }
  $wb.Close($false)
}

$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Remove-Item "c:\Users\user\Desktop\know-graph-lab\stores\千面上帝\sample_c3.txt" -ErrorAction SilentlyContinue

Write-Host "`n完成！成功: $totalOK 筆，失敗: $totalFail 筆"
