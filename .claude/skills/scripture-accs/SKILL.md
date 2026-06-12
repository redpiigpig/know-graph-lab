---
name: scripture-accs
description: 把《古代基督信仰聖經註釋叢書》(ACCS, IVP/校園) 的教父註釋嵌進 /scripture 聖經閱讀器 — 經文逐節對照不動，按一個「教父註釋」鈕即在每個 ACCS 經文段落（pericope）下方展開「總論＋具名教父引文」區塊（經文上‧註釋下版面）。資料走 accs_commentary 表（verse_start..verse_end 對齊段落）；來源用校園書房繁中版掃描 PDF，Gemini 結構化 OCR→純函式 parser→入庫。與 [[scripture-fathers]] 分工：fathers 做「教父全集整卷翻譯/精修上 /fathers」；本 skill 做「ACCS 註釋嵌進聖經逐節閱讀」。Use when 要新增/重 OCR 某卷 ACCS 經文註釋、調 /scripture 註釋版面、改 accs_commentary schema 或 parser、推廣到創世記以外的書卷。
---

> ⚙️ 引擎政策：OCR 走 **Gemini Vision（主）→ Haiku Vision（明確下令才開、一次一本）**，2-strike 429 退出（[[feedback_ocr_strategy]] / [[feedback_ocr_two_strike_quota]]）。中文一律繁體（[[feedback_traditional_chinese_only]]）。
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
`python scripts/tests/test_accs_commentary.py`（或 `pytest`）— 19 例：節範圍解析（單節/連字/全形冒號/
跨章夾斷/亂碼）、教父譯名收斂、build_rows 的 pericope/entry 排序與空 body 跳過。改 parser 必先補測試。

## 現況（2026-06-12）
- ✅ schema / parser+測試 / API / reader UI（toggle + 經文上註釋下）/ ingest 腳本 全部到位、build 綠。
- ⏳ **創世記 ch1 真實 ACCS 內容尚未 OCR**：當下 Gemini 配額 429（prepayment depleted）。先用
  `scripts/seed_accs_genesis_demo.py` 灌了 **公有領域示範 placeholder**（我自寫的繁中摘要，非校園原文，
  source_vol 標「（公有領域示範…）」）讓版面可審。**Gemini 配額回復（台灣 ~15:00）或 user 下令開 Haiku Vision 後**，
  跑 ingest_accs_genesis.py 取代之；取代前先 `seed_accs_genesis_demo.py --delete` 清掉示範列。
- 🔜 待 user 看過版面 → 推廣：創 1-11 全章 → 創 12-50 → 其他書卷（每卷 PDF 在同一 27 冊 folder）。

## See also
- [[scripture-fathers]] — 教父全集整卷翻譯/精修（/fathers）；ACCS 譯名決策同源
- [[scripture-canon]] / [[scripture-gnostic]] — 三表 N-欄 reader + 純函式 test-first 範式
- [[translation-glossary]] — 教父譯名主譯權威
- [[feedback_ocr_strategy]] — Gemini 預設、Haiku 一次一本
