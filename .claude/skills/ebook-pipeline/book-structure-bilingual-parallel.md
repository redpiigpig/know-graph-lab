# Bilingual-Parallel Books — Reader Spec

雙語並列參考書（如 Denzinger《公教會之信仰與倫理教義選集》拉中對照、未來各種 ACCS 雙語、思高拉中本聖經注釋等）的 reader 結構。

擴充自 [book-structure-spec.md](./book-structure-spec.md)，**完全向後相容** — 新欄位 optional，不影響現有 1896 本 `standard` mode 書。

> 🟢 **Status**: 設計階段 2026-05-27。Denzinger 中譯 PDF (ebook_id `568726d3-967e-457a-ab69-7452b21d606f`, 2430 頁) OCR 跑完後，本 spec 用來指導 segmenter + reader Vue 實作。

---

## 1. Book metadata 新欄位

`ebooks` table 加一欄：

| 欄 | 型別 | 預設 | 說明 |
|---|---|---|---|
| `display_mode` | `text` | `'standard'` | reader 模式選擇器 |

值：
- `'standard'` — 現有 reader（單欄、cover hero、楷書 blockquote 等，golden template 《基督教要義》驗證）
- `'bilingual-parallel'` — 雙欄並列（Denzinger / 雙語 ACCS / 思高拉中聖經注釋等）
- `'reference-indexed'` — 預留給 CIC 教會法典之類「以條號為導航主軸」的書

---

## 2. Chunk schema 擴充

沿用 [book-structure-spec.md §每 chunk 必要欄位](./book-structure-spec.md#每-chunk-必要欄位) 的 schema，新加 4 個 optional 欄位**只給 bilingual-parallel 用**：

| 欄 | 型別 | 例 | 說明 |
|---|---|---|---|
| `source_lang` | `'en' \| 'lat' \| 'grc' \| 'heb' \| 'syr'` | `'lat'` | 平行欄語言（既有 schema 只有 `'en'`，本 spec 擴充值域） |
| `dh_number` | `int?` | `1235` | 唯一 DH/canon 編號 — jump anchor |
| `dh_range` | `[int, int]?` | `[1228, 1230]` | 連續多條合一 chunk 時的範圍 |
| `section_type` | `'header' \| 'entry' \| 'commentary'?` | `'entry'` | render hint |

`section_type` 三種：

- `'header'` — 大公會議名稱／教宗在位期／通諭名稱等分段標題。**全寬跨兩欄渲染**。
  - chunk content：標題＋年代範圍 markdown
  - source_text：可空
  - chapter_path：例「特利騰大公會議 (1545-1563) ▸ 第三會期 信德象徵令」
- `'entry'` — 一條 DH 教義條目。**雙欄並列渲染**。
  - chunk content：中文翻譯
  - source_text：拉丁／希臘原文
  - chapter_path：例「DH 1235 — 任何暴君法令」
  - dh_number 必填
- `'commentary'` — 編譯者註、歷史背景、出版書目。**單欄中文渲染**（跨兩欄寬）。
  - chunk content：中文註解
  - source_text：空（commentary 純中文）
  - chapter_path：例「DH 1235 註解」

舊 `chunk_type` 仍維持 DB CHECK constraint 三值（`page/chapter/section`）：
- `'header'` → `chunk_type='chapter'`
- `'entry'` → `chunk_type='section'`
- `'commentary'` → `chunk_type='section'`（區分靠 `section_type` 欄）

---

## 3. Reader layout

```
┌──────────────────────────────────────────────────────────────────┐
│ 〔書名〕                              [中／中拉／拉] [DH 跳轉 ____] │  ← 頂條
│ 〔chapter_path〕                                                  │  ← 麵包屑
├────────────────────────────────────┬─────────────────────────────┤
│  ▸ Latin column                    │  繁體中文                    │
│                                    │                              │
│ 1228 Christus sine talibus         │ 28. 沒有這些魯愚的部目，    │  ← 'entry'
│      monstruosus capitibut         │     基督更好地藉由散居…    │     dh_number=1228
│      per suos veraces discipulos…  │                              │
│                                    │                              │
│ 1229 Apostoli et fideles…          │ 29. 在教宗職位被建立之前… │
├────────────────────────────────────┴─────────────────────────────┤
│ ① 註解（commentary — 跨欄）                                       │
│ 1407 年 11 月 23 日，布吿勞 (Burgundy) 公爵約望謀殺奧爾良…       │  ← 'commentary'
├──────────────────────────────────────────────────────────────────┤
│ Section header（跨欄）                                            │  ← 'header'
│ # 康士坦茨大公會議 (1414-1418) ▸ 第十六場會議 (1415-07-06)        │
├────────────────────────────────────┬─────────────────────────────┤
│ 1235 Quilibet tyrannus potest…     │ 任何暴君可以由其任何封…     │  ← 'entry'
└────────────────────────────────────┴─────────────────────────────┘
```

### CSS grid layout

```css
.bilingual-reader {
  display: grid;
  grid-template-columns: [latin] 1fr [zh] 1fr;
  column-gap: 2rem;
}

/* 'entry' rows: 兩欄 */
.entry .latin-col  { grid-column: latin; }
.entry .zh-col     { grid-column: zh; }

/* 'header' & 'commentary': 全寬 */
.header, .commentary {
  grid-column: latin / -1;
}

/* DH badge floating left of Latin col */
.dh-badge {
  position: sticky;
  left: -2.5rem;
  width: 2.5rem;
  font-weight: 700;
  color: rgb(180 83 9);  /* amber-700 */
  font-family: ui-serif;
}
```

### 三段顯示切換（toolbar 切換鈕）

| 模式 | CSS 控制 | 用途 |
|---|---|---|
| 中拉對照 | 兩欄都顯示（預設）| 研究、神學翻譯比對 |
| 僅中文 | `.latin-col { display: none }`、grid 改 1fr | 一般閱讀 |
| 僅拉丁 | `.zh-col { display: none }`、grid 改 1fr | 學者用 |

實作：頂條三段 toggle button → 改 root class（`.mode-zh-only` / `.mode-lat-only`），CSS 切換顯示。

### DH 跳轉

頂條 `<input>` 接受 DH 番號（如 `1520`），按 Enter →
- 查 chunk 內 `dh_number === 1520` 或 `dh_range` 包含
- `el.scrollIntoView({ behavior: 'smooth', block: 'start' })`
- URL hash 同步 `#dh-1520` 方便分享

### Sidebar TOC

沿用 [book-structure-spec.md §TOC 顯示標準](./book-structure-spec.md#toc-顯示標準-reader-ui) 規則：
- 父著作 (volume) 樹（教宗 / 大公會議 chronological）
- 子節 anchors（會期 / 通諭）
- 單頁 vs 多頁 volume 同樣的 ▸/▾ 規則

範例 Denzinger TOC：

```
壹 ▸ 本書介紹                 (front matter, no volume)
貳 ▸ 如何應用                 (front matter)
參 ▸ 閱讀指南                 (front matter)
肆 ▸ 詳細目錄                 (front matter)
─────
[時代分段，按 DH 編號]
1-100      使徒時代 (1-2 世紀)            volume
  ├─ DH 1-30 …
101-450    早期 (3-5 世紀)               volume
  ├─ DH 100-200 尼西亞 325
  ├─ DH 215-301 君士坦丁堡 381
  ├─ DH 250-300 以弗所 431
  └─ DH 300-350 迦克墩 451
451-1450   中世紀                        volume
  ├─ DH 600 第二次君士坦丁堡 553
  ├─ …
  ├─ DH 800-870 拉特朗 IV 1215
  └─ DH 1200-1240 康士坦茨 1414-18 ← 任何暴君法令在此
1500-1900  特利騰大公會議 1545-63        volume ★★★
  ├─ DH 1500-1539 Session 3-4 信德
  ├─ DH 1520-1583 Session 6 成義 ★
  ├─ DH 1635-1661 Session 13 聖體
  └─ …
3000-3075  梵蒂岡第一屆 1869-70           volume
  ├─ DH 3000-3045 Dei Filius
  └─ DH 3050-3075 Pastor Aeternus
3300-4100  19-20 世紀通諭                 volume
  └─ DH 3475-3500 Pascendi 1907 反現代主義
4100-4500  梵蒂岡第二屆 1962-65            volume
  └─ DH 4145 Lumen Gentium 21 主教祝聖
─────
附錄一 系統索引                            (back matter)
附錄五 基督教（新教）歷代信仰表白           (back matter, DH 5600-5680)
```

---

## 4. Segmenter pipeline

新 script `scripts/segment_denzinger.py`，將 OCR 完的 page-level chunks 轉成 DH-indexed chunks：

### 演算法

```python
def segment(page_chunks: list[dict]) -> list[dict]:
    """
    Input:  list of {chunk_index, chunk_type='page', page_number, content}
    Output: list of {chunk_index, chunk_type, section_type, chapter_path,
                     content, source_text, source_lang='lat',
                     dh_number?, dh_range?, page_numbers}
    """
    # Phase 1: detect DH boundaries + extract entries
    # Per page: split content into blocks by `^\s*(\d{3,5})\s+(.+)` markers
    # Classify each block as Latin (low CJK) or Chinese (high CJK)
    # Pair same-DH-number Latin + Chinese blocks

    # Phase 2: detect section headers
    # patterns: 第N場會議 | 教宗XXX (年-年) | 《XXX》 通諭 | 大公會議名稱
    # split into 'header' chunks at boundaries

    # Phase 3: detect commentary
    # blocks between DH entries that don't start with DH number
    # heuristic: contain phrases like "本選集 N 條" or 【出版】 or are 100% Chinese
    # → 'commentary' chunk

    # Phase 4: consolidate page_numbers (entries may span pages)
    ...
```

### Regex 草稿

```python
DH_MARKER  = re.compile(r'^\s*(\d{3,5})\s+(.+)', re.MULTILINE)
SECTION_RE = [
    re.compile(r'^第\s*\d+\s*場會議'),                  # 大公會議會期
    re.compile(r'^[A-Z][a-zA-Z]+[\s\w]+\s*\(\d{4}'),    # 教宗名 (年份)
    re.compile(r'^《.+》\s*通諭'),                       # 通諭名
]
COMMENTARY_HINTS = ['本選集', '【出版】', '【參考】', 'cf. DH']
CJK_RE = re.compile(r'[一-鿿]')
```

### 風險

OCR 噪聲：
- 部分 DH 番號被 OCR 誤抓鄰近頁碼（如「727」是書頁碼非 DH）→ 用「DH 範圍應遞增＋連續」過濾離群值
- 拉中混排在一頁底部時可能 Haiku 沒分乾淨 → fallback 啟 LLM-free 語言分塊
- 註解區可能混入拉丁引文 → 標 source_lang 但仍 commentary type

### 跑法

```bash
python scripts/segment_denzinger.py 568726d3-967e-457a-ab69-7452b21d606f
  --dry-run                       # 看 segment 結果不寫 DB
  --write-jsonl                   # 寫新 chunks 進 _chunks/{id}.bilingual.jsonl
  --apply                         # 真寫 DB + 更新 display_mode + R2 push
```

---

## 5. Reader Vue 改動

[pages/ebook/[id].vue](../../../pages/ebook/[id].vue)：

```vue
<script setup>
const { data: book } = await useFetch(`/api/ebooks/${id}`)
const isBilingual = computed(() => book.value?.display_mode === 'bilingual-parallel')
</script>

<template>
  <StandardReader v-if="!isBilingual" :book="book" :chunks="chunks" :toc="toc" />
  <BilingualReader v-else :book="book" :chunks="chunks" :toc="toc" />
</template>
```

新元件 `components/ebook/BilingualReader.vue`：
- 頂條三段切換 + DH 跳轉 input
- 主區用 CSS grid 渲染 chunks
- TOC drawer 共用既有 `EbookTocSidebar` 元件
- 註腳系統共用 `EbookFootnotes`（既有 `[^N]` 雙向 anchor 邏輯）

shared:
- cover hero（既有 `EbookCoverHero`）
- 編輯按鈕 ✏️（既有，但雙語編輯時要拆兩欄 textarea）
- 全文搜尋（既有，但 bilingual 要同時搜 content + source_text）

---

## 6. 驗證規則擴充

`scripts/validate_book_structure.py` 加 bilingual-parallel 專用 rule：

### STRUCTURAL（FAIL）

| Rule | 描述 |
|---|---|
| R030 | 若 `display_mode='bilingual-parallel'`，至少 50% chunks 有 `source_text` 非空 |
| R031 | `source_text` 非空時 `source_lang` 必填 |
| R032 | `dh_number` 在書內唯一（DH 番號不重複）|

### TOC / 內容（WARN）

| Rule | 描述 |
|---|---|
| R033 | `dh_number` 單調遞增（書內 DH 編號應大致排序）|
| R034 | `section_type='entry'` 必有 `dh_number` 或 `dh_range` |
| R035 | `section_type='commentary'` 不應有 `dh_number`（commentary 是註解、不是條目）|

---

## 7. 與 `/creeds` 接口

OCR + segmenter 完成後，**Phase D 抽 canon 中譯到 `/creeds`**：

```python
# scripts/_denzinger_to_creeds.py
# 對每場大公會議的 DH 範圍，取 Chinese chunks → 寫進 data/creeds/.../{slug}-chinese.txt
COUNCIL_DH_RANGES = {
    'early-03-ephesus':           (250, 268),
    'early-04-chalcedon':         (300, 305),
    'early-05-constantinople-ii': (421, 438),
    'early-06-constantinople-iii':(550, 559),
    'early-07-nicaea-ii':         (600, 605),
    'medieval-08-constantinople-iv': (650, 664),
    # ...
    'trent-04': (1501, 1508),  # Session 4 正典聖經
    'trent-06': (1520, 1583),  # Session 6 成義令
    # ...
    'vatican-i-df': (3000, 3045),
    'vatican-i-pa': (3050, 3075),
}
```

寫進每個 `-chinese.txt` 後，46 份中譯缺口一次補齊。

---

## 維護紀錄

| 日期 | 修改 |
|---|---|
| 2026-05-27 | 初稿；針對 Denzinger 2430 頁 OCR 結果設計；待 OCR 完成驗證 regex |
