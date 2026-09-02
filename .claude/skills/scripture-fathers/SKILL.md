---
name: scripture-fathers
description: 教父全集（Schaff ANF 10 卷 + NPNF1 14 卷 + NPNF2 14 卷 + ACCS 27 卷）中譯／精修流程。包含 CCEL EPUB packaging 問題的特殊處理、NCX-driven consolidator、multi-h3 splitter、A+B+C 三層校對、教父翻譯詞庫對接。本 skill 從 [[ebook-translate]] 分出，專責「教父原典」這一塊；ebook-translate 留給一般電子書翻譯。Use when 翻新一卷 Schaff／ACCS、補精修舊卷、`/fathers` 頁面要新增已精修書、`/translation-glossary` 詞庫要加教父詞條、Haiku 校對教父書並 backfill 名詞、處理 cross-work bleed／footnote 格式異常。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash-0731`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。


> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。

# 教父全集翻譯精修 Skill

「教父原典」翻譯有跟一般電子書翻譯不一樣的需求：CCEL EPUB packaging 把多個 letter 塞同一個 HTML 檔造成 cross-work bleed、章節標題會吞內文、術語人地名要在跨卷之間保持一致。這 skill 集中處理這一切。

對應 source：
- **Schaff ANF**（Ante-Nicene Fathers）10 卷 — ~AD 100-325 教父
- **Schaff NPNF1**（Nicene & Post-Nicene Fathers Series 1）14 卷 — 主要奧古斯丁 + 金口若望
- **Schaff NPNF2**（Series 2）14 卷 — 東方教父（亞他那修／巴西流／貴格利…）
- **ACCS**（IVP Ancient Christian Commentary on Scripture）27 卷

對應頁面（**2026-07-19 起 /fathers 為獨立子站，UI/UX 與電子圖書館切開**）：
- `/fathers` — 教父著作 listing，羊皮紙古典風，按系列分組（自訂 header，入口仍從 `/scripture-canon/christianity`）
- `/fathers/[id]` — **專屬羊皮紙 reader**（非共用 `/ebook/[id]` 圖書館 reader）；中／對照／單一來源切換、卷→書→段三層目錄、朗讀、字級主題設定；annotations／書籤／編輯／原頁下載這些「圖書館」功能刻意不放進來以強化區隔
- reader 與圖書館 reader 共用純渲染核心 `lib/ebook-render.ts`（escapeHtml/inlineFmt/renderMarkdown/renderTocPage/buildParallelColumns），避免兩邊 footnote／對照解析漂移
- 資料仍走共用 `ebooks`／`ebook_chunks` 表 + `/api/ebooks/[id]` API（沒有另做 schema 遷移）
- `/translation-glossary` — 教父翻譯詞庫（5 個 tab，249+ 神學家、159+ 名詞）

> 📌 **2026-07-20 進行中**：見 repo 根目錄 [`SESSION_HANDOFF_fathers_2026-07-20.md`](../../../SESSION_HANDOFF_fathers_2026-07-20.md)。
> 重點：① `/fathers` 已獨立成羊皮紙子站（完工）；② **「標題吞內文」排版修復未完** —— 實際 **1,455 chunk／5,776 處／全 37 卷**（不是 228，舊數字是 T2 每 chunk 只報第一個所造成的低估），工具 `scripts/fix_fathers_heading_swallow.py`，冪等可續跑，建議掛排程分批；③ T11 漏譯 537 處待查。
>
> 🚨 **Drive 改版**：`_chunks` 已移到 `G:\我的雲端硬碟\資料\知識圖工作室\_chunks`，repo 內 91 支腳本／102 處仍指舊路徑且**失敗時靜默跳過**（會假裝「全部修好了」）。跑任何 JSONL 腳本前先確認路徑，或設 `EBOOK_CHUNKS_DIR`。

🟢 **黃金模板 = ANF Vol 1**（[[anf-vol1-golden-template]]）。新 session 接手要先驗證 Vol 1 通過再開新卷。

---

## 完整 5+ 步驟 pipeline（v4 鎖定）

```
EPUB（Drive/CCEL 來源）
    │
    ▼
[1] translate_ebook_to_zh.py  ← 章節級 LLM 翻譯（--engine auto = Gemini → NVIDIA → Haiku）
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
python scripts/translate_ebook_to_zh.py $EBOOK --engine auto --resume   # auto = Gemini → NVIDIA deepseek-v4-flash → Haiku 救急（2026-06-04 統一 Gemini-first）
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

### 坑 4: JSONL 雙語雙存（dual-state bug，Vol 3 實證 2026-05-28）

舊版 pipeline 的 idempotency bug：某次 partial re-translate 把英文原文 chunks 跟翻譯後中文 chunks **同時保留**在 JSONL 中（不是 dedupe，是並存）。Vol 3 上線時 1362 chunks，前 600 是 100% 英文（vol = English category names），後 762 才是 100% 中文（vol = None，chapter_path 是 raw `anfNN.x.y.html`）。reader 顯示一半英文一半中文。

**偵測 snippet**（放在 `scan_translated_book.py` 或一次性檢查）：
```python
import re
zh_run = en_run = 0
for r in rows:
    content = r.get('content','') or ''
    if not content: continue
    zh = len(re.findall(r'[一-鿿]', content))
    if zh / max(len(content),1) > 0.3: zh_run += 1
    elif zh / max(len(content),1) < 0.05: en_run += 1
# 若 en_run + zh_run ≈ len(rows) 且兩者皆顯著 → 雙語雙存
```

**修法**：保留中文 chunks，刪除英文 chunks；re-index 0..N-1；對應 [[#tip-2-anf-file-prefix-volume-map]] 重新指派 volume。

### 坑 4.5: title_en 不一定保留 anf<NN>.x.y.html 前綴（Vol 7 實證 2026-05-29）

translate_ebook_to_zh.py 通常會把 source HTML 檔名 (`anf04.iv.iii.i.html` 等) 存進 `title_en` 給後續 backfill 使用。但 Vol 7 的 translate 跑出來 `title_en` 全變成英文 NCX 章節文字 (例：`'b ook i.'`, `'the divine institutes'`, `'Chap. III.—Of What Subjects...'`)。原因未確認 (可能 EPUB packaging 差異 / 翻譯版本差異)，但下游影響重大：

- `_fix_vol_auto.py` / `_fix_volN_volumes.py` 的 `PREFIX_TO_VOL` 完全 0 match
- 必須改用 boundary-based forward-propagate：walk chunks，title_en 對英文 NCX label regex match 設 boundary，把 current_vol propagate 到下個 boundary 之前所有 chunks

實作見 [`_fix_vol7_volumes_v2.py`](../../../scripts/_fix_vol7_volumes_v2.py)。新 vol 一開始時先 sample 5-10 個 chunks 看 title_en 形狀，**確認是 anf prefix 還是英文文字** 再決定走 PREFIX_TO_VOL 還是 boundary-based。

### 坑 4.6: 深層巢狀多論著卷 — `consolidate_by_ncx` 會打散順序（NPNF2 V10 安波羅修實證 2026-06-05）
title_en 是英文 NCX label（非 npnf 前綴）**且**該卷有深層巢狀多論著（如安波羅修：論教士職分／論聖靈／
論其兄之死／基督信仰闡釋／論奧蹟／論懺悔／論貞女／論寡婦 各含 Intro+Book/Chapter 多層）時，
`consolidate_by_ncx` 會**把論著標題 chunk 抽到檔尾、章節 chunk 留在前段、順序錯置**（V10 實證：
333 chunks 中 0-298 章節無 volume、299-330 論著標題擠在尾端，章節從「第32章」開頭＝源順序已毀）。
內容不丟但 metadata 與順序不可信，且 pre-consolidate 乾淨版會被覆蓋無法復原。

**鐵則：多論著大卷（title_en=英文 NCX label）翻完後直接 boundary-walk，不要跑 `consolidate_by_ncx`。**
boundary-walk 在乾淨源順序上 walk：論著名以 chunk 形式出現（"On the Duties of the Clergy." 等）設
boundary、propagate current 論著到後續 "Chapter N"/"Book I" chunks（比照 `_fix_vol7_volumes_v2.py` /
`_fix_vol33_hilary_damascus.py`）。**翻完先別 consolidate，先 sample title_en**：若見英文論著名 + "Chapter N"
分離 → 走 boundary-walk；若 consolidate 已誤跑致順序毀 → 隔離壞檔（`.consolidate-corrupt.bak`）+ 移除
工作 jsonl + 重譯（translate 從 EPUB 出乾淨源順序，pre-consolidate 中文無備份只能重譯）。

### 坑 4.7: translate 最後 re-sort 用非唯一 title_en → 多作品卷閱讀順序打散（NPNF2 V11 實證 2026-06-11）
`translate_ebook_to_zh.py` 結尾「sorted to source order」原本用 `title_en` 當 dict key 建排序表，但
多作品卷每部都有「Chapter I/II…」**title_en 不唯一** → dict 只留每標籤**最後一筆**，所有同名 chunk
塌縮成同一排序鍵 → **跨作品閱讀順序整個打散**（V11 實證：蘇皮修《神聖歷史》/格西安《會院規章》《會談錄》
《駁聶斯脫里》章節隨機交錯；翻譯當下順序其實是對的，是這步 re-sort 毀掉）。validate 0 FAIL **抓不到**
（結構合法、只是順序錯），spot-check reader 內容才看得出。

**根治**：已把排序鍵改成 `source_text`（==`content_en`，每 chunk 唯一），見 translate.py ~line 1059。
**已上架卷救援**：`source_text` 唯一 → 重抽 EPUB 文件順序 (`epub_to_chunks`)、用 source_text 比對還原順序、
re-index，無需重譯（範本 `_fix_vol35_reorder.py`，1204/1204 全配對）。**新卷精修先 spot-check 3-4 個深層
chunk 內容是否同作品連續**（坑 4.6/4.7 都靠這抓）；亂了就先 reorder 再 boundary-walk。

### 坑 5: bare volume vs book-specific volume 並存（Vol 2 實證）

例：同一個 JSONL 裡同時出現 `volume='革利免《教師》'` 跟 `volume='革利免《教師》卷一/二/三'` — 前者是 polish 沒抓到 book number 的殘留 chunks，會被誤標到錯誤分組。

**修法**：walk 所有 chunks；對 bare-vol chunks（不含「卷」字）查鄰近 chunks 是否有 specific 版（同 vol prefix），有就 inherit。在我 fixVol2 腳本中用：
```python
def specific_book(vol): return vol and '卷' in vol
# 對每個 bare-vol chunk，先後向再前向各找 10 步內 specific 版本
```

---

## Pipeline-level tips（橫跨 Vol 1/2/3 整理）

### Tip 1: validate 0 FAIL 不等於 reader 完美

`validate_book_structure.py` 只檢結構（chunk_index 連續、chunk_type 合法、chapter_path 非空）。**內容可能還是中英混雜或 dual-state**（見坑 4）。一定要 spot-check reader 開幾頁實際看一下，不要 100% 信賴 validator。

### Tip 2: ANF file-prefix → volume map（救援已半譯 book）

教父書都用 CCEL 命名 `anfNN.X.Y.Z.html`。如果 chunks 還掛這種 chapter_path，可不必重 consolidate，直接用 file-prefix 對應 NCX 結構回填 volume：

```python
# ANF Vol 2 例
PREFIX_TO_VOL = [
    ('anf02.ii.ii.', '黑馬牧者：異象篇'),
    ('anf02.iii.ii.', '他提安致希臘人辭'),
    ('anf02.iv.ii.i.', '提阿非羅致奧托呂庫書 卷一'),
    # …按 NCX 對照
]
# 倒序 sort 讓 longest prefix 先匹配
```

實證效益：Vol 2 178 個 chunks 重新指派 volume（修一個 partial-consolidate 留下的 Theophilus 被錯標 Tatian 的 bug），Vol 3 762 個全部對應好。

### Tip 3: sequential 第N章 fallback

當大量 chunks 的 chapter_path 是翻譯變體（如「提阿非羅致奧多利古」「奧托呂庫」「歐多魯克」並存）而 R011 大量 WARN，最簡單的解：直接用 volume 名 + sequential 編號重命名：

```python
per_vol = {}
for r in rows:
    vol = r.get('volume')
    if not vol: continue
    n = per_vol.get(vol, 0) + 1
    per_vol[vol] = n
    r['chapter_path'] = f'{vol} 第{n}章'
```

Vol 2 R011 146 → 0，Vol 3 R012 159 → 0 都靠這招收尾。

### Tip 4: B-layer LLM false positive 警惕

Haiku 4.5 校對最常見的 false positive：建議把詞庫已經規定的中文音譯改回**英文音譯**。例 (2026-05-28)：建議「革利免」應為「克雷門」（錯！Κλήμης 是希臘文，思高/和合本都用「革利免」）。

**處理原則**：先比對 `/translation-glossary` 的 `name_recommended`：
- 若 LLM 建議 = 詞庫 → 採納，加進 TERM_FIXES_BY_BOOK 收斂變體
- 若 LLM 建議 ≠ 詞庫 → **反向**修，把出現的變體列入 TERM_FIXES 收斂回詞庫值

詳見 [[feedback-glossary-strict-authority]]。

### Tip 5: 不要 conflate 同名異人

Saturus（殉道者，與 Perpetua 同死）vs Saturninus（羅馬農業神 Saturnus 或圖盧斯主教）— 兩個人，兩個名。早期 sweep 曾經把 `薩圖魯 → 薩圖爾努斯` 錯誤合併，必須分開：
- 薩圖魯：殉道者 Saturus
- 薩圖爾努斯：羅馬神 Saturn / 主教 Saturninus

加進 TERM_FIXES 前要確認**是不是同一個人物**，不只看字面相似。

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

## 參考現成中譯本校準（名著專用，2026-05-30 user 通則）

名著教父著作（《懺悔錄》《論道成肉身》《安東尼傳》《論三位一體》等）網上多有權威中譯本。**政策：參考校準，不入庫、不取代。**

- reader 永遠只顯示**我的逐節對齊譯文** — 因為對照功能（中／中英對照／英）要求譯文跟 NPNF/ANF 英文原文**逐節結構對齊**，現成譯本按自己的分段走，塞不進對照框架。
- 現成中譯只在 **B 層校對**當「黃金參考」：比對語意、神學術語、人地名 → 標出我的譯文偏差 → 修我自己的文字（**保持分段不變**）。
- ⚠️ **版權**：現成譯本多有版權（商務／校園／道風等）。**絕不存進 DB / R2**，只在校對當下 transient 使用。
- 實作：精修結構定好後，對名著 chunk `WebFetch` 對應段落 → 加進 `llm_proofread_book.py` 的 reference 上下文 → 採納語意/術語修正。

已查參考來源：
| 著作 | 現成中譯 |
|---|---|
| 奧古斯丁《懺悔錄》| 周士良譯（商務印書館，經典定譯）|
| 奧古斯丁《上帝之城》(De Civitate Dei) | 王曉朝譯（人民出版社）／吳飛譯（上海三聯，三冊）|
| 奧古斯丁《論基督教教義》(De Doctrina Christiana) | 石敏敏譯（中國社會科學）|
| 奧古斯丁《論三位一體》(De Trinitate) | 周偉馳譯（上海人民／商務）|
| 亞他那修《論道成肉身》(On the Incarnation) | 聖弗拉基米爾神學院版／校園相關 |
| 亞他那修《安東尼傳》| 陳劍光譯（1990 恩奇事業，據拉丁/希臘/英古本）|

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

## 品質回歸測試 — `test_fathers_quality.py`（每卷品質鎖定）

把 /fathers contract 的門檻寫成可重複跑的回歸測試，**確認每一卷品質固定不倒退**。
上架後若有人重譯 / 重整 / 手改造成品質滑落，這支會抓出來。

```bash
python scripts/test_fathers_quality.py            # 測全部已精修卷（REFINED_IDS ∩ TERM_FIXES_BY_BOOK）
python scripts/test_fathers_quality.py <id> ...   # 只測指定卷
# exit 0 全過；1 任一卷任一門檻 FAIL
```

逐卷 5 道固定門檻：

| 門檻 | 檢查 | 來源 |
|---|---|---|
| **G1** | validate_book_structure → 0 FAIL | 結構（chunk_index 連續 / chapter_path 非空…）|
| **G2** | scan T9 cross-bleed = 0 | CCEL packaging 跨作品 bleed |
| **G3** | scan T1 title-bleed = 0 | 標題吞內文 |
| **G4** | TERM_FIXES_BY_BOOK 每個變體在內文出現 **0 次** | 名詞收斂鎖定（金口若望/優西比烏…變體全歸一）|
| **G5** | 無 dual-state（zh chunk 比例 ≥ 0.7、無 >10 連續英文內文 chunk）| 英中並存 bug |

**新卷上架前必跑**：`test_fathers_quality.py <新id>` 綠燈才算精修完成。
**G4 是「固定品質」的核心**：TERM_FIXES 規則更新後，舊卷要 `sweep --only-t8` 重套再測
（2026-06-01 首跑抓到 ANF Vol1 思高書名未收斂 = 規則後加未重 sweep，重 sweep 即修）。

### T9 偵測器精修（2026-06-01，全卷受益）
首跑時 ANF Vol2 報 T9×10、Vol7 T9×2，**經查全是偵測誤報**（非真 bleed）。根因 +修法：
- **檔名型 `title_en`**（`anf02.iv.ii.ii.xxxi.html`）無法跟 NCX 書信名 token 比對 → `build_ncx_index`
  加 `file_stems`，T9 用最長 file-stem prefix 把檔名解析回正確作品再比。
- **索引 section header**（`### THEOPHILUS.` 緊接 `#### INDEX OF SUBJECTS.`，全卷主題索引被併進
  最後內容頁）→ h3 後 80 字內有 index marker 就跳過。
- **標籤型 `title_en`**（純作品名/章標題，`_entry_parent` 也解不出 parent）→ 身分無法解析，
  英文比對不可靠 → 跳過該 chunk（作品自己標題出現在自己頁面不再誤判）。
修完 `test_fathers_quality.py` **24/24 全 PASS**。改動只縮誤報、不遮蔽身分明確 chunk 的真 bleed。

---

## /fathers 頁面 contract

ebook_id 加進 `pages/fathers/index.vue` 的 `REFINED_IDS` set 後，自動顯示「已精修」綠色 badge。標準是：

1. ✅ validate_book_structure.py 0 FAIL
2. ✅ scan_translated_book.py T9 cross-bleed = 0
3. ✅ T1 標題 bleed = 0
4. ✅ 詞庫 backfill 完成
5. ⚠️ 殘留 T2/T10/T11 INFO/WARN 可接受（多為 LLM 翻譯細節）

**鎖定方式**：跑 `test_fathers_quality.py <id>` 綠燈 = 上 4 項全過。

不到上面 4 個門檻 = 維持「粗譯」(amber) 狀態。

---

## 整晚自動精修一卷（unattended overnight playbook）

把 ebook_id 餵進這個流程，~6-8h 後完整精修上架。

```bash
EBOOK=<new-vol-ebook-id>

# 0. 備份原英文 JSONL，避免 dual-state bug
# ⚠️ 必須用 mv（移走）不可用 cp！留下英文 .jsonl 後 --resume 會用 title_en 當 skip-set
#    把全部英文 chunk 當「已完成」跳過 → 整本英文/dual-state（2026-06-04 vol32 踩過）。
mv "G:/我的雲端硬碟/資料/知識圖工作室/_chunks/$EBOOK.jsonl" \
   "G:/我的雲端硬碟/資料/知識圖工作室/_chunks/$EBOOK.en.bak.jsonl"

# 1. 翻譯 (~3-6h)
nohup python -u scripts/translate_ebook_to_zh.py $EBOOK --engine auto \
   > scripts/logs/translate_$EBOOK.log 2>&1 &
# 等 "ebooks row updated" 出現才往下

# 2. 結構 cleanup
PYTHONIOENCODING=utf-8 python scripts/polish_translated_book.py $EBOOK
PYTHONIOENCODING=utf-8 python scripts/consolidate_by_ncx.py $EBOOK
PYTHONIOENCODING=utf-8 python scripts/sweep_book_quality.py $EBOOK
PYTHONIOENCODING=utf-8 python scripts/multi_h3_splitter.py $EBOOK

# 3. Volume backfill — 看 title_en 是 anfNN.* (PREFIX) 還是英文 NCX (boundary)
# 寫 _fix_volN_volumes.py：(a) PREFIX_TO_VOL 從 NCX 抽 depth-1 (b)
# EN_TO_ZH_VOL override consolidate 留下的英文 letter-page vol (c)
# force-rename chapter_path → `<vol> 第N章`
PYTHONIOENCODING=utf-8 python scripts/_fix_vol<N>_volumes.py

# 4. D1 1-10 章合一頁 (median 3000 chars 閾值)
PYTHONIOENCODING=utf-8 python scripts/consolidate_letters.py $EBOOK

# 5. D2 parent_volume backfill — 先把新教父加進 PARENT_RULES
PYTHONIOENCODING=utf-8 python scripts/backfill_parent_volume.py $EBOOK

# 6. T1 enhanced + 驗證
PYTHONIOENCODING=utf-8 python scripts/sweep_book_quality.py $EBOOK --only-t1
PYTHONIOENCODING=utf-8 python scripts/validate_book_structure.py $EBOOK
PYTHONIOENCODING=utf-8 python scripts/scan_translated_book.py $EBOOK

# 7. B-layer Haiku 校對 (~35 min for 742 chunks @ workers=2)
nohup python -u scripts/llm_proofread_book.py $EBOOK --workers 2 \
   > scripts/logs/proofread_$EBOOK.log 2>&1 &
# 抽 TERM_FIXES 加進 sweep_book_quality.TERM_FIXES_<vol> → 再 sweep --only-t8

# 8. glossary backfill (按 _vol5/9 模板寫 seed_glossary_anf_vol<N>.py)
PYTHONIOENCODING=utf-8 python scripts/seed_glossary_anf_vol<N>.py

# 9. REFINED_IDS + commit + push
# 編 pages/fathers/index.vue 把 ebook_id 加進 REFINED_IDS set
```

**關鍵提示**：
- **預設 `--engine auto` = Gemini → NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731` → Haiku 救急（三層，2026-06-04 統一 Gemini-first）**；每層 2-strike + 6h cooldown（連兩次掛 → 退下一層 6h 再回探）。`--engine haiku` 現為 **Haiku-first**（2026-06-05 user Max 訂閱；免費池乾就直接開 Haiku，見 [[feedback_engine_nvidia_no_haiku]]）。
- 🚨 **`--resume` 用 title_en 當 skip key → title_en 大量重複的大卷會誤跳缺漏（NPNF2 V11 實證 2026-06-10）**：
  V11（塞維魯+文森+卡西安，1214 chunks）崩在 664、resume 時 `skip-set size 106`（664 chunk 只 106 unique
  title_en，章號跨作品狂重複）。resume 會把 665+ 任何 title_en 撞到前 106 的源 chunk 全跳過 → 缺數百 chunk。
  **鐵則：大卷（>500 chunk 或多作者多作品）崩潰後不要 resume 續，改 fresh 重譯**（隔離 partial 到
  `.partialN.bak`，移走工作 jsonl，translate 無 skip-set 全譯）。小卷 title_en 夠獨特才可安全 resume。
  根治待辦：把 resume skip key 從純 title_en 改 (title_en, 出現序號) 複合鍵或 source-ordinal。
- ⚠️ **NVIDIA 只能用 deepseek-v4-flash**：唯一保留段落對齊 + `{{p:N}}`/`[^N]` marker 的；qwen3-next/llama-3.3 雖快但段落崩、marker 壞，不可當 NVIDIA 主力。
- 並行多卷時兩卷切不同 engine 分散 quota（如一卷 auto、一卷 gemini）；**同一卷切勿開兩個 process**（race 同一 JSONL → dual-state bug）
- B-layer 跟翻譯不要同時跑（都搶 Anthropic quota）
- `_fix_volN_volumes.py` 是 one-shot 腳本，gitignore (`_*` 已排除)
- `validate 0 FAIL` 是上架硬門檻；scan T2/T5 WARN 可接受

---

## D1 + D2 大改造（2026-05-29 完成）

### D1: 1-10 章合一頁 + 註釋下沉

`consolidate_by_ncx.py` 在 Vol 2-9 對 split_oversized chunks 處理不力，多數 letter 沒能合進 letter page，造成「每章一頁」過度切散。新增 [`consolidate_letters.py`](../../../scripts/consolidate_letters.py)：

- 按 `volume` group consecutive chapter chunks
- 中位數 char/chapter < 3000 → 短書信／講道 → 10 章/page 合併
- 中位數 ≥ 3000 → 長篇論述 → 維持每章一頁（避免破壞長文閱讀體驗）
- 跳過 front matter (封面/前言/書名頁/索引/序言/目錄)
- 保留 parent_volume / volume / page_numbers / source_lang
- chapter_path → `<vol> 第N-M章`（單章時 `第N章`）

實證效果（chunks → 合併後）：
```
Vol 2:  433 → 71   (52 page + 19 other)
Vol 3:  762 → 91   (85 page + 6 other)
Vol 4:  742 → 152  (73 page + 79 other)
Vol 5:  611 → 105  (63 page + 42 other)
Vol 6:  684 → 139  (66 page + 73 other)
Vol 7:  489 → 79   (53 page + 26 other)
Vol 9:  349 → 92   (30 page + 62 other)
```

**坑 6: footnote 必須留 inline (不可剝到 footnotes dict)** — reader 的 `renderMarkdown` 是 SCAN content text 找 `——————` 分隔線 toggle 進 footnote mode、收集 (N) lines 到底部統一 section。如果 consolidator 把 footnote 剝掉 reader 就看不到。consolidate_letters 第一版犯了這錯，寫 [`_fix_letter_pages_inject_footnotes.py`](../../../scripts/_fix_letter_pages_inject_footnotes.py) 從 dict 重新注回 content（gitignore 一次性 hotfix，正式版 consolidate_letters 已修正）。

### D2: 同教父作品在目錄相鄰（parent_volume backfill）

[`backfill_parent_volume.py`](../../../scripts/backfill_parent_volume.py) — 用 90+ pattern 規則從 `volume` substring 推 `parent_volume`：

- 「依納爵...」 → 「依納爵」
- 「革利免致...」 → 「羅馬的革利免」（Vol 1 + Vol 9）
- 「革利免《...》」「革利免勸...」 → 「亞歷山卓的革利免」（Vol 2）
- 「特土良...」「佩爾佩圖亞...」 → 「特土良」
- 「俄利根...」 → 「俄利根」
- 「希波呂圖...」「居普良...」「該猶...」「諾瓦提安...」 → 對應教父
- Vol 6 minor fathers（亞歷山卓的彼得/亞歷山大/狄奧尼修...、阿凱勞斯、美多第烏、阿諾比烏 等）
- apocrypha (彼得福音/啟示錄/保羅異象/...) → 「(新約偽典)」/「(舊約偽典)」/「(殉道記)」

實證設定：Vol 2: 431 / Vol 3: 757 / Vol 4: 734 / Vol 5: 603 / Vol 6: 677 / Vol 7: 480 / Vol 9: 336 = **4018 chunks set parent_volume**。Vol 1 原本已有 107，現累計 reader 三層樹（parent → volume → entries）完整 work across 全部 ANF。

新卷的 SOP：consolidate_letters → backfill_parent_volume → validate。Reader 自動 group。

---

## 待精修書清單（按優先序）

| Order | Book | Status | 備註 |
|---|---|---|---|
| ✅ 1 | ANF Vol 1 | 已精修 | 黃金模板，validate 0 FAIL/WARN |
| ✅ 2 | ANF Vol 2 (Fathers of the Second Century) | 已精修 | Hermas/Tatian/Theophilus/Athenagoras/革利免（亞歷山卓）。validate 0 FAIL · 2 WARN |
| ✅ 3 | ANF Vol 3 (Tertullian Apologetic + Anti-Marcion) | 已精修 | 24 個 Tertullian 著作；曾遇 1362→762 dual-state bug。validate 0 FAIL · 0 WARN |
| ✅ 4 | ANF Vol 4 (Tertullian IV + Minucius + Commodian + Origen — De Principiis + Contra Celsum) | 已精修 | 首次 from-scratch 全自動。validate 0 FAIL · 0 WARN |
| ✅ 5 | ANF Vol 5 (Hippolytus + Cyprian + Caius + Novatian) | 已精修 | Hippolytus Refutation 深層巢狀。validate 0 FAIL · 0 WARN |
| ✅ 6 | ANF Vol 6 (Gregory Thaumaturgus + Dionysius + Africanus + Anatolius/Minor + Archelaus + Methodius + Arnobius) | 已精修 | 多東方教父。validate 0 FAIL · 0 WARN |
| ✅ 7 | ANF Vol 7 (Lactantius + Asterius + Victorinus + Didache + 使徒憲令 + 2 Clement + 早期禮儀) | 已精修 | title_en 走英文 NCX label 不走 anf07.* 前綴 → 用 boundary-based v2 修。validate 0 FAIL · 0 WARN |
| ✅ 8 | ANF Vol 8 (Twelve Patriarchs + Excerpts + Pseudo-Clementine + NT Apocrypha + Decretals + 早期敘利亞文獻) | 已精修 | dual-state bug (1633→1238)、EN_PARENT_TO_ZH 收 133 page-vol、D1 251 chunks (112 page)、D2 247 parent、glossary +40/+28、validate 0 FAIL · 0 WARN |
| ✅ 9 | ANF Vol 9 (彼得福音 + 狄阿特撒龍 + Apocalypses + Visio Pauli + Apocryphal Acts) | 已精修 | dual-state bug (497→349)、45 unique vols、D1 D2 都套。validate 0 FAIL · 1 WARN |
| ✅ 10 | ANF Vol 10 (Bibliography + General Index) | minimal | CCEL EPUB 無正文，僅 header 譯，不標精修 |
| ✅ 11 | NPNF1 Vol 1 (Augustine Confessions + Letters) | 已精修 | consolidate_by_ncx + 中文 relabel（懺悔錄卷一-十三/書信）|
| ✅ 12 | NPNF2 Vol 4 (Athanasius) | 已精修 | prefix-vol 22 著作 + consolidate_letters，762 TERM 收斂 |
| ✅ 13 | NPNF1 Vol 2 (City of God + On Christian Doctrine) | 已精修 | **fix_npnf_tree.py** 首用：上帝之城 22 卷 |
| ✅ 14 | NPNF1 Vol 3 (Holy Trinity + Doctrinal/Moral Treatises) | 已精修 | fix_npnf_tree |
| ✅ 15 | NPNF1 Vol 4 (Anti-Manichaean + Anti-Donatist) | 已精修 | fix_npnf_tree |
| ✅ 16-25 | NPNF1 Vol 5-14（駁伯拉糾派…奧古斯丁 V5-8 + 金口若望 V9-14）| 已精修 | 金口若望命名鎖定 |
| ✅ 26-29 | NPNF2 Vol 1（優西比烏）/ 2（蘇格拉底+索佐門）/ 3（狄奧多勒+耶柔米）/ 5（尼撒格列高里）| 已精修 | 巢狀 override (vol26/28) |
| ✅ 30 | NPNF2 Vol 6（耶柔米 Jerome — 書信 + 論著 + 導論）| 已精修 | NVIDIA 4 帳號 deepseek 收尾；`_fix_vol30_jerome.py` 把 115 英文 NCX 卷名 relabel 成繁中 + 三層樹（導論/序言/論著/書信）；validate 0 FAIL/0 WARN · test_fathers_quality PASS |
| ✅ 31 | NPNF2 Vol 7（耶路撒冷的區利羅《教理講授》+ 拿先斯的格列高里《講演集》《書信集》）| 已精修 | `_fix_vol31_cyril_gregory.py`；TERM 1352 處（西瑞爾→區利羅/額我略→格列高里/巴西略→巴西流）；test_fathers_quality PASS；glossary+B層待補 |
| ✅ 32 | NPNF2 Vol 8（凱撒利亞的巴西流 — 論聖靈 + 六日創造論 + 書信集）| 已精修 | `_fix_vol32_basil.py`；4 作品 WORK 層+sequential；TERM 1691 處（巴西略→巴西流 ×1049/該撒利亞→凱撒利亞）；test_fathers_quality PASS；書信逐封繁中+glossary+B層待補 |
| ✅ 33 | NPNF2 Vol 9（普瓦捷的希拉里 + 大馬士革的若望）| 已精修 | `_fix_vol33_hilary_damascus.py`（PREFIX_TO_VOL 雙作者樹：論三位一體 12 卷/論會議/詩篇講道 + 正統信仰詳解 4 卷）；Haiku-first 翻譯（免費池乾）；TERM 222 處；test_fathers_quality PASS。**約翰/若望不收斂**（約翰福音=約翰、大馬士革的若望=若望，分工正確）|
| ✅ 34 | NPNF2 Vol 10（米蘭的安波羅修）| 已精修 | `_fix_vol34_ambrose.py`；⚠️ 章節源順序跨論著錯置（spot-check 證實）→ 不假造論著樹，**粗分三區（導論/論著選/書信選）**；隔離 consolidate 壞檔重譯；TERM 670 處（盎博羅削→安波羅修）；test PASS |
| ✅ 35 | NPNF2 Vol 11（蘇皮修 + 勒蘭的文生 + 若望‧格西安）| 已精修 | `_fix_vol35_reorder.py`（修 translate 排序 bug 還原順序）+ `_fix_vol35_severus_vincent_cassian.py`（boundary-walk 三作者樹）；TERM 701 處（瑪爾定/格西安/文生）；test_fathers_quality PASS · validate 0 FAIL |
| ✅ 36 | NPNF2 Vol 12（大良 Leo + 大額我略 Gregory）| 已精修 | title_en=npnf212.* 前綴→`_fix_vol12_leo_gregory.py` PREFIX-to-vol（大良 導論/書信集/講道集 · 大額我略 導論/牧靈規則/書信集）；570→108 頁；TERM baseline-only（利奧/良 同指教宗+皇帝，刻意不收斂）；test PASS · validate 0 FAIL |
| ✅ 37 | NPNF2 Vol 13（大額我略 II + 厄弗冷 + 阿弗拉哈特）| 已精修 | `_fix_vol13_gregory_ephraim_aphrahat.py` PREFIX-to-vol（大額我略 書信集卷九-十四 · 敘利亞的厄弗冷 讚美詩/聖詩/講道 · 波斯賢士阿弗拉哈特 論證集）；277→49 頁；TERM 430 處（艾弗冷→厄弗冷/亞弗拉哈特→阿弗拉哈特/波斯智者→賢士；**圖爾的格列高裡先保護成格列高里**再 格列高裡→額我略，避免併到 Gregory of Tours；以法蓮≠艾弗冷不碰）；test PASS · validate 0 FAIL |
| ✅ 38 | NPNF2 Vol 14（基督教會七大公會議）| 已精修 | `_fix_vol14_councils.py` PREFIX-to-vol（trailing-dot key 防 vii./viii. 誤配；單 parent「基督教會七大公會議」+ 15 區段：7 大公會議+教區/地方會議法規+使徒法典附錄）；722→88 頁；TERM 西里爾→區利羅/聶斯脫裡→聶斯脫里/格列高理→格列高里（**避碰 大額我略二世=教宗 Gregory II、Leo 利奧/良=教宗+皇帝**）；test PASS · validate 0 FAIL。**🎉 Schaff 全集 38 卷收官** |

---

## 2026-05-29 譯名決策（拉丁/希臘/亞美尼亞/敘利亞/科普特五傳統分流）

apply_translation_decisions_20260529.py 已套到 DB + Vol 1-9 chunks。**之後新譯卷必須遵循此標準**：

| 傳統 | 原則 | 代表性對應 |
|---|---|---|
| 拉丁 (Roman Catholic) | Clemens/Gregorius `-us` 字尾保留古典漢語譯名 | **羅馬的克勉**（Clemens, ≠ Klēmēs）／**額我略**（去掉「大」前綴）|
| 希臘東方教父 | 保留 `-os/-ios` 多音節，避免拉丁化字尾干擾 | **亞歷山卓的革利免**（Κλήμης）／**拿先斯的格列高里**（「里」非「理」）／**亞歷山卓的區利羅**（≠ 西里爾）／**凱撒利亞的巴西流**（≠ 大巴西略；巴西略 → 巴西流）|
| 亞美尼亞 | 凸顯子音結尾 (`r`)，不套希臘/拉丁尾 | **啟蒙者格里高爾**（Grigor Lusavorich）|
| 敘利亞 | 還原閃米特喉音/塞音/閉音節，拒希臘/希伯來化 | **敘利亞的厄弗冷**（Aphrem）／**尼尼微的伊沙克**（≠ 以撒）／**波斯賢士阿弗拉哈特**（亞→阿）／**他提安**（學術慣譯保留）|
| 科普特 (2026-06-12 user 拍板) | **僅限「名字本為科普特語」的原生埃及/沙漠教父**；希臘化亞歷山卓教父（名本希臘）仍走希臘。原生名按**波海里腔**還原，拒希臘/拉丁尾 | **帕宏**（Pachomius ⲡⲁϧⲱⲙ，≠帕科繆）／**舍努特**（Shenoute ϣⲉⲛⲟⲩⲧⲉ，純科普特）／**皮紹依**（Pishoi/Bishoy）／**帕夫努特**（Paphnutius ⲡⲁⲡⲛⲟⲩⲧⲉ）／**奧諾夫里**（Onnophrius，←埃及 Wennefer）／**貝薩**（Besa）／**菲布**（Phib）|

### 同名分流（重要）

- **革利免 vs 克勉**：
  - 羅馬的克勉（Clemens, 拉丁）→ Vol 1（1st/2nd Clement）、Vol 7（2 Clement）、Vol 8（Pseudo-Clementine 偽克勉文集 + Two Epistles 論貞潔書信）、Vol 9（Epistles of Clement）
  - 亞歷山卓的革利免（Κλήμης, 希臘）→ Vol 2（《教師》《雜文集》《富者得救》《勸勉希臘人辭》)；Vol 8 狄奧多托殘篇也是亞歷山卓的
- **格列高里/額我略**：教宗 Gregory I → 額我略；其他 Gregory（Naz/Nyssa/Palamas/Sinai/Thaumaturgus）→ 一律「格列高里」（「里」非「理」）
- **巴西流 vs 巴西略**：Basil the Great → 凱撒利亞的巴西流；歷史上任何 Basil(eios) → 巴西流。**禁用「巴西略」**
- **區利羅 vs 西里爾（Κύριλλος 同字根、按人/受容傳統分流）**：
  - 教父（希臘文底本）→ **區利羅**：亞歷山卓的區利羅、耶路撒冷的區利羅。V14 已收斂 西里爾/西瑞爾→區利羅（皆亞歷山卓主教）。
  - 斯拉夫人的使徒 St Cyril/Constantine（9c，與美多德造字）→ 斯拉夫式 **西里爾**（即「西里爾字母 Cyrillic」）。**「西里爾」非錯字，是這一位的定名**，遇到斯拉夫使徒語境不可收斂成區利羅。
- **科普特第五支（2026-06-12 user 拍板定案，已入庫）**：四傳統（拉丁/希臘/敘利亞/亞美尼亞）加 **科普特** 為第五支，
  **範圍限「名字本為科普特語」者**——希臘化亞歷山卓教父（區利羅、亞他那修）名字本是希臘名、科普特只借用，**仍走希臘**
  （故 Cyril of Alex = 區利羅，不取科普特活誦讀音 Kirollos/كيرلس）。科普特支真正適用：沙漠/原生埃及教父，名字
  希臘-拉丁化反失真者。原則：原生科普特名按**波海里腔（現存禮儀腔）**還原，拒希臘/拉丁尾。
  **定案譯名（`seed_glossary_coptic.py` 已入 `theologians` 表，first_source=「科普特第五支」）**：
  - Pachomius → **帕宏**（ⲡⲁϧⲱⲙ Pakhom，≠帕科繆/巴霍米烏斯）· Shenoute → **舍努特**（ϣⲉⲛⲟⲩⲧⲉ，純科普特無希臘對應）·
    Pishoi/Bishoy → **皮紹依**（ⲡⲓϣⲱⲓ）· Paphnutius → **帕夫努特**（ⲡⲁⲡⲛⲟⲩⲧⲉ Papnoute，≠帕弗努提烏斯）
  - Onnophrius/Onuphrius → **奧諾夫里**（ⲁⲃⲉⲛⲛⲟⲫⲣⲓⲟⲥ ←埃及 Wennefer）· Besa → **貝薩**（ⲃⲏⲥⲁ，舍努特繼任者）· Phib → **菲布**（ⲫⲓⲃ，帕宏同伴）
  - **邊界（仍走希臘/聖經，不入科普特支）**：Macarius the Great = **馬卡里烏斯**（Μακάριος 希臘名）· Antony = **安東尼** · Moses the Black = **摩西** · Poemen 走希臘音譯。
  - 流程依 [[feedback_glossary_ancient_name_priority]]：候選先列清單給 user 逐一定奪後才入庫（本批已完成）。

### 新譯卷起手 checklist

翻譯前先 `/translation-glossary` 頁面查 5 個 tab 對應，特別注意：
1. 若該卷含 Pseudo-Clementine / Apocrypha → 確認 Roman Clement 用「克勉」
2. 若含 Cappadocian Fathers (Basil/Gregory Naz/Gregory Nyssa) → 「巴西流／格列高里」
3. 若含 Cyril of Alex. → 「區利羅」不是「西里爾」
4. 若含 Syriac 教父 → 確認 Aphrahat 用「阿弗拉哈特」、Isaac of Nineveh 用「伊沙克」

`sweep_book_quality.TERM_FIXES_ANF_COMMON` 可加 cross-vol baseline 規則，新卷翻完一律 `sweep --only-t8` 套一遍收歛變體。

---

## 🚧 下個 session 接手清單（2026-06-03 更新 — 新 session 監測用）

**使用者指令**：開放式循環 — 一次跑 1 卷（配額緊，2-way 以上會互卡），translate → 精修
→ glossary → REFINED → commit/push，自動接下一卷沿 NPNF2 順序跑。已授權整晚自動 +
auto-push。**git 在 master 跑教父**（user 拍板；feat/coach-language 是別人的功能分支，別碰）。

### ✅ 已完成精修上架（master，test_fathers_quality 全 26 卷 PASS）
- **ANF Vol 1-9**（前次）
- **NPNF1 全 14 卷**：V1-4（前次）+ V5-14 本輪
  （駁伯拉糾派/登山寶訓/約翰福音講道/詩篇講解/金口若望 V9-14）
- **NPNF2**：V1 優西比烏 · V2 蘇格拉底+索佐門 · V3 狄奧多勒+耶柔米+魯菲努斯 ·
  V4 亞他那修（前次）· V5 尼撒的格列高里
- 譯名鎖定：**金口若望**（非屈梭多模）· **狄奧多勒**（非狄奧多雷）· **格列高里**（里非理）

### ✅ 本輪完成
- **vol30 NPNF2 V6 耶柔米** `d229a6d4-14de-4e28-92de-4855c75cbf68` — translate（NVIDIA 4 帳號 deepseek
  收尾）→ polish → consolidate_by_ncx → `_fix_vol30_jerome.py`（115 英文 NCX 卷名 relabel 繁中 +
  三層樹）→ validate 0 FAIL/0 WARN → test_fathers_quality PASS → REFINED_IDS。詞庫 backfill 未跑
  （配額；可日後補）。**B 層 LLM 校對未跑**（當晚全 provider 配額耗盡）— 日後配額足時補 `llm_proofread_book.py`。

### ✅ 本輪完成（2026-06-04）
- **vol31 NPNF2 V7（耶路撒冷的區利羅《教理講授》+ 拿先斯的格列高里《講演集》《書信集》）** `af2cf8a7-b169-432c-863d-632647c8ab67`
  - 翻譯 173→172 chunks（無 dual-state，zh 0.96）→ polish → consolidate_by_ncx（→137）→
    `_fix_vol31_cyril_gregory.py`（61 英文 NCX 卷名 relabel 繁中 + 72 書信本文按 NCX 收件人群組命名 +
    三層樹：耶路撒冷的區利羅／拿先斯的格列高里）→ consolidate_letters（→73，書信 10 封/頁）→
    `TERM_FIXES_NPNF2_V7`（1352 處）→ validate 0 FAIL → **test_fathers_quality PASS**（G1-G5 全綠，33 TERM 變體歸零）→ REFINED_IDS。
  - **譯名鐵則（詞庫權威）**：Cyril of Jerusalem = **耶路撒冷的區利羅**（西瑞爾/西里爾/居里羅 是變體，已收斂）；
    Cyril of Alexandria = 亞歷山卓的區利羅（兩 Cyril 都「區利羅」，靠教座前綴分辨）；
    Gregory（Naz/Nyssa）= **格列高里**（額我略只留教宗 Gregory I，已把誤譯的額我略 ×60 收斂）；
    Basil = **巴西流**（禁巴西略，已收斂 ×211）；Nazianzen = **拿先斯**（非納齊安）。
  - **未跑**（配額；可日後補）：詞庫 glossary backfill、B 層 `llm_proofread_book.py`。
- **vol32 NPNF2 V8（凱撒利亞的巴西流 — 論聖靈 + 六日創造論 + 書信集）** `3c48472c-fbca-48fb-9db1-ca5a08827ef3`
  - 翻譯 429 chunks（fresh，無 dual-state zh 0.99）→ polish → consolidate_by_ncx（→411）→
    `_fix_vol32_basil.py`（4 作品 WORK 層繁中 + work 內 sequential 編號，skill Tip 3；單作者三層樹）→
    consolidate_letters（書信中位數≥3000 不合併，每封一頁）→ `TERM_FIXES_NPNF2_V8`（1691 處）→
    validate 0 FAIL → **test_fathers_quality PASS**（34 TERM 變體歸零）→ REFINED_IDS。
  - 譯名：Basil=**巴西流**（收斂巴西略 ×1049）；Caesarea=**凱撒利亞**（收斂該撒利亞）；Gregory=**格列高里**（額我略只留教宗）。
  - **未跑**（配額）：書信 357 封逐封 recipient 繁中（目前 sequential「書信第N封」，bilingual reader 仍可見英文 recipient）、glossary backfill、B 層校對。
- **vol33 NPNF2 V9（普瓦捷的希拉里 + 大馬士革的若望）** `709f43f9-724c-4cd5-b6b0-570d26083d24`
  - Haiku-first 翻譯（免費池乾）131 chunks → `_fix_vol33_hilary_damascus.py`（PREFIX_TO_VOL 雙作者樹：
    論三位一體 12 卷/論會議/詩篇講道 + 正統信仰詳解 4 卷）→ consolidate_letters 131→42 → TERM 222 處 →
    test_fathers_quality PASS → REFINED_IDS。**約翰/若望不收斂**（約翰福音=約翰、大馬士革的若望=若望 分工正確）。
- **vol34 NPNF2 V10（米蘭的安波羅修）** `fd8a09e7-a6ab-4818-a6d7-6722e50da773`
  - ⚠️ **坑 4.6 踩過**：consolidate_by_ncx 對深層巢狀多論著打散順序 → 隔離 `.consolidate-corrupt.bak` + 重譯。
  - 章節源順序**跨論著錯置**（spot-check 證實 chunk140=Faith/200=Repentance 相鄰）→ 不假造論著樹，
    `_fix_vol34_ambrose.py` **誠實粗分三區（導論/論著選/書信選）** → consolidate_letters →55 → TERM 670 處
    （盎博羅削→安波羅修）→ test_fathers_quality PASS → REFINED_IDS。

### ✅ 本輪完成（2026-06-11）
- **vol35 NPNF2 V11（蘇皮修 + 勒蘭的文生 + 若望‧格西安）** `24c53ede-8787-442e-a3ba-0cd55d0effac` — **已精修上架**
  - 06-06 翻到 664 撞 Haiku 牆死、06-10 fresh 重譯又在 816 因三池全乾死掉 → 06-11 早上 `--engine haiku`
    fresh 第三次重譯，~3.7h 譯完 1204 chunks（zh 1.00 無 dual-state）。
  - **踩到坑 4.7（新）**：譯完 reader 順序跨作品亂掉 = translate 結尾用非唯一 title_en re-sort →
    `_fix_vol35_reorder.py` 用 source_text 比對 EPUB 文件順序還原（1204/1204），並根治 translate.py 排序鍵。
  - `_fix_vol35_severus_vincent_cassian.py` boundary-walk 三作者樹（蘇皮修《聖瑪爾定傳》/書信集/對話錄/
    存疑書信/神聖歷史 · 勒蘭的文生《勸誡錄》· 若望‧格西安《會院規章十二書》/《會談錄》三部/《論主之降生：
    駁聶斯脫里七書》）→ consolidate_letters 1204→132 → `TERM_FIXES_NPNF2_V11`（瑪爾定/格西安/文生，701 處）
    → test_fathers_quality PASS → REFINED_IDS。
  - **譯名（user 06-11 定）**：Martin of Tours=**瑪爾定**（非馬丁=路德同形；詞庫無此聖人條目）。
  - **未跑**（可日後補）：glossary backfill、B 層 `llm_proofread_book.py`。

### ✅ Schaff 全集 38 卷收官（2026-06-12）
- **ANF 10 + NPNF1 14 + NPNF2 14 = 38 卷全部已精修上架。** V11-V14 本輪 2026-06-11〜12 完成（見上表）。
- 譯名鎖定彙整：蘇皮修/勒蘭的文生/若望‧格西安/瑪爾定（V11）· 大良/大額我略（V12 user 拍板保留「大」）·
  敘利亞的厄弗冷/波斯賢士阿弗拉哈特（V13）· 區利羅/聶斯脫里/格列高里（V14）。
- **名稱收斂鐵則（V12-V14 反覆踩到）**：收斂前必 probe 變體 + spot-check 同名異人；sweep_t8 按 key 長度
  遞減套用，可用「長 key 先保護」處理雙人衝突（圖爾的格列高里、大額我略二世、以法蓮、皇帝李奧）。

### 🔄 下一步（待 user 指示）
- **ACCS 走向已轉軌（2026-06-12 user 拍板）**：不再走「英文整卷翻譯上 /fathers」，改為
  **把 ACCS 教父註釋嵌進 /scripture 聖經逐節閱讀器**（經文上‧註釋下，按段落 pericope）。
  → 新 skill **[[scripture-accs]]**（schema/parser/OCR/reader 全到位，創世記原型先做）。
  來源用**校園書房繁中版掃描 PDF**（Drive 27 冊 folder，含創世記）OCR，不再自譯英文。
  本 skill（scripture-fathers）只負責教父全集整卷；ACCS 註釋嵌入歸 scripture-accs。

### 🧭 本輪（2026-06-05〜10）關鍵改進與教訓（新 session 必讀）
1. **譯名修正**：Cyril of Jerusalem = **耶路撒冷的區利羅**（非西瑞爾；user 抓出、詞庫權威確認）。
2. **cp/mv footgun**：備份英文 jsonl 必須 `mv`（移走）非 `cp` —— 留下英文檔 `--resume` 會 skip 全部英文 chunk → dual-state。見 playbook step 0。
3. **引擎 `--engine haiku` 改 Haiku-first**（user Max 訂閱；免費池乾就直接開 Haiku，不空轉等 15:00）。見 [[feedback_engine_nvidia_no_haiku]]。
4. **坑 4.6**：多論著大卷（title_en=英文 NCX label）**勿跑 consolidate_by_ncx**（會打散順序），翻完直接 boundary-walk。
5. **🚨 resume 缺漏**：大卷（>500 chunk）崩潰**勿 resume**（title_en 重複→誤跳缺數百 chunk），改 fresh 重譯。
6. **不可 kill 別人任務**（[[feedback_no_kill_other_tasks]]）；只停自己這輪啟動、且 ebook-id 精準過濾的 process。
7. **git**：並行 mueller/jung 任務有 auto-commit/push hook，常造成 push 被拒（remote 領先）。本地 commit 安全，會跟下輪同步；**不要 stash/rebase 動到並行任務的 unstaged 檔**。

### ⚙️ 引擎現況（2026-06-04 重做 — 3-tier）
- 預設 **Gemini → NVIDIA → Haiku**（user 2026-06-04 統一政策「gemini 優先，然後 nvidia，最後 haiku」；見本檔頂 line 6 引擎政策 header）。
  - **Gemini**（主）4 keys，**每日太平洋午夜重置 ≈ 台灣 15:00**；撞牆退 NVIDIA。
  - **NVIDIA**（2nd）deepseek-v4-flash，**4 帳號 key round-robin + 每 key 429 cooldown 120s + 全域 6s 節流**。
    `NVIDIA_MODELS=["nvidia/nemotron-3-super-120b-a12b"]`（唯一保留段落對齊 + {{p:N}}/[^N] marker 的模型；
    qwen3-next 雖快但壓段落、毀 marker，**勿用**）。⚠️ **單帳號免費為「一次性/月 credit」非每日**，4 帳號約
    40 分鐘全耗盡，過夜不一定回血。
  - **Haiku**（3rd 救急）走 Claude Max OAuth，**前兩池都乾才動**；batch 久了 Anthropic 帳號也會 429
    （跟互動用量互搶），慢但能擠出。`_secondary`/`_gemini_or_haiku` helper。
- **G: Drive 寫入已韌性化**（`_drive_write`，2026-06-04）：Drive 斷線會退避重試（最多 ~30min）等 remount，
  不再 FileNotFoundError 硬崩。**踩過：6/04 上午 G: 掉線害 translate 崩在第 8 chunk**。
- 2026-06-03→04 引擎演進記錄：原 gemini→haiku → 試 nvidia-first（單 key 429/timeout 退回 gemini-first）
  → user 加 4 NVIDIA 帳號 → user 加 Haiku 第三層（一度定 NVIDIA-first）→ **2026-06-04 user 改回統一 Gemini-first（Gemini→NVIDIA→Haiku）**。相關 commit
  `5aa6fe9`(4-key round-robin)、Haiku 復活、G: 韌性。

### ⚙️ 操作鐵則（踩過的坑，務必遵守）
1. **每卷上架前跑 `python scripts/test_fathers_quality.py <id>` 綠燈才算數**（G1 validate 0 FAIL /
   G2 T9=0 / G3 T1=0 / G4 TERM_FIXES 變體全 0 / G5 無 dual-state）。
2. **🔁 Drive 同步會默默還原已上架卷**（雲端舊版蓋回本地 jsonl，變體/標題 bleed 回來）。
   `test_fathers_quality.py`（全跑）會抓到 → 對該卷 `sweep_book_quality.py <id>`（含 --only-t8/t1）
   重套即修。**ANF Vol2 已反覆中招**，新 session 定期全跑把關。
3. **NPNF2 巢狀 book bug**：fix_npnf_tree 把「Prolegomena 當卷一、含子書的大作 lumped 成單卷」。
   翻完 dry-run 一看卷數爆量（如某卷 150+ chunks）就知道中招 → 寫 `_fix_vol<N>_*.py`
   title_en prefix override（範本 `_fix_vol26_constantine.py` / `_fix_vol28_npnf2v3.py`），
   把真子書/導論/書信拆開。override 後若 `前言` 章號重複 → 重排 `前言` 章號（見 vol26/28 做法）。
4. **OAuth**：translate 讀 `~/.claude/.credentials.json`；token 過期會 Haiku 401。配額同時耗盡會卡死
   →（user 登入著時）token 會自動 refresh，kill+`--resume` 重啟即接上。Gemini 全 key exhausted →
   fallback Haiku；兩者皆掛就等配額重置。
5. 卡死/崩潰 → kill 該卷 python 行程 + `--resume` 重啟，partial chunks 不丟。
6. **glossary（/translation-glossary）已被改成「各領域獨立表」新架構，由別的作業負責，教父線別碰。**

### 接續佇列（NPNF2，逐卷；✅ 已全數完成 2026-06-12）
**V11-V14 已全部精修上架（見「Schaff 全集 38 卷收官」節）**：
V11 `24c53ede-8787-442e-a3ba-0cd55d0effac` / V12 大良 `02a08547-6fb5-44b2-8a59-9b1f625f3a54` /
V13 `90b55879-7179-41d7-9f6c-f6587a3dd429` / V14 七大公會議 `63853a97-68be-441c-8dce-063ae89405c5`。
ACCS 已轉軌至 [[scripture-accs]]（嵌進聖經逐節閱讀器，不再整卷翻上 /fathers）。**翻每卷前先 `/translation-glossary` 查該卷人物 ★建議譯名**（迦帕多家/區利羅
見 2026-05-29 譯名決策節）。

---

## 第三欄原文：中文 / 英文 / 拉丁‧希臘（2026-08-30 起）

教父卷本來是兩欄——`content` 繁中、`source_text` Schaff 英譯。補第三欄原典之後
就是使用者要的「中文 英文 原文」三欄。reader 本來就吃 N 欄
（`pages/fathers/[id].vue` 的 `v-for="lang in parallelColumns.langs"`），資料補上去
就會長出來，不必動前端。

```bash
python scripts/fathers_add_original.py --work augustine-confessions
python scripts/fathers_add_original.py --work all      # 改了對齊邏輯就整批重跑           # 只驗不寫
python scripts/fathers_add_original.py --work augustine-confessions --apply   # 寫回 JSONL
python scripts/upload_chunks_to_r2.py upload --id <ebook_id> --force          # 只重傳這一本
```

新增一部著作＝在 `scripts/fathers_add_original.py` 的 `WORKS` 登一筆：站上哪一本
ebook、原文語言、原典網址、**每卷幾章**（章數是原典的權威值，用來判站上缺不缺章，
不可以拿站上的章數回填）。純函式核心在 `scripts/fathers_original.py`，測試在
`scripts/tests/test_fathers_original.py`。

### 已收的原文（`WORKS` 登記表）

| 著作 | 站上冊次 | 原文 | 對齊 | 命中 |
|---|---|---|---|---|
| 奧古斯丁《懺悔錄》 | NPNF1 Vol 1 | 拉丁‧The Latin Library | 逐節 | 395/395（100%）|
| 奧古斯丁《上帝之城》 | NPNF1 Vol 2 | 拉丁‧The Latin Library | 逐章 | 539/557（97%）|
| 特土良 23 部 | ANF Vol 3 | 拉丁‧The Latin Library | 逐章 | 691/733（94%）|
| 特土良後期 8 部＋密努修 | ANF Vol 4 | 拉丁‧The Latin Library | 逐章 | 141/143（99%）|
| 使徒教父＋猶斯定＋偽依納爵 21 部 | ANF Vol 1 | 希臘‧First1KGreek TEI | 逐章 | 441/497（89%，見下）|
| 俄利根《駁塞爾蘇斯》八卷 | ANF Vol 4 | 希臘‧First1KGreek TEI | 逐章 | 589/589（100%）|
| 優西比烏《教會史》十卷 | NPNF2 Vol 1 | 希臘‧Perseus TEI | 逐章 | 118/118（100%）|
| 優西比烏《君士坦丁傳》＋兩篇頌辭 | NPNF2 Vol 1 | 希臘‧First1KGreek TEI | 逐章 | 233/233（100%）|
| 阿諾比烏《駁異教徒》七卷 | ANF Vol 6 | 拉丁‧The Latin Library | 逐章 | 301/322（93%）|
| 美多德《十處女宴飲集》 | ANF Vol 6 | 希臘‧First1KGreek TEI | 逐章 | 80/82（98%）|
| 巴西流《書信集》356 封 | NPNF2 Vol 8 | 希臘‧Perseus TEI | 逐段（見下） | 575/1168（49%）|
| 亞他那修《駁亞流派講辭》四篇 | NPNF2 Vol 4 | 希臘‧First1KGreek TEI | 逐節 | 185/196（94%）|
| 蘇皮丘‧塞維魯《編年史》兩卷 | NPNF2 Vol 11 | 拉丁‧The Latin Library | 逐章 | 104/105（99%）|
| 蘇皮丘‧塞維魯《聖瑪爾定傳》 | NPNF2 Vol 11 | 拉丁‧The Latin Library | 逐章 | 27/27（100%）|
| 勒蘭的文森《勸誡錄》 | NPNF2 Vol 11 | 拉丁‧The Latin Library | 逐章 | 33/33（100%）|
| 拉克坦提烏《論逼迫者之死》 | ANF Vol 7 | 拉丁‧The Latin Library | 逐章 | 52/52（100%）|
| 拉克坦提烏《神學原理》卷一 | ANF Vol 7 | 拉丁‧The Latin Library | 逐章 | 22/179（12%，那邊只有卷一）|
| 諾瓦提安《論三位一體》 | ANF Vol 5 | 拉丁‧The Latin Library | 逐章 | 26/26（100%）|
| 奧古斯丁《論三位一體》十五卷 | NPNF1 Vol 3 | 拉丁‧The Latin Library | 逐章 | 191/202（95%）|
| 蘇格拉底《教會史》七卷 | NPNF2 Vol 2 | 希臘‧First1KGreek TEI | 逐章 | 130/130（100%）|
| 索佐門《教會史》九卷 | NPNF2 Vol 2 | 希臘‧First1KGreek TEI | 逐章 | 205/205（100%）|
| 金口若望《論司祭職》六卷 | NPNF1 Vol 9 | 希臘‧Migne PG 48 自家 OCR | 逐節 | 40/50（80%）|
| 《佩爾佩圖亞與費莉西塔斯殉道記》 | ANF Vol 3 | 拉丁‧First1KGreek TEI | 逐章 | 6/6（100%）|
| 耶柔米《書信集》150 封 | NPNF2 Vol 6 | 拉丁‧Corpus Corporum（PL 22） | 逐節 | 474/482（98%）|
| 迦仙《會院規章》十二書 | NPNF2 Vol 11 | 拉丁‧Corpus Corporum（PL 49） | 逐章 | 216/270（80%）|
| 迦仙《會談錄》第一部（1–10） | NPNF2 Vol 11 | 拉丁‧Corpus Corporum（PL 49） | 逐章 | 245/245（100%）|
| 迦仙《會談錄》第二部（11–17） | NPNF2 Vol 11 | 拉丁‧Corpus Corporum（PL 49） | 逐章 | 72/120（60%）|
| 迦仙《會談錄》第三部（18–24） | NPNF2 Vol 11 | 拉丁‧Corpus Corporum（PL 49） | 逐章 | 99/127（78%）|
| 迦仙《論主之降生》七書 | NPNF2 Vol 11 | 拉丁‧Corpus Corporum（PL 50） | 逐章 | 111/111（100%）|

### 拉丁原典：The Latin Library 沒有的，先查 Corpus Corporum，不要動手 OCR

蘇黎世大學的 **Corpus Corporum**（mlat.uzh.ch）把**整套 Migne PL 做成了機讀 TEI**
——5,277 部、8,550 萬字、1,528 位作者，全部可取。先前判定「兩個易取的拉丁站都沒
有、只能走 PL 掃描本 OCR」的那幾位，其實全都在裡面：

| 作者 | Corpus Corporum idno | 部數 | 字數 |
|---|---|---|---|
| Hieronymus Stridonensis（耶柔米） | 879 | 104 | 231 萬 |
| Cyprianus Carthaginensis（居普良） | 878 | 18 | 15.2 萬 |
| Joannes Cassianus（迦仙） | 1063 | 4 | 23.7 萬 |
| Ambrosius Mediolanensis（安波羅修） | 958 | 45 | 110 萬 |

取法（前端是 JS，但底下兩支 PHP 端點可以直接打）：

```bash
# 目錄：/38 是 Patrologia Latina 這個 corpus，往下是 作者 → 作品 → 文本
curl "https://mlat.uzh.ch/php_modules/navigate.php?load=/38/879&group_by="
curl "https://mlat.uzh.ch/php_modules/navigate.php?load=/38/879/576&group_by="   # → 文本 idno
# 取 TEI 全文
curl "https://mlat.uzh.ch/php_modules/download.php?idno=7132&type=file-xml"
```

已查到的文本 idno：耶柔米《書信集》7132、迦仙《會院規章》7531／《會談錄》7530／
《論主之降生》7557、居普良《論教會的合一》127（其餘 17 部同一層取得到）。

#### 多卷著作：卷次一定要逐塊寫死在 spec 裡，不可以讓機器配

`cc-book` 模式把中譯依「章號掉回第一章」切成一塊一卷，再把塊配到原典的卷。配對
**不自動做**——spec 的 `blocks` 逐塊明列卷次（`None` ＝那一塊不收），而且每一筆都
是讀過該塊第一章的中譯與拉丁文確認過的。

🚨 **「章數相等而且唯一」不足以當配對的依據。** 迦仙《會談錄》第三部的第一塊有
   16 章，原典第十八次會談有 17 章、第十九次剛好 16 章——自動配就唯一地配到第
   十九次去了。兩邊都是同一位作者的沙漠會談錄，逐章排得整整齊齊，命中率 100%。
   是讀了第一章才發現中譯寫「我們如何來到狄奧爾科斯並受到皮阿蒙修士長的接待」而
   拉丁文是「論保羅長老的共居修院，及某兄弟的忍耐」。

🚨 **卷次配對正確，章號仍可能整卷錯開一位。** NPNF 的中譯把 Migne 的某一章拆成兩
   章：《會院規章》第一、八、十一書與《會談錄》第十三、十七、十八、二十次都多一
   章。多出來的那一章之後整卷往下錯一格，而每一格都還是同一卷、同一題材。所以
   **即使 spec 指名了卷次，章數不相等的那一塊照樣整塊留空**——迦仙這五部因此少
   收了 7 卷，命中率從「看起來的」92% 降到 80%。少收的是錯的那些。

🚨 **中譯可能整卷沒收，而且不留任何痕跡。** 《會院規章》缺原典第六書〈論淫亂之
   靈〉、《會談錄》缺第十二與第二十二次會談。中譯那邊只是「第五場爭戰」接著「第
   三場爭戰（貪財）」——章號自己從一重來，看不出中間少了一整卷。`blocks` 那一列
   的跳號就是這件事的紀錄。

🚨 **譯者導論會混進來。** 《會院規章》那個前綴的第一塊是 NPNF 譯者寫的〈若望‧格
   西安的生平〉〈格西安著作的歷史、手稿及版本〉兩章，不是迦仙的書。硬配的話會拿
   到《會院規章》第一書的頭兩章——都是拉丁散文，讀起來完全正常。

🚨 **`<emph>` 幾乎都是 Migne 的欄號**（1,123 個裡 1,113 個是純數字），而且夾在句子
   中間（`Saepe <emph>1</emph> a me…`）。不剔掉的話拉丁文裡會冒出一串莫名其妙的
   數字。`<note>` 一樣要剔、tail 一樣要接回去。`strip_apparatus()` 兩件一起做。

🚨 **每一封信的第一段是 Migne 的 argumentum（內容提要），不是正文。** 150 封裡有
   27 封的第一節沒有自己的 `<div3>`，正文落在 `<div1>` 那一層的 `<p>`——不認出提要
   的話那 27 封的第一節全部拿到提要。提要是第三人稱的拉丁散文，貼在第三欄讀起來
   完全像正文。判法：那一段幾乎整段包在 `<hi>` 裡（斜體）。

🚨 **節不一定是 `<div1>` 的直屬子節點。** 有序言或問題目次的信（117、120、121）多
   一層 `<div2>`，只找直屬子節點的話那三封整封空著，而其餘 147 封滿分——看起來像
   那三封本來就沒有原文。用 `iter()` 找後代。

🚨 **信號取 `<div1>` 的順序，不取 head 裡的羅馬數字。** 126 封寫成「EPISTOLA XVI.」，
   另外 24 封寫成「EPISTOLA XLVIII,」（逗號）或整個沒有 head。但兩者一致與否是最好
   的閘：150 個 div1 逐一比對全部相符，所以順序可信。不符就整封不收。

### 希臘原典先查 First1KGreek，不要動手 OCR

**Open Greek and Latin 的 First1KGreek** 有機讀的 TEI，涵蓋面比預期廣得多：
使徒教父（tlg1271 革利免／tlg1443 伊格那丟／tlg1622 坡旅甲／tlg1216 巴拿巴）、
猶斯定（tlg0645 三部＋tlg0646 致丟格那妥）、亞歷山卓的革利免（tlg0555）、
**俄利根（tlg2042）**、愛任紐（tlg1447，但只有希臘殘篇）。

```
https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/{作者}/{作品}/{檔名}.xml
```

🚨 **檔名不統一**，不要照 `{作者}.{作品}.1st1K-grc1.xml` 套——有的是 `opp-grc1`、
   有的是 `perseus-grc2`。先用 GitHub contents API 列目錄取實際檔名。

🚨 **`chapter_path` 與內文可以整批對不上，而且是漸進的。** 耶柔米那一冊（NPNF2
   Vol 6）的中譯少收了第 130、133、135 封，路徑卻照著目錄一路排下去——於是從第
   140 段起每一段的標題都指著**前一封**信，到第 158 段時路徑還寫著〈致貴婦切蘭提
   婭〉，內文已經是《保羅隱士傳》了。用 chapter_path 當鍵的話那三十幾段會整批配到
   隔壁那封信的拉丁文：同一位作者、同樣的書信文體，讀起來完全正常。

   **這一冊的信號一律由內文自己的標題讀**（`declared_letter_no()`）。同一冊裡至少
   十四種寫法：第一信／信件第四封／Letter VIII./第十一函／十二、／書信第十三封／
   XVI./第二十二封／信簡四十／信函 L./第60封信／第一三一號／信第一百四十四封／
   信件CL.。「第一三一號」是逐位寫的（131），「第一百三十一」是進位寫的，兩種都要認。

   🚨 取**最早出現**的那個編號，不是「第一種成立的寫法」。〈書簡 LVI〉的導言第二句
      就寫著「寫給耶柔米的第一封信」，先試「第N封信」那一式會讀成第 1 封——而第 1 封
      本來就在，於是同一段拉丁文被貼到兩個地方，兩邊都通順。

   🚨 取**最長的那一串**，不是第一串。這一冊的〈導論〉六節編成 I.–VI.，照樣成立一串
      「第 1–6 封」而且排在最前面。取第一串只會收到那六段導論——而那六段真的配上了
      耶柔米前六封信的拉丁文，六段都是拉丁散文，看不出問題。閘是三條一起：從宣告
      「第一封」起算、段序連續、信號嚴格遞增。

   **這一冊的 chapter_path 本身還沒修**（第 140 段之後的標題、以及第 158 段起被安到
   論著上的書信標題都還是錯的）。第三欄是對的，標題還是錯的——要修得重跑分段。

🚨 **前綴叫什麼不代表那一段裝的就是那部。** 耶柔米那一冊的「首位隱士保羅傳」那一
   段裝的其實是《駁路西弗派對話錄》，「被擄修士馬爾庫斯傳」那一段裝的是《駁約維
   尼安》的綱目。兩部的拉丁本 The Latin Library 都有，接上去命中率也有 20–26%，
   內容卻全不相干。同一冊的「致瑪爾切拉」那十七段倒是乾乾淨淨（書信 XXIII 起，
   每段開頭就寫著編號）。**動工前先讀那一段的第一段中文**。

   耶柔米這一冊的書信已收（2026-09-02，474/482）：走 Corpus Corporum 的 PL 22
   TEI，見上面那一節。**同一冊末尾的論著（〈首位隱士保羅傳〉那一批）仍然不能收**
   ——那幾段的 chapter_path 與內文根本不是同一部書，見下一條。

🚨 **原典把序也編成第一節時，整篇會差一章。** 《佩爾佩圖亞殉道記》拉丁本的第一節
   是序，ANF 的章號從序之後才起算——站上第一章＝拉丁本第二節。差一章的錯位讀
   起來完全通順（都是同一段殉道敘事），命中率照樣 6/6。spec 用 `chapter_offset`
   修正。判法：拿站上第一章的**正文**（不是章標題）去比對，別看標題。

🚨 **偽依納爵長篇本十三封在 `tlg1443.tlg002`，而檔裡的 `n` 不照傳統排序。** 實際是
   1 致瑪利亞、2 特拉勒、3 馬內夏、4 他爾索、5 腓立比、6 非拉鐵非、7 士每拿、
   8 坡旅甲、9 安提阿、10 黑羅、11 以弗所、12 羅馬、13 瑪利亞致依納爵。照傳統排序
   猜 `#N` 會整封配到別封——章數相近的那幾封（士每拿 14 / 特拉勒 14）看起來會完全
   正常。取檔後先印每一封的 `<head>` 對過再寫進 spec。
   《坡旅甲殉道記》是另一個 tlg（1484.tlg001，24 章），不在 tlg1622 底下。

🚨 **ANF 第一卷的中譯分段是「自己這部的尾巴＋下一部的開頭」。** 「依納爵致他爾索
   人書」那一段收的是他爾索書第 9–10 章，接著就是《致安提阿人書》的第 1–6 章；
   「致特拉勒人書」那兩段的後半是《致羅馬人書》第一到第六章（章題「作為囚犯」
   「容我成為野獸的獵物」都是羅馬書的）。照編號查的話那幾列會拿到本部的希臘文
   ——同一位作者、同樣的文體，讀起來完全正常，而命中率是 100%。

   `align_part()` 現在兩道一起用，**順序不能反**：先按 chapter_path 宣告的章範圍
   濾掉離得太遠的（差幾章很正常，分段處常多一兩章；差十章以上就是別部的），再在
   濾完的序列上找「掉回第一、二章」的地方切斷。反過來的話，《駁黑摩根》第一章前
   面那個誤讀的「21.」會造成假重編，整部 1–45 章全被切掉（實測 46→7）。
   代價是 ANF 第一卷從「496/497」變成 441/497——少掉的那 55 列本來就是配錯的。

   根治要在分段那一層（cross-work bleed，見本 skill 前面的 multi_h3_splitter）。

⚠️ **偽依納爵長篇本不要拿來補那七封真書。** 一度以為那個「第二遍章號」是長篇本，
   把 `tlg1443.tlg002` 對應的那封當第二卷餵進去、靠 `assign_books()` 分——排出來
   100%，但配的是別封信。是先讀了中譯的章題才發現的。

🚨 **一個前綴壓了好幾部著作時，那個「卷N」不是原典的卷次。** NPNF1 第三卷的
   「奧古斯丁教義論集」一個前綴壓了七部：卷一是《論三位一體》十五卷、卷二是
   《信望愛手冊》122 章…。這個「卷」是第幾部著作，拿去查原典的卷次會全錯。
   spec 加 `site_book` 挑出那一部並把卷次拿掉，之後就走一般的分卷判斷。
   （這一冊先前被預檢判成「未分篇」而跳過——其實是分了，只是分在卷次那一層。）

🚨 **行標第六種：`[I 1]` 開新章、`[2]` 是同一章的下一節。** 奧古斯丁《論三位一體》
   是這樣。用 `parse_bracketed_chapters` 讀會把 `[2]` 當成第二章——卷一變成 21 章
   （實際 13 章），而且每一章都從節的中間開始，讀起來完全通順。

🚨 **原典電子本只收了第一卷時，錯配是七卷份的。** 拉克坦提烏《神學原理》站上是
   七卷連號的第1-188章、中譯逐卷重編（1–23、1–20、1–30…），而 The Latin Library
   只有卷一 23 章——直接查的話每一卷的第 5 章都會配到卷一第 5 章。上面那條
   「有分卷＋LIS 低」的規則擋不住（原典只有一卷）。判準是**站上宣告的章數遠超過
   原典的章數**（188 vs 23）。擋掉之後 per 只填得出卷一那 22 章，其餘照實空著。

   反例要留意：依納爵那幾封書信的編號也會從頭再走一次（6…12、1…6），但那是短、
   長兩種抄本各編一次號、走的是同一封信，flat 給的是對的。所以不能只看「編號有
   沒有掉回 1」。

🚨 **行標又多一種寫法：`章 (節) 正文`。** 蘇皮丘‧塞維魯《編年史》《聖瑪爾定傳》
   的章號在行首、節號用括號夾、同行接正文（`1 (1) Res a mundi exordio…`）。
   `parse_chapter_markers()` 對這種回 0 章。用 `parse_dotted_chapters(mark=PAREN_MARK)`。
   同一冊的迦仙（《會院規章》285 章、《會談錄》24 篇）已收（2026-09-02）：走
   Corpus Corporum 的 PL 49/50 TEI，見上面那一節。

🚨 **「編號變小＝換了一卷」這種回頭偵測不可靠。** 亞他那修《駁亞流派講辭》四篇
   的中譯節號各自從一起算，而 chapter_path 的「第1章…第35章」只是分段序號、給不
   出任何範圍。`book_of()` 的回頭偵測被資料裡的重疊騙到——第8章收 1–9、第9章又
   從 1 開始（但兩段都還在第二篇）——切出八篇而不是四篇，命中率 31%，錯配的那些
   看起來完全正常。改用原典自己給的資訊：每篇幾節是已知的（64/82/67/36），在
   「同一篇內遞增、不超過該篇節數」的限制下用 DP 找最多錨點成立的切法
   （`assign_books()`），94%。`align_part()` 現在同時算四種鍵法取最高分。

🚨 **書信集沒有章可以對，只有段落順序——所以寧可空著。** 巴西流《書信集》的
   Perseus TEI 只有 letter 一層，信裡的分段是 `<p>`，不帶編號。NPNF 中譯的節號
   走本篤版的分節，一節常等於原文兩三段（第五封：中譯 2 節、原文 4 段），356 封
   裡段數真的相等的只有 92 封。硬排的話第二節配到第二段，往後整封錯開一格而讀
   起來完全通順。`align_letter()` 因此只在三種確定的情形下填：收信人那一行對
   `<head>`、剩下的段數剛好相等、或中譯只剩一段（整封併進那一格）。
   另外有 88 封的中譯把收信人與正文第一段併成一段——不認出來的話段數會少一段，
   而少一段有時剛好等於原文段數，整封位移一格照樣填滿。靠第二段的長度判別。

   《論聖靈》三十章與《六日創世講道》九講兩個 TEI 庫都沒有（Perseus 的 tlg2040
   只有 tlg002、tlg004），要補得走 Migne PG 29／32 自家 OCR。

🚨 **中譯的「第N章」與內文的「N.」可能是兩套編號。** 阿諾比烏《駁異教徒》七卷的
   chapter_path 是整部連續號（第71-80章），內文卻是逐卷重編的（第二卷第六章寫成
   「6.」）。直接拿「6」查整部第 6 章，七卷全部查得到、報 100% 命中，內容卻全是
   第一卷的。`align_part()` 因此同時算三種鍵法取最高分，並在「這一部有分卷 ＋ 錨
   點的最長遞增子序列不到六成 ＋ chapter_path 自己沒帶卷次」時直接把連續鍵法判
   死。判準不能只數「編號掉了幾次」——《駁黑摩根》正文裡一個誤讀的「21.」就掉兩
   次，那本其實是乾淨的 1–45。

🚨 **The Latin Library 的檔案可能是節本。** 阿諾比烏第七卷該有 51 章，那邊只收到
   第 34 章；另有 2.19、5.25、7.16、7.17 四章沒有行標。前六卷的章數（65/78/44/37/
   45/27）與中譯完全吻合，所以累計基底是對的，缺的部分就照實空著。

🚨 **The Latin Library 會擋。** 短時間內連抓會回 Cloudflare 的 Access Denied，而
   `strip_html()` 照樣回一份「內容」——解析出 0 章，看起來像網站改版。帶
   User-Agent、抓完隔幾秒。

🚨 **站上的「卷N」不一定等於原典的卷N，而且位移不一定是固定的。** 優西比烏那一冊
   標到「教會史 卷十三」，但《教會史》只有十卷：卷一是譯者導論、卷十是附錄〈巴勒
   斯坦的殉道者〉、卷十三是補充註釋，真正的十卷散在卷二–卷九與卷十一–卷十二。用
   固定偏移的話最後兩卷會配到別卷的希臘文**而照樣顯示滿分**。所以 spec 支援
   `book_map` 逐卷明列，沒列到的不收。**動工前先逐卷印出第一段內容確認。**

🚨 **同一個目錄裡可能混著英譯檔，不可盲取第一個 xml。** 優西比烏 tlg2018/tlg002 在
   First1KGreek 有 `1st1K-eng1`（英文）與 `1st1K-grc1`（只有 4,815 個希臘字元的殘
   本）；完整希臘本在 Perseus 的 `perseus-grc2`（54.7 萬字元）。**取檔後先數希臘
   字元再決定用哪個。**

🚨 **章那一層不一定叫 `chapter`。** 提阿非羅《致奧托呂庫書》那份只有 book/section
   兩層，硬找 chapter 會解析出 0 章。`parse_tei_chapters()` 找不到就退用 section。

🚨 **TEI 有 `book` 這一層時，鍵一定要帶卷次。**《駁塞爾蘇斯》八卷的章號各自從一
   起算（71/79/81/99/65/81/70/76 章）。只用章號當鍵的話八卷互相覆蓋，最後每一卷
   都拿到第八卷的內容——**命中率照樣滿分**，三欄照樣排得整整齊齊。單卷著作
   （伊格那丟、革利免）沒有那一層，卷次留 None。

🚨 **`<note>` 是校勘註釋，必須整個剔掉**，但刪的時候要把它的 `tail` 接回去，
   否則註釋後面那一截正文會一起消失，而讀者看到的仍是一段通順的希臘文。

🚨 **伊格那丟七封真書裝在同一個 TEI 檔**（`subtype="epistle"` n=1..7，Migne 順序
   是以弗所／馬內夏／特拉勒／羅馬／非拉鐵非／士每拿／坡旅甲）。序號錯一位，希臘
   文照樣通順，只是換了一封信——**收之前一定要逐封驗專有名詞與章數**（以弗所
   21+序、馬內夏 15+序、特拉勒 13+序、羅馬 10+序、非拉鐵非 11+序、士每拿 13+序、
   坡旅甲 8+序）。驗的時候記得把大小寫與音調正規化，`ΕΦΕΣΙΟΥΣ` 不會直接等於
   `Ἐφεσ`。

只有 First1KGreek 沒收的才走 Migne PG 掃描本的自家 OCR（見 `fathers_pg_ocr.py`）
——金口若望就是那種情況（tlg2062 不在裡面）。

### 作品名比對要「完全相符」，不可以 startswith

🚨 ANF 第一卷同時收〈依納爵致以弗所人書〉與〈依納爵致以弗所人書（敘利亞文版）〉。
   敘利亞短本是另一個文本，用 startswith 就會把標準希臘本配到它身上，而三欄照樣
   排得整整齊齊（命中數還從 24 變成 34，看起來像進步）。用 `work_name()`。

🚨 `work_name()` 也要剝掉單獨的「卷N」後綴：《懺悔錄》卷二整卷收成一段，路徑沒有
   「第N章」，不剝就會被當成另一部著作而整卷跳過（395 → 379）。

### 逐章查表一定要帶卷次

🚨 《上帝之城》22 卷，每卷章號都從一起算。查表漏掉卷次的話，卷十三的第一章會拿到
   **卷一**第一章的拉丁文——命中率 514 看起來還不錯，其中卻有一部分是別一卷的內容。
   帶回卷次後 539/557。只有真正沒有卷這一層的單卷著作才退回 `(None, n)`。

### 兩個 TEI 庫收了誰 —— 別再一部一部猜

問 GitHub 的 `contents/data`，作者代號那一層一次就拿得到（First1KGreek 309 個、
Perseus 100 個）；作者夾底下的 `__cts__.xml` 有 `groupname`，可以直接對名字。

實測 tlg2000–2130 之間兩庫合起來只有 27 個作者代號，**尼撒的格列高里
（tlg2017）、耶路撒冷的西里爾（tlg2110）都不在**——那兩冊不用再找了。有的但還
沒用到的：tlg2021 Epiphanius、tlg2041 Marcellus、tlg2058 Philostorgius。

### 挑下一冊：先跑 `fathers_alignability.py`

```bash
python scripts/fathers_alignability.py                 # 全 39 冊總覽，按可對齊部數排序
python scripts/fathers_alignability.py --volume 4e3d   # 某一冊逐部細看
```

補第三欄靠的是**中譯裡的錨點**（節號或章標題）。原典再齊全，中譯這邊沒有錨點就
放不上去——而腳本只會回報「命中 0」，看起來像取源壞掉。這支預檢一次分辨兩種死路：

- **未分篇** —— 一冊把好幾部獨立著作壓成一個前綴（安波羅修「論著選」340 章）。
- **中譯失去章結構** —— 逐部切得乾淨，但每部內文的「第N章」標題不見了。
  ANF 第二卷就是這樣：革利免《雜文集》八卷只剩 16 個標題（該有 154 個），英文側
  連標題都沒有、中文側也沒有頁錨，整冊排在 39 冊的最後段（3 可對齊部／13）。

### 挑下一冊之前，先看那一冊「有沒有逐部切開」

🚨 別憑節號密度挑。我曾照節號密度（89%）挑了安波羅修，結果 NPNF2 Vol 10 把《論
   教牧職分》《論聖靈》《論奧祕》《論懺悔》《論童貞》壓成單一個「論著選 第1–340
   章」，跟《論三位一體》是同一個病，根本做不了。要看的是 chapter_path 有幾個不
   同的作品前綴：前綴多＝逐部切開；前綴少而章號很大＝被壓成一團。

已知被壓成一團、要先重新分篇才收得了的：NPNF2 Vol 10（安波羅修「論著選」340 章
一個前綴）、NPNF1 Vol 3（奧古斯丁教義論集 244 章）、NPNF1 Vol 4（駁摩尼派／駁多
納徒派）、ANF Vol 5（居普良論述集 196 章）、NPNF1 Vol 8（詩篇講解 149 章）。

反過來，逐部切得乾淨、還沒做的與各自的取源狀況：

- **NPNF2 Vol 4（亞他那修 24 部）** — 希臘，First1KGreek 沒收，要 PG 25–26 OCR。
- ~~ANF Vol 4 的俄利根~~ — 《駁塞爾蘇斯》八卷已收（tlg2042/tlg001，589/589）。
  同冊的《論原理》**不收**：希臘文只存 Philocalia 裡的殘篇，完整本是盧菲努的拉丁
  譯（PG 11），First1KGreek 沒有。硬拿殘篇去配會讓四卷大部分留白而看不出原因。
- **NPNF2 Vol 6（耶柔米 20 部）** — 拉丁有，但那一冊是按「收信人」分部（致瑪爾切
  拉、致奧古斯丁…），要先做「收信人 → 書信編號」的對照表才接得上。
- **ANF Vol 7（Lactantius 17 部）** — The Latin Library 只有《神學原理》第一卷
  （188 章裡的 23 章），取源太薄，要另找 CSEL 或 PL。

### 一冊多部：`parts`

一冊裡收了好幾部各自獨立的著作（特土良那冊 23 部）就用 `parts` 逐部登記，每部
有自己的 chapter_path 前綴與原典網址。同一個前綴登記多個網址＝那一部原典分成
好幾卷；`parts_of()` 會把它們併成同一部。

🚨 **多卷著作的中譯有兩種編號習慣，同一冊裡都有，機器分不出來。**《駁馬吉安》
五卷是整部連續編號 1–145（原典各卷的章號要累計接續才對得上，不累計就是 0/145）；
《論婦女裝飾》兩卷卻是每卷從第一章重來（要按卷分開對，卷次靠章號回頭偵測）。所以
`fetch_original()` 兩種鍵都備好，`align_part()` 各對一次、取命中高的那個——猜錯的
那一種通常是 0 命中，差距非常明顯。

### 原典的章標寫法，同一個網站同一位作者就有五種

The Latin Library 的特土良：`I. [1] …`（行首羅馬數字接正文）／`I` 獨佔一行／
`Capitulum I`／`CAPUT 1.`（阿拉伯數字）／整篇不換行只能在行中找 `CAP. 1.`。
所以 `parse_chapter_markers()` 不預設任一種，五種都掃一遍取命中最多的。

🚨 `CAP` 後面的句點可有可無：de Ieiunio 只有第一章寫「CAP.  I.」，其餘全是
   「CAP II.」。硬要那個句點，那一篇就只認得出第一章（實測 3/15 → 15/15）。

🚨 每一種都要允許**行首縮排**。少了 `[ 	]*`，只要那個檔的行有縮排就一個章標也
   掃不到，而腳本只回報「命中 0」——看不出是格式沒對上還是原典真的沒有那些章。
   實測有四部就是栽在這裡。

🚨 章號序列用**最長遞增子序列**挑，不要用「最多往後跳 N 章」的門檻。
   de Praescriptione 那個檔本身就缺第 4–22 章，III 之後直接跳 XXIII，門檻一擋
   就只剩三章。但也不能完全不管：正文裡任何大寫羅馬字母加句點的行（縮寫、人名
   縮寫）都會被讀成天文數字的章號，把後面整串毀掉。LIS 兩邊都顧得到。

🚨 章內文要切到「下一個章標**之前**」。切到之後的話每一章都會把下一章的標記吞
   進來，畫面上只是多幾個字，實際上章與章的邊界整個錯開。

🚨 **《論三位一體》先別做**。拉丁原文有（`augustine/trin1–15`），但站上 NPNF1 Vol 3
把它和《創世記字義解》等併成一個「奧古斯丁教義論集」，共用同一組卷號，從
chapter_path 分不出哪一卷屬哪一部。硬接會把《創世記字義解》的中譯配上《論三位
一體》的拉丁文。要收得先把那一冊重新分篇。

### 對齊靠古典編號，不靠語意

The Latin Library 的行標 `1.11.17` ＝ liber.caput.paragraphus，而站上的中英譯段落
開頭正好帶著同一組**節號**（「17. 我自幼就聽聞了…」／「17. Even as a boy I had
heard…」）。那是唯一可靠的鍵。

另有第四種 `roman`：原典行標是章號（見下「原典的章標寫法」），中譯只有「第N章」
標題 → 逐章對齊。特土良全集那一系。

🚨 **只按章對會錯**。一章十節的拉丁若整團塞給該章第一段，之後整欄往下錯開，而
畫面上完全看不出來。首例《懺悔錄》按節對齊命中 395/395。

沒有節號的著作（《上帝之城》這一系）退一級走 `mode: "chapter"`：原典行標是方括號
羅馬數字（`[Pr]` `[I]` `[II]`，序言記為第 0 章），對到中譯的「第N章」標題。粗，
但位置是對的——粗而對，好過細而錯位。

🚨 **卷次一律用 `zh_numeral()` 現算，不要列舉對照表。** 先前的 `ZH_NUM` 只列到
「二十」，《上帝之城》有 22 卷，卷二十一與卷二十二整整兩卷靜靜地沒被解析到：腳本
照跑、不報錯，只是那兩卷沒有原文。

### 三道防線（都是在擋「看起來成功的失敗」）

1. **覆蓋率閘** —— 站上章節 vs 原典章節逐卷比。首跑就抓到站上《懺悔錄》卷一只到
   第 18 章、**第 19–20 章中英文都不存在**。書打得開、讀起來順，兩章卻不見了。
2. **對不上就留空，絕不往下順推。** 順推一次，之後整欄全錯。
3. **頁尾導覽列過濾**（`SITE_CHROME`）—— The Latin Library 每頁末尾的站台連結位在
   最後一個段標「之後」，不擋就會被接到該卷最後一節的尾巴，13 卷全中。

### 對照欄的等段數契約

`zipParallel` 按索引 zip，而 reader 重建欄位時 `.filter(Boolean)` 會丟掉空白段。所以
只填部分位置的欄位，空位必須放 `BLANK_PARAGRAPH`（U+200B，見
`lib/multilang-sources.ts`）——普通空字串與 NBSP 都會被 trim 掉，一被丟掉，之後每
一列都上移。

### 覆蓋率閘會分辨兩種缺口

- 「站上中譯沒有第 N 章」＝ 我們的中譯缺內容。實例：《懺悔錄》卷一第 19–20 章、
  《上帝之城》卷十三第七章（中譯從第六章直接跳到第八章）。
- 「原典電子本沒有第 N 章」＝ 取源網站自己缺。實例：The Latin Library 的 civ18
  從 `[XXXI]` 直接跳到 `[XLVII]`，中間 15 章根本沒收。

責任歸屬不同，處理方式也不同（前者要補譯，後者要換取源），所以訊息分開講。

### ⚠ 既有問題：中英兩欄本身有 10% 嚴重錯位

補第三欄時量出來的：全教父 4,611 段裡，**中英正文段數不符 3,241 段（70%），相差一
倍以上 451 段（10%）**。根因是英譯那側常有**沒有配對的註釋分隔線**——一條
`———…`（15 字以上）就把它之後的整段正文都歸成註釋，正文憑空少掉。例：《懺悔錄》
卷七第 21 章，中文 24 段、英文只剩 3 段。

最嚴重的幾冊：Chrysostom 使徒行傳講道集 34%、奧古斯丁詩篇釋義 27%、Gregory
Thaumaturgus 卷 27%、Chrysostom 論司鐸職分 24%。

**2026-08-31 已修，且不動任何既有資料**：改成 reader 端在渲染前用共有錨點重排來源
欄（`alignByAnchors`，`lib/multilang-sources.ts`）。三把鑰匙，取配對最多的那把：

| 鑰匙 | 樣子 | 覆蓋 |
|---|---|---|
| 節號 | 「17. 我自幼就聽聞了…」／`17. Even as a boy…` | 29% |
| 頁錨 | `{{p:226}}`（parser 在兩側都會輸出） | 27% |
| 章號 | 「第二章——…」／`Chapter 2.—…`／`Chapter II.` | 9% |

合計 65% 的段落改走錨點對齊，其餘 35% 沒有共有標記（多半是前置頁）維持索引對照。

🚨 **取配對最多的，不是第一個有命中的。**《上帝之城》卷十三有 3 個共有頁錨、4 個
共有章號；先到先贏會選到較粗的頁錨，章標題就整整差一列。

🚨 錨點必須在**渲染成 HTML 之前**抓——節號與 `{{p:NNN}}` 一旦變成 HTML 就沒了。

排除過的假設：分隔線門檻（15 個破折號）訂太高。量過，降到 8 個也只從 30% 變 31%，
不值得動這條全站共用的規則。

---

## 跟 [[ebook-translate]] 的分工

| 範圍 | 歸屬 |
|---|---|
| 教父原典翻譯（Schaff / ACCS） | **scripture-fathers**（本 skill）|
| 教父詞庫整合（/translation-glossary backfill）| **scripture-fathers** |
| CCEL EPUB packaging 處理 | **scripture-fathers** |
| multi_h3_splitter / cross-bleed | **scripture-fathers** |
| /fathers 頁面 contract | **scripture-fathers** |
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
- [[scripture-canon]] — 《基督教大藏經》教父卷的逐卷連結由 `scripts/dazangjing_link_fathers.py` 解析
- [glossary.md](../ebook-translate/glossary.md) — 教父人名／聖經書卷／神學術語 markdown 表（DB 之外的補充）
