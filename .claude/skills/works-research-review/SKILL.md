---
name: works-research-review
description: 「論文寫作」計畫的研究回顧／文獻綜述工具（/works 論文計畫頁底「研究回顧」分頁）— 把一篇研討會論文升級改寫成期刊論文時，附一份結構化文獻綜述：30+ 筆書目（作者／年／題／刊／語言／所屬面向／立場／摘要／全文連結），按 4 大主題脈絡分組；開放取用的外文文獻再抓全文逐段切段、逐段翻成繁中，左欄逐段中譯／右欄原文（英、德…）兩欄對照。架構仿 [[scripture-gnostic]]（documents/versions/sections 三表 + N 欄 reader），翻譯走 [[ebook-translate]] 引擎，解析／切段／對齊 gate 走 scripts/lit_review.py（純函式，test-first）。同時把 /works 拆成「書籍寫作 / 論文寫作」兩區。Use when 要把某篇研討會論文放進論文寫作計畫並做文獻綜述、新增／重抓某筆文獻全文、調研究回顧 reader、補逐段翻譯、把 /works 分書籍/論文。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：任一邊超過 2000px 會炸掉整個 session。

# 研究回顧 Skill（Literature Review — 原文/中譯 逐段對照）

把一篇**研討會論文**放進**論文寫作**計畫，作為改寫成**期刊論文**的工作底稿，並在該計畫頁底**「研究回顧」分頁**附一份結構化**文獻綜述**：

- **書目層**：每筆文獻的 作者／年／題名／刊名or出版社／語言／所屬面向／立場／摘要／全文連結，按報告的 **4 大主題脈絡**分組（文本考證／女性議題／詮釋爭論／跨傳統比較）。
- **全文層（選配）**：**開放取用**的外文文獻（JBE 全卷、漢堡大學 PDF、公有領域書）再抓全文 → 切段 → 逐段翻繁中 → **左欄逐段中譯／右欄原文**兩欄對照（英、德…皆同）。版權書只放書目＋摘要＋連結。

第一案＝**八敬法（aṭṭhagarudhammā）綜述**，掛在 `c1`〈昭慧法師的戒律學思想與實踐：以性別議題為核心〉論文計畫底下。

這是 portal 家族裡跟 `/gnostic` 最像的一塊（DB-backed、逐段對齊、N 欄 reader），差別只在**單位是「論文書目」而非「經典文獻」**，且**綁在 writing_project 底下**而非獨立 portal。

---

## 🟢 狀態

- ✅ **純函式核心（test-first，32 例綠）** — [scripts/lit_review.py](../../../scripts/lit_review.py) + [scripts/tests/test_lit_review.py](../../../scripts/tests/test_lit_review.py)：ref_key / 語言偵測 / 主題 taxonomy / 單筆 block 解析 / 整份綜述解析 / PDF-text 切段（去頁碼/running header/接合斷字）/ HTML 切段 / 對齊 gate
- ✅ **論文「真實參考文獻」並存（2026-06-04）** — 同一 paper 計畫可同時掛「主題綜述」（4 主題）＋「論文實際引用書目」（依文獻類型 7 類）＋「英文改寫補充文獻」（理論框架/英文研究）。parser 認得三套標頭（`THEMES` + `DOC_TYPE_THEMES` 佛典與檔案/專書著作/期刊文章/研討會與專書論文/學位論文/報刊與雜誌/網路文章 + `SUPPLEMENT_THEMES` 性別與佛教理論框架/台灣佛教與人間佛教，並 `SECTION_LABELS = 三者聯集`）；ingest 加 `--entries-only`（不覆蓋既有專案 meta）＋`--display-offset N`（排序）＋`--all-unavailable`（整份版權書目 → 只入書目＋連結）；reader（[pages/works/[slug]/index.vue](../../../pages/works/)）在第一個書目類型組前插入「論文參考文獻」分界標題。
  - 首案＝**c1〈昭慧法師的戒律學思想與實踐〉**，`bajingfa` 現有：八敬法綜述 29（display 0-28）＋真實參考文獻 39（[lit_review_zhaohui_references.md](../../../scripts/data/)，display 100+，全中文）＋英文改寫補充 9（[lit_review_zhaohui_en_supplement.md](../../../scripts/data/)，display 200+，版權 unavailable）＝**77 筆**。
  - **英文期刊改寫修改建議書**：[scripts/data/c1_英文期刊改寫_修改建議.md](../../../scripts/data/)（投稿定位 emic→etic／文獻回顧改 problem-driven／八敬法比較律藏六點論證鏈／逐節意見／候選期刊／action checklist）。
  - **不動論文原文 c1.txt**。
- ✅ **論文計畫頁改分頁（2026-06-04）** — [pages/works/[slug]/index.vue](../../../pages/works/) 對 `kind='paper'` 改成 tab：**研究回顧 / 修改建議 / 原文 / 書摘**（修掉「登入後空編輯器佔滿、其它都看不到」）。修改建議＝抓 `public/content/works/<paper_ref>-revision-memo.md` 用內建迷你 markdown renderer（無外部套件）渲染；原文＝內嵌 `public/content/papers/<paper_ref>.txt`＋連到 /papers reader。memo 須同步放 public（源檔在 scripts/data/）。
- ✅ **DB schema** — [database/lit-review-schema.sql](../../../database/lit-review-schema.sql)（`lit_review_entries` + `lit_review_sections` 兩表 + RLS public read + seed `orig`/`zh` 版本）；[database/writing-projects-v3-kind.sql](../../../database/writing-projects-v3-kind.sql)（`writing_projects` 加 `kind`(book/paper) + `paper_ref`）
- ✅ **/works 分區** — [pages/works/index.vue](../../../pages/works/index.vue) 拆「書籍寫作 / 論文寫作」兩區（依 `kind`）
- ✅ **reader + API** — [pages/works/[slug]/index.vue](../../../pages/works/[slug]/index.vue) 論文計畫頁底「研究回顧」分頁（按主題列書目）＋ [pages/works/[slug]/review/[ref].vue](../../../pages/works/) 原文/中譯兩欄逐段 reader；[server/api/lit-review/*.get.ts](../../../server/api/lit-review/)（entries / entry）
- ✅ **ingest 驅動腳本** — [scripts/ingest_lit_review.py](../../../scripts/ingest_lit_review.py)（`--seed` 入書目；`--fetch-fulltext --resume` 過夜抓全文＋翻譯）；報告原文存 [scripts/data/lit_review_eight_garudhammas.md](../../../scripts/data/)
- 🔄 **全文逐段對照（進行中，2026-06-04 09:35 暫停）**：八敬法案 **14 篇開放取用 PDF 連結已補實**（Anālayo 漢堡 11 篇 `…/pdf/5-personen/analayo/*.pdf` + JBE Case/Tsedroen + Bodhi bhikkhuni.net + Hüsken 2010 alokavihara）；逐段持久化翻譯（Gemini→NVIDIA→Haiku），受配額限速約 55 段/時。
  - **目前進度（DB 真實段數）**：`foundation`（Anālayo 2016）**202/456**、`cullavagga`（2015）**3/114**，共 **205 段**入庫；其餘 12 篇 PDF 尚未開始。
  - **▶ 新 session 接續指令**：`python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project bajingfa --resume --engine gemini --pace 1`（`done_zh_indices` 會跳過已翻段落、從缺口接續；entry 仍標 pending/fetched 不影響 resume）。log 寫 `c:/tmp/lit_review_overnight.log`。
  - **待補連結**：Hüsken 2000（JBE vol 7）、von Hinüber 2000（德文，無開放 PDF）— 仍無開放 PDF；Horner 1930（PD）已補 archive.org（in.ernet.dli.2015.53363，整本掃描，作參考連結，未抓全文）。
- 💡 **漢堡 Anālayo PDF 命名規律**：`buddhismuskunde.uni-hamburg.de/pdf/5-personen/analayo/{foundation,cullavagga,gurudharma,legality,revival-bhikkhuni,mahapajapati,theravadavinaya,theories-foundation,validity,bhikkhuni-controversy}.pdf`（HEAD 探測後再入庫，避免 404 算 fail）
- ✅ **中文書目開放取用連結回填（2026-06-05）**：`scripts/patch_lit_urls.py`（讀 `{ref_key: url}` JSON，curl 驗證後 PATCH `fulltext_url`，只動既有 ref_key）。bajingfa 已回填 **13 筆**經 curl 200 驗證的免費連結 — 釋惠敏《比丘尼受戒法與傳承之考察》(NTU 佛研 PDF×2 dup)、林崇安《八敬法的演變》(舊 ss.ncu 連結死→NTU 佛圖鏡像)、釋常圓《大愛道比丘尼經之佛教女性觀》(towisdom)、李玉珍《受戒施教》(中研院近史所)/《出家入世》(NTU museum)、楊惠南《當代台灣佛教出世性格》(NTU)、印順《初期大乘》《原始佛教聖典之集成》《教制教典與教學》《四分律》(CBETA Y0035/Y0033/Y0021/T1428)、〈阿難過在何處〉(yinshun-edu y27_04)、Horner 1930(archive.org)。
  - **華藝（Airiti）付費牆無法直接下載**；策略＝改抓免費鏡像（臺大佛圖 buddhism.lib.ntu.edu.tw、CBETA、中研院、towisdom、yinshun-edu、archive.org）。
  - **新增 3 筆印順／清德律學脈絡**（`lit_review_zhaohui_yinshun_qingde.md`，`--entries-only --display-offset 300`）：印順《教制教典與教學》(專書, CBETA)、釋清德《印順導師的律學思想》(專書, 法界 2001 版權)、釋清德〈印順法師戒律與教制觀之研究〉(學位論文, 香光書目)。bajingfa 現 **80 筆**。
  - **仍無免費連結的條目**：多為版權專書（法界／正聞《千載沉吟》《律學今詮》《令梵行久住》／英文 monographs Gross/Faure/Collett/Ohnuma/Jones/Madsen…）與昭慧散見報刊／簡體轉載／FB 的時論；前者依版權姿態維持 `unavailable`，後者因簡體轉載＋連結品質不過關，依[[feedback_traditional_chinese_only]]暫不掛。
- ✅ **昭慧時論回填（hongshi.org.tw，2026-06-05）**：昭慧法師個人文章在其官網 `hongshi.org.tw/master-chao-hwei-article-page.php?n=N`（穩定數字 ID）。**該站 WAF 擋 bot（WebFetch/curl 皆 403）**，無法逐頁 curl 驗證或枚舉索引；改以 Google 索引（標題精確命中）認定。已掛〈當代大愛道的二次革命——廢除八敬法宣言〉n=608（廢除八敬法宣言兩條目共用）。其餘昭慧 op-ed（奴性教育／PlayBoy／佛教與女性／論出家二眾）未能從 search 取得確切 n=，暫缺。
- ✅ **南傳／藏傳傳承中斷與恢復 + 西方女剃男（2026-06-05，使用者指定）**：`lit_review_zhaohui_lineage.md`，7 筆英文開放取用（curl 200），歸 `#跨傳統比較`，`--display-offset 320`。南傳＝Alliance for Bhikkhunis〈A Lotus at Dawn〉(1996 薩爾納特)、Barre Center(11c 斯里蘭卡斷絕→1998 菩提伽耶恢復)；藏傳＝Thubten Chodron(根本有部比丘尼從未確立)、達賴喇嘛訪談(2007 漢堡會議兩方案、未逕行)、Lion's Roar(2022 不丹首傳 gelongma)、Buddhistdoor(尼眾現況)；西方女剃男先例＝Smith College〈Women's Ordination in Sōtō Zen〉(曹洞得度不分性別，女 roshi 為男弟子授戒)。bajingfa 現 **87 筆**（跨傳統比較 12 筆）。

---

## 版權姿態

- **全文只收開放取用 / 公有領域**：JBE（Journal of Buddhist Ethics，全卷開放）、漢堡大學 buddhismuskunde PDF、blogs.dickinson.edu、聖嚴法師數位典藏、NTU 佛研、政大學術集成、towisdom / hongshi PDF、Horner 1930（PD）。
- **版權書（如某些合集）**：只放 `fulltext_status='unavailable'` 的書目＋摘要＋連結，不抓全文。
- **中譯欄永遠是逐段自譯**（同 [[scripture-gnostic]] / [[scripture-fathers]] 姿態：第三方中譯不入庫）；中文文獻本身不需中譯欄（`language='zh'` → 不建 sections，書目層即可）。

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

## SOP — 把某論文的「真實參考文獻」補成額外參考頁面（不動論文原文）
1. 從論文（`public/content/papers/<id>.txt` 的「參考文獻」段）原樣轉錄成 `scripts/data/lit_review_<topic>_references.md`，**用文獻類型當 `#` 標頭**（七大類，須與 `DOC_TYPE_THEMES` 的 label 完全一致）；每筆轉成 `【作者】（年）〈題〉，《刊/書》`＋`語言：`／（可選）`所屬面向：`／`立場：`／`摘要：`／網路文章附 `> **全文**：[label](url)`。年代寫成乾淨 `（YYYY）`（避免 `（1965.03.22）` 這類抓不到年）；同題上/下把（上）（下）放進 `〈…〉` 內以免 ref_key 撞鍵。
2. dry-parse 檢查：`python -X utf8 -c "..."` 確認 entries 數、無重複 ref_key、每筆有 theme/title。
3. `python -X utf8 scripts/ingest_lit_review.py --seed --entries-only --display-offset 100 --report scripts/data/lit_review_<topic>_references.md --project <slug>`（`--entries-only` 不覆蓋既有專案；`--display-offset` 排在綜述之後；中文文獻自動標 `unavailable`、不抓全文）。
4. 不要碰論文原文檔；reader 自動在第一個書目類型組前顯示「論文參考文獻」分界。

## SOP — 補單筆 / 重翻
直接對該 `entry_id` 重抓＋重翻＋upsert（UNIQUE(entry_id,version_code,order_index) 覆蓋）。

---

## See also
- [[scripture-gnostic]] — 最近的同構案例（documents/versions/sections + 逐段對照 + 純函式 test-first）；本 skill 照搬其架構
- [[ebook-translate]] — 翻譯引擎 / quota / fallback / 對齊重翻
- [[translation-glossary]] — 佛教／宗教學名詞中譯（翻譯前鎖譯名；八敬法人名如 Anālayo 阿那律陀？先查詞庫）
- [[ebook-collected-works]] — N 欄逐段對照 reader 同源姿態
- /works（寫作計畫）— 本 skill 在其底下加 paper 區 + 研究回顧分頁
