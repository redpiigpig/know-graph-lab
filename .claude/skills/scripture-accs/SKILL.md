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

## 🧭 下個 session 接手清單（2026-06-25 晚更新）

> **2026-07-02 狀態快照**：exo ✅710 / lev ✅53 / **num ✅271 列（36 章齊、空 body 0、空 father 0）已 `.done`** 完成入庫。
> **deu ⏳ 0 列，未開始**——排程已重新啟用（Ready），會跳過出/利/民、等 Sonnet 5h 窗回血後自動跑申命記（Gemini 4 key credit **永久乾**，deu 只能靠 Sonnet）。
> — num 收尾始末：7/01 退避空 checkpoint 後由排程 Sonnet 逐頁重 OCR 至 95/96；最後 p.379 卡在 Sonnet 額度牆（Gemini 亦乾）。**由 Claude 直接判讀該頁**補 3 則（19:9 居普良《書信集》、19:11-22 概述、19:15 帕特留《解釋舊約與新約》）＋接回 p.378 ref 19:2（比德）跨頁截斷續文，手工寫進 checkpoint 正確頁序後 `--resume`（0 頁待 OCR）走 parser upsert + 寫 `.done`。
> **根因已修 ✅（2026-07-03）**：`ocr_batch_claude` 兩條「吞失敗成空頁」路徑已改 raise——(a) 非零退出即使 blob 不含 `rate_limit` 字串也 raise（不再 `return []`）；(b) 無 success result event（回應截斷）也 raise。只有模型明確回空陣列才記空頁。這就是 7/01 num 全空 & 7/03 deu 26–32 章 26 頁被誤記空頁的元凶。
> **deu 重 OCR 中（2026-07-03）**：deu 首輪假 `.done`（161 列但缺 2,3,26–32 章＝p.491–516 等 38 頁被誤記空）。已丟掉 38 空頁記錄＋刪 `.done`，背景迴圈 `c:/tmp/accs_deu_reocr.sh`（Sonnet）重 OCR 中；排程 `ACCS_OTIII_Resume` 暫時 Disabled 避免並行，deu 完成後記得重新 Enable（或本卷全完成就維持 Disabled）。
>
> **📌 num 待收尾（user 2026-07-02 指定「之後跟 deu 一起做」）**——7/02 抽查（p.339 內容全對、36 章齊、空 body/father 0）發現兩類：
> **①教父譯名同一人多寫法要收斂**（對齊 `/translation-glossary` 主譯再 UPDATE）：安波羅修/安博(Ambrose)、特土良/特士良(Tertullian)、拿先斯的格列高里/納西盎的貴格利(Naz. Gregory)、塞普勒斯的狄奧多勒/狄奧多雷(Theodoret)；另 father 欄雜訊 3 筆（「託區利羅名作品」「八經註釋集萃」「多儒」＝疑截斷自迦修多儒）。
> **②跨頁截斷續文未併回** 約十餘筆（例 5:6「…這句話是甚麼意思？聖」、7:89「…處理疑」、8:7「…蒙揀選事」）——比照創世記「續行併入」逐筆把下一頁頁首半句接回。兩道等 deu OCR 完一起跑（比照 Genesis 收尾）。

### A0. ACCS OT III（出/利/民/申）OCR — **OCR 中（排程 ACCS_OTIII_Resume，2026-06-25 起跑）🔴 接手關注**
- **來源**：合卷 PDF `古代基督信仰聖經註釋叢書2-5 出 利 民 申.pdf`（ACCS OT III＝出/利/民/申 四書，614 頁，
  已複製本地 `c:/tmp/古代基督信仰聖經註釋叢書2-5 出利民申.pdf`）。**四書一起跑**（user 2026-06-25 指定）。
- **🚨 頁界（已人工核定四書 title page，offset PDF=書頁+44，務必照用）**：目錄(PDF 11)書頁 出 1 / 利 229 / 民 289 / 申 385 / 附錄 479。
  → **exo PDF 45–272 · lev 273–332 · num 333–428 · deu 429–522**（45/273/333/429 各為該書標題頁、523=附錄）。
  **🚨 各書頁界絕不可越界**！四書 ref 都是「1:1…N:N」無書名，跨界會把下一本誤掛上一本（ref 無法分辨）。故**每書各自 --book + 頁界分開跑**。
- **跑法**：排程 `ACCS_OTIII_Resume`（每 **30 分**、battery-ok、IgnoreNew、ExecTimeLimit 6h）跑 `scripts/accs_resume_otiii.ps1`：
  依序 exo→lev→num→deu，各 `ingest_accs_genesis.py --book {code} --pages {range} --engine sonnet --batch 1 --resume`；
  某書沒寫 `.done`（rate-limit 中退）就停本輪、下次續同書；某書 `.done` 了就同輪接下一本。
  checkpoint `c:/tmp/accs_{code}_…出利民申.raw.jsonl`、log `scripts/logs/accs_otiii.log`、各書完成寫 `…raw.done`。
  **🚨 絕不可 --replace**（清光該 book_code）。dry-run 已驗 parse OK（PDF47→3 entries、auto 章路由）。
- **接手第一件事**：`Get-ScheduledTaskInfo ACCS_OTIII_Resume` + 各書 checkpoint 頁數
  （exo 228 / lev 60 / num 96 / deu 94 頁）有沒有在長。注意 ingest **每輪結束才 upsert**，跑一半時 DB 可能還是上輪數字，以 checkpoint 頁數為準。
  2026-06-25 起跑當下 Sonnet 5h 窗剛被創世記 ~60 次 Vision 燒乾→頭幾輪多 rate-limit 空跑，窗刷新才推進；~478 頁估數天。
  每書完成後比照創世記：驗章數/品質 → 跑 blank-father 救援（`accs_resolve_blank_fathers.py --book {code}` ＋視需要 footnote-aware Vision）。全卷完成後 `Disable-ScheduledTask ACCS_OTIII_Resume`。

### A. ACCS 創世記 OCR — **全書完成 ✅（創 1-50，2026-06-24）**
- **創 1-11 完成**：316/316 頁、698 列（67 總論+631 引文）。`.done`＝`c:/tmp/accs_gen_…創1-11.raw.done`；
  排程 `ACCS_Gen_Resume` **已 Disable**。
- **創 12-50 完成 ✅（2026-06-24）**：654/654 頁全 OCR、`…創12-50.raw.done` 已寫。排程 `ACCS_Gen2_Resume` **已 Disable**
  （比照 1-11 完成後收尾慣例）。內容頁到 PDF p.551 為止，p.552-654 為空白頁/索引（正確產 0 entries）。
  收尾跑法＝`Disable-ScheduledTask` 後跑 direct（batch 1）；rate-limit/網路 blip 用 `c:/tmp/accs_g2_loop.sh`
  迴圈重啟續傳（remaining 0 才停），最後一輪含 upsert 全本 1262 列。
- **全 Genesis DB 終態（book_code=gen）**：**1,960 列**（229 總論 + 1,731 引文）、**49 章**（**唯缺第 36 章**＝以掃族譜，
  ACCS OT II 本身無釋經，非漏 OCR；ch33/34/35 同樣稀疏 3/2/5 列）、90 位具名教父。
- **品質再稽核（2026-06-24 全書）全綠**：blank_body=0、bad_verse_range=0、簡體殘留=0、亂碼=0。
  視覺核對 p.549（創 50:17-20）與 DB 逐則吻合（敘利亞的厄弗冷/金口若望、節範圍、作品名皆對）。
- **本輪修正的教父譯名收斂**（對齊 `/translation-glossary` 主譯，已寫進 `FATHER_FIXES` + 補測試 + DB UPDATE 共 198 列）：
  奧利振→俄利根（5）；敘利亞人以法蓮→敘利亞的厄弗冷（139，OCR 草頭 蓮≠連）；
  亞歷山太/大的區利羅·西里爾·濟利祿→亞歷山卓的區利羅（39）；亞歷山太/大的革利免→亞歷山卓的革利免（14）；亞歷山太的斐羅→亞歷山卓的斐羅（1）。
- **blank-father 救援全清（2026-06-25）：121 → 0 ✅**。三段式：
  ① **續行併入**（`scripts/accs_resolve_blank_fathers.py`，純函式 `plan_blank_father_fixes` + pytest）：
     前列 comment 句中斷裂→併 body＋繼承 father，刪 46 來源碎片 = 45 則。
  ② **作品回填**：work_title 全書唯一對應某 father→補名 = 21 則。①②body 字數守恆、DB gen 1,960→**1,914**。
  ③ **footnote-aware Sonnet Vision**（user 拍板跑）：對殘留 54 render 該頁＋**前一頁**，依
     inline 粗體署名／頁末註腳來源碼（**FC/PG/CSEL/SC 冊號→作者**，例 FC 82=金口若望、FC 91=厄弗冷、
     CS 101=俄利根《論禱告》）／跨頁上文判定，50 high＋1 med＋字面/匿名補 3 = 54 全定（含
     2 個「body 只是截斷的教父名」直接依字面補、《埃及教父語錄》=Apophthegmata 匿名→佚名）。
  → **全 Genesis comment 100% 具名**（distinct_fathers 90；blank_father=0）。Vision proposals 存
     `c:/tmp/accs_father_proposals.jsonl`、備份 `c:/tmp/accs_gen_backup_20260625.json`。
- **終態稽核**：rows 1,914 / chs 49（缺 36 以掃族譜）/ blank_father 0 / blank_body 0 / bad_verse 0 /
  簡體 0 / body 405,730 字（全程零文字損失）。
- **🚨 鐵則（若日後重跑）**：跑 12-50 **絕不可加 `--replace`**！會刪光整個 book_code=gen（含創 1-11）。章號不重疊，直接 upsert 累加。
- **引擎**：**Sonnet**（`--engine sonnet`，Max OAuth）。Haiku 退兩次、Gemini key credit 乾。**必 `--batch 1`**（見雷⑤）。
- **跑法慣例**：單次 pass＝`accs_resume_g2.ps1`（排程用）；曾試 `accs_loop*.ps1` auto-relaunch 迴圈，但**detached loop process 會被系統反覆 reap 死掉**（不適合無人值守）→ **改用 OS 排程**（survives reboot/登出/session 切換）。
  **排程與 direct run 二擇一、別並行**（搶同一 checkpoint）。**換 session／離開電腦時靠排程自動跑**。
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
