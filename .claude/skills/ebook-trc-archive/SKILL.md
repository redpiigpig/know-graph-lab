---
name: ebook-trc-archive
description: 把 thereformedcatholic.org（TRC，中文改革宗神學 AList 檔案站）系統性收進本專案 —— **兩邊平行收**：①檔案本身入電子圖書館／全集（Drive 正本→轉錄→reader 可讀）②書目條目入《基督教大藏經》/scripture-canon/christianity（時代×藏×正/外）。含站點 API 用法、逐檔限速下載規矩、簡→繁轉換、以及餵給大藏經分類器的 record 轉接。Use when 要抓／續抓 TRC 的某個分類、要把 TRC 書目歸入大藏經、要處理該站的巢狀作品集結構、或使用者提到「改革宗那個下載站」「thereformedcatholic」。
---

# TRC 改革宗檔案站收錄

> **授權**：使用者已取得站方授權作**私人收藏**用（2026-08-24 告知）。
> **🚨 站方資源有限——一次一個檔、檔與檔之間留間隔，絕不並發、絕不整批抓。** 這是使用者明確要求，不是建議。

## 站點怎麼打

AList 檔案站，前端掛在 `/download`：

```
POST https://thereformedcatholic.org/download/api/fs/list
Content-Type: application/json
{"path": "/", "password": "", "page": 1, "per_page": 1000, "refresh": false}
```

- 🚨 **base_path 是 `/download`**。直接打 `https://thereformedcatholic.org/api/fs/list` 會回 **WordPress 的 404 頁（HTTP 200 + HTML）**，看起來像成功其實不是。判斷方式：看 `Content-Type` 是不是 `application/json`。
- 主站是 WordPress，AList 只是掛在 `/download` 底下的 SPA（`window.ALIST.base_path`）。頁面本身是 JS 動態載入，`WebFetch` 只會拿到 `TRC` 三個字，**必須走 API**。
- 走 Cloudflare，但列目錄不需要特殊 header。

普查腳本：**`scripts/trc_catalog.py`**

```bash
python scripts/trc_catalog.py            # 走全樹 → c:/tmp/trc_catalog.json
python scripts/trc_catalog.py --report   # 只讀既有清單出分類/副檔名統計
```

每次列目錄之間 `sleep(2.0)`（`DELAY`）。單一目錄失敗不中斷整棵樹。

## 站點結構的坑

根目錄 18 個分類（宗派／時代／主題混編）：

> 改革宗・改革宗荷蘭・長老宗・路德宗・安立甘・公理宗・批判地學習的浸派・批判地學習的衛斯理派・初代教會・前抗議教・信綱及教理問答・聖經・神學詞典・詩歌集・羅馬公教・異端・大合集・其他資料

- **巢狀很深**，且深度不規則。作品集底下常再分「每部書 → 原版 ORIGINAL／各譯本」，例如
  `/公理宗/湯馬斯布魯克斯/布魯克斯作品集/08基督測不透的豐富/原版 ORIGINAL`；
  信綱類底下按「譯本」分（趙中輝譯本／錢曜誠譯本…）。
  → **同一部作品會有多個檔**。入庫前要先判斷「這幾個檔是同一本的不同版本」，別當成不同書。
  → 多譯本時依 [[feedback_collected_works_latest_traditional_edition]]：繁體優先、繁體中取最新。
- **「大合集 Large Collection」可能是打包檔**，先確認體積再決定碰不碰（[[feedback_r2_small_derivatives_only]]：掃描原檔／整本 PDF／>10MB 一律不上 R2，進 Drive）。
- 檔名幾乎全簡體（`海德堡要理问答注释`、`长老制教会治理规范`）——見下「簡轉繁」。

## 兩邊平行收（使用者定調）

| | 收什麼 | 去哪 |
|---|---|---|
| **電子圖書館／全集** | **檔案本身**（PDF/EPUB 全文） | Drive `{category}/`（正本，[[feedback_drive_canonical_storage]]）→ `scripts/ingest_new_books.py` → 轉錄 → reader |
| **基督教大藏經** | **書目條目**（不是全文） | `data/dazangjing/{era}.ts`，`DazangWork` 一筆 |

同一本書兩邊都有身分：藏經條目用 **`DazangWork.link`** 指回站內閱讀器。

### 餵給大藏經分類器

🚨 **`dazangjing-sweep` 這支 workflow 不能直接用**——它的 Sweep 階段是上網查各國國家圖書館 API（DNB／BnF／OpenLibrary／IA）**按主題撈書目**，不吃現成檔案清單。可重用的只有它的 Classify／Verify 概念。

正確接點是分類器本身：

```bash
python scripts/dazangjing_catalog_ai.py once --input <records.json> \
       --ledger data/dazangjing/source-catalog/classified-records.jsonl
```

輸入是 `{"records": [ ... ]}`，每筆 record 的形狀（比照既有 ledger）：

```json
{"source": "trc", "query": "<來源分類路徑>", "title": "...", "author": "...",
 "date": "...", "language": "chinese", "subjects": ["..."],
 "url": "<TRC 路徑>", "raw_id": "<TRC 路徑>", "classification_status": "unclassified"}
```

分類器逐筆吐：`decision · title_orig · title_zh · author · era · place · language · eraKey · collectionKey · canon · confidence · reason_zh · needs`
——`eraKey`（四時代）＋`collectionKey`（十藏）＋`canon`（正/外）就是大藏經的三軸座標。

**分類器會自己排除現代研究專著**（`decision: "drop_secondary_study"`），只收原典。TRC 裡大量當代解經書／講道集會被濾掉，不會污染藏經目錄——這正是要的行為，別去繞過它。

**🚨 不自動入庫**：分類結果是**待審提案**，經使用者過目才寫進 `data/dazangjing/{era}.ts`。策展流程走 `scripts/dazangjing_catalog_curate.py`。

## 🚨 簡轉繁

TRC 幾乎整批簡體。轉換走 [[ebook-translate]] 的**簡→繁子管線**：`opencc s2tw` + `TRAD_FIXES`，
純規則、**不用 LLM、不吃任何額度**。

**書目欄位也要轉，不只內文**——`title_zh` / `author` / `note` 進大藏經之前都要過同一道，
否則藏經目錄會混進簡體。這是 [[feedback_traditional_chinese_only]] 的硬規則（DB／檔案／對話任何中文皆然）。

## 建議順序

1. 先確認 `c:/tmp/trc_catalog.json` 在不在；不在就跑普查（巢狀很深，會跑一陣子）。
2. 出**完整清單＋分類統計**，以及「哪些入藏／哪些只入圖書館／哪些兩邊都不收」的提案，**給使用者過目**。
3. 確認後才開始逐檔下載。**先從小檔、公有領域為主的類別**（初代教會／信綱／詩歌集）試通整條流程，再往大檔走。
4. 每檔下載後立刻走 ingest 進 Drive，**別囤在本機**。

## 相關

[[ebook-pipeline]]（parse/OCR/standardize）・[[ebook-translate]]（簡→繁／外文→繁中）・
[[ebook-collected-works]]（作家全集）・[[scripture-canon]]（/creeds 信條，TRC 信綱類可對接）・
[[project_dazangjing]]（大藏經體例：四時代×十藏，別發明「古典十藏」傘狀名）
