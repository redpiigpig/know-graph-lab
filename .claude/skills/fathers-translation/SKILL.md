---
name: fathers-translation
description: 教父全集（Schaff ANF 10 卷 + NPNF1 14 卷 + NPNF2 14 卷 + ACCS 27 卷）中譯／精修流程。包含 CCEL EPUB packaging 問題的特殊處理、NCX-driven consolidator、multi-h3 splitter、A+B+C 三層校對、教父翻譯詞庫對接。本 skill 從 [[ebook-translate]] 分出，專責「教父原典」這一塊；ebook-translate 留給一般電子書翻譯。Use when 翻新一卷 Schaff／ACCS、補精修舊卷、`/fathers` 頁面要新增已精修書、`/translation-glossary` 詞庫要加教父詞條、Haiku 校對教父書並 backfill 名詞、處理 cross-work bleed／footnote 格式異常。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。

# 教父全集翻譯精修 Skill

「教父原典」翻譯有跟一般電子書翻譯不一樣的需求：CCEL EPUB packaging 把多個 letter 塞同一個 HTML 檔造成 cross-work bleed、章節標題會吞內文、術語人地名要在跨卷之間保持一致。這 skill 集中處理這一切。

對應 source：
- **Schaff ANF**（Ante-Nicene Fathers）10 卷 — ~AD 100-325 教父
- **Schaff NPNF1**（Nicene & Post-Nicene Fathers Series 1）14 卷 — 主要奧古斯丁 + 屈梭多模
- **Schaff NPNF2**（Series 2）14 卷 — 東方教父（亞他那修／巴西流／貴格利…）
- **ACCS**（IVP Ancient Christian Commentary on Scripture）27 卷

對應頁面：
- `/fathers` — 教父著作 listing，按系列分組
- `/ebook/[id]` — 個別卷的閱讀界面
- `/translation-glossary` — 教父翻譯詞庫（5 個 tab，249+ 神學家、159+ 名詞）

🟢 **黃金模板 = ANF Vol 1**（[[anf-vol1-golden-template]]）。新 session 接手要先驗證 Vol 1 通過再開新卷。

---

## 完整 5+ 步驟 pipeline（v4 鎖定）

```
EPUB（Drive/CCEL 來源）
    │
    ▼
[1] translate_ebook_to_zh.py  ← 章節級 Haiku 翻譯
    含 [^N] refs / {{p:N}} page markers / 末尾 (N) body 腳註區
    │
    ▼
[2] polish_translated_book.py  ← chapter_path 清理、volume 標記
    │
    ▼
[3] consolidate_by_ncx.py  ← 按 NCX 樹合成 letter pages（≤10 章/頁）
    含：
    - Elucidation back-fold（Book III 註解折進 Book III 末頁）
    - 封面／前言 normalize（chunk 0→封面；TitlePage+Preface→merge 前言）
    - parent_volume 三層樹（依納爵 ⊃ 致以弗所人書／致馬內夏人書…）
    - 索引尾頁 stray volume 清除
    │
    ▼
[4] sweep_book_quality.py  ← T1+T2+T3+T8 自動修
    T1: 標題吞內文（body marker 切到正確位置）
    T2: 單一 h3 vs volume 漂移（30% 位置守門）
    T3: 直引號 "" → 「」、'' → 『』
    T8: per-book TERM_FIXES 名詞統一（哥林多/科林斯 等）
    │
    ▼
[5] multi_h3_splitter.py  ← 多 h3 segment 分發到不同目標 chunk
    處理 CCEL packaging 把下一封信 intro 灌進上一封 chunk 末尾的問題
    Safety guards: >70% source chunk 或 >18K chars 一律拒絕
    │
    ▼
[6] auto_fix_cross_bleeds.py  ← 單 h3 cross-bleed 補丁
    多重 bleed 場合用 multi_h3_splitter，單純的 forward intro 移動用這個
    │
    ▼
A+B+C 三層校對：
    A 靜態 scan_translated_book.py（T1-T11）
    B Haiku 文字 llm_proofread_book.py
    C Haiku Vision screenshot + vision_proofread_book.py
    │
    ▼
[7] merge_proofread_reports.py → REVIEW_<id>.md
    │
    ▼
[8] seed_glossary_anf_vol1.py 樣板 → 詞庫 backfill 進 /translation-glossary
    │
    ▼
R2 + DB previews 同步 / /fathers 頁面標「已精修」
```

---

## 跑新卷的最小流程

```bash
EBOOK=<new-vol-ebook-id>

# 1. 翻譯（已有 v4 pipeline 自動跑這幾步）
python scripts/translate_ebook_to_zh.py $EBOOK --engine haiku --resume
python scripts/polish_translated_book.py $EBOOK
python scripts/consolidate_by_ncx.py $EBOOK
python scripts/sweep_book_quality.py $EBOOK   # 所有 T1-T3+T8

# 2. 修 CCEL packaging cross-bleeds
python scripts/multi_h3_splitter.py $EBOOK    # 多 h3 分發

# 3. 驗證
python scripts/validate_book_structure.py $EBOOK
python scripts/scan_translated_book.py $EBOOK

# 4. 校對（可選但推薦）
python scripts/llm_proofread_book.py $EBOOK              # B 文字
node    scripts/screenshot_book.mjs --ebook $EBOOK       # C-1 截圖
python scripts/vision_proofread_book.py --ebook $EBOOK   # C-2 視覺
python scripts/merge_proofread_reports.py $EBOOK         # → REVIEW_<id>.md

# 5. 詞庫 backfill（每本書產出特有名詞）
# 依照 seed_glossary_anf_vol1.py 樣板，新增 seed_glossary_<book>.py
python scripts/seed_glossary_<book>.py

# 6. 標記為「已精修」
# 編 pages/fathers/index.vue 把該 ebook_id 加進 REFINED_IDS set
```

預期耗時：~3.5 小時翻譯 + 30 分鐘校對 + 1 小時 cross-bleed 手動處理 = **半天/卷**。

---

## CCEL EPUB 三大坑（教父專屬問題）

跟一般電子書不一樣，CCEL 的 EPUB 有結構問題會擴散到下游：

### 坑 1: 一個 HTML 檔裝多封信

例：`ignatius_martyrdom.html` 裡同時有 Ignatius 殉道記正文 + Barnabas 書信導讀 + Barnabas 書信正文。原本 pipeline 假設「1 HTML = 1 chunk = 1 letter」，這就壞了。

**修法**：
1. consolidate_by_ncx 用 NCX 而非檔案邊界
2. multi_h3_splitter 處理「同 chunk 多 h3」案例
3. scan_translated_book T9 (NCX-driven cross-bleed detect) 抓漏網

ANF Vol 1 實證：22 個 cross-bleed → 4 個 auto_fix 解決 → 6 個 multi_h3_splitter 解決 → 0 殘留

### 坑 2: 章節標題吞內文

例：原文 `Chapter I.—Occasion of the epistle.` 翻譯後變成「第一章—書信寫作的契機既然我看到你」（「既然我看到你」是內文第一句）。

**修法**：sweep_book_quality T1 用 body marker（既然/誠然/親愛的/讓我們/蓋…）偵測 + 自動切到正確位置 + 內文 prepend

### 坑 3: 章節都有獨立 footnote section

CCEL 格式：每章一個 separator + footnotes，10 章 page 就有 10 個 separator。

**修法**：reader 端的 renderMarkdown toggle 邏輯（body↔footnotes flip per separator）+ 末尾收集所有 footnotes 集中渲染

---

## 詞庫整合（[[translation-glossary]] 對接）

教父書翻譯有大量 proper noun，跨卷必須一致。流程：

1. 翻譯**前**到 `/translation-glossary` 確認譯名（5 個 tab：人名／地名／作品名／教派名／神學名詞）
2. 翻譯**中**：sweep_book_quality 的 `TERM_FIXES_<book>` 表自動套用（哥林多/科林斯 → 哥林多 等）
3. 翻譯**後**：跑 `seed_glossary_<book>.py` 把該書新出現的名詞 backfill 進 DB，標 `first_source = '<book>'`

### 人名 5 個次分類（按卒年自動劃分）

- **聖經人物**: NT/OT 人物（手標 — Paul 保羅、Mary 馬利亞、Salome 撒羅米、Clopas 革羅帕、Cephas 磯法）
- **初代教會** (-638): 教父／護教士／東方教父（Ignatius 依納爵、Justin 猶斯定、Irenaeus 愛任紐…）
- **中世紀教會** (638-1517): 經院神學家（Anselm／Aquinas／Bonaventure…）
- **近代教會** (1517-1910): 宗改 + 清教徒 + 覺醒運動
- **現代教會** (1910+): Barth／Tillich／Niebuhr 等

ANF Vol 1 完成後共 49 條新詞庫條目進入：9 person + 14 place + 11 work + 8 sect + 7 term。

### 名詞統一表 (TERM_FIXES_<book>)

[`sweep_book_quality.py`](../../../scripts/sweep_book_quality.py) 維護一張 `TERM_FIXES_BY_BOOK` 字典，每本書一條目：

```python
TERM_FIXES_ANF_VOL_1 = {
    # Corinth → 哥林多 (Protestant)
    "科林多": "哥林多", "科林斯": "哥林多", ...
    # Paul → 保羅 (Protestant)
    "聖保祿": "聖保羅", "保祿": "保羅",
    # Philippi → 腓立比
    "斐理伯人書": "腓立比人書", "斐理伯": "腓立比",
    # Cephas
    "革法": "磯法",
    # Smyrna
    "士麥那": "士每拿",
    # Aristion
    "亞里斯頓": "亞里斯鐸",
    ...
}
```

新卷翻譯後跑 B（Haiku 文字校對）的 TERM issues 整理進此表，再 `sweep --only-t8` 套一遍。

---

## A+B+C 三層校對（教父書必跑）

跑完翻譯一定要過三層：

| 層 | 工具 | 抓什麼 | 成本 | 跑時 |
|---|---|---|---|---|
| **A** | `scan_translated_book.py` | T1-T11 結構/翻譯品質規則 | $0 | 5 秒 |
| **B** | `llm_proofread_book.py` | 名詞前後不一致、漏譯、誤標人物、語義異常 | ~$0.30 | ~5 分 |
| **C** | `screenshot_book.mjs` + `vision_proofread_book.py` | 字級錯位、排版異常、視覺缺漏 | ~$0.50 | ~10 分 |

合併 → `merge_proofread_reports.py` → `scripts/logs/REVIEW_<id>.md`（按 priority 排序的人工複查清單）

ANF Vol 1 完整跑結果：A 37 + B 615 + C 161 = 109/112 chunks 有 issues。Top 緊急 chunks 標出來逐個修。

---

## /fathers 頁面 contract

ebook_id 加進 `pages/fathers/index.vue` 的 `REFINED_IDS` set 後，自動顯示「已精修」綠色 badge。標準是：

1. ✅ validate_book_structure.py 0 FAIL
2. ✅ scan_translated_book.py T9 cross-bleed = 0
3. ✅ T1 標題 bleed = 0
4. ✅ 詞庫 backfill 完成
5. ⚠️ 殘留 T2/T10/T11 INFO/WARN 可接受（多為 LLM 翻譯細節）

不到上面 4 個門檻 = 維持「粗譯」(amber) 狀態。

---

## 待精修書清單（按優先序）

| Order | Book | Status | 備註 |
|---|---|---|---|
| ✅ 1 | ANF Vol 1 | 已精修 | 黃金模板 |
| 🟡 2 | ANF Vol 2 (Fathers of the Second Century) | 粗譯 + sweep + 詞庫 + 結構修 | 2026-05-28：① T2/T3/T8 sweep（T2 43 / T3 695 / T8 118 fixes）② 13 個 partial-consolidate letter_page chunks 改 chunk_type→page、英文 vol→中文（他提安致希臘人辭 / 雅典那哥拉護基督徒辭 / 論死者復活 / 革利免勸勉希臘人辭）③ 178 個 chunks volume 對照 NCX file-prefix 重新指派（修 Theophilus iv.ii.* 被錯標 Tatian 的 bug）④ 242 個 anf02.x.y.html chapter_path → `<中文 vol> 第N章` ⑤ 詞庫 backfill 55 條（24 person + 31 term）⑥ R2 + DB 已同步。**validate 從 13 FAIL → 0 FAIL**；殘留 R011 146 WARN（chapter_path 跟 vol 翻譯版本不一致，需 LLM 校對）。Vol 2 NCX 對應已寫進 LETTER_CN_LABELS，未來想做完整 letter-page consolidation 可：(a) 把 13 個現存 letter_pages 拿掉、(b) 跑 `python scripts/consolidate_by_ncx.py 4e3d16fc-ef4f-420f-a3ec-56e2e92d659f` |
| 🟡 3 | ANF Vol 3 (Tertullian) | 粗譯 + sweep + 詞庫 + 結構修 | 2026-05-28：① T2/T3/T8 sweep（T2 7 / T3 595 / T8 271 fixes）② 594 個 chunks volume 英→中（Apologetic.→特土良護教文集／Anti-Marcion.→特土良駁異端文集／Ethical.→特土良倫理文集／Indexes→索引）③ 詞庫 backfill 52 條（9 person + 43 term）④ R2 + DB 已同步。**validate 0 FAIL**；殘留 1093 WARN（768/1362 chunks 仍無 vol — split_oversized 子片段；要解需跑 consolidate_by_ncx，NCX 對應已寫進 LETTER_CN_LABELS、`python scripts/consolidate_by_ncx.py 364dac2e-410f-4906-be63-8bb86b4865ee`，但 dry-run 顯示 787/863 會分到 front-matter，要先研究 split_oversized 子片段對齊問題） |
| 4 | NPNF1 Vol 1 (Augustine Confessions) | 粗譯 | |
| 5 | NPNF2 Vol 4 (Athanasius) | 粗譯 | |
| 6-38 | Vol 3-10 ANF / Vol 2-14 NPNF1 / Vol 1-14 NPNF2 | 粗譯 | 重大用戶優先順序排定 |

---

## 跟 [[ebook-translate]] 的分工

| 範圍 | 歸屬 |
|---|---|
| 教父原典翻譯（Schaff / ACCS） | **fathers-translation**（本 skill）|
| 教父詞庫整合（/translation-glossary backfill）| **fathers-translation** |
| CCEL EPUB packaging 處理 | **fathers-translation** |
| multi_h3_splitter / cross-bleed | **fathers-translation** |
| /fathers 頁面 contract | **fathers-translation** |
| 一般中譯／簡轉繁 / 非教父書 | [[ebook-translate]] |
| EPUB parser / Haiku/Sonnet/Gemini engine 設定 | [[ebook-translate]]（基礎設施）|
| translate_ebook_to_zh.py 本體 | [[ebook-translate]] |

---

## See also

- [[anf-vol1-golden-template]] — 黃金模板的所有規格 + 驗證指令
- [[ebook-translate]] — 翻譯基礎設施（engine／quota／OAuth refresh）
- [[ebook-pipeline]] — parse/OCR/standardize 上游
- [[translation-glossary]] — 詞庫工具
- [book-structure-spec.md](../ebook-pipeline/book-structure-spec.md) — chunk schema + R/T 規則完整對照
- [glossary.md](../ebook-translate/glossary.md) — 教父人名／聖經書卷／神學術語 markdown 表（DB 之外的補充）
