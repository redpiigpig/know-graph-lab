---
name: scripture-accs
description: 把《古代基督信仰聖經註釋叢書》(ACCS, IVP/校園) 的教父註釋嵌進 /scripture 聖經閱讀器 — 經文逐節對照不動，按一個「教父註釋」鈕即在每個 ACCS 經文段落（pericope）下方展開「總論＋具名教父引文」區塊（經文上‧註釋下版面）。資料走 accs_commentary 表（verse_start..verse_end 對齊段落）；來源用校園書房繁中版掃描 PDF，Gemini 結構化 OCR→純函式 parser→入庫。與 [[scripture-fathers]] 分工：fathers 做「教父全集整卷翻譯/精修上 /fathers」；本 skill 做「ACCS 註釋嵌進聖經逐節閱讀」。Use when 要新增/重 OCR 某卷 ACCS 經文註釋、調 /scripture 註釋版面、改 accs_commentary schema 或 parser、推廣到創世記以外的書卷。
---

> ⚙️ 引擎政策（2026-06-14 更新）：掃描中文 OCR 品質 **Sonnet > Gemini ≫ Haiku**。
> Haiku Vision 對掃描中文錯字/漏字/合併嚴重（user 退過兩次），**已棄用**。
> Gemini 品質佳但**每日額度與 jung/mueller 等並行任務共用、常乾**。
> → 現役引擎 = **Sonnet（`--engine sonnet`，Claude Max OAuth，5h 滾動額度）**，多頁批次（`--batch`）省額度。
> `ingest_accs_genesis.py` 支援 `--engine gemini|haiku|sonnet`。中文一律繁體（[[feedback_traditional_chinese_only]]）。
> 🚨 截圖／渲染頁 ≤2000px（[[feedback_screenshot_2000px]]）。

# ACCS 教父註釋嵌入聖經閱讀器 Skill

把 ACCS（27 冊）的教父釋經，以 **catena（經文段落 → 總論 → 具名教父引文）** 的原體例，
嵌進 `/scripture` 既有的多版本逐節對照閱讀器。**第一個案例＝創世記**（user 2026-06-12 指定先做、
看過再推廣到其他書卷）。

## 為什麼不走 /fathers 整卷翻譯那條路
ACCS 不是「一卷教父著作」，而是**按聖經章節排列的教父釋經彙編**。讀者要的是「讀某節經文時，
順手看歷代教父怎麼解這節」。所以它該長在 `/scripture` 經文旁，不是 `/fathers` 書架上。
→ 獨立資料表 + 經文閱讀器內的 toggle，**不重用** translate/consolidate 那套整卷 pipeline。

## 版面決策（user 2026-06-12 拍板）
**經文上‧註釋下，按 ACCS 段落分段。**（不是兩欄。）理由：ACCS 註釋是段落級、長度不一、一則可跨數節，
塞進逐節對照的兩欄格子會大量空格＋對不齊。經文維持原多版本逐節對照；每個 ACCS pericope 之下插入
**可摺疊**的教父註釋區塊（總論斜體 + 各教父引文，末尾掛「教父《作品》」出處）。

## 架構（三層，仿 [[scripture-canon]] / [[scripture-gnostic]] 的純函式 test-first 風格）

```
校園繁中版掃描 PDF（G:/.../電子書/世界宗教/基督教/IVP - 古代基督信仰聖經註釋叢書 (27 冊)/）
   │  全是掃描影像（無 text layer）→ 必 Gemini Vision OCR
   ▼
[scripts/ingest_accs_genesis.py]  ← 逐頁渲染 → Gemini 結構化 JSON（response_schema）
   每則 {ref, kind(overview|comment), heading, father, father_en, work, body}
   │
   ▼
[scripts/accs_commentary.py]  ← 純函式核心（無 env/網路；pytest 全綠）
   parse_verse_range('1:1-2',1)=(1,2) · normalize_father('屈梭多模')='金口若望'
   build_rows() → 指派 pericope_order / entry_order，收斂教父譯名
   │
   ▼
accs_commentary 表（database/accs-commentary-schema.sql）
   UNIQUE(book_code,chapter,verse_start,verse_end,entry_order) → 冪等 upsert
   │
   ▼
[server/api/scripture/commentary.get.ts]  ← 按 pericope_order group 成 pericopes[]
   │
   ▼
[pages/scripture/[book]/[chapter].vue]  ← 「教父註釋」toggle + segments 計算（經文分段對齊 pericope）
```

## 資料表 `accs_commentary`
`book_code, chapter, verse_start, verse_end, pericope_order, entry_order,
section_kind('overview'|'comment'), heading, father_name, father_name_en, work_title,
body_zh, source_vol`。一列 = 一個總論或一則教父引文。RLS 公共讀 / authenticated 寫（對齊 bible_verses）。
套 schema：`node scripts/apply-accs-schema.mjs`（Management API，見 [[reference_supabase_management_api]]）。

## 跑新一卷（或新一章）的流程
```bash
# 0. 在 G: 找到該卷校園版 PDF（27 冊 folder 內），先人工翻 PDF 找該章對應「實體頁碼」範圍
# 1. 結構化 OCR 入庫（一次一章，跑完 spot-check 再下一章）
python scripts/ingest_accs_genesis.py \
   --pdf "G:/我的雲端硬碟/資料/電子書/世界宗教/基督教/IVP - 古代基督信仰聖經註釋叢書 (27 冊)/古代基督信仰聖經註釋叢書1 創1-11.pdf" \
   --book gen --chapter 1 --pages 46-58 \
   --source-vol "ACCS OT I（創 1–11）" --dry-run   # 先 --dry-run 看切段對不對
# 去掉 --dry-run 正式入庫（冪等 upsert）
# 2. spot-check：/scripture/gen/1 開「教父註釋」鈕，看 pericope 切分、教父出處、順序
# 3. 新增的教父譯名變體 → 收進 accs_commentary.FATHER_FIXES（對齊 /translation-glossary 主譯）
```
- `--pages` 是 **PDF 實體頁碼**（PDF 含前言/讚譽/導論數十頁，章內容頁要人工先定位）。
- 跨頁未完段落：parser 用同 `ref` 把跨頁同段落 merge（build_rows 依首見順序給 pericope_order，
  故**頁碼要照順序跑**）。
- 教父譯名一律對齊 [[translation-glossary]] 主譯（屈梭多模→金口若望、巴西略→巴西流、西里爾/區利羅依
  [[scripture-fathers]] 譯名決策；FATHER_FIXES 只收同一人異寫，**不碰同名異人**）。

## 測試
`python scripts/tests/test_accs_commentary.py`（或 `pytest`）— **34 例**：節範圍解析（單節/連字/全形冒號/
跨章夾斷/亂碼）、`parse_full_ref`/`build_rows_auto`（整本自動分章+章內 carry-forward）、教父譯名收斂、
繁體強制（opencc s2twp）/`has_simplified`/`normalize_body`、build_rows 的 pericope/entry 排序與空 body 跳過。
改 parser 必先補測試（user 很在意 test-first）。

---

## 🧭 下個 session 接手清單（2026-06-14 晚更新）

### A. ACCS 創世記 OCR — **從零重 OCR 中（batch 1，已能穩定推進）**
- **引擎演進**：原用 Haiku Vision（Gemini 額度乾），但 **Haiku 掃描中文品質不合格**（錯字「住握裙/傅變/逐生」、
  漏字、漏小標、合併；user 退兩次）。Gemini 品質佳但**每日額度被並行任務吃光**。
  → **定案 Sonnet**（`--engine sonnet`，Max OAuth，5h 滾動額度）。**2026-06-14 已實測 Sonnet 內容品質佳**
  （繁體乾淨、catena 結構正確、教父名／作品名準）。
- **資料現況（重要）**：整夜排程因下列三雷空跑 → **DB 與 checkpoint 都被清空，從零重來**。目前 DB 只有
  **創 1:1 共 7 列**起跳（已驗 pipeline end-to-end：OCR→build_rows_auto→正規化→DB 正確）。
  **2026-06-15 早上找到真因（非額度，見雷⑤⑥）後 batch 1 已能穩定逐頁推進**。
  **只剩被退掉的 Haiku 備份** `c:/tmp/accs_gen_創1-11.haiku.bak.jsonl`（別當成品）。
  內容頁約 PDF **p46 起**（p1-45 前言，OCR 回 0 entries 正常）。
- **跑法**：`ingest_accs_genesis.py --book gen --pages 1-316 --engine sonnet --batch 1 --replace --resume`
  （**必 batch 1**；checkpoint 在 `c:/tmp/accs_gen_*.raw.jsonl`，逐頁寫；全頁完成寫 `.done`）。
  Windows 排程 **`ACCS_Gen_Resume`（每 2h）** 跑 `scripts/accs_resume.ps1`（已改 batch 1）；
  **排程＝唯一擁有者**（`MultipleInstances=IgnoreNew`），跑 direct run 時先 `Disable-ScheduledTask` 免撞同一 checkpoint，
  完成後再 `Enable`。一頁 ~1–2 分（node 冷啟動，慢但穩）。
- **接手第一件事**：看 DB（`accs_commentary` where book_code=gen）rows 有沒有在長；創 1-11 完成 → 跑創 12-50
  （PDF：`…創12-50.pdf`，OT II）。
- **⚠️ 2026-06-14 整夜空跑的真因（皆已修，別重蹈）**：
  ① **G:（Google Drive 串流碟）會卸載** → PDF 不可達；`accs_resume.ps1` 已加自我修復（偵測 G: 未掛載就跑
     `launch.bat` 等 60s）。② **編 `.ps1` 掉 UTF-8 BOM** → PowerShell 5.1 以 Big5 誤讀中文 → parse error 靜默失敗；
     改 .ps1 後務必存 **UTF-8 with BOM**。③ 排程 `DisallowStartIfOnBatteries=True` + 筆電在電池 → task 永久 "Queued"
     不執行；已改 `AllowStartIfOnBatteries`+`DontStopIfGoingOnBatteries`。④ **G: 串流碟逐頁 on-demand 抓雲端，
     長跑時 `render_page` 會無限卡死**（python 零 CPU、無 child、卡 2h）；`accs_resume.ps1` 已改**一次性複製 PDF
     到 `c:/tmp`（同 stem 以保 checkpoint 對得上）**、OCR 全程只讀本地檔。
  ⑤ **OCR 卡死的真因（一整夜誤判成「Max 額度乾」，其實不是）**：(a) 我自己加的
     `subprocess.CREATE_NEW_PROCESS_GROUP` flag 會改 `claude.cmd`→node 的 console/stdin 行為，**每個含圖請求都卡到
     300s 逾時**（即使 Max 回 `rate_limit status=allowed`）；移除 flag 後單頁秒回。(b) **多圖一次呼叫（batch≥2）也卡**
     ——~2MB 單行 stream-json 撐爆 CLI parser；**必 `--batch 1`**（一頁一呼叫）。逾時用 **Popen + `taskkill /F /T` 連孫殺**
     才能真退（但別加 PROCESS_GROUP flag）。診斷招式：`claude -p --model sonnet "OK"` 純文字若秒回＝Max 沒問題，
     問題在含圖請求本身。⑥ **單頁偶發逾時別 break 整輪**：batch 1 時一頁卡頓會停掉整本；已改**跳過該頁續跑、連續 3 次才退**。
  ⑦ `--replace` 曾在「本次 0 rows」時仍 delete → 清空全書；已修為「rows 為空就不刪不寫」（這就是這次資料被清的舊雷）。
- **2026-06-15 早上狀態**：找到真因後 **batch 1 已能穩定逐頁推進**；DB rows 從 7→33→持續長中。一頁 ~1–2 分（node 冷啟動）。
  接手只需看 DB rows 有沒有在長；要手動推就 `Disable-ScheduledTask` 後跑 direct（batch 1），完成寫 `.done` 再 `Enable`。
- **demo placeholder**：`seed_accs_genesis_demo.py`（公有領域示範）已不在庫；要清殘留用 `--delete`。

### B. /scripture「各教會傳統 canon」重構 — **已完成上架（C 工程）**
見下方「各傳統 canon 結構」整節。四傳統書序＋次經綠卡＋補編黃標＋canon-aware reader＋衣索匹亞教會秩序書 全上線。
**仍待**：① 8 卷衣索匹亞教會秩序書（徒遺/徒教/六法典）**只有結構與名稱、無經文內容**（需另找來源）。
② reader 端「補編真內嵌成母卷章」（但以理 13/14、詩篇151 顯示在母卷章序內，而非連到補編書頁）——目前是母卷章選單後方連結 + 補編頁標「屬於次經範圍」。③ 詩篇完整 versification 跨傳統對齊表（目前靠「同傳統同編號系統」+ 提示）。

---

## 各傳統 canon 結構（`bible_canon_books`，2026-06-14 建）

`/scripture` index 與 reader 依「所選 canon」呈現該傳統**自己的書序、第二正典、補編、書名**。

### 資料表 `bible_canon_books`
`canon, book_code, testament('ot'|'nt'), sort_order, is_deutero, chapter_count(覆寫;NULL=用bible_books),
name_override, abbr_override(傳統專屬書名), parent_code(補編所屬母卷), has_additions(母卷含補編),
section(新約子分類如「教會秩序書」)`。PK(canon,book_code)。RLS 公共讀。
- **單一來源 = `scripts/seed_canon_order.py`**（種 catholic/orthodox/syriac/ethiopian；冪等 upsert）。
  `database/bible-canon-order.sql` 只剩 schema（舊 catholic INSERT 已註解）。欄位 ALTER 用 Management API 加過。
- 端點 `server/api/scripture/canon-order.get.ts` 回 `{canon: [rows]}`；index/reader 各 `$fetch` 一次。

### 顏色語意（user 拍板）
- **綠卡 = 整卷第二正典**（多比/友弟德/智慧/德訓/巴錄/瑪加伯…，`is_deutero`）。
- **黃卡 = 含次經補編之正典書**（`has_additions`）：但以理（蘇撒納/貝耳與大龍/阿匝黎雅）、詩篇（詩151）、
  以斯帖（希臘增補）、巴錄（耶肋米亞書信）。**補編不出獨立書卡**（`parent_code` 指母卷 → index 跳過）。
- reader：補編卷（sus/bel/aza/ps2/epj）開啟時頂部橫幅「**屬於次經範圍**·為《母卷》補編」；母卷章選單後方列補編連結。

### 各傳統重點（卷數）
- **新教 66**：用 bible_books 預設（無此表 → fallback 和合本序）。
- **天主教 77**：思高/拉丁通行本序；7 整卷次經 interleaved（綠）；但/以斯帖/巴（黃，補編）。
- **東正教 82**：七十士序——**小先知在大先知前**、**公函在保羅書信前**（拜占庭）、詩151+默拿舍禱詞、4瑪加伯附錄。
  **厄斯德拉採 LXX 命名（name_override）**：1es=以斯拉A(Ἔσδρας Αʹ)、ezr=以斯拉上、neh=以斯拉下(Ἔσδρας Βʹ)。
- **敘利亞 72**：Peshitta——**新約 22 卷**（無 2彼/2-3約/猶/啟）。
- **衣索匹亞 94**：禧年書/以諾一書/巴錄四書併入舊約；**新約 35** = 27 + 「**教會秩序書**」子分類（`section`）8 卷：
  徒遺(十二使徒遺訓)/徒教(使徒教訓) + 六法典〔秩典(秩序典)/訓典(訓令典)/戒典(戒律典)/規典(規章典)/聖上(聖約前典)/聖下(聖約後典)〕。
  **codes**：e_didache/e_didasc/e_sinodos1-4/e_kidan1-2（bible_books 已建，**無經文內容**）。

### 書名政策（user 訂正）
**只有天主教用思高本書名**（`name_sigao`/`abbr_sigao`，見 database/bible-books-sigao.sql；注意亞=亞毛斯/匝=匝加利亞/
納=約納/瑪=瑪竇/拉=瑪拉基/若=若望 同字不同書陷阱）；**其餘所有傳統（新教/東正/敘利亞/衣索匹亞）一律和合本**。
例外：`name_override`（如東正教以斯拉A/上/下）優先於上述。

### canon-aware reader（內容差異）
`/scripture/[book]/[chapter]?canon=X`：依傳統挑預設對照版本（DB 有 33 版本：思高/Vulgate/LXX/Peshitta/
教會斯拉夫/亞美尼亞/科普特/俄文/Brenton…）。**同傳統欄位採同一編號系統**（天主教思高/Vulgate=七十士編號、
新教和合/希伯來=希伯來編號）→ 詩篇等編號差異自然呈現，**免脆弱的重對齊表**。詩篇頁有編號差異提示；nav 顯示傳統標籤。
CANON_PREFS / displayBookName / canonQS 等在 `[chapter].vue`。

### 相關檔案（canon 部分）
`database/{bible-canon-order,bible-books-sigao}.sql` · `scripts/seed_canon_order.py` ·
`server/api/scripture/canon-order.get.ts` · `pages/scripture/index.vue` · `pages/scripture/[book]/[chapter].vue`。

## See also
- [[scripture-fathers]] — 教父全集整卷翻譯/精修（/fathers）；ACCS 譯名決策同源
- [[scripture-canon]] / [[scripture-gnostic]] — 三表 N-欄 reader + 純函式 test-first 範式
- [[translation-glossary]] — 教父譯名主譯權威
- [[feedback_ocr_strategy]] — Gemini 預設、Haiku 一次一本
