---
name: research-review
description: 「論文寫作」計畫的研究回顧／文獻綜述工具（/works 論文計畫頁底「研究回顧」分頁）— 把一篇研討會論文升級改寫成期刊論文時，附一份結構化文獻綜述：30+ 筆書目（作者／年／題／刊／語言／所屬面向／立場／摘要／全文連結），按 4 大主題脈絡分組；開放取用的外文文獻再抓全文逐段切段、逐段翻成繁中，左欄逐段中譯／右欄原文（英、德…）兩欄對照。架構仿 [[gnostic-library]]（documents/versions/sections 三表 + N 欄 reader），翻譯走 [[ebook-translate]] 引擎，解析／切段／對齊 gate 走 scripts/lit_review.py（純函式，test-first）。同時把 /works 拆成「書籍寫作 / 論文寫作」兩區。Use when 要把某篇研討會論文放進論文寫作計畫並做文獻綜述、新增／重抓某筆文獻全文、調研究回顧 reader、補逐段翻譯、把 /works 分書籍/論文。
---

> ⚙️ **引擎政策**：LLM 翻譯走 [[ebook-translate]] 既有 pipeline（章節級 Sonnet/Gemini + 逐段對齊 gate）。本 skill 不重造引擎、quota 協調、fallback。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：任一邊超過 2000px 會炸掉整個 session。

# 研究回顧 Skill（Literature Review — 原文/中譯 逐段對照）

把一篇**研討會論文**放進**論文寫作**計畫，作為改寫成**期刊論文**的工作底稿，並在該計畫頁底**「研究回顧」分頁**附一份結構化**文獻綜述**：

- **書目層**：每筆文獻的 作者／年／題名／刊名or出版社／語言／所屬面向／立場／摘要／全文連結，按報告的 **4 大主題脈絡**分組（文本考證／女性議題／詮釋爭論／跨傳統比較）。
- **全文層（選配）**：**開放取用**的外文文獻（JBE 全卷、漢堡大學 PDF、公有領域書）再抓全文 → 切段 → 逐段翻繁中 → **左欄逐段中譯／右欄原文**兩欄對照（英、德…皆同）。版權書只放書目＋摘要＋連結。

第一案＝**八敬法（aṭṭhagarudhammā）綜述**，掛在 `c1`〈昭慧法師的戒律學思想與實踐：以性別議題為核心〉論文計畫底下。

這是 portal 家族裡跟 `/gnostic` 最像的一塊（DB-backed、逐段對齊、N 欄 reader），差別只在**單位是「論文書目」而非「經典文獻」**，且**綁在 writing_project 底下**而非獨立 portal。

---

## 🟢 狀態

- ✅ **純函式核心（test-first，26 例綠）** — [scripts/lit_review.py](../../../scripts/lit_review.py) + [scripts/tests/test_lit_review.py](../../../scripts/tests/test_lit_review.py)：ref_key / 語言偵測 / 主題 taxonomy / 單筆 block 解析 / 整份綜述解析 / PDF-text 切段（去頁碼/running header/接合斷字）/ HTML 切段 / 對齊 gate
- ✅ **DB schema** — [database/lit-review-schema.sql](../../../database/lit-review-schema.sql)（`lit_review_entries` + `lit_review_sections` 兩表 + RLS public read + seed `orig`/`zh` 版本）；[database/writing-projects-v3-kind.sql](../../../database/writing-projects-v3-kind.sql)（`writing_projects` 加 `kind`(book/paper) + `paper_ref`）
- ✅ **/works 分區** — [pages/works/index.vue](../../../pages/works/index.vue) 拆「書籍寫作 / 論文寫作」兩區（依 `kind`）
- ✅ **reader + API** — [pages/works/[slug]/index.vue](../../../pages/works/[slug]/index.vue) 論文計畫頁底「研究回顧」分頁（按主題列書目）＋ [pages/works/[slug]/review/[ref].vue](../../../pages/works/) 原文/中譯兩欄逐段 reader；[server/api/lit-review/*.get.ts](../../../server/api/lit-review/)（entries / entry）
- ✅ **ingest 驅動腳本** — [scripts/ingest_lit_review.py](../../../scripts/ingest_lit_review.py)（`--seed` 入書目；`--fetch-fulltext --resume` 過夜抓全文＋翻譯）；報告原文存 [scripts/data/lit_review_eight_garudhammas.md](../../../scripts/data/)
- ⬜ **全文逐段對照**：開放取用文獻整批抓＋翻（過夜 `--fetch-fulltext --resume`，URL 多為 report 內 `......` 遮蔽需先 WebSearch 補實連結）

---

## 版權姿態

- **全文只收開放取用 / 公有領域**：JBE（Journal of Buddhist Ethics，全卷開放）、漢堡大學 buddhismuskunde PDF、blogs.dickinson.edu、聖嚴法師數位典藏、NTU 佛研、政大學術集成、towisdom / hongshi PDF、Horner 1930（PD）。
- **版權書（如某些合集）**：只放 `fulltext_status='unavailable'` 的書目＋摘要＋連結，不抓全文。
- **中譯欄永遠是逐段自譯**（同 [[gnostic-library]] / [[fathers-translation]] 姿態：第三方中譯不入庫）；中文文獻本身不需中譯欄（`language='zh'` → 不建 sections，書目層即可）。

---

## Schema（仿 gnostic，放 database/lit-review-schema.sql）

```sql
lit_review_entries (
  id BIGSERIAL PK,
  project_slug FK → writing_projects(slug) ON DELETE CASCADE ON UPDATE CASCADE,
  ref_key TEXT,                  -- make_ref_key()：'analayo-2016-the-foundation-history'
  authors, title, venue TEXT,
  year INT,
  language TEXT,                 -- 'en'/'zh'/'de'/…（detect_language）
  theme TEXT,                    -- 4 大脈絡之一（report `#` 主題標題）
  dimension TEXT,                -- 所屬面向（文本考證 / 詮釋爭論 …）
  stance TEXT,                   -- 立場（可空）
  abstract_zh TEXT,              -- 摘要（繁中）
  fulltext_url TEXT,
  fulltext_status TEXT,          -- pending / fetched / translated / unavailable
  display_order INT,
  UNIQUE(project_slug, ref_key)
)
lit_review_sections (            -- 只有抓了全文的外文文獻才有
  id BIGSERIAL PK,
  entry_id FK → lit_review_entries(id) ON DELETE CASCADE,
  version_code TEXT,             -- 'orig'（原文）/ 'zh'（逐段中譯）
  order_index INT,               -- 原文↔中譯 對齊鍵
  text TEXT, char_count INT,
  UNIQUE(entry_id, version_code, order_index)
)
```

對齊承諾：同一 `entry_id` 下，`orig` 與 `zh` 的 section **逐 order_index 一一對應**（`assert_aligned` 寫入前硬檢查）。

`writing_projects` v3 加 `kind`（`'book'` 預設 / `'paper'`）＋ `paper_ref`（連到 /papers 的 id，如 `'c1'`）。

---

## Pipeline（每筆文獻）

```
[0] --seed  讀 scripts/data/lit_review_*.md → parse_review_report()
       │      → {summary, gaps, entries[…]}；建/更新 paper 計畫 + upsert 書目
       ▼
[1] 補實連結  report 內 URL 多為 `......` 遮蔽 → WebSearch 補出真實 PDF/HTML 連結
       │      （版權書直接 fulltext_status='unavailable'，止步）
       ▼
[2] 抓全文   開放取用 PDF（pymupdf/pdfplumber 取文字）或 HTML（requests）
       │      → extract_paragraphs_from_text() / _from_html() → [原文段…]
       ▼
[3] 翻譯     每段原文→繁中（ebook-translate 引擎），術語照翻譯詞庫
       │      ⚠️ 逐段 upsert（不是整篇做完才寫）：學術 PDF 動輒 400+ 段
       │      （foundation.pdf=456 段），quota 一定中途斷；每翻完一段立刻
       │      存（missing_indices 算還沒翻的），--resume 從缺口接續、不重來
       ▼
[4] 狀態     全篇都翻完 → fulltext_status='translated'；中途斷 → 'fetched'（部分）
       │      reader 即時看得到已翻段落（未翻段顯示原文 + 「—」）
       ▼
[5] reader 驗證（研究回顧分頁 → 點該筆 → 左中譯／右原文 兩欄逐段）
```

翻譯引擎 / quota / fallback / 對齊重翻 — 全部沿用 [[ebook-translate]]。

---

## 純函式核心 — scripts/lit_review.py（test-first）

| 函式 | 作用 |
|---|---|
| `THEMES` / `THEME_LABELS` | 4 大主題 taxonomy（key / label / order）|
| `detect_language(label)` | 語言 label（英文/中文/德文…）→ ISO code |
| `make_ref_key(authors, year, title)` | 穩定 url-safe key；同作者同年用題名 slug 區辨；純 CJK 用 `zh<hash>` |
| `parse_entry_block(block)` | 單筆【作者】（年）〈題〉，《刊》… → dict（article 用〈〉、book 用《》）|
| `parse_review_report(md)` | 整份綜述 → `{summary, gaps, entries}`；每筆掛所在 `#` 主題 |
| `extract_paragraphs_from_text(text)` | PDF 取出的純文字 → 段落（去頁碼/running header/接合斷字）|
| `extract_paragraphs_from_html(html)` | HTML 全文頁 → 段落（去 script/style/nav）|
| `align_ok` / `assert_aligned(orig, zh)` | 逐段對齊 gate |

測試：`python -X utf8 -m pytest scripts/tests/test_lit_review.py -q`（26 例）。

---

## SOP — 新增一篇論文計畫 + 文獻綜述

1. 把綜述報告存成 `scripts/data/lit_review_<topic>.md`（沿用 user 給的格式：`#主題標題` 分組、`【作者】（年）〈題〉，《刊》`、`語言：`／`所屬面向：`／`立場：`／`摘要：`／`> **全文**：[label](url)`）。
2. `python -X utf8 scripts/ingest_lit_review.py --seed --report scripts/data/lit_review_<topic>.md --project <slug> --paper-ref <id>`：建 `kind='paper'` 計畫 + upsert 書目。
3. WebSearch 補實 report 內遮蔽的全文連結（更新 report 或直接 patch `fulltext_url`）。
4. 過夜 `python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project <slug> --resume --engine gemini`：抓開放取用全文 → 切段 → 逐段翻 → 對齊 → upsert。
5. 跑 reader 確認研究回顧分頁 + 兩欄逐段；commit + push（[[feedback-auto-push]]）；更新本 SKILL.md 狀態（[[feedback-skill-md-keep-current]]）。

## SOP — 補單筆 / 重翻
直接對該 `entry_id` 重抓＋重翻＋upsert（UNIQUE(entry_id,version_code,order_index) 覆蓋）。

---

## See also
- [[gnostic-library]] — 最近的同構案例（documents/versions/sections + 逐段對照 + 純函式 test-first）；本 skill 照搬其架構
- [[ebook-translate]] — 翻譯引擎 / quota / fallback / 對齊重翻
- [[translation-glossary]] — 佛教／宗教學名詞中譯（翻譯前鎖譯名；八敬法人名如 Anālayo 阿那律陀？先查詞庫）
- [[collected-works-multilang]] — N 欄逐段對照 reader 同源姿態
- /works（寫作計畫）— 本 skill 在其底下加 paper 區 + 研究回顧分頁
