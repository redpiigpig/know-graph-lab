---
name: translation-glossary
description: 「翻譯定名」通用名物中譯對照工具（/translation-glossary，**已升為首頁頂層卡、移出聖經 portal**） — 原本只有教父／神學家＋神學名詞，2026-06-03 起擴為全領域：聖經人物／教父神學家／神學名詞（神學兩表）＋哲學家／科學家／歷代帝王／國名與城市／神祇與宗教名詞（各領域新表）＋一頁翻譯原則。核心規則：按原文不按英文、沿用良好古譯／意譯、音意結合（亞歷山卓>亞歷山大城、馬爾堡>馬布爾）、名根一致（name_root：密特→密特拉/密特里達迪、塞琉→塞琉古/塞琉西亞）。Use when 翻書前鎖定任何人名／地名／神祇／帝王／哲人科學家譯名、新增領域條目、校對名根一致性、改翻譯原則頁。串 [[ebook-translate]]。2026-07-01 加「官制與行政區」分頁：外國政權官名／職務／行政區名按「朝代 register」中譯（商周/戰國秦/漢/魏晉/唐/明清…），解決「總督/行省」氾濫、無層次感；見 [offices_register_blueprint.md](offices_register_blueprint.md)。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。


# Translation Glossary Skill（「翻譯定名」）

## 🆕 2026-06-03 升級：頂層卡「翻譯定名」+ 全領域擴充

`/translation-glossary` **從聖經 portal 第 6 卡升為首頁頂層卡**（移出 `/scripture-canon`），並從「神學專用」擴成「**通用名物中譯**」。

**決策（user 拍板）**：保留神學兩表（theologians / theological_terms），**各新領域各建一表**：

| Tab | 表 | 領域專屬欄 |
|---|---|---|
| 翻譯原則 | （靜態頁） | — |
| 人名（含聖經人物 era） | theologians | person_era / role |
| 神學名詞 / 地名 / 作品名 / 教派名 | theological_terms | entity_type |
| 哲學家 | `philosophers` | school / era / nationality |
| 科學家 | `scientists` | field / era / nationality |
| 歷代帝王 | `historical_rulers` | polity / title / reign |
| 國名與城市 | `place_names` | place_type / modern_name |
| 神祇與宗教名詞 | `deities` | religion / entity_type / domain_of |

5 張新表同一核心 shape：`name_original / name_original_lang / name_romanized / name_english / name_recommended(★) / name_variants(；分隔) / recommendation_reason / name_root / notes / sort_order`。Schema：[database/glossary-domains-schema.sql](../../../database/glossary-domains-schema.sql)（RLS 比照神學表）。純函式核心：[scripts/glossary_naming.py](../../../scripts/glossary_naming.py)（DOMAINS taxonomy + 名根一致性 + 變體解析；測試 [scripts/tests/test_glossary_naming.py](../../../scripts/tests/test_glossary_naming.py)）。

### 翻譯原則（翻譯原則頁 + 全工具的鐵則）
1. **按原文，不按英文**（希臘／拉丁／原民族語為準）。
2. **沿用良好古譯／既有意譯**，不強制全音譯。
3. **音意結合**：有良好音譯配意譯就結合 — 例「亞歷山卓」優於「亞歷山大城」、「馬爾堡」優於「馬布爾」。
4. **名根一致**（`name_root`）：同一來源根的譯名要一致 — 密特拉系（root 密特）→ 密特拉／密特里達迪；塞琉古系（root 塞琉）→ 塞琉古／塞琉西亞／塞琉西亞-泰西封。`check_root_consistency()` 自動抓「掛了 root 卻沒含 root 字串」的條目（如 root 塞琉 卻寫「西流基」）。
5. **王朝命名（帝國／國名）**：以王朝命名的帝國採「**王朝名-民族／國名 帝國**」格式 — 鄂圖曼-土耳其帝國／阿契美尼德-波斯帝國／薩珊-波斯帝國／阿拔斯-阿拉伯帝國／塞琉古-希臘帝國／卡洛林-法蘭克帝國。**例外**：只跟單一人物相關（一人所建、逝後即分裂或更名）→ 直接用人名，不加王朝-民族：亞歷山大帝國／帖木兒帝國／拿破崙帝國。常見短稱（鄂圖曼帝國、塞琉古帝國）放 `name_variants`。

> ⚠️ **古名／古譯處理（2026-06-04，使用者逐項定奪）**：已套用使用者核可的改動：
> - **安息帝國**（＞帕提亞，源自王朝自稱 Aršak；place_names，root 改安息）
> - **查拉圖斯特拉**（＞瑣羅亞斯德，按阿維斯陀原文；deities entity_type=教主）
> - **祆教**（＝瑣羅亞斯德教；deities `religion` 欄一律用此）
> - **伊本‧西那**（＞阿維森納）、**伊本‧魯世德**（＞阿威羅伊）— 伊斯蘭學者按阿拉伯原文，拉丁化退為變體；**惟 Maimonides 維持「邁蒙尼德」不改**（使用者指定）
> - **Yahweh → 雅威**（theological_terms 新增；僅 Yahweh 這個讀音形式用雅威，四字神名/耶和華傳統不動）
> - **東方亞述教會 → 景教**（theological_terms 新增 sect；Nestorianism＝聶斯多留主義 教義條保留不動）
> - **Krishna 不在此處理**（使用者另一 session 處理，deities 維持 克里希那）
>
> **規則**：(1) 已廢、現代無人使用的中文古譯（大秦/拂菻/大食/天竺/身毒…）**一律不用**，連變體都不放；(2) 任何「古譯／原文 vs 英文轉譯」候選，**先列清單給使用者逐項定奪，不可自行套用**（使用者明確要求的流程）。Yahweh/景教 為直接 upsert 進 theological_terms（非 seed 腳本）。

### 🆕 2026-06-04：國名與城市（`place_names`）首批策展完成（268 筆）

`places` tab 從 4 筆示範擴成 **268 筆人工策展**（含王朝命名通則，見原則 5）。**這批刻意不走 LLM**——「確定譯名」需人工權威判斷（聖經傳統優先、台陸變體、名根一致），LLM 自填過去多次被使用者糾正。Seed：[scripts/seed_glossary_places.py](../../../scripts/seed_glossary_places.py)（純資料 hand-curated，`--dry` 預覽，內建重複鍵＋名根自檢，`on_conflict=name_english` idempotent；已加 `place_names_name_english_key` unique constraint）。

涵蓋：古代近東帝國／政權、波斯希臘羅馬政權、中世紀近代帝國、古代地區／行省、兩河波斯城市、黎凡特聖經城市、埃及北非、希臘小亞、義大利西方教會史城市、**全球現代國家（國名 158）+ 首都大城**。

**這批的兩條額外定名規則**（補上面 4 原則）：
- **聖經地名以和合本／思高傳統為 `name_recommended`，史學/學界譯放 `name_variants`**：安提阿(史學安條克)、推羅(泰爾)、別迦摩(帕加馬)、書珊(蘇薩)、該撒利亞=凱撒利亞、挪弗(孟斐斯)…
- **現代國名以台灣（外交部）慣用為 `name_recommended`，大陸/港譯放 `name_variants`**：寮國(老撾)、義大利(意大利)、衣索比亞(埃塞俄比亞)、奈及利亞(尼日利亞)、紐西蘭(新西蘭)、沙烏地阿拉伯(沙特)、喬治亞(格魯吉亞)…中亞「-斯坦」台灣慣省略(哈薩克 vs 哈薩克斯坦)。

待續：① 中世紀／近代歐洲城市（教會會議城、宗改城）尚淺 ② 東亞／印度本土古都 ③ 河流山脈等自然地名 ④ 是否把 places 納入 [[ebook-translate]] glossary.md 自動 export（目前 export 只含人名）。

### 🆕 2026-06-04：歷代帝王（`historical_rulers`）策展（145 筆）

`rulers` tab 從 3 筆擴成 **145 筆人工策展**。Seed：[scripts/seed_glossary_rulers.py](../../../scripts/seed_glossary_rulers.py)（同 places 政策，純資料、`--dry`、名根自檢、`on_conflict=name_english`；加 `historical_rulers_name_english_key` unique constraint）。

涵蓋：亞述/新巴比倫/瑪代/阿契美尼德波斯諸王（聖經王）、古埃及法老+托勒密、塞琉古、馬其頓、**羅馬皇帝 30 位（奧古斯都→末代西羅馬，涵蓋逼迫教會諸帝＋迦克墩/敘任權相關）**、拜占庭、薩珊、哈里發、鄂圖曼蘇丹、神羅/卡洛林（查理‧馬特→丕平→查理曼→虔誠者路易）、近代歐洲、薩法維/蒙兀兒、**中國 15（秦始皇→慈禧）、日本 8（神武→明治）、印度 5（旃陀羅笈多/阿育王/迦膩色迦…佛教史相關）**、蒙古/帖木兒、以色列猶大列王+希律。

**兩條規則**：
- **`polity` 欄對齊 `place_names` 的王朝-民族帝國名**，使兩 tab 一致。
- **聖經帝王：通行學界譯為 `name_recommended`，和合本/思高譯放 `name_variants`**（居魯士=古列、薛西斯=亞哈隨魯、革老丟、奧古斯都=該撒亞古士督…）。
- 既成中譯分流標 `notes`：鄂圖曼(王朝) vs 奧斯曼(開國者 Osman)；哈里發奧斯曼(Uthman) vs Osman 非同人。中國/日本/印度帝王 name_english 用英文音譯、name_recommended 用中文本名/廟號。

### 🆕 2026-06-04：哲學家／科學家／神祇三 tab 補齊

- **`philosophers`（53）** [scripts/seed_glossary_philosophers.py](../../../scripts/seed_glossary_philosophers.py)：蘇格拉底前→雅典三哲→希臘化各派→羅馬→**亞歷山大斐洛＋新柏拉圖（與教父關係密切）**→伊斯蘭 Falsafa→近代→現代詮釋學。台譯★、陸譯放變體（笛卡兒/笛卡爾、海德格/海德格爾…）。
- **`scientists`（35）** [scripts/seed_glossary_scientists.py](../../../scripts/seed_glossary_scientists.py)：希臘羅馬→伊斯蘭黃金時代→科學革命→近現代。
- **`deities`（100）** [scripts/seed_glossary_deities.py](../../../scripts/seed_glossary_deities.py)：原 37 筆多諾斯底術語，補主流神系（希臘/羅馬/埃及/北歐/印度/瑣羅亞斯德）＋**聖經 ANE 神祇（巴力/亞舍拉/大袞/摩洛/搭模斯/馬爾杜克…和合本譯為★）**。Mithra 掛名根「密特」與密特里達迪一致。（去重：刪 Pleroma 重複列。）

待續：各帝國更中段諸王、東亞/印度更多帝王、哲學家中世紀經院（多與 theologians 重疊）、是否把各 tab 納入 [[ebook-translate]] glossary.md export。

### 🆕 2026-07-01：官制與行政區（`official_titles`）+ 朝代 register 對應

**問題（使用者）**：翻外國政權的官名／職務名／行政區名過去**過於重複、沒有層次感** —— 動不動「總督／行省」，時代也對不上。要的是**外國政權官制與行政區跟漢字文化圈有「時代對應＋政體體例對應」**，中國詞不夠可借日／韓／越漢字官職。

**核心設計（兩層）**：
1. **register 對應（制對應）**：把外國政權按「**社會發展階段＋政治氣質**」（共時性，非日曆年代）對到一個朝代 register。純核心 `ADMIN_REGISTERS`（**10 桶**）：商周制／春秋制／戰國秦制／漢制／魏晉制／唐制／**宋制**／**遼金元制**／明清制／周封建五等爵。**遼金元制**（南北面雙軌、萬戶千戶百戶、達魯花赤）專供**游牧/征服帝國**（安息/塞爾柱/蒙古諸汗國/帖木兒）；拜占庭跨唐[軍區]/宋[晚期文官]兩制（如羅馬跨漢/魏晉）。
2. **逐條對照**：每個外國職／區劃 → 建議中譯，掛上所屬 register；**舊的扁平譯（總督；行省）降到 `name_variants`** 供對照。

**關鍵洞見**：**「總督／行省／副王」不是錯，是明清 register 的詞** —— 只用在奧斯曼／蒙兀兒／俄／近世殖民帝國，不套波斯／羅馬／亞述。且帝國晚期逐層對到魏晉三級（`大區行臺(行臺尚書令)→州(刺史)→郡(太守)`）＝使用者要的「層次感」。

**使用者已定調範例**：埃及 Nome/Nomarch＝州／州伯；亞述 Shaknu＝鎮監；波斯 Satrap＝州／州伯；希臘化 Strategos＝郡／郡尉；羅馬前期 Provincia＝行省（Proconsul 牧／Legatus 都護），埃及特區 Praefectus＝大尹，猶太 Praefectus（本丟彼拉多）＝都尉（隸敘利亞大行省的**郡**非行省）；羅馬晚期三級＝大區行臺／州刺史／郡太守；東羅馬 Theme/Strategos＝軍道／節度使；阿拉伯 Wilayah/Amir＝道／經略使；奧斯曼 Sanjak/-bey＝旗／旗主；西班牙 Viceroy＝副王、Captain General＝提督；英 Governor-General/Governor/Lt.Gov＝大總督／總督／巡撫；法 Résident supérieur＝統監（借日治朝鮮詞）。Shophet＝士師。

**檔案**：
- 藍圖＋全對照總表：[offices_register_blueprint.md](offices_register_blueprint.md)（阿卡德→近世殖民；【核】使用者定調 vs【提】AI 提案待拍板）
- 純核心：[scripts/glossary_naming.py](../../../scripts/glossary_naming.py)（`ADMIN_REGISTERS` / `REGISTER_BY_POLITY`（羅馬＝["漢制","魏晉制"]）/ `registers_for_polity` / `check_register_valid` / `check_register_matches_polity`）
- 測試：[scripts/tests/test_offices_register.py](../../../scripts/tests/test_offices_register.py)（21 綠）
- Schema：[database/glossary-offices-schema.sql](../../../database/glossary-offices-schema.sql)（`official_titles`；新欄 `register` / `admin_level` / `entity_type` / `polity`；unique=(name_english, polity)）
- Seed：[scripts/seed_glossary_offices.py](../../../scripts/seed_glossary_offices.py)（hand-curated **68 筆**、`--dry` 預覽＋自檢、`on_conflict=name_english,polity`）
- UI：[pages/translation-glossary/index.vue](../../../pages/translation-glossary/index.vue) tab「官制與行政區」（GENERIC 表 + register 子篩選 chip，依 sort_order 呈發展階段順序＝層次感）

**狀態（2026-07-01）**：✅ 表已建、seed 68 筆上線、Vue tab 已接。巴比倫地方首長定為楚職**縣公**。⏳ 蒙兀兒/俄/法/奧德/荷/日【提】細項待確認；文體翻譯（台語文讀／粵語）屬「漢譯世界史計畫」更大願景，本表只做官職／行政區定名。

**SOP**：翻書前定書中政權 → 查 register →（不夠用查日韓越）→ 抽官名/區劃清單逐項對照（hand-curated 不走 LLM）→ 定案進 seed（先 `--dry` 過自檢）→ `export_glossary_from_db.py` 同步 cheat sheet。

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

**Tab 切換**：翻譯原則 / 人名（含聖經人物 era）/ 哲學家 / 科學家 / 歷代帝王 / 國名與城市 /
神祇與宗教名詞 / 官制與行政區 / 神學名詞 / 地名 / 作品名 / 教派名（各領域對應上方 schema 表）。
「官制與行政區」（`official_titles`）另有 `register`（八桶）／`admin_level`／`entity_type` 篩選。

> ⚠️ 早期曾用「theologians.figure_type 分流 monarch/philosopher」的權宜做法（2026-06-03 commit
> 923e643），已被本頁頂「各領域獨立表」新架構取代並回收（figure_type 欄與相關 rows 已刪）。
> 君主→`historical_rulers`、哲學家→`philosophers` 專表。

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
- [[scripture-canon]] — `/scripture-canon` portal hub，本 skill 是其第 6 個子工具
- [pages/translation-glossary/index.vue](../../../pages/translation-glossary/index.vue) — UI
- [scripts/seed_translation_glossary.py](../../../scripts/seed_translation_glossary.py) — master list + 批次填
- [database/translation-glossary-schema.sql](../../../database/translation-glossary-schema.sql) — DDL
