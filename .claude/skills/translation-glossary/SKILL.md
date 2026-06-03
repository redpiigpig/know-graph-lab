---
name: translation-glossary
description: 神學家／神學名詞中譯對照工具（/translation-glossary） — ~150 位教父／神學家 + ~165 條神學名詞，每筆含原文／生卒／國籍／6 個傳統中譯（新教／思高／東正教／香港／台灣／中國學界）+ 建議譯名 + 理由。Use when 翻譯新教父書（ANF/NPNF/ACCS）前要先鎖定相關人名譯名／新增神學家／補譯名差異／使用者要校對建議譯名。本 skill 與 [[ebook-translate]] 串接，後者翻譯前都應該先來這裡確認。
---

# Translation Glossary Skill

**目的**：當「不同傳統對同一個教父／神學名詞有完全不同中譯」（如 Justin Martyr = 新教 *游斯丁* / 思高 *猶斯定* / 東正教 *尤斯丁*）時，翻譯前先在 `/translation-glossary` 確認該書應採哪個譯法，避免 LLM 自選一個導致使用者糾正後要回頭修 chunks。

跟 [[ebook-translate]] 並列：
- ebook-translate 處理「英文 → 繁中內文翻譯」
- translation-glossary 處理「人名／術語譯名標準化」
- 兩者都用同一份 `[[ebook-translate]]/glossary.md` 為 LLM prompt 來源，但本 skill 多了 DB 化的可校對 UI

## 上線狀態（2026-05-22）

✅ Portal tile：`/scripture-canon` 第 6 格「神學家與名詞中譯」
✅ Page：[pages/translation-glossary/index.vue](../../../pages/translation-glossary/index.vue)
✅ Schema：[database/translation-glossary-schema.sql](../../../database/translation-glossary-schema.sql)
✅ Seed script：[scripts/seed_translation_glossary.py](../../../scripts/seed_translation_glossary.py)
- 155 位教父 master list（使徒教父 → 近代 + 華人）
- 165 條神學名詞 master list（三一論／基督論／救恩論／教會學／聖事／末世論／解經／制度／神學人類學／倫理靈修／信經／神論／異端 共 13 類）
- 各筆 7 個傳統中譯 + 建議 + 理由都由 LLM 預填

## 資料 schema

兩個並列表：

### `theologians`
| 欄位 | 用途 |
|---|---|
| `name_english` (UNIQUE) | 英文常用名 — lookup / upsert key |
| `name_original` + `name_original_lang` | 希臘 Ἰουστῖνος / 拉丁 Augustinus；lang = grc/lat/syc/cop/arm/heb |
| `name_latin_std` | 拉丁化標準名 e.g. Iustinus Martyr — sort key |
| `nationality` | 出身地（繁中）e.g. 撒瑪利亞 / 北非 / 加帕多家 |
| `born_year` / `died_year` | int，BC 用負數 |
| `century` | "2c" / "4-5c" — UI 篩選 |
| `school` | 學派（亞歷山大 / 安提阿 / 拉丁西方 / 加帕多家 / 經院 / 改革宗 / ...）|
| `role` | 身份（使徒教父 / 護教士 / 教父 / 教會博士 / 改教家 / 異端 / ...）|
| `name_protestant` | 新教中譯（華聯／證主／校園／改革宗）|
| `name_catholic_sgs` | 思高傳統（教廷／思高聖經學會）|
| `name_orthodox` | 東正教（東亞主教教區）|
| `name_hk` | 香港（基文／道風）|
| `name_tw` | 台灣（光啟／輔大）|
| `name_china_academic` | 中國學界 |
| `name_recommended` | ★建議採用譯名 |
| `recommendation_reason` | 建議理由（2-3 句）|
| `sort_order` | 年代排序 |

### `theological_terms`
類似結構，把 `name_*` 換成 `zh_*`，多 `definition_zh` 釋義欄。

## UI 功能

**Tab 切換**：人名（神學家）/ **君主** / **哲學家** / 地名 / 作品名 / 教派名 / 神學名詞

> **君主／哲學家 tab（2026-06-03）**：`theologians` 表加 `figure_type` 欄
> （`theologian` 預設 / `monarch` / `philosopher`）；三個「人」tab 都讀 theologians
> 依 figure_type 分流，重用 people 表渲染。`monarch` = 希臘化君主 + 羅馬皇帝（64）；
> `philosopher` = 蘇前→新柏拉圖主義希臘羅馬哲人（37）。seed =
> [scripts/seed_monarchs_philosophers.py](../../../scripts/seed_monarchs_philosophers.py)
> （含 reclassify 已存在人物：柏拉圖/亞里斯多德/蘇格拉底等 theologian→philosopher）。
> 兩 tab 平面依年代排序、無 era 子 tab、不顯示新教/天主教變體欄。

**篩選**：
- 神學家 tab：世紀（1c / 2c / ... / 20c）
- 名詞 tab：分類（三一論 / 基督論 / ...）

**搜尋**：搜尋框覆蓋原文／英文／拉丁化／所有 7 欄中譯／建議譯名／國籍

**編輯模式**（右上 checkbox）：
- 開啟後點 row 展開的細節區出現 inline form
- 可改 `name_recommended` + `recommendation_reason` + `notes`（人物）
- 可改 `zh_recommended` + `recommendation_reason` + `definition_zh`（名詞）
- 儲存直接寫 Supabase（用 `useSupabaseClient` 客戶端 PATCH）

**★** 標記：表內 highlight 顯示 `name_recommended`（金色），告訴使用者這是預填的建議；其他 6 欄是各傳統供參。

## 批次生成 SOP

新 master list 條目要批次預填時：

```bash
# Smoke test 5 筆
python scripts/seed_translation_glossary.py --target people --engine haiku --limit 5

# 全批（resume = 只跑 name_recommended 還是 null 的）
python scripts/seed_translation_glossary.py --target both --engine haiku --resume

# 只跑名詞
python scripts/seed_translation_glossary.py --target terms --engine haiku
```

`--engine`：
- `gemini` — 預設先 gemini 4-key rotation，失敗 fallback haiku
- `haiku` — 直接 haiku（觀察 Gemini 全 key 撞 quota 時用這個）

**經驗（2026-05-22）**：
- Gemini 4 key 全 429 在沒長期使用情況下也會撞（似乎連續同帳號相關 batch 會被 throttle）→ 預設改 haiku 反而穩
- Haiku 偶爾 529 Overloaded → script 已加 retry [0,30,60,120,240,480] 秒 backoff
- 1 batch = 5 entries（人物）/ 6 entries（名詞）— 控品質且避免超 max_tokens
- 全批 ~150 + 165 = 約 31 + 28 ≈ 60 batch × 12-30s = 估 30-60 分鐘

## Prompt 強化關鍵

`PERSON_PROMPT` 內嵌 17 位教父的真實傳統差異對照表（如 Clement = 革利免/克萊孟/克勒孟；Origen = 奧利金/奧利振/奧利根；Augustine = 奧古斯丁/奧斯定）。

**重要**：沒有這個表 Haiku 會偷懶把多個傳統欄填同一個譯名（觀察過：smoke test 第 1 版幾乎所有人都填「羅馬的克萊門特」全欄重複）。加了範例後 Haiku 真的給出差異。

新增大量人物時，挑 3-5 位確定知道有傳統差異的，加進 prompt 範例表強化。

`TERM_PROMPT` 也有類似 hint（homoousios → 同質／同性同體；Theotokos → 神之母／天主之母）。

## 跟 ebook-translate 的串接

DB 是真理，ebook-translate 的 `glossary.md` + `PROMPT_TMPL` 是從 DB **自動同步**生成的副本。

### Export 流程（DB → glossary.md + PROMPT_TMPL）

```bash
python scripts/export_glossary_from_db.py
```

這支 script 做兩件事：

1. **寫 `.claude/skills/ebook-translate/glossary.md`**：在 `<!-- AUTO-GLOSSARY:theologians:START -->` / `:END` markers 之間生成全 DB 249 位人物的 markdown table，按 12 個年代段（使徒教父1-2c / 尼西亞前3c / ... / 21c 當代）分段，每筆顯示「英文／拉丁 | 原文 | 年代 | ★建議譯名 | 其他傳統變體」。
2. **更新 `scripts/translate_ebook_to_zh.py`**：在 `# AUTO-PROMPT-PEOPLE:START` / `:END` markers 之間寫入 `AUTO_PROMPT_PEOPLE` 字串（只取 pre-1500 = Schaff ANF/NPNF/ACCS 涉及範圍），再用 string concat 拼進 `PROMPT_TMPL` 給 Gemini／Haiku／Sonnet 翻譯時當 cheat sheet。

### 翻新書前 SOP

1. ebook ingest 完成、要開始翻譯前
2. 跑 `--inspect` 看 source 主要會出現的人物
3. 開 `http://localhost:3010/translation-glossary` 用搜尋框查每位人物的 ★建議
4. 不確定的（DB 沒有 / ★建議 待校）→ 編輯模式 inline 改 → 儲存
5. **跑 `python scripts/export_glossary_from_db.py`** 同步到 glossary.md + PROMPT_TMPL
6. 開翻

### Markers 設計理由

用 HTML comment markers 而不是直接覆寫整檔，原因：
- `glossary.md` 還包含 **聖經書卷縮寫**、**神學術語**、**ACCS vol 12 / ANF Vol 1 特定術語** 等手寫段，不能被 export 蓋掉
- `translate_ebook_to_zh.py` PROMPT_TMPL 還有 **諾斯底專名 / 聖經引用格式 / Markdown 結構規則** 等手寫指令，只人名段要自動換

未來改進：自動化 — script 讀 EPUB 抓 proper noun list → 跟 DB cross-check 找差異 → 列出待確認清單。

## 已知未實作 / 待擴充

- ❌ **export glossary**：DB → ebook-translate `glossary.md` markdown 自動同步（目前手動雙寫）
- ❌ **新增人物 UI**：目前只能編輯，新增要直接改 master list + 重跑 seed
- ❌ **多書差異標記**：哪本書用哪個譯名（同人不同書可能用不同譯）
- ❌ **依書類自動切建議**：例如翻 ACCS 用新教偏好；翻天主教文獻自動切思高
- ❌ **校對狀態欄**：使用者校過的 row 標「已校對」（目前沒這欄）

## 常見坑

- **Haiku 多個傳統欄填一樣的譯名**：prompt 範例不夠 → 加更多 `examples_of_differentiation`
- **某位人物在某傳統真的沒獨立譯名**：填 null 而非編造（已在 prompt 明說，但 Haiku 偶爾還是會編 — 校對時刪掉）
- **OAuth token 過期**（worker 跑 > 8h）：script 已有 `_refresh_anthropic` 自動 re-read credentials.json
- **批次 LLM 失敗整 script 死**：早期版本 fill_xxx 只 catch RuntimeError，2026-05-22 改 catch Exception → 個別 batch 失敗會 continue 不整 script 退
- **OverloadedError 529** 不 retry → 改成功 backoff retry（與 RateLimitError 同處理）

## See also

- [[ebook-translate]] — 翻譯 pipeline，本 skill 是其譯名前置確認步驟
- [[scripture-canon-portal]] — `/scripture-canon` portal hub，本 skill 是其第 6 個子工具
- [pages/translation-glossary/index.vue](../../../pages/translation-glossary/index.vue) — UI
- [scripts/seed_translation_glossary.py](../../../scripts/seed_translation_glossary.py) — master list + 批次填
- [database/translation-glossary-schema.sql](../../../database/translation-glossary-schema.sql) — DDL
