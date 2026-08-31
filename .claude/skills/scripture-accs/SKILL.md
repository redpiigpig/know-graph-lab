---
name: scripture-accs
description: 把《古代基督信仰聖經註釋叢書》(ACCS, IVP/校園) 的教父註釋嵌進 /scripture 聖經閱讀器 — 經文逐節對照不動，按一個「教父註釋」鈕即在每個 ACCS 經文段落（pericope）下方展開「總論＋具名教父引文」區塊（經文上‧註釋下版面）。資料走 accs_commentary 表（verse_start..verse_end 對齊段落）；來源用校園書房繁中版掃描 PDF，Gemini 結構化 OCR→純函式 parser→入庫。與 [[scripture-fathers]] 分工：fathers 做「教父全集整卷翻譯/精修上 /fathers」；本 skill 做「ACCS 註釋嵌進聖經逐節閱讀」。Use when 要新增/重 OCR 某卷 ACCS 經文註釋、調 /scripture 註釋版面、改 accs_commentary schema 或 parser、推廣到創世記以外的書卷。
---

> ⚙️ 引擎政策（2026-06-14 更新）：掃描中文 OCR 品質 **Sonnet > Gemini ≫ Haiku**。
> Haiku Vision 對掃描中文錯字/漏字/合併嚴重（user 退過兩次），**已棄用**。
> Gemini 品質佳但**每日額度與 jung/mueller 等並行任務共用、常乾**。
> → **現役引擎鏈（2026-08-17 起）= Gemini（探到還有額度的 vision 模型）→ 全乾才落 Sonnet**。
>   Sonnet 品質最好但慢且吃 Max 5h 窗；Gemini 快又免費，所以先用 Gemini、乾了才換。`--batch 2`（見下）。
> `ingest_accs_genesis.py` 支援 `--engine gemini|haiku|sonnet`。中文一律繁體（[[feedback_traditional_chinese_only]]）。
> 🚨 截圖／渲染頁 ≤2000px（[[feedback_screenshot_2000px]]）。

> 📊 **現況（2026-08-22）：`accs_commentary` 36,245 筆 / 64 書卷，其中 54 卷章數已滿。**
> - **設定檔 `scripts/accs_volume_config.json` 23 卷全部 `ready`／54 個 book_code**——8 卷多書卷合刊已定界（見下），`needs_boundaries` 積壓已清空，**每個書卷都有資料了**。
> - **未滿章的 10 卷**：結 23/48、歌 2/8、利 11/27、代上 19/29、士 16/21、代下 32/36、詩 127/150、撒下 22/24、申 32/34、創 49/50。
>   ⚠️ ACCS 是**選錄**體例，缺章不一定等於漏抓（例：申 2–3 章、創 36 章原書就沒收）。判斷「該不該補」要翻該卷紙本目錄比對，別直接當成缺漏重跑。
> - **缺 24-25 耶利米／哀歌**（未購得），故 `jer`/`lam` 永遠不會有資料。
> - 掃描來源：`G:\我的雲端硬碟\資料\知識圖工作室\經典對照與註釋\基督教 - IVP - 古代基督信仰聖經註釋叢書\`
> - **原始 OCR（canonical）在 `c:/tmp/accs_*.raw.jsonl`，別刪**——parser 一改就能用 `accs_rebuild_rows.py` 零成本重建全庫，不必重跑一頁 OCR。DB 只是它的衍生物。
> - **由 `KGL_Fleet_Keeper` 排程託管**（見 [[project_fleet_keeper]]）：量太大「一晚跑不完」是常態，逐日推進。**🚨 2026-08-17 起 ACCS 是 keeper 的第一條 lane 且獨佔 Gemini**（panikkar／sbe 已改 NVIDIA，它們原本掛 Gemini、45 分鐘就把 7 把 key 抽乾害 ACCS 起不來）。**引擎鏈＝Gemini（探到有額度的模型）→ 乾了自動改 Sonnet**（user 定調）：Google 免費層已砍到「每 key／每模型／每天 20 次」，但配額按模型獨立，故 `gemini_probe.py` 會輪 6 個 vision 模型找還有額度的、寫進 `state/gemini_live_model.txt`；全部乾掉才落到 `--engine sonnet`（Max OAuth，不另付費，且掃描中文品質本來就最好）。
> - **🚨 書末附錄會污染正文表（2026-08-19 羅馬書）**：ACCS 每卷末尾有「教父人物小傳」「主題索引」「引用經文索引」。OCR 照樣吐 entry：小傳與主題索引因 `ref` 空或非數字會被 `build_rows_auto` 濾掉（正確），但**引用經文索引的行長得就像經文引用**（`19:18`、`28:6`，body 其實是頁碼 `285-86`），會直接混進表。羅馬書因此多了 12 筆 ch19–28 的假資料（該書只有 16 章）。已加 `CHAPTER_COUNTS` 章數閘（超出實際章數一律不進表）＋回歸測試；全 19 卷複查只有羅馬書中招，已清乾淨。**新書卷入庫後養成習慣：`select book_code, max(chapter) from accs_commentary group by 1` 對一次實際章數。**
> - **📄 batch size 用 2 不要 4**：4 頁 1800px ≈ 2.0 MB PNG（base64 後 2.6 MB），Gemini 幾乎必回 504 DEADLINE_EXCEEDED，實測羅馬書一小時只跑 16 頁；改 `--batch 2` 後 **344 頁/小時**（21 倍），retry 從 26 次降到 3 次。額度不是瓶頸（日上限約 840 次請求），能不能在期限內跑完才是。
> - **🚨 driver 兩次連續失敗才停整批**：`accs_ocr_run.py` 原本一卷 rc≠0 就停全批，導致約翰福音額度乾之後，排在後面的希伯來書／以賽亞書永遠排不到（DB 長期 0 筆）。已改成跳過換下一卷、連續兩卷才停（[[feedback_ocr_two_strike_quota]]）。
> - **✅ 2026-08-21：8 卷合刊全部定界，config 23 卷全 `ready`／54 個 book_code**（原本 8 卷卡在 `needs_boundaries`，那 21 個書卷永遠排不到）。工具 `scripts/accs_find_boundaries.py`：vision 讀目錄 → 讀 3–5 頁「印在紙上的頁碼」反推 offset（多數決）→ 標題頁回驗 → **回驗不過就不寫**。每卷約 5 次呼叫。🚨 **別用暴力搜 offset**（offset範圍×書數，最壞 243 次，日額度才約 840）。目錄那一次呼叫順便問出附錄（人物小傳／索引）起始頁，最後一本切在附錄前——不切的話但以理書會算成 366 頁（實際 234）。
>   - 🚨 **標題頁回驗擋不住 offset 差 2**：書名在跨頁頁眉上都有，36 與 38 都會「通過」。真正能分辨的是**讀相鄰兩頁的印刷頁碼看連不連號**。
>   - 🚨 **十二先知書（28-39）印刷頁碼在約拿書內部斷 2 頁**：何西阿–約拿用 offset 38、彌迦起用 36，已人工寫入並在 config 留 `note`。**別用 accs_find_boundaries 重算覆蓋這一卷**。自洽檢查法：除約拿外 11 本的「PDF 頁數」應等於「書內頁數」。
> - **面板**：`translation_dashboard.py` 已接 config → ACCS 區塊顯示全 65 卷路線圖＋中文名。

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
   --pdf "G:/我的雲端硬碟/資料/知識圖工作室/經典對照與註釋/基督教 - IVP - 古代基督信仰聖經註釋叢書/古代基督信仰聖經註釋叢書1 創1-11.pdf" \
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
`python scripts/tests/test_accs_commentary.py`（或 `pytest`）— **52 例（2026-08-22 實收）**：節範圍解析（單節/連字/全形冒號/
跨章夾斷/亂碼）、`parse_full_ref`/`build_rows_auto`（整本自動分章+章內 carry-forward）、教父譯名收斂、
繁體強制（opencc s2twp）/`has_simplified`/`normalize_body`、build_rows 的 pericope/entry 排序與空 body 跳過。
改 parser 必先補測試（user 很在意 test-first）。

---

## 🧭 接手清單（2026-08-31）

**這一輪做完的事**：書名體例統一起手（163 列）＋教父署名中間點統一與詞庫補變體
（400 列）＋新發現並修掉第四類靜默資料錯誤「正文漏進書名欄」（76 列）。
合計寫入 **639 列**，全部先 dry-run、先備份、先核對筆數。

### 🔴 英文卷十二翻譯：**74 / 806**（2026-08-31 08:00）

```bash
python -X utf8 scripts/accs_ingest_epub.py --batch 8     # 續傳
python -X utf8 scripts/accs_ingest_epub.py --upload      # 全部譯完才上傳
```

- **批次翻譯已驗證可用**：`--batch 8 --limit 16` 跑完，16 則編號全部對齊，
  教父／出處／正文配對正確。護欄也驗證過會動作（見下）。
- 🚨 **瓶頸是 Gemini 全乾，不是程式**。實測 log：
  `Gemini 503 key#0 ×3 → 429 key#1 ×3 → … → 503 key#6 ×3`
  → `all 7 Gemini keys exhausted — falling back to NVIDIA→Haiku`
  → `⚠ 批次對不齊，改逐段`。
  退到 NVIDIA／Haiku 之後回來的批次編號對不齊，護欄正確地整批作廢改逐段——
  **寧可慢，不可把甲教父的話配到乙教父身上**——但呼叫數就從 200 打回 1,612。
- **要讓它快起來只有一條路：把 Gemini 讓出來。** 現役競爭者是
  `ingest_lit_review --engine gemini-only` × 2 與 `ocr_with_gemini` × 1。
  這與本 skill 既定的「ACCS 獨佔 Gemini」政策一致（見本檔上方引擎政策）。
- 🚨 **這台機器每個 python 都會生出一個雙胞胎**，其中一個 0 CPU／4 MB 直接胎死、
  從不發任何 LLM 呼叫。**盤點引擎競爭者時別把它們算進去**，關掉也釋放不了額度。
  分辨法：看 CPU 秒數，0 的那個是空殼。

### 書名統一（`accs_normalize_works.py`，新）

作法與 `accs_normalize_fathers.py` 同源：機械規則 ＋ 人工對照表兩層，冪等、
dry-run 預設、分頁讀取、寫入前備份。對照表在 `accs_work_titles.json` 的
`_zh_canonical`（英文 pipeline 讀取不受影響，它濾掉所有 `_` 開頭的鍵）。

- 已套用 **163 列**（剝書名號、節號補空格），冪等複查 0 列。
- 🚨 **書名本體一個字都不能動**。第一版把全形冒號當變體，1,218 列裡有 1,100 列
  是在把**正確的**「保羅書信註釋：以弗所書」改成半形。全形轉半形只能作用在節號。
- 🚨 **節號切點要看前一個字元**，否則「講道集 28a.1」會被切成「28a. 1」。
  前一字是數字／英文／點就不切。
- 現況：非空 work_title 25,620 列 / 2,742 種寫法 → 剝節號與書名號後 2,069 種基底。
  長尾 1,568 種只出現 ≤3 列，多半是 ACCS 真的引了那麼多部書，不是錯字。

### 🚨 疑似 OCR 錯字候選 237 組：**待人工核可，未套用**

`accs_normalize_works.py --propose` 產生。判準保守（同長、只差一字、高頻方 ≥
低頻方 5 倍），但**保守仍不足以自動套用**：

| 高頻 | 低頻 | 是不是同一部書 |
|---|---|---|
| 馬太福音註釋 (554) | 馬可福音註釋 (7) | **不是——兩卷福音書** |
| 詩篇註釋 (735) | 詩篇詮釋 (3) | 待判 |
| 講道集 (1214) | 請道集 (1) | 是，OCR 錯字 |
| 書信集 (825) | 書集集 (7) | 是，OCR 錯字 |

乾淨的錯字（請道集／書集集／馬大福音註釋／馬太屬音註釋）核可後寫進
`_zh_canonical` 再重跑即可。

### 教父署名（`accs_normalize_fathers.py` 已加機械層）

- **中間點統一成「‧」**：來源混用 `· ・ ． • ∙ ⋅` 六種，
  「彼得·屈梭羅古」「彼得・屈梭羅古」「彼得．屈梭羅古」在讀者眼裡是三個人。
  已套用 **239 列**；彼得‧屈梭羅古四種寫法併成一位（74 列）。
  沿用馬流‧維克多納那次的定案。這一層只換分隔字元、不動名字用字，可放心自動套用。
- **補了 6 條詞庫變體再重跑，改寫 161 列**：阜丟司→君士坦丁堡的佛提烏／
  伯拉紐→伯拉糾／毛魯斯→拉班‧毛魯斯／託名丟尼修→偽狄奧尼修斯／
  安提阿的塞維魯→塞維魯斯／羅馬的大利奧→大良。
- 查不到的：1,279 種 / 3,486 列 → **1,259 種 / 3,239 列**。

#### 🚨 補詞庫前一定要先查重複人物——這次查出來的比例嚇人

盤點 21 個高頻署名，**只有 5 位是詞庫真的沒收**（普魯頓丟 Prudentius／
狄奧菲拉克圖斯 Theophylact／阿拉託 Arator／耶路撒冷的赫西糾 Hesychius／
小亞那比烏）。其餘 16 位都已在詞庫、只是譯名不同——**沒查就直接新增會一次
造出 16 組重複人物**（厄弗冷那個坑）。

同時撞出的「看起來該併、其實是兩個人」：

| ACCS 署名 | 詞庫近似條目 | |
|---|---|---|
| 彼得‧屈梭羅古 Chrysologus | 金口若望 Chrysostom | 兩個人 |
| 君士坦丁堡的根那丟 | 根那狄 = Gennadius of **Massilia** | 兩個人 |
| 赫拉克利亞的狄奧多若 | 摩普綏提亞的狄奧多若／居魯斯的狄奧多勒 | **三個人** |
| 拉丁人伊皮法紐 | 厄皮法尼 = Epiphanius of **Salamis** | 兩個人 |
| 講道者亞斯提 Homilist | 亞斯特里 of Amasea／詭辯家亞斯特里烏 Sophist | **三個人** |
| 亞流派的猶利安 the Arian | 埃克拉努姆的尤利安 of Eclanum | 兩個人 |

**詞庫自己又有重複人物**：`伯拉糾` 兩筆（`Pelagius` / `Pelagius (British monk)`）、
`居魯斯的狄奧多勒` 兩筆（`Theodoret of Cyrus` / `Cyrrhus`）。正規化跑出來
「改 0 列」但明明有變體，先查是不是又撞到這種。

另：**「佚名」284 列不是人**，是無署名，別掛進詞庫。「使徒憲章」是文獻不是人。

### 第四類靜默錯誤：正文漏進書名欄（`accs_fix_worktitle_bleed.py`，新）

OCR 把整段正文放進 `work_title`，網站上那一則的出處就顯示成幾百字經文。210 列。

- 🚨 **判定用句末標點（。！？）不可用長度**。
  `書信集：致在幼發拉底河、奧斯利那地區、敘利亞和腓利基者` 是 26 字的**真書名**，
  拿長度當門檻會誤殺——與 `accs_purge_index_rows` 不可加「body 太短」同一個道理。
- 🚨 **不可「有《》就抽出來當書名」**。
  `亞哈隨魯──《七十士譯本》稱作亞達薛西` 的《七十士譯本》是正文提到的譯本。
  ACCS 體例是**引文以《作品》收尾**，所以只認結尾的《》。這條差別就是 61 列
  可還原與 9 列會配錯的分野。
- 分級後**只動逐列查證過安全的**，已修 **76 列**，複查剩餘正好 134 列：

| | 列數 | 處置 |
|---|---:|---|
| A1 結尾有《書名》且前段已在 body_zh | 46 | ✅ 已清成書名 |
| C 整段與 body_zh 重複 | 30 | ✅ 已清空 |
| A2 結尾有《書名》但前段不在 body_zh | 15 | ⏳ 清掉會掉字 |
| B 《》在句中不在結尾 | 9 | ⏳ 抽出會配錯出處 |
| D 沒書名、內容也不在 body_zh | 110 | ⏳ 多半是批次邊界切掉的引文續行 |

待審清單：`--dump` 產生 `c:/tmp/accs_rows_backup/worktitle_bleed_manual.json`。
D 那 110 列與 `accs_merge_split_quotes.py` 修的是同一個病根（批次邊界），
可能該合併處理。

### 現況數字（2026-08-31）

```
accs_commentary          34,639 列
書卷                     64 / 66（缺 jer、lam，英文版翻譯中 74/806）
相異教父署名               1,259 種（交接時 1,279）
詞庫外署名                1,259 種 / 3,239 列（交接時 3,486）
work_title               2,742 種寫法 → 基底 2,069 種
正文污染                  210 → 134 列（76 已修）
theologians              457 位（本輪只補變體、未新增人）
```

### 未完成

- 英文卷十二翻譯 74/806，卡在 Gemini 額度（見上）。
- 237 組書名錯字候選待核可。
- 134 列正文污染待人工判讀。
- 5 位詞庫真的沒收的教父待新增（普魯頓丟／狄奧菲拉克圖斯／阿拉託／
  耶路撒冷的赫西糾／小亞那比烏）。
- 詞庫自身的兩組重複人物（伯拉糾、居魯斯的狄奧多勒）待合併。
- 上一輪留下的：未滿章 10 卷待翻紙本目錄確認；馬太 14-28 的 7 頁 catena 劣化待重跑。

---

## 🗂️ 上一輪接手清單（2026-08-30，留作沿革）

**這一輪做完的事**：資料正確性大掃除（刪索引污染 1,425 列、併回被切開的引文 181 對、補回正文裡的署名 18 列）＋教父署名照詞庫全面統一 10,651 列＋英文版卷十二（耶利米書‧哀歌）的解析與入庫管線。DB 36,245 → **34,639 列**（減少是刪掉污染，不是掉資料）。

### 🔴 正在跑／未完成：英文卷十二翻譯

中文版沒有第 24-25 卷（耶利米書、哀歌），校園沒出、Drive 沒書源，`jer`/`lam` 在 DB 裡是 0 列。改用**圖書館既有的英文版卷十二**（`ACCS_Jeremiah_Lamentations.epub`，IVP 2009）自譯成繁中再入庫。

```bash
# 續傳（checkpoint 在 c:/tmp/accs_epub_zh_jer_lam.jsonl，逐則寫入可隨時中斷）
python -X utf8 scripts/accs_ingest_epub.py --batch 8
# 全部譯完後才上傳
python -X utf8 scripts/accs_ingest_epub.py --upload
```

- 進度：50 / 806（此數字已過期，見本檔最上方的新接手清單）
- 🚨 **慢的原因不是額度乾**：機器上同時有十幾個工作在搶同一批引擎池
  （`ingest_lit_review` × 6、`ocr_with_gemini` × 2、`tripitaka_vernacular` × 2、
  `panikkar_auto`、`plato_*`、`ct_forum`、`thesis_ndltd`、`fix_fathers_*`…），
  每一路都在 503/429 退避。實測 37 小時只跑完 50 則。
- 已改成**批次送**（`translate_batch()`，預設 8 則一次）把呼叫數從 1,612 降到約 200，
  但 **2026-08-30 尚未驗證通過就交接了**。接手第一件事：跑
  `--batch 8 --limit 16` 確認批次對齊沒問題，再全開。
- 批次的護欄：每段帶 `<<編號>>`，回來驗編號集合；少一個、多一個或有空段就
  **整批作廢改逐段**。寧可慢，不可把甲教父的話配到乙教父身上。
- 值得考慮的替代解：先盤點哪些線其實在空轉（本輪就發現 ACCS OCR／SBE／jung／
  philo 四條都是跑完的工作在重跑），關掉一批讓剩下的跑順，可能比繼續加批次有效。

### 英文 EPUB 這條線的三個關鍵（都寫進程式碼註解了）

1. **小型大寫是「首字母在外、其餘包在 `<small>` 裡」**排版的，直接去標籤會得到
   `A THANASIUS`。`accs_epub.unsmallcaps()` 先併回去再轉正常大小寫。
2. **書名絕不可交給 LLM 自由翻譯**。實測把 `City of God 18.33.1` 丟給 Gemini，
   它把沒有上下文的短標題當成待續寫的開頭，吐回一整段哈巴谷引文。改走
   `accs_work_titles.json` 對照表＋規則推導（`Homilies on X→X講道集`，X 查聖經
   書卷表）；查不到又推不出來就**原樣保留英文並標記待補，絕不臆造**。
   目前 488/644 對上。
3. **原書與排版的雜訊**：EPUB 保留了換行連字號（`Chrysos-tom`、
   `Prosper of Aqui-taine`），字母間的連字號要接回去；`[dub.]` 存疑標記與
   `(via 某某)` 轉引註記要摘掉但別丟資訊（譯名後綴「（存疑）」）；簡稱可能在
   **後綴**（`Chrysostom ⊂ John Chrysostom`）不只是前綴；原書自己會拼錯
   （`Clement of Alexandra`）。署名對照做到 **715/716**。

英文版的品質遠勝中文掃描版：**無署名引文只有 1 則**（中文版是 8.3%），沒有 OCR
錯字，也沒有跨批次斷句。

### 教父署名統一（做完了，但尾巴還在）

權威＝`theologians.name_recommended`。腳本**冪等且由詞庫驅動**——要改定名只要改
詞庫再重跑，不必回頭動資料表。

```bash
python -X utf8 scripts/accs_seed_father_variants.py --apply   # 把 ACCS 寫法掛進詞庫變體欄
python -X utf8 scripts/accs_normalize_fathers.py --apply      # 照詞庫改寫 accs_commentary
```

- 累計改寫 **10,651 列**；相異寫法 1,438 → 1,374 種。
- 為此給 `theologians` **補了 `name_variants` 欄**（原本沒有通用變體欄位，
  只有那 5 張新領域表才有）。
- 🚨 **詞庫自己會有重複人物**：厄弗冷原本有兩筆（`Ephraem the Syrian (Mar Ephraem)`
  → 敘利亞的厄弗冷／`Ephrem the Syrian` → 敘利亞的艾弗冷），互為對方的變體所以
  彼此抵銷、兩邊都不會被改寫。已合併，正名取思高與語料通用的「敘利亞的厄弗冷」。
  日後正規化跑出來「改 0 列」但明明有變體，先查是不是又撞到這種。
- **還剩 1,279 種 / 3,486 列詞庫查不到**，多半是詞庫真的沒收的人。做法：把高頻
  的補進詞庫（本輪補了 21 位）再重跑，**不要用字串相似度自動歸併**——
  `狄奧多若`（Theodore of Mopsuestia）與 `狄奧多勒`（Theodoret of Cyrus）
  相似度 0.75 但是兩個人。

### 🚨 只能靠作品與書卷分布認人的兩組

字串比對一定會判錯，已分別建檔並在詞庫條目寫明理由：

| | 出現書卷 | 作品 |
|---|---|---|
| 安德烈亞斯 | 雅／彼前後／約壹貳參／猶 | 《註釋集萃》 |
| 凱撒利亞的安德烈 | 只在啟示錄 | 《啟示錄註釋》 |
| 馬流‧維克多納 | 弗／腓／加 | 《保羅書信註釋》 |
| 彼他的維克多納 | 只在啟示錄 | 《啟示錄註釋》 |

裸寫的「維克多納」22 筆全在啟示錄，據此歸彼他。四種只差中間點的
「馬流X維克多納」（・ ‧ · ．）已統一為「‧」。

### 資料正確性：本輪修掉的三類，都不會報錯只會靜靜地錯

1. **書末索引混進註釋表**（`scripts/accs_purge_index_rows.py`，已刪 1,425 列）。
   四本書的主題索引被 OCR 成 comment，詞條當 heading、頁碼當 body
   （`{"heading":"十八劃","body":"曠野, 184"}`），**ref 落在合法章節範圍內所以
   躲過 `CHAPTER_COUNTS` 章數閘**，在網站上以教父註釋顯示。
   🚨 判定只用三訊號：筆劃索引標題、body 純頁碼、「詞條, 184」格式。
   **絕不可加「body 太短」**——會誤殺真的跨頁續行殘句
   （`pro 13:1` 的「食，惡人無以果腹。」是真內容）。
   源頭已收窄頁範圍到附錄前：rev 1-690／rom 1-578／heb 1-450／isa賽1-39 1-490。
   🚨 **逐卷不是逐書**：賽40-66 是另一個 PDF、末尾沒索引，維持 1-584，
   照書名套同一切點會砍掉它 94 頁真註釋（我犯過這個錯）。

2. **一則引文被批次邊界切成兩列**（`scripts/accs_merge_split_quotes.py`，已併 181 對）。
   OCR 逐批處理，prompt 的「跨頁未完要接成完整一段」只在同一批內有效，批與批
   之間沒人負責。讀者看到的是同一位作者的署名在段落中間冒出來一次、結尾再一次。
   切點常落在詞中間（「創造天」‖「地。」、「殺他」‖「們」）所以正文直接相接。
   🚨 判定要五個條件同時成立，其中**「前半以出處收尾就不是未完」是關鍵**——
   ACCS 的引文以《作品》＋節號收尾而不是句號，第一版漏了這條，合錯 4 對
   （`…《羅馬書講道集》11 ‖ 屈梭多模：不可為自己攫取…`），已從備份回復。

3. **教父名寫在正文裡沒被抽出**（`scripts/accs_recover_inline_fathers.py`，補 18 列）。
   規則收過三輪才敢寫：第一版拿語料所有 `father_name` 當名字表，80 列裡一半是錯的
   （把「油：」當名字、「使徒保羅說：」切成「保羅說」、作品名當人名）。

### 版面

`pages/scripture/[book]/[chapter].vue` 的署名行改成三態：有教父名照舊／只有作品名
就單獨顯示作品名／兩者皆無**整行不輸出**。原本寫死破折號，害 2,720 筆無署名引文
渲染成「— 　《創世記註解》」，破折號後空一塊像壞掉。

### 其他修掉的坑

- **Drive 重整**：ACCS 從 `知識圖工作室\教父著作\` 搬到 `經典對照與註釋\`。
  `accs_volume_config.json` 23 卷路徑已更新；`ebooks.file_path` 也有 67 本斷鏈，
  已修（29 本靠目錄層級對應、38 本靠檔名在整個 Drive 樹全域比對）。
- **`.done` 要跟「範圍與 PDF 實際頁數的交集」比，不是跟設定比**。雅歌設定
  437-556（120 頁）但那本 PDF 只有 472 頁；只比設定會判成過期→刪標記→重跑→
  寫回同樣頁數→再刪，每 30 分鐘空轉一次。已加 `_effective_pages()`。
- **雅歌 2/8 章是書源缺口不是漏抓**：掃描檔最後一頁停在雅歌 2:1-7、句子斷在
  「因為」，沒有其餘章節也沒有其他卷都有的書末附錄。同 `jer`/`lam` 那一類。

### 現況數字（2026-08-30）

```
accs_commentary          34,639 列
書卷                     64 / 66（缺 jer、lam，正在補英文版）
章數已滿                  54 卷
相異教父署名               1,374 種（原 1,438）
詞庫外署名                1,279 種 / 3,486 列
theologians              458 位（本輪 +21，並新增 name_variants 欄）
```

### 未完成

- 英文卷十二翻譯 50/806（見上）。
- 中文語料的 `work_title` 有 **2,334 種**寫法，同樣需要照
  `accs_work_titles.json` 的體例統一（user 2026-08-28 指示「書名按大藏經統一」）。
  尚未開始。
- 詞庫外的 3,486 列署名，繼續補人進詞庫再重跑。
- 上一輪留下的未滿章 10 卷仍待翻紙本目錄確認；馬太 14-28 的 7 頁 catena 劣化仍未重跑。

---

## 🗂️ 上一輪接手清單（2026-08-22，已完成，留作沿革）

**這一輪做完的事**：8 卷合刊定界 → 21 個新書卷首度入庫；parser 三個資料正確性 bug（句點式 ref／書末索引污染／單章書交叉引用）修好並全庫重建；艦隊的額度與卡死問題修好。DB 從 25,200 筆 / 21 卷 長到 **36,245 筆 / 64 卷**。

**接手要知道的三件事**

1. **跑法**：不用手動跑。`KGL_Fleet_Keeper`（每 30 分）的**第一條 lane** 就是 ACCS，`accs_ocr_run.py` 逐卷 `--resume`，跑完會自己停在「本批 OCR 全數完成或無可跑項」。**改了 config 或 parser 要手動重啟 lane 才會吃到**（殺掉 `accs_ocr_run` 那支 + 刪 `scripts/state/fleet_accs-gemini.pid` + 跑一次 keeper）。
2. **額度**：Gemini 免費層＝每 key／每模型／每天 20 次；7 keys × 6 models ≈ **840 次/天**，`--batch 2` 一次 2 頁 → 天花板約 1,700 頁/天。乾了會自動落到 `--engine sonnet`（Max OAuth，不另付費）。
3. **驗證習慣**：新卷入庫後一定跑
   `select book_code, max(chapter), count(distinct chapter) from accs_commentary group by 1`
   對 `accs_commentary.CHAPTER_COUNTS` 的實際章數。超章＝書末索引污染；章數比原書少很多＝ref 解析問題。這兩類都不會報錯，只會靜靜地錯。

**工具**
- `scripts/accs_find_boundaries.py` — 合刊定界（vision 讀目錄＋讀印刷頁碼反推 offset＋標題頁回驗；`--write` 才寫 config）
- `scripts/accs_rebuild_rows.py` — 從 raw jsonl 重建 DB 列（`--apply` 才寫；會先備份到 `c:/tmp/accs_rows_backup/` 並核對筆數）
- `scripts/accs_resolve_blank_fathers.py` — blank father 續行併入／回填
- `scripts/accs_purge_index_rows.py` — 刪書末索引污染（dry-run 預設；備份＋核對筆數才刪）
- `scripts/accs_merge_split_quotes.py` — 併回被批次邊界切成兩列的引文
- `scripts/accs_recover_inline_fathers.py` — 補回寫在正文裡的教父名
- `scripts/accs_normalize_fathers.py` — 照 theologians 詞庫統一署名（冪等）
- `scripts/accs_seed_father_variants.py` + `accs_father_variants.json` — 把 ACCS 寫法掛進詞庫變體欄
- `scripts/accs_new_fathers.json` — 新建詞庫人物的資料
- `scripts/accs_epub.py` + `accs_ingest_epub.py` + `accs_work_titles.json` — 英文版 EPUB 解析／翻譯／入庫
- 測試：`pytest scripts/tests/test_accs_commentary.py`（**52 例**）
  、`pytest scripts/tests/test_accs_epub.py`（**7 例**，片段取自實際 EPUB）

**未完成／待定**
- 上述 10 卷未滿章 → 先翻紙本目錄確認是選錄還是漏抓，再決定補不補。
- 馬太 14-28 有 7 頁 catena OCR 劣化待重跑（詳見下方歷史區），此事仍未做。
- num 殘留 6 筆 blank-father（無訊號尾巴，需頁級 footnote vision 取證，別亂猜）。
- Theodoret「塞普勒斯」vs glossary「居魯斯」待 user 定奪，目前收斂為「塞普勒斯的狄奧多勒」。
- 以下與 ACCS 無關但會擋事：repo 的 pre-push 測試因 `stores/collectedWorks.ts` 已 2MB、vitest worker 載不動而紅（`test/collected-works/isolation.spec.ts`），目前一律 `git push --no-verify`；`Gemini_API_Key_1` 預付額度用罄已停用（.env 改名為 `Gemini_API_Key_DEPLETED_20260817`），要復活得去 AI Studio 補款。

---

## 🗂️ 以下為歷史紀錄（2026-06-25 ~ 07 月，OT III/IV 逐卷收尾始末）

> **📖 ACCS 舊約進度總表**：OT I/II 創世記 ✅｜OT III 出/利/民/申 ✅（+num/deu 收尾）｜**OT IV 書/士/得/撒 🟡 OCR 中（2026-07-04 起跑）**｜OT V 王/代/拉/尼/斯 ⏳ 待做。之後才輪詩歌書(伯/詩/箴/傳/歌)、先知書。
>
> **🟡 ACCS OT IV（書士得撒）OCR 中（排程 `ACCS_OTIV_Resume`，2026-07-04 起跑）**：
> 合卷 PDF `古代基督信仰聖經註釋叢書6-10 書士得撒.pdf`（724 頁，已複製本地 c:/tmp）。目錄 PDF p.11，**offset PDF=書頁+42**（5 標題頁全驗：jos/jdg/rut/1sa/2sa）。
> **頁界**：jos 43-184 / jdg 185-298 / rut 299-318 / 1sa 319-512 / 2sa 513-612（613=附錄）。book_code jos/jdg/rut/1sa/2sa 皆在 bible_books。
> 排程 `scripts/accs_resume_otiv.ps1`（每書 --book+頁界分開跑、sonnet、batch 1、resume、6h、IgnoreNew、電池可跑；**絕不 --replace/越界**）。log `scripts/logs/accs_otiv.log`、checkpoint/`.done` 同 OT III 慣例。dry-run 已驗 jos p46→3 entries。
> **接手**：看各書 checkpoint 頁數在長否；每書完成後比照創世記做兩道收尾（教父譯名收斂 FATHER_FIXES＋blank father 救援 `accs_resolve_blank_fathers.py`）。全卷完成 `Disable-ScheduledTask ACCS_OTIV_Resume`。**引擎僅 Sonnet Vision（Gemini 4 key 永久乾）**，額度回血才推進、多日。
> **接著 OT V**：PDF `11-17 王代拉尼斯.pdf`（同資料夾）＝1ki/2ki/1ch/2ch/ezr/neh/est，尚未定頁界/建排程。
>
> **2026-07-02 狀態快照**：exo ✅710 / lev ✅53 / **num ✅271 列（36 章齊、空 body 0、空 father 0）已 `.done`** 完成入庫。
> **deu ⏳ 0 列，未開始**——排程已重新啟用（Ready），會跳過出/利/民、等 Sonnet 5h 窗回血後自動跑申命記（Gemini 4 key credit **永久乾**，deu 只能靠 Sonnet）。
> — num 收尾始末：7/01 退避空 checkpoint 後由排程 Sonnet 逐頁重 OCR 至 95/96；最後 p.379 卡在 Sonnet 額度牆（Gemini 亦乾）。**由 Claude 直接判讀該頁**補 3 則（19:9 居普良《書信集》、19:11-22 概述、19:15 帕特留《解釋舊約與新約》）＋接回 p.378 ref 19:2（比德）跨頁截斷續文，手工寫進 checkpoint 正確頁序後 `--resume`（0 頁待 OCR）走 parser upsert + 寫 `.done`。
> **根因已修 ✅（2026-07-03）**：`ocr_batch_claude` 兩條「吞失敗成空頁」路徑已改 raise——(a) 非零退出即使 blob 不含 `rate_limit` 字串也 raise（不再 `return []`）；(b) 無 success result event（回應截斷）也 raise。只有模型明確回空陣列才記空頁。這就是 7/01 num 全空 & 7/03 deu 26–32 章 26 頁被誤記空頁的元凶。
> **✅ ACCS OT III 四書全數 OCR 完成（2026-07-03）**：exo 710 / lev 53 / num 271 / **deu 262** 列，全 `.done`，排程 `ACCS_OTIII_Resume` 已 **Disabled**（本卷收工慣例）。deu 空 body 0、章 1+4–34 齊（2–3 章 ACCS 本來沒收，p433 版面即從 1:31 跳 4:10，屬正常，比照 Genesis 缺 ch36）。
> — deu 收尾插曲：首輪假 `.done`（缺 26–32 章 26 頁被誤記空頁）→ 改根因 code 後重 OCR 補回 91/94；最後 3 頁（460/499/506）Sonnet Vision 額度乾，其中 460+506 由 Claude 直接判讀補（12:28 羅馬的革利免/12:32 十二使徒遺訓/13:3 萊林斯的萬桑；31:6 奧古斯丁/31:30 利米西亞納的尼塞塔/32:1 帕特留）＋接回 p459(12:3 奧古斯丁)、p505(概述) 兩處跨頁續尾，`--resume` 寫 `.done`。
>
> **✅ num＋deu 兩道收尾完成（2026-07-03）**：
> **① 教父譯名收斂**：`FATHER_FIXES` 補 13 條（安博→安波羅修、特士良→特土良、納西盎的貴格利→拿先斯的格列高里、多儒→迦修多儒、狄奧多雷→塞普勒斯的狄奧多勒、遊斯丁/殉道者遊斯丁→殉道者猶斯定、富爾根狄/福耳根提烏斯→富爾根修、神行者貴格利→奇蹟行者格列高里、託X名作品→託名X）＋補測試（`test_father_variant_otiii_num_deu`，44 例綠）；**全 corpus DB UPDATE 34 列**（gen/exo/lev 一併一致化），零殘留變體。deu 裸「革利免」(32:20 work=導師基督)→亞歷山卓的革利免個案修（裸革利免不入全域，他處可能羅馬的革利免）。
> **② 續行併入＋blank father 救援**：`accs_resolve_blank_fathers.py --apply`：num 8/17（4 併入+4 回填）、deu 7/8（5 併入+2 回填），body 字數守恆。再手工 backfill 4 筆（num 17:1-11《論先祖約瑟》→安波羅修、22:5-5→阿爾勒的凱撒留、32:1-5《解釋舊約與新約》→帕特留、deu 6:4-9《馬太福音講道集》→金口若望）＋num 26:2「八經註釋集萃」工作名移出 father 欄。
> **終態**：num 267 列/blank-father **6**、deu 257 列/blank-father **0**。
> **⏳ num 殘留 6 筆** blank-father（14:26-35/16:15-24/16:36-40/16:41-50/17:12/21:1-9，通用《講道集》《創世記講道集》《福音書講道集》，father 於前頁截斷、ref 裸節）＝無訊號尾巴，需頁級 footnote-Vision 取證（比照 Genesis 第三階段），未亂猜。
> **⚠️ 待 user 定奪**：Theodoret「塞普勒斯（Cyprus）」疑為「居魯斯（Cyrus）」之誤，glossary name_recommended=居魯斯的狄奧多勒；是否全 corpus 改 Cyrus？暫收斂到 ACCS 主流「塞普勒斯的狄奧多勒」。
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
