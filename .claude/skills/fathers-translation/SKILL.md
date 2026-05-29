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

## 整晚自動精修一卷（unattended overnight playbook）

把 ebook_id 餵進這個流程，~6-8h 後完整精修上架。

```bash
EBOOK=<new-vol-ebook-id>

# 0. 備份原英文 JSONL，避免 dual-state bug
mv "G:/我的雲端硬碟/資料/電子書/_chunks/$EBOOK.jsonl" \
   "G:/我的雲端硬碟/資料/電子書/_chunks/$EBOOK.en.bak.jsonl"

# 1. 翻譯 (~3-6h)
nohup python -u scripts/translate_ebook_to_zh.py $EBOOK --engine gemini \
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
- `--engine gemini` 走 Gemini→Haiku 2-strike + 6h cooldown 自動切換（[[ebook-translate#gemini-haiku-2-strike-6h-cooldown-全域規則-2026-05-29]]）
- 並行多卷時兩卷切不同 engine 分散 quota
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
| 🔄 8 | ANF Vol 8 (Twelve Patriarchs + Excerpts + Pseudo-Clementine + NT Apocrypha + Decretals + 早期敘利亞文獻) | **翻譯中** | ebook `d09946ab-154b-4a97-853f-751cbb346221`；log `scripts/logs/translate_vol8_2026-05-29.log` |
| ✅ 9 | ANF Vol 9 (彼得福音 + 狄阿特撒龍 + Apocalypses + Visio Pauli + Apocryphal Acts) | 已精修 | dual-state bug (497→349)、45 unique vols、D1 D2 都套。validate 0 FAIL · 1 WARN |
| 10 | ANF Vol 10 (Bibliography + General Index) | 粗譯（小，4 chunks）| |
| 11 | NPNF1 Vol 1 (Augustine Confessions) | 粗譯 | |
| 12 | NPNF2 Vol 4 (Athanasius) | 粗譯 | |
| 13-38 | NPNF1 Vol 2-14 / NPNF2 Vol 1-3 + 5-14 + ACCS 待補卷 | 粗譯 | 重大用戶優先順序排定 |

---

## 🚧 下個 session 接手清單（2026-05-29 18:00 留）

當前 turn 主要完成：Vol 9 全套（dual-state/PREFIX/T1/glossary/REFINED_IDS）、D2 parent_volume backfill (Vol 2-9, 4018 chunks)、D1 consolidate_letters (Vol 2-9 半數 chunks 合進 page)、SKILL.md 更新。**下個 session 起手要做這些**：

### 立即做（Vol 8 接手）

Vol 8 (`d09946ab-154b-4a97-853f-751cbb346221`) 上個 session 已翻完 +
watchdog 已跑 Phase 4。下一步：

```bash
EBID=d09946ab-154b-4a97-853f-751cbb346221

# 1. 檢查 dual-state bug（仿 Vol 9）
PYTHONIOENCODING=utf-8 python -c "
import json, re
from pathlib import Path
p = Path('G:/我的雲端硬碟/資料/電子書/_chunks/$EBID.jsonl')
rows = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
en = zh = 0
for r in rows:
    c = r.get('content','') or ''
    if not c.strip(): continue
    zhr = len(re.findall(r'[一-鿿]', c)) / max(len(c),1)
    if zhr > 0.15: zh += 1
    else: en += 1
print(f'zh: {zh} / en: {en} (en>0 chunks 就有 dual-state，照 _fix_vol9_volumes.py 套路寫 _fix_vol8.py 刪英文重檔)')
"

# 2. Volume backfill
PYTHONIOENCODING=utf-8 python scripts/_fix_vol8_volumes.py

# 3. consolidate_letters
PYTHONIOENCODING=utf-8 python scripts/consolidate_letters.py $EBID

# 4. parent_volume backfill (Vol 8 vols 加進 backfill_parent_volume.py 後)
# 看 Vol 8 出來的 unique vols 是否要補規則：
PYTHONIOENCODING=utf-8 python -c "
import json
from collections import Counter
from pathlib import Path
p = Path('G:/我的雲端硬碟/資料/電子書/_chunks/$EBID.jsonl')
rows = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
for v, c in Counter(r.get('volume') for r in rows).most_common():
    if v: print(f'  {c:4d}  {v}')
"
# 補規則到 backfill_parent_volume.py 然後跑
PYTHONIOENCODING=utf-8 python scripts/backfill_parent_volume.py $EBID

# 5. T1 enhanced
PYTHONIOENCODING=utf-8 python scripts/sweep_book_quality.py $EBID --only-t1
PYTHONIOENCODING=utf-8 python scripts/validate_book_structure.py $EBID

# 6. glossary backfill (write seed_glossary_anf_vol8.py based on _vol9 template)
# 12 patriarchs, Pseudo-Clementine, Apostolic Constitutions, NT apocrypha 等

# 7. REFINED_IDS 加 d09946ab-... 進 pages/fathers/index.vue

# 8. commit + push
```

### 後續可選

- consolidate_letters 整合進 `_vol89_watchdog.py` 之類自動化流程（或退役 watchdog）
- 索引 chunks 改用 `chapter_type='index'`（reader 現用 `isIndexEntry()` regex，可動，但 type 判斷更穩定）
- Reader breadcrumb 顯示 `<教父><作品> 第N-M章` 而非只有 vol（如「居普良《論述集》第1-10章」）

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
