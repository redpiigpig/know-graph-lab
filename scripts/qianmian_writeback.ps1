# ============================================================
# Write back qianmian (千面上帝) citations from Excel to DB
# - Insert 8 new books with researched metadata
# - Insert 3 journal_articles
# - Update 88 excerpts with book_id / journal_article_id / page_number
# - Non-book sources (URL/Bible/Lactantius) go directly into page_number
# ============================================================

$envLines     = Get-Content "c:\Users\user\Desktop\know-graph-lab\.env"
$ACCESS_TOKEN = ($envLines | Where-Object { $_ -match "^SUPABASE_ACCESS_TOKEN=" }) -replace "SUPABASE_ACCESS_TOKEN=",""
$API_BASE     = "https://api.supabase.com/v1/projects/vloqgautkahgmqcwgfuo/database/query"

function Invoke-SQL([string]$sql) {
  $bodyObj  = [ordered]@{ query = $sql }
  $bodyJson = $bodyObj | ConvertTo-Json -Compress -Depth 2
  $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyJson)
  $req = [System.Net.HttpWebRequest]::Create($API_BASE)
  $req.Method = "POST"; $req.ContentType = "application/json; charset=utf-8"
  $req.Headers.Add("Authorization", "Bearer $ACCESS_TOKEN")
  $req.ContentLength = $bodyBytes.Length
  $s = $req.GetRequestStream(); $s.Write($bodyBytes, 0, $bodyBytes.Length); $s.Close()
  $resp = $req.GetResponse()
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream(), [System.Text.Encoding]::UTF8)
  $json = $reader.ReadToEnd(); $resp.Close()
  return $json | ConvertFrom-Json
}

function Esc([string]$s) {
  if ($null -eq $s -or $s.Trim() -eq "") { return "NULL" }
  $escaped = $s.Trim() -replace "'","''"
  return "'$escaped'"
}

# ------------------------------------------------------------
# Phase 1: Upsert 8 new books, get IDs
# ------------------------------------------------------------
Write-Host "=== Phase 1: Upsert 8 new books ==="

$newBooks = @(
  [ordered]@{
    title="從聖典到教史：巴利佛教的思想交涉"; author="黃柏棋"; translator=$null;
    publisher="明目文化"; publish_place="台中"; publish_year=2009;
    original_title=$null; original_author=$null; original_publisher=$null; original_publish_year=$null;
    metadata_source="台大佛學數位圖書館 (黃柏棋,政大宗教所)"
  },
  [ordered]@{
    title="「諾斯」與拯救：古代諾斯替主義的神話、哲學與精神修煉"; author="張新樟"; translator=$null;
    publisher="三聯書店"; publish_place="北京"; publish_year=2005;
    original_title=$null; original_author=$null; original_publisher=$null; original_publish_year=$null;
    metadata_source="三聯哈佛燕京叢書"
  },
  [ordered]@{
    title="眾神降臨之前：在沉默中重現的印度河文明"; author="安德魯‧魯賓遜"; translator="周佳";
    publisher="中國社會科學出版社"; publish_place="北京"; publish_year=2021;
    original_title="The Indus: Lost Civilizations"; original_author="Andrew Robinson";
    original_publisher="Reaktion Books"; original_publish_year=2015;
    metadata_source="豆瓣讀書 35197213"
  },
  [ordered]@{
    title="前中國時代：公元前4000—前2300年華夏大地場景"; author="李琳之"; translator=$null;
    publisher="商務印書館"; publish_place="北京"; publish_year=2021;
    original_title=$null; original_author=$null; original_publisher=$null; original_publish_year=$null;
    metadata_source="商務印書館 ISBN 9787100198134"
  },
  [ordered]@{
    title="西塞羅全集第三卷：神性論篇"; author="西塞羅"; translator="王曉朝";
    publisher="人民出版社"; publish_place="北京"; publish_year=2007;
    original_title="De Natura Deorum"; original_author="Marcus Tullius Cicero";
    original_publisher=$null; original_publish_year=-45;
    metadata_source="人民出版社《西塞羅全集》第三卷,王曉朝譯"
  },
  [ordered]@{
    title="碰撞與交融：希臘化時代的歷史與文化"; author="楊巨平"; translator=$null;
    publisher="中國社會科學出版社"; publish_place="北京"; publish_year=2018;
    original_title=$null; original_author=$null; original_publisher=$null; original_publish_year=$null;
    metadata_source="中國社會科學出版社「希臘化文明研究」第一卷 ISBN 9787520317498"
  },
  [ordered]@{
    title="不可能的帝國：西班牙史"; author="雷蒙德‧卡爾"; translator=$null;
    publisher="東方出版中心"; publish_place="上海"; publish_year=2019;
    original_title="Spain: A History"; original_author="Raymond Carr";
    original_publisher="Oxford University Press"; original_publish_year=2000;
    metadata_source="東方出版中心 ISBN 9787547315378"
  },
  [ordered]@{
    title="巴哈歐拉啟示錄(第四卷):馬茲拉伊與巴海,1877—1892"; author="阿迪卜‧塔希爾扎德"; translator=$null;
    publisher="馬來西亞巴哈伊出版社"; publish_place="馬來西亞"; publish_year=$null;
    original_title="The Revelation of Bahá'u'lláh, Volume 4: Mazra'ih and Bahji, 1877-92";
    original_author="Adib Taherzadeh"; original_publisher="George Ronald"; original_publish_year=1987;
    metadata_source="mybahaibook.org 中文版線上"
  }
)

$bookKeys = @("baliFojiao","nuoSi","zhongShenJiangLin","qianZhongguo","xiSailuo","penghuangJiaoRong","bukenengDiguo","bahaOulaQishi")
$bookIds = @{}

for ($i=0; $i -lt $newBooks.Count; $i++) {
  $b = $newBooks[$i]
  $key = $bookKeys[$i]
  $sql = @"
INSERT INTO books (title, author, translator, publisher, publish_place, publish_year,
                   original_title, original_author, original_publisher, original_publish_year,
                   metadata_source)
VALUES ($(Esc $b.title), $(Esc $b.author), $(Esc $b.translator),
        $(Esc $b.publisher), $(Esc $b.publish_place),
        $(if ($null -ne $b.publish_year) { $b.publish_year } else { "NULL" }),
        $(Esc $b.original_title), $(Esc $b.original_author), $(Esc $b.original_publisher),
        $(if ($null -ne $b.original_publish_year) { $b.original_publish_year } else { "NULL" }),
        $(Esc $b.metadata_source))
ON CONFLICT (title) DO UPDATE SET
  author = EXCLUDED.author,
  translator = EXCLUDED.translator,
  publisher = EXCLUDED.publisher,
  publish_place = EXCLUDED.publish_place,
  publish_year = EXCLUDED.publish_year,
  original_title = EXCLUDED.original_title,
  original_author = EXCLUDED.original_author,
  original_publisher = EXCLUDED.original_publisher,
  original_publish_year = EXCLUDED.original_publish_year,
  metadata_source = EXCLUDED.metadata_source
RETURNING id
"@
  $r = Invoke-SQL $sql
  $bookIds[$key] = $r[0].id
  Write-Host ("  [{0}] {1} -> {2}" -f $key, $b.title, $r[0].id)
  Start-Sleep -Milliseconds 500
}

# Look up existing book IDs we'll reuse
$existingLookups = @{
  "yuanWenqi"     = "二元神論"
  "beiYincang"    = "被隱藏的眾神"
  "zhuiXunYindu"  = "《追尋印度史詩之美》"
}
foreach ($k in $existingLookups.Keys) {
  $title = $existingLookups[$k]
  $r = Invoke-SQL "SELECT id FROM books WHERE title = $(Esc $title) LIMIT 1"
  if ($r.Count -gt 0) {
    $bookIds[$k] = $r[0].id
    Write-Host ("  existing [{0}] {1} -> {2}" -f $k, $title, $r[0].id)
  } else {
    Write-Host "  WARN: existing book '$title' not found"
  }
  Start-Sleep -Milliseconds 300
}

# ------------------------------------------------------------
# Phase 2: Insert 3 journal_articles
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== Phase 2: Insert 3 journal_articles ==="

$articles = @(
  [ordered]@{
    key="liuHuizhen";
    title="從《佛般泥洹經》線索探討漢譯佛經中轉輪王觀念"; author="劉慧珍";
    venue=$null; publish_year=$null; issue_label=$null
  },
  [ordered]@{
    key="kangLe";
    title="轉輪王觀念與中國中古的佛教政治"; author="康樂";
    venue=$null; publish_year=$null; issue_label=$null
  },
  [ordered]@{
    key="fengJinpeng";
    title="畢達哥拉斯：從人到神的演變—「古史層累」現象的西方個案探究"; author="馮金朋";
    venue="古代文明"; publish_year=2009; issue_label="第3卷第1期"
  }
)

$articleIds = @{}
foreach ($a in $articles) {
  $sql = @"
INSERT INTO journal_articles (title, author, venue, publish_year, issue_label)
VALUES ($(Esc $a.title), $(Esc $a.author), $(Esc $a.venue),
        $(if ($null -ne $a.publish_year) { $a.publish_year } else { "NULL" }),
        $(Esc $a.issue_label))
RETURNING id
"@
  $r = Invoke-SQL $sql
  $articleIds[$a.key] = $r[0].id
  Write-Host ("  [{0}] {1} -> {2}" -f $a.key, $a.title, $r[0].id)
  Start-Sleep -Milliseconds 500
}

# ------------------------------------------------------------
# Phase 3: Build update plan for 88 excerpts
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== Phase 3: Build update plan ==="

$citPath = "c:\Users\user\Desktop\know-graph-lab\scripts\qianmian_88_citations.txt"
$lines = Get-Content $citPath -Encoding UTF8

# Parse the file: extract (db_id, citation) pairs
$pairs = @()
$curId = $null
foreach ($l in $lines) {
  if ($l -match '^\s+db_id\s+:\s+(\S+)') {
    $curId = $matches[1].Trim()
  }
  elseif ($l -match '^\s+citation\s+:\s+(.+)$') {
    $cit = $matches[1].Trim()
    $pairs += [PSCustomObject]@{ db_id=$curId; cit=$cit }
  }
  elseif ($l -match '^\s+url\s+:\s+(.+)$') {
    $cit = $matches[1].Trim()
    $pairs += [PSCustomObject]@{ db_id=$curId; cit=$cit }
  }
}
Write-Host "Parsed pairs: $($pairs.Count)"

# Dispatch each citation -> {book_id, journal_article_id, page_number}
function Dispatch([string]$cit) {
  # URLs
  if ($cit -match '^https?://') {
    return @{ book_id=$null; journal_article_id=$null; page_number=$cit }
  }
  # Lactantius (Edict of Milan primary source)
  if ($cit -match '^from Lactantius') {
    return @{ book_id=$null; journal_article_id=$null; page_number=$cit }
  }
  # Bible/scripture references starting with 《
  if ($cit -match '^《') {
    # Normalize 章 to :  e.g. "《約伯記》31章26-28節" -> "《約伯記》31:26-28"
    $p = $cit -replace '章','：' -replace '節',''
    return @{ book_id=$null; journal_article_id=$null; page_number=$p }
  }

  # Book/journal citations - detect by author prefix
  $COMMA = [char]0xFF0C

  # 蔡源林,被隱藏的眾神推薦序,...
  if ($cit -match '蔡源林') {
    $page = "蔡源林推薦序"
    if ($cit -match '頁(.+)$') { $page = "蔡源林推薦序，頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["beiYincang"]; journal_article_id=$null; page_number=$page }
  }

  # 黃柏棋〈永恆的神話創作...〉。潘俊琳,《追尋印度史詩之美》序
  if ($cit -match '永恆的神話創作' -or $cit -match '潘俊琳') {
    return @{ book_id=$bookIds["zhuiXunYindu"]; journal_article_id=$null;
              page_number="黃柏棋〈永恆的神話創作、不朽的宗教關懷〉序" }
  }

  # 王曉朝,西塞羅《論神性》導言
  if ($cit -match '王曉朝.*論神性') {
    return @{ book_id=$bookIds["xiSailuo"]; journal_article_id=$null; page_number="王曉朝導言" }
  }

  # 黃柏棋/琪,巴利佛教的思想交涉,頁X
  if ($cit -match '巴利佛教的思想交涉') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["baliFojiao"]; journal_article_id=$null; page_number=$page }
  }

  # 張新樟,諾斯與拯救,頁X
  if ($cit -match '諾斯與拯救') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["nuoSi"]; journal_article_id=$null; page_number=$page }
  }

  # 安德魯‧魯賓遜,眾神降臨之前,頁X
  if ($cit -match '眾神降臨之前') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["zhongShenJiangLin"]; journal_article_id=$null; page_number=$page }
  }

  # 李琳之,前中國時代,頁X
  if ($cit -match '前中國時代') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["qianZhongguo"]; journal_article_id=$null; page_number=$page }
  }

  # 楊巨平,希臘化時代的歷史與文化,頁X
  if ($cit -match '希臘化時代的歷史與文化') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["penghuangJiaoRong"]; journal_article_id=$null; page_number=$page }
  }

  # Raymond Carr,不可能的帝國:西班牙史
  if ($cit -match '不可能的帝國') {
    $page = $null
    if ($cit -match '頁([\d\s\-]+)') { $page = "頁$($matches[1].Trim())" }
    return @{ book_id=$bookIds["bukenengDiguo"]; journal_article_id=$null; page_number=$page }
  }

  # 阿迪卜‧塔赫薩德,巴哈歐拉的天啟(第四卷),頁X
  if ($cit -match '巴哈歐拉的天啟') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["bahaOulaQishi"]; journal_article_id=$null; page_number=$page }
  }

  # 元文琪,二元神論...,頁X
  if ($cit -match '元文琪.*二元神論') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$bookIds["yuanWenqi"]; journal_article_id=$null; page_number=$page }
  }

  # 馮金朋,畢達哥拉斯:從人到神的演變,頁X (journal article!)
  if ($cit -match '馮金朋.*畢達哥拉斯') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$null; journal_article_id=$articleIds["fengJinpeng"]; page_number=$page }
  }

  # 康樂,...。轉引自:劉慧珍,...,頁X (secondary cite)
  if ($cit -match '康樂.*轉輪王觀念') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "轉引自劉慧珍，頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$null; journal_article_id=$articleIds["kangLe"]; page_number=$page }
  }

  # 劉慧珍,〈從《佛般泥洹經》...〉,頁X
  if ($cit -match '劉慧珍') {
    $page = $null
    if ($cit -match '頁(.+)$') { $page = "頁$($matches[1])".TrimEnd('。') }
    return @{ book_id=$null; journal_article_id=$articleIds["liuHuizhen"]; page_number=$page }
  }

  # Fallback: unhandled
  Write-Host "  [WARN] unhandled citation: $cit"
  return @{ book_id=$null; journal_article_id=$null; page_number=$cit }
}

# Build update plan keyed by db_id
$plan = @{}  # db_id -> { book_id, journal_article_id, page_number }
foreach ($p in $pairs) {
  $d = Dispatch $p.cit
  if (-not $plan.ContainsKey($p.db_id)) {
    $plan[$p.db_id] = @{
      book_id            = $d.book_id
      journal_article_id = $d.journal_article_id
      page_number        = $d.page_number
      sources            = @($p.cit)
    }
  } else {
    # Duplicate — check if same dispatch result, else merge as multi-source
    $existing = $plan[$p.db_id]
    if ($existing.book_id -eq $d.book_id -and
        $existing.journal_article_id -eq $d.journal_article_id -and
        $existing.page_number -eq $d.page_number) {
      # exact dup, ignore
    } else {
      # different source for same excerpt — merge into page_number, keep first as primary
      $note = $p.cit
      $existing.page_number = "$($existing.page_number)；又見：$note"
      $existing.sources += $p.cit
    }
  }
}

Write-Host "Unique db_ids to update: $($plan.Keys.Count)"

# ------------------------------------------------------------
# Phase 4: Run UPDATE for each db_id
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== Phase 4: Run UPDATEs ==="

$ok = 0; $fail = 0
foreach ($id in $plan.Keys) {
  $u = $plan[$id]
  $bookSet = if ($u.book_id) { "book_id = $(Esc $u.book_id)::uuid" } else { "book_id = NULL" }
  $jaSet   = if ($u.journal_article_id) { "journal_article_id = $(Esc $u.journal_article_id)::uuid" } else { "journal_article_id = NULL" }
  $pgSet   = if ($u.page_number) { "page_number = $(Esc $u.page_number)" } else { "page_number = NULL" }

  $sql = "UPDATE excerpts SET $bookSet, $jaSet, $pgSet WHERE id = $(Esc $id)::uuid"
  try {
    Invoke-SQL $sql | Out-Null
    $ok++
  } catch {
    $fail++
    $msg = $_.Exception.Message
    Write-Host "  FAIL $id : $($msg.Substring(0,[Math]::Min(150,$msg.Length)))"
  }
  Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "=== Done! OK=$ok FAIL=$fail ==="

# Summary check
$summary = Invoke-SQL @"
SELECT
  count(*) FILTER (WHERE book_id IS NULL AND journal_article_id IS NULL) AS no_source,
  count(*) FILTER (WHERE book_id IS NOT NULL) AS with_book,
  count(*) FILTER (WHERE journal_article_id IS NOT NULL) AS with_journal,
  count(*) AS total
FROM excerpts e
JOIN excerpt_book_projects ebp ON ebp.excerpt_id = e.id
WHERE ebp.book_project_id = '2d950579-0358-477a-8d12-978e8cc8e3a5'
"@
Write-Host ""
Write-Host "DB after update:"
$summary | Format-Table total, with_book, with_journal, no_source -AutoSize
