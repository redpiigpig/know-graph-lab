
> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（`https://integrate.api.nvidia.com/v1`，`deepseek-ai/deepseek-v4-flash`，4 key 輪流＋間隔節流避 429）→ Haiku（最後救急）**。視覺／OCR 走 Gemini Vision／Haiku Vision。見 [[feedback_engine_nvidia_no_haiku]]。

# 雷蒙‧潘尼卡全集 — 案例盡職調查（版權 / 卷目 / 來源）

第三個 ebook-collected-works 案例（繼榮格、馬克斯‧穆勒之後）。**先讀本檔再開工。**

## 一句話結論

雷蒙‧潘尼卡（Raimon Panikkar, 1918–2010）是**二十世紀宗教間／宗教內對話、比較神學與跨文化哲學的巨擘**——天主教神父、哲學／化學／神學三博士，以**「宇宙神人共融（cosmotheandric）」**直觀、**「宗教內對話（intrareligious dialogue）」**與**《印度教中未識的基督》**馳名。他**卒於 2010 → 全部著作受版權保護至約 2080**（life+70），跟**榮格同型、跟穆勒相反**：網路無乾淨合法公有領域全文，第三方中譯本一律不入庫。**採 English-first（[[feedback_jung_nonpd_english_first]]）：私人站非公有領域來源可用，英文先輸入、繁中逐步補。**

唯一比榮格更棘手的架構性差異：潘尼卡**用多種語言原創寫作**（加泰隆語／西班牙語／義大利語／英語／德語／法語），他的 **Opera Omnia（全集）是「按主題重編」而非「按出版序」**，同一卷內各篇原文語言不一。故「逐段三欄對齊」只有在**「同一文本恰有原文＋英譯兩版」**時才嚴格成立；多數卷先走**英＋繁中雙語**，日後個別文本若取得平行原文版再升三欄。

## 語言策略（2026-06-12 user 拍板）

**English-first，英＋繁中雙語為預設**；個別文本若另有平行原文版（西／義／加泰）→ 升英＋原文＋繁中三欄。

- reader 主欄永遠是**我的逐段繁中譯文**；對照欄預設 `source_order=["en"]`；有平行原文版時 `["en","es"]` / `["en","it"]` / `["en","ca"]`。
- 起手卷《印度教中未識的基督》**原文即英文**（1964 倫敦初版，1981 修訂）→ 首卷走**英＋繁中雙語**驗 pipeline；其西班牙文版《El Cristo desconocido del hinduismo》日後可升三欄。
- 來源語言短標：`{en:'英', es:'西', it:'義', ca:'加泰', de:'德', fr:'法', sa:'梵'}`（reader langLabel 已支援動態 map）。

## 版權狀態（極簡）

| 項目 | 卒年/出版 | 地位 | 備註 |
|---|---|---|---|
| 潘尼卡本人全部著作（各語言原文＋英譯）| 卒 2010 | **受版權至約 2080**（life+70）| 無公有領域卷 |
| Opera Omnia 英文版（Orbis Books, Maryknoll, 2010–2022）| 現行商業出版 | **受版權** | Milena Carrara Pavan 主編 |
| Opera Omnia 義文版（Jaca Book）| 現行商業出版 | **受版權** | 與 Vivarium 基金會合作 |
| 既有第三方中譯（若有）| — | 不論版權，**一律不入庫** | 沿用本 skill 姿態；只當校對 transient 參考 |

> **跟榮格同型、跟穆勒相反**：穆勒全清可全自動跑；潘尼卡與榮格一樣**全部受版權**。處理姿態：**reader 只放我自己的逐段繁中＋來源語言原文欄**，第三方中譯絕不入庫；來源文字走本機 script/檔案流轉，我（Claude）不在對話貼整段受版權原文。English-first（私人站非 PD 可用）→ 英文先進結構、繁中慢慢補。

## 《Opera Omnia》卷目（12 卷，Orbis 英文版 2010–2022 / Jaca Book 義文版）

主編 Milena Carrara Pavan（潘尼卡晚年祕書兼遺產執行人），與塔維爾泰特（Tavertet, Catalonia）**維瓦里翁基金會（Vivarium Foundation）**合作。**按主題重編**為 12 卷（部分卷分兩部 .1/.2）：

| 卷 | 英文題 | 繁中暫定卷名 | 宗教學相關度 | 備註 |
|---|---|---|---|---|
| **I.1** | Mysticism: The Fullness of Life | 神祕：生命的圓滿 | ★★★★ | |
| **I.2** | Spirituality: The Way of Life | 靈性：生命之道 | ★★★★ | |
| **II** | Religion and Religions | 宗教與諸宗教 | ★★★★★ | |
| **III.1** | Christianity: The Christian Tradition | 基督宗教：基督宗教傳統 | ★★★★ | |
| **III.2** | Christianity: A Christophany | 基督宗教：基督顯現 | ★★★★ | Christophany 為潘尼卡自鑄詞 |
| **IV.1** | Hinduism: The Vedic Experience | 印度教：吠陀經驗 | ★★★★★ | 即《The Vedic Experience / Mantramañjarī》1977 |
| **IV.2** | Hinduism: The Dharma of India | 印度教：印度的達磨 | ★★★★★ | |
| **V** | Buddhism | 佛教 | ★★★★★ | |
| **VI.1** | Cultures and Religions in Dialogue: Pluralism and Interculturality | 文化與宗教的對話：多元論與跨文化性 | ★★★★★ | |
| **VI.2** | Cultures and Religions in Dialogue: Intercultural and Interreligious Dialogue | 文化與宗教的對話：跨文化與宗教間對話 | ★★★★★ | |
| **VII** | Hinduism and Christianity | 印度教與基督宗教 | ★★★★★ | **含《印度教中未識的基督》← 起手卷** |
| **VIII** | Trinitarian and Cosmotheandric Vision | 三一與宇宙神人共融觀 | ★★★★★ | cosmotheandric 招牌概念 |
| **IX.1** | Mystery and Hermeneutics: Myth, Symbol, and Ritual | 奧祕與詮釋學：神話、象徵與禮儀 | ★★★★ | |
| **IX.2** | Mystery and Hermeneutics: Faith, Hermeneutics, and Word | 奧祕與詮釋學：信仰、詮釋與道言 | ★★★★ | |
| **X.1** | Philosophy and Theology: The Rhythm of Being (Gifford Lectures) | 哲學與神學：存在的韻律（吉福德講座）| ★★★★★ | 1989 愛丁堡吉福德講座，2010 成書 |
| **X.2** | Philosophy and Theology — Part Two | 哲學與神學（下）| ★★★★ | |
| **XI** | Sacred Secularity | 神聖的世俗性 | ★★★★ | |
| **XII** | Space, Time, and Science | 空間、時間與科學 | ★★★ | |

> `parent_volume` 用「卷主題」（如「印度教與基督宗教」⊃ 各篇），`volume` 用單卷／單書繁中名。
> **排序建議（宗教學/宗教間對話優先）**：印度教中未識的基督（起手）→ 宗教與諸宗教 → 文化與宗教的對話 → 三一與宇宙神人共融觀 → 印度教（吠陀經驗）→ 其餘。

## 起手卷：《印度教中未識的基督》The Unknown Christ of Hinduism（1964, 修訂 1981）

**為何選它**（user 拍板）：潘尼卡**最著名、最具代表性、最具象徵意義**的作品；印度教與基督宗教交會的奠基之作；「宇宙神人共融」與「宗教內對話」思想的源頭文本。**原文即英文**（1964 倫敦 Darton, Longman & Todd 初版；1981 大幅修訂增訂版）→ 首卷走**英＋繁中雙語**最乾淨地驗 pipeline，不必先解跨語對齊。

**結構（修訂版 1981）**：導論 + 數章（圍繞「基督在印度教中隱然臨在」「梵—基督」「全基督 / the whole Christ」等主題）。章節標題清楚 → 走 `scripts/align_editions.py` 章節錨點即可切段。

**日後升三欄**：西班牙文版《El Cristo desconocido del hinduismo》為平行版，取得後可比照穆勒《宗教學導論》升英／西／繁中三欄。

## 來源紀錄

| 版本 | 來源 | 狀態 | 備註 |
|---|---|---|---|
| 英文《The Unknown Christ of Hinduism》1981 修訂版 | shadow library（Anna's Archive / libgen，**私人自用，user 拍板 2026-06-12**）抓 PDF/EPUB 到本機 | ⏳ 待取得 | 受版權；只入我的繁中＋英文對照欄，不貼整段原文於對話。**注意：archive.org 上的「Panikkar」多為 K.M. Panikkar（史學家），非 Raimon；本人那兩本（`unknownchristofh0000raim` 1967 / `..._q2h1` 1981）皆 inlibrary 借閱制、djvu.txt 受限** |
| 西班牙文《El Cristo desconocido del hinduismo》| 同上 | 日後 | 升三欄用 |
| Opera Omnia VII《Hinduism and Christianity》(Orbis 2018) | 商業出版 | 受版權 | 卷編體例參考用 |

> **與穆勒/榮格不同：潘尼卡無 archive.org djvu 乾淨全文。** 來源多為受版權 PDF/EPUB（私人站）→ 抽文字後品質視來源而定，髒檔走 Gemini OCR reflow（比照 mueller_build 的 reflow）。**先抽一章評估雜訊再決定切分策略。**

## 中譯本叢集（第三方，私人參考用，user 拍板 2026-06-12）

潘尼卡有相當完整的**中譯叢集**，主力譯者**王志成（浙大哲學系）、思竹**，多收於「宗教與世界叢書」「第二軸心時代文叢」（簡體）。本站私人自用 → **可入庫當「參考層」**（簡體 opencc→繁中，[[feedback_traditional_chinese_only]]），但**只當我逐段自譯的校對對照／使用者參照，不取代主欄**（見 [SKILL.md](SKILL.md) 處理姿態私人例外）。

（2026-06-12 逐一查證；✅=書目已證，⚠️=書確存在但出版社/年/ISBN 未在此環境查實，待取檔時核版權頁）

| 原書 | 中譯本 | 譯者 | 出版社 | 年 | ISBN | 核對 |
|---|---|---|---|---|---|---|
| The Unknown Christ of Hinduism | **《印度教中未知的基督》** | 王志成、思竹 | 四川人民出版社 | 2003 | 9787220061684 | ✅ douban 1270684（228 頁‧宗教與世界叢書）**← 起手卷** |
| （諸宗教相遇）| 《對話經：諸宗教的相遇》 | 王志成 | 四川人民出版社 | 2008 | 9787220076619 | ✅ douban 3354914 |
| The Cosmotheandric Experience | 《宇宙—神—人共融的經驗：正在湧現的宗教意識》 | 王志成、思竹 | 宗教文化出版社 | 2005 | — | ✅ 百度百科 5990394（出版社/年已證，ISBN 待）|
| The Intra-religious Dialogue | 《宗教內對話》 | 王志成、思竹 | 宗教文化出版社 | 2001 | — | ⚠️ 年已證，ISBN 待 |
| The Invisible Harmony | 《看不見的和諧》 | 王志成、思竹 | 江蘇人民出版社 | — | — | ⚠️ 待核 |
| Cultural Disarmament: The Way to Peace | 《文化裁軍：通向和平之路》 | 思竹、王志成 | 四川人民出版社 | — | — | ⚠️ 待核 |
| A Dwelling Place for Wisdom | 《智慧的居所》 | 王志成、思竹 | 江蘇人民出版社 | — | — | ⚠️ 待核 |

> ⚠️ 三本未查實者：此 sandbox 的 web 搜尋對簡體書庫（豆瓣/百度/CNKI）穿透差、baike 與書店頁 403。書確實存在（王志成/思竹潘尼卡譯介系列），但出版社/年/ISBN 以「取得電子檔時看版權頁」為準，勿照本表當定論。譯者搭配多為「王志成、思竹」二人。

> 中譯本多為**簡體掃描／電子書**，取得同走 shadow library（私人自用）或圖書館。**簡體一律先 opencc s2tw + TRAD_FIXES 轉繁**再用。

### 兩種工作流（user 拍板 2026-06-12）

| 情況 | 工作流 | 主欄 | 對照欄 | 腳本模式 |
|---|---|---|---|---|
| **已有完整中譯** | **參考譯本逐段對照（不重譯）** | 既有中譯（第三方‧參考，簡→繁）| 英文原典 | `panikkar_build.py --src <en> --zh-src <zh>`（REFERENCE 模式，無 LLM）|
| **無中譯** | English-first 自譯 | 我的逐段繁中親譯 | 英文原典 | `panikkar_build.py --src <en>`（assemble_pilot，走引擎）|

- **「已有全文中譯就不重譯，直接把參考的放進來逐段對照」**（user 明示）：既有中譯本＝主欄、英文原典＝對照欄、**逐段對齊**。標明「第三方參考譯本」。中譯品質由原譯者負責，我不再自譯。
- **起手卷《印度教中未知的基督》恰有四川人民中譯 → 走 REFERENCE 模式**：英文原典 + 王志成/思竹中譯逐段對照，零 LLM 成本、最快上架。
- 對齊：英中是同一文本的翻譯對，章序一致 → `pair_sections` 按章序配對、章內 `align_secondary` 把英文補到中譯段數（中譯為準）。對不齊整段塞。CJK 章標題（導論/第一章/第N節…）由 `_CJK_HEADING_RE` 偵測切段。
- 反之**無中譯的卷**（多數 Opera Omnia 卷）仍走 English-first 自譯。

## 對齊策略（本卷）

1. 起手卷**英＋繁中雙語**：無跨語對齊問題，中文跟我自己的分段走、英文逐段並陳（`source_order=["en"]`）。
2. 章節錨點切分：英文章標題（Introduction / Chapter N / 命名章）→ `align_editions.py` anchor join（`parse_chapter_number` 已支援 EN/羅馬數字）。
3. 日後升三欄（英＋西＋繁中）時：英西兩版同一文本、章骨架一致 → 章內逐段順序＋長度比對齊（比榮格 Hinkle 改寫好對），對不齊整段塞。
4. 起手仍**先 1 章 smoke test**（`--limit`）→ 確認譯名／分欄效果再全跑。

## 詞庫焦點

潘尼卡橫跨**比較神學／宗教哲學／印度學／三一神學**，自鑄大量概念 → 專屬 [panikkar_glossary.md](panikkar_glossary.md)：
- 招牌自鑄詞：cosmotheandric（宇宙神人共融）、intrareligious dialogue（宗教內對話，**有別於** interreligious 宗教間對話）、Christophany（基督顯現）、tempiternity（時永）、diatopical hermeneutics（跨地詮釋學）、homeomorphic equivalence（同構等價）、ecosophy（生態智慧）
- 核心概念：pluralism（多元論）、the whole Christ（全基督）、advaita（不二）、radical Trinity（根本三一）、the Rhythm of Being（存在的韻律）、sacred secularity（神聖的世俗性）
- 跟 `/translation-glossary` 重疊處（吠陀、奧義書、梵 Brahman、達磨 dharma、業 karma、不二 advaita、三位一體…）→ **以 `name_recommended` 為權威**（[[feedback_glossary_strict_authority]]）
- 人名：Raimon Panikkar→雷蒙‧潘尼卡（早期署名 Raimundo；不寫「帕尼卡」）；Milena Carrara Pavan→米蓮娜‧卡拉拉‧帕萬

## 🚀 新 session 接手清單

> 基建（reader N 欄、`align_editions.py`、`multilang_chunks.py`、`translate_collected_work.py`、`scripts/panikkar_build.py`）全部就緒、test-first、已 push — **不用重做**，直接接真語料。

**穩定步（每章照做，比照 mueller_build）**：
1. **取文字**：上網找英文全文（私人站）→ 抽文字 → 清行內頁碼/腳註雜訊 → 章節 sections（髒檔走 Gemini OCR reflow）。
2. **章節切分**：英文章標題即錨點。
3. **逐段對齊**：雙語只需英文逐段並陳；中文跟我自己分段。
4. **親譯**：英→繁中，**先查 [panikkar_glossary.md](panikkar_glossary.md) 鎖術語**；新人名地名先查 [[translation-glossary]]。
5. **建雙語/三欄**：`content=繁中`、`sources={en}`（或 +es/it）、`source_text` 鏡像 primary → 走 `scripts/multilang_chunks.py` 寫 JSONL → 驗 zh/en 段數相等 → R2 + previews。

**ebook_id**：起手 pilot `55555555-5555-4555-8555-555555555555`（《印度教中未識的基督》）。

### ⚠️ 雷區
- **全部受版權** → 來源檔靠 user 提供或私人站抓；**我不在對話貼整段受版權原文**，文字走本機檔案。
- 潘尼卡英文是 20 世紀學術散文，**長句多、梵/拉丁/希臘原文夾注密**（Brahman, advaita, Logos, plērōma…）→ 譯時保留原文夾注（括號），術語鎖死。
- **自鑄詞最易亂**（cosmotheandric / Christophany / tempiternity）→ 詞庫鎖死，跨卷一致是硬指標。
- 段數對齊閘照跑（zh/en row 數不等 → reader 錯位）；cover chunk 0 必備（reader page 1 永遠當封面，內容從 chunk 1 起）。

## See also

- [SKILL.md](SKILL.md) — 多語對照 pipeline 主文件
- [panikkar_glossary.md](panikkar_glossary.md) — 潘尼卡比較神學／宗教哲學術語表（英/原文/繁中）
- [jung_collected_works.md](jung_collected_works.md) — 第一個案例（榮格，受版權 English-first 方法論本卷沿用）
- [mueller_collected_works.md](mueller_collected_works.md) — 第二個案例（穆勒，build 腳本 reflow/align 模式本卷沿用）
- [[translation-glossary]] — 跨領域名物中譯權威（吠陀/奧義書/梵/達磨/不二等以此為準）
- [[feedback_jung_nonpd_english_first]] — 私人站非 PD 可用、英文先輸入
