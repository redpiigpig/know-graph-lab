
> ⚙️ **引擎政策（2026-06-04 更新）**：所有 LLM 工作一律**優先用 NVIDIA（輝達，`https://integrate.api.nvidia.com/v1`，預設文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避免 429）**，第二層 fallback 用 Gemini，**第三層救急才用 Haiku（NVIDIA→Gemini→Haiku；前兩個免費池都用罄時才動 Haiku）**。視覺類用 NVIDIA 視覺模型（如 `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`）。

# 榮格全集 — 案例盡職調查（版權 / 卷目 / 來源）

第一個 ebook-collected-works 案例。**先讀本檔再開工。**

## 一句話結論

榮格（C. G. Jung, 1875–1961）的「全集」有兩套權威編輯本：德文 **Gesammelte Werke (GW)**（Walter / Patmos / Olten）與英文 **Collected Works (CW)**（R. F. C. Hull 譯，Princeton / Bollingen）。**兩套多數卷仍在版權內**，網路免費全文多為盜版掃描 PDF。**乾淨合法的公有領域來源只有 1929 前的早期著作**，而且早期德文原典與後來 CW 改寫本是**不同版本**，逐段對齊只在「同一文本的德＋英」嚴格成立。

## 版權狀態

| 項目 | 卒年/出版 | 地位 | 備註 |
|---|---|---|---|
| 榮格本人著作（德文原文，作者權利）| 卒 1961 | 歐盟 life+70 → **2032-01-01** 進公有領域 | 在此之前德文 GW 原文受保護 |
| 英文 CW（Hull 等譯本）| 1953–1979 編 | 譯本**獨立版權**（Princeton/Bollingen）| 即使原文公有，譯本仍可能受保護 |
| 既有第三方中譯（商務/國際文化/類型出版…）| 近年 | 受保護 | **絕不入庫**；僅 B 層校對 transient 參考 |
| **1929 前早期著作（美國法）**| 見下 | **公有領域** | 唯一乾淨合法來源 |

> 處理姿態見 [SKILL.md](SKILL.md)「開工前必讀」：reader 只顯示**我的繁中譯文＋來源語言原文欄**；第三方中譯本不入庫；版權內來源走本機 pipeline，不在對話貼整段原文；**公有領域卷優先**。

## 公有領域可用的早期著作（乾淨來源）

這些 1929 前出版，美國公有領域，有合法全文（archive.org / Wikisource）：

| 著作 | 德文原典 | 英譯（公有領域）| 對齊可行性 |
|---|---|---|---|
| 《Wandlungen und Symbole der Libido》(1912, Deuticke) | ✅ archive.org 全文 | ✅ *Psychology of the Unconscious*（Hinkle 譯, 1916）| ⚠️ 德＝1912 原典、英＝1916 譯**同源**，可逐段對；但**≠** CW Vol 5《Symbols of Transformation》(Hull 改寫本) |
| 《Über die Psychologie der Dementia praecox》(1907) | ✅ | 部分 | — |
| *Collected Papers on Analytical Psychology* | — | ✅ (1916/1917) | 英文文集 |
| *The Theory of Psychoanalysis* | 1913 講稿 | ✅ (1915) | — |
| *VII Sermones ad Mortuos*（七次對死者的佈道）| ✅ (1916 私印) | ✅ | 短篇，易做三欄 demo |
| 《Psychologische Typen》(1921) | ✅ 德文 1921（美 PD）| Baynes 英譯受版權 | 德文 PD，英譯不一定 |

**建議起手卷**：用《Wandlungen》(1912 德) + 《Psychology of the Unconscious》(1916 英 Hinkle) 做第一個三欄樣本 — 兩版同源、皆公有領域、來源乾淨，最適合驗證 reader N 欄 + 對齊 pipeline。**標清楚這是 1912/1916 早期版，非 CW Vol 5。**

## CW / GW 20 卷對照（卷目 = 書目事實）

> ⚠️ 多數卷仍在版權內（見上表）。卷目僅作 corpus 規劃 / volume 命名用。

| CW | 英文卷名 | GW | 對應 | 繁中暫定卷名 |
|---|---|---|---|---|
| 1 | Psychiatric Studies | 1 | ✓ | 精神醫學研究 |
| 2 | Experimental Researches | 2 | ✓ | 實驗研究（字詞聯想）|
| 3 | The Psychogenesis of Mental Disease | 3 | ✓ | 精神疾病的心理成因 |
| 4 | Freud and Psychoanalysis | 4 | ✓ | 佛洛伊德與精神分析 |
| 5 | Symbols of Transformation | 5 | ✓ | 轉化的象徵 |
| 6 | Psychological Types | 6 | ✓ | 心理類型 |
| 7 | Two Essays on Analytical Psychology | 7 | ✓ | 分析心理學二論 |
| 8 | The Structure and Dynamics of the Psyche | 8 | ✓ | 心靈的結構與動力 |
| 9i | The Archetypes and the Collective Unconscious | 9/1 | ✓ | 原型與集體無意識 |
| 9ii | Aion | 9/2 | ✓ | 伊雍（Aion）|
| 10 | Civilization in Transition | 10 | ✓ | 轉變中的文明 |
| 11 | Psychology and Religion: West and East | 11 | ✓ | 心理學與宗教：西方與東方 |
| 12 | Psychology and Alchemy | 12 | ✓ | 心理學與煉金術 |
| 13 | Alchemical Studies | 13 | ✓ | 煉金術研究 |
| 14 | Mysterium Coniunctionis | 14 | ✓ | 神祕合體（Mysterium Coniunctionis）|
| 15 | The Spirit in Man, Art, and Literature | 15 | ✓ | 人、藝術與文學中的精神 |
| 16 | The Practice of Psychotherapy | 16 | ✓ | 心理治療實務 |
| 17 | The Development of Personality | 17 | ✓ | 人格的發展 |
| 18 | The Symbolic Life | 18 | ✓ | 象徵的生命 |
| 19 | General Bibliography | — | — | 總書目 |
| 20 | General Index | — | — | 總索引 |

> 宗教研究焦點（使用者領域）：**CW 11（心理學與宗教）、12–14（煉金術三部）、9i/9ii（原型/伊雍）** 對宗教學最相關，可優先排序 — 但全在版權內，須走本機處理路徑。

## 對齊注意

- CW 段落多有 Bollingen 段碼 `[¶ N]`；GW 對應段碼可當 join key（[SKILL.md](SKILL.md) 對齊策略 1）。
- Vol 5 是經典坑：CW《Symbols of Transformation》是 Jung 1952 大改寫，跟 1912《Wandlungen》結構差很多 → 別把 1912 德文跟 CW5 英文硬對。
- 煉金術卷（12–14）大量拉丁文引文 + 圖版 → OCR 噪聲高，圖版另存。

## 來源紀錄

| 卷 | 德文來源 | 英文來源 | 取得狀態 |
|---|---|---|---|
| 早期《Wandlungen》1912 | archive.org `Jung_1912_Wandlungen`（PD，**純掃描無文字層**，426 頁）| **Project Gutenberg #65903** Hinkle 1916 HTML（PD，乾淨結構）| ✅ 已驗證 |
| CW 11 / 12–14 等版權卷 | 本機處理路徑 | 本機處理路徑 | — |

## Pilot 實況（2026-06-03，真資料跑過）

起手卷 = 1912《Wandlungen》(de) ＋ Hinkle 1916《Psychology of the Unconscious》(en)。實際跑出三個關鍵結論：

1. **德文必須重 OCR**：archive.org 的 1912 PDF 是**純圖像無文字層**；archive.org 自家 djvu OCR 章節標題不成行（`anchor_coverage=0`）。**本專案 Gemini/Haiku 重 OCR 開頭 14 頁 → 乾淨還原結構**：偵測到 `ERSTER TEIL`／`Einleitung`／`I.`／`II.` 標題。✅ 路線可行。
2. **Gemini 全 4 把 key 配額/額度耗盡**（key#1 prepay depleted、#2-4 quota exceeded）→ 走 Haiku image-OCR fallback 成功。⚠️ 影響全專案預設 OCR/翻譯引擎，user 需注意 Gemini 帳單。
3. **🔴 德 1912 ↔ 英 1916 不逐段對齊（實證）**：Hinkle 重組了結構 —
   - 她自己加了長篇 translator's introduction（≠ Jung 的 Einleitung）；heading 自動對齊會抓錯（把 Jung 的 Einleitung 對到 Hinkle 自序）。
   - 用 **Ferrero 法文題詞**當指紋才定位到真對應：德 `Einleitung` = 英 `CHAPTER I — CONCERNING THE TWO KINDS OF THINKING`。
   - 但**章內段落仍對不齊**（英 Ch I 有 74 段、德 4 段；Freud 提及散落非對應段）。→ **正確逐段三欄需人工逐句配對 + 我親譯**，非自動 run 能成。

### ✅ 首個真實三欄切片上架（2026-06-03）
走 (a) 人工配對：用**內容指紋**（非 heading）確認德 Einleitung = 英 §8 INTRODUCTION（兩者皆譯同一段 Freud/Ödipus 文字，Hinkle 的 heading 對齊會抓錯）。我**親譯整章「引論」（Einleitung）5 段**德文→繁中（詞庫鎖定），建 trilingual ebook（`ebook_id 22222222-2222-4222-8222-222222222222`，test 用，2 chunks＝封面 + 引論整章），reader 三欄（中/德/英）逐段對齊：截圖實證 ✅ + JSONL 段數對齊驗證（zh=de=en=6 段，heading 同列）✅。
- 方法鎖定：**逐章先用內容指紋配對 de↔en 章節，再人工逐段對齊 + 親譯**。heading／epigraph 不可靠（Ferrero 題詞在多處出現）。
- 工具：`scripts/_jung_ocr_slice.py`（OCR slice）、`scripts/_jung_pilot_build.py`（build，皆 `_` gitignore 一次性）。
- 擴充：同法逐段補完整章 → 再下一章；德文重 OCR 待 Gemini 配額回復或續用 Haiku。

### 結論與下一步抉擇
機械 pipeline 全部就緒且實證；卡點是**跨版逐段對齊是編輯級人工活**（Hinkle 非段落同構）。User 已拍板走 **(a) 逐章人工配對 + 親譯**。

---

## 🚀 新 session 接手清單（2026-06-04 更新）

> User 指示：開新 session 接著把榮格三欄做下去。**方法已穩定且改成可續傳結構，照下面做即可。**

### 🆕 可續傳結構（2026-06-04 重構）
- **每章一個 JSON**：`.claude/skills/ebook-collected-works/jung_data/chNN.json`（持久化、已 commit、不在 tmp）。
  schema：`{chunk_index, chapter_path, volume, parent_volume, title_en, rows:[{zh,de,en},…]}`。每個 row = 一個對齊段（heading 也算一 row，zh/de/en 用 `## ` 前綴）。
- **組裝器**：`python scripts/jung_build_all.py`（**注意：無底線前綴才不會被 `/scripts/_*.py` gitignore；已 commit**）→ 讀 cover + 所有 `jung_data/ch*.json`（排序）→ 寫 reader JSONL + upsert DB。**內建對齊閘**：任何 chapter 的 zh/de/en row 數不等就 `SystemExit`。
- **加新章節**：用 `c:/tmp/_jung_append.py` 的 `add(zh,de,en)`+`flush()`（append 到指定 chNN.json），分批寫 `_jung_ch?_bN.py` 跑完再 `_jung_build_all.py`。每批 commit。
- **詩／跨語字串**：用 blockquote（每行 `> ` 前綴、單 `\n`、**絕不可有 `\n\n`**），reader 才會保留換行又不破壞段對齊（renderMarkdown：blockquote split `\n`→`<br>`；一般 `<p>` 會把單 `\n` 併成空格）。

### 目前成果（已上架、已驗證）
- **Test ebook**：`ebook_id = 22222222-2222-4222-8222-222222222222`（圖書館「世界宗教／深層心理學」，標題「力比多的轉化與象徵（試譯·德英中三欄）」）。
- **✅ 第一章「引論」(Einleitung)**：6 rows（`ch01.json`）。
- **✅ 第二章「論兩種思維」(Über die zwei Arten des Denkens = Hinkle Ch I)**：**全章 77 rows**（`ch02.json`，含莫里克〈少女初戀之歌〉blockquote 補譯；Hinkle 英譯本略此詩）。逐段對齊（zh=de=en=77）✅，截圖實證 ✅。16,678 繁中字。
- **✅ 第三章「米勒幻想的分析預備材料」(= Hinkle Ch II, The Miller Phantasies)**：**全章 20 rows**（`ch03.json`，含羅斯丹《大鼻子情聖》西哈諾訣別詩＋臨終獨白兩段法文詩補譯〔Hinkle 略〕、米勒法文自述引文）。
- **✅ 第四章「創世讚歌」(Der Schöpferhymnus = Hinkle Ch III, The Hymn of Creation)**：**全章 95 rows**（`ch04.json`，含米勒英文〈創世讚歌〉三節詩、約伯哀歌16章、愛倫坡〈烏鴉〉兩節、浮士德/約伯「上帝打賭」、約伯記40–41章貝赫摩特/利維坦讚歌、塞內卡致路奇里烏斯兩段、奧古斯丁、居蒙論密特拉教、塞內卡聖林與「神住在每個正直者裡」收尾）。本章是全書最長、宗教學最豐（邏各斯/靈/童貞之母、神的雙重本性、基督教 vs 密特拉教、認罪即移情）。19,281 繁中字。
- **✅ 第五章「飛蛾之歌」(Das Lied von der Motte = Hinkle Ch IV)**：**全章 111 rows**（`ch05.json`，全書最長，20,027 繁中字）。含米勒〈飛蛾致太陽〉詩、Faust三段詩、維吉爾第四牧歌、馬太10:34、神＝力比多/懷神即是神、埃及《亡靈書》成神歌、密特拉禮儀希臘文（七蛇少女/七牛神/赫利俄斯-密特拉/火之祈求）、三位基督教神祕家內在之光、尼采〈榮耀與永恆〉〈烽火〉、**太陽陽具+霍內格名案**、啟示錄人子三異象、基督即新太陽（斐洛/安博羅修/梅利托/偽居普良/金口若望/優西比烏/奧古斯丁）、太陽英雄抒情高潮、垂死復活之神、拜倫〈天與地〉全劇收尾（安娜/阿荷利芭瑪呼求、利維坦浪沫、雅弗預言→救贖者/太陽英雄＝力比多意象）。
  - ⚠️ **OCR 雷區（續第二部沿用）**：德文腳註與正文交錯亂序——**以 `jung_ch5_en2.txt`（含詩節 [V#]）英文正文順序為 row 粒度**，德文照英文段落拼接跳腳註；Hinkle 偶把德文正文移至他處（如 Conceptio Immaculata 移到 Part II），依英文 grain 此處略、到該處再補。

### 🎉 第一部（Erster Teil）全部譯竣 — 引論＋第二～五章，共 309 段 / 62,177 繁中字

### 🚧 第二部（ZWEITER TEIL）進行中
- **✅ 第二部第一章「力比多面面觀」(Aspects of the Libido = ZWEITER TEIL 引論)**：**全章 40 rows**（`ch06.json`）。德文 6136–6627 / 英文 HTML 6116–6524。含《白騾奧義書》樓陀羅讚（2,3,4,7,8,11,12-15）+《羯陀奧義書》拇指大小內在自性、太陽=神=力比多、浮士德「眾母親」鑰匙場景＋魔鬼成善之力、拇指仙童=陽具象徵、卡比里諸神/伊達山達克堤利/尖帽=包皮、神聖男童 puer aeternus/底比斯瓶畫法勒斯=普里阿普斯、宗教英雄=力比多擬象、**「力比多」術語考**（西塞羅 Tusc.IV 拉丁定義＋斯多噶 βούλησις vs 欲念、撒路斯特、梵文 lúbhyati 哥德語 liufs 詞源、力比多=生物學界的能量〔羅伯特‧邁爾〕）。
- **✅ 第二部第二章「力比多的概念與發生學理論」(The Conception and Genetic Theory of Libido)**：**全章 22 rows**（`ch07.json`）。德文 6628–7385 / 英文 HTML 6525–7081（en 22 entries、無詩節）。含 性學三論力比多=性驅力/移置/Triebbündel、佛洛伊德妄想症長引文、早發性癡呆現實喪失、榮格「心靈能量」→發生學力比多再定義、批評亞伯拉罕、繁衍驅力/叔本華意志/投置、**斐涅斯-愛若斯/普羅提諾 太一-智性-世界靈魂=三位一體**（希臘 μία οὐσία ἐν τρισὶν ὑποστάσεσιν）、邏各斯與甘露/阿芙羅狄忒之鴿=聖靈、原力比多去性化（昇華 vs 壓抑）、自體情慾→自閉(Bleuler)修訂、**霍內格扁平地球偏執症+太陽陽具/施皮爾賴因酒=精液、佐西默斯煉金異象、土水=母**、象徵=情結消解入思維整體=藝術驅動力、施泰因塔爾「就像」類比驅力。西塞羅/撒路斯特拉丁＋梵文/哥德語詞源散見 Ch I 末段。抽取腳本 `c:/tmp/_jung_extract_ch7.py`。
- **✅ 第二部第三章「力比多的轉化——原始人類發明的一個可能源頭」(The Transformation of the Libido)**：**全章 71 rows**（`ch08.json`，17,971 繁中字）。德文 7386–8947 / 英文 HTML 7082–8168（en 71 entries，6 詩節）。含 緊張性憂鬱患者太陽穴鑽洞案例、力比多前性發展階段（蝴蝶蛹期）/退行兩案例、**普羅米修斯=印度鑽火木 Pramantha**（Kuhn manthâmi-μανθάνω、弗勒癸阿斯火鷹、婆利古）、鑽火木=陽具/阿耆尼自女陰生、韋伯取火祭儀、**梨俱吠陀鑽火之歌**、Nodfyr+1268拉內科斯特拉丁、瓦昌迪求孕舞、取火=交媾替代物/節奏為要、亂倫禁忌→去性化→大地母親農耕、**廣林奧義書創世神話**（阿特曼裂分為夫妻、自口手生火）、口手前性區（口=女陰手=陽具）、語言起源=驅力轉外那一刻、**愛多列雅/廣林奧義書 火-言語-自我之光**、詞根 bhâ/svénô/své 發聲=太陽、**歌德浮士德序幕二詩/荷爾德林太陽少年/曼尼利烏斯/梵語 têjas 八義**、神祕合唱、agnis=阿耆尼=基督中介者、**但以理3烈火窯+1471貧民聖經三一/合一**、以賽亞/厄弗冷、阿耆尼=蘇摩=不死之藥=力比多、**取火=劫奪/被禁之物=手淫/阿拉丁神燈**、縱火手淫案例、儀式=對手淫退行的法律防護、Diana of Aricia 扯枝=manthâmi reiben/reissen 亂倫層。抽取腳本 `c:/tmp/_jung_extract_ch8.py`。
- **✅ 第二部第四章「英雄的無意識起源」(The Unconscious Origin of the Hero)**：**全章 61 rows**（`ch09.json`，23,753 繁中字）。德文 8948–10730 / 英文 HTML 8169–9496（en 61 entries）。含 力比多擬人化為英雄=太陽軌跡、米勒第三創作奇萬托佩爾、被動內傾=無能去愛/抵抗=逆流回源/拉羅希福柯論怠惰、可怕母親、無意識一致性vs個體化（叔本華哈特曼/中國人面孔）、教皇=可見之神=愛自己投射的無意識、安泰俄斯、斯芬克斯=可怕母親=厄喀德娜譜系、阿茲特克=投射的受壓抑性人格、母親之手/金雉=阿耆尼、奇萬托佩爾命名巫術（伊西斯奪拉之名）、波波卡特佩特擬聲、肛門與尊崇/糞便與黃金/孩子排便=繁衍理論/龍布羅梭/塗糞迎接、向後扔母骨（丟卡利翁）、亞哈斯維爾流浪猶太人/希德爾/古蘭經18章山洞七眠子/摩西尋兩海交會（雙角者 Dhulqarnein）/基督=以利亞=希德爾=赫利俄斯橋樑/吉爾伽美什恩奇都=亞哈斯維爾原型/密特拉殺牛祭兩持炬者=兩強盜=三位一體=太陽神話/馬克羅比烏斯太陽四齡/摩羯山羊魚=魚=孩子=力比多更新/施洗約翰聖靈與火、諸神=力比多=我們的不朽者、三位一體源自陽具象徵、太陽=陽具月亮=陰道/門=阿提斯=母親亂倫→閹割/英雄=漫遊者尋失去的母親=受苦無意識之神話、**歌德浮士德「眾母親」全場景收尾**。⚠️ **Hinkle 章界註記**：英德 Ch IV 同止於浮士德「眾母親」詩（德 D183–D222，D223「v.」即 Ch V 標記）；無 Hinkle 位移。抽取腳本 `c:/tmp/_jung_extract_ch9.py`。
- **✅ 第二部第五章「母親與重生的象徵」(Symbols of the Mother and of Rebirth)**：**全章 208 rows**（`ch10.json`，**全書最大章**，42,233 繁中字）。德文 10731–14190 / 英文 HTML 9497–11982（208 entries / 12 詩節）。含 E168/E169 龍-提什特里亞、Heddernheim 密特拉四圖→十架之神贖亞當罪、E171+V172 奧丁懸樹九夜詩、E173–E188 十字象徵整段＋柏拉圖《蒂邁歐篇》世界靈魂（墨西哥十架人祭/菲萊奧西里斯/環首十字 Crux Ansata/德魯伊樹十字/耆那知識樹/世界靈魂=X 聖安德烈十字=母親/巨匠造物神/第歐根尼木桶/阿特曼分裂結合）、E189–E199 圖姆/赫利奧波利斯+古英語瑪利亞與十字架對唱（馬斯科吉水上十字獻祭/圖姆「其母之父」/尤薩斯秋分/因陀羅眼=生殖器/阿伽托得蒙蛇/赫努姆=結合/兩位伊西斯）、E200–E207 收尾（亂倫禁忌=馴化強制/宗教昇華動物動力/米勒紫色海灣詞源 κόλπος=母胎/浮士德追日詩二首/falaise→wa-ma=媽媽）。抽取腳本 `c:/tmp/_jung_extract_ch10.py`。

  **🔑 新 session 續傳細則（ch10 專用，照做即可）：**
  1. **工作檔**（c:/tmp，被清就重建）：`jung_ch10_de.txt`（538 段，標 `[D0]`…）＋ `jung_ch10_en.txt`（208 entries，標 `[E0]`…/`[V0]`詩節）。重建：`python c:/tmp/_jung_extract_ch10.py`（它讀 `c:/tmp/jung_wandlungen_de_1912.txt` 第 10731-14190 行 + `c:/tmp/jung_pou_en_1916.html` 第 9496-11982 行；這兩來源檔若也沒了見下「要重抓的檔」）。
  2. **每批做法**（仿 `c:/tmp/_jung_ch10_a.py`…`_az.py`）：①讀下一批 `[EN]` 英文 + 對應 `[DM]` 德文（英文正文 entry 順序＝row 粒度，德文照英文段落拼接、跳腳註 `N )`）；②寫一個 `_jung_ch10_XX.py`：`json.load` ch10.json → 逐 row `add(zh, de, en)` → `doc["rows"].extend(new)` → 寫回（`ensure_ascii=False, indent=1`）；③德文清 OCR（常見：Bild/Relief/Rê/Tiernatur/Greek 還原乾淨 polytonic／digamma；跨 `[D]` 片段以 smart-join 接、`-` 結尾去連字號）；④詩/聖經/希臘/拉丁照規則（詩 blockquote `> ` 每行；聖經 zh=和合本；作者英文詩 de=en；古典希臘/拉丁/Homer 引文 de=德譯 en=英譯 zh親譯）；⑤`python scripts/jung_build_all.py`（**對齊閘**：`len(zh)==len(de)==len(en)` 不等會 SystemExit）；⑥`git add ch10.json && git commit -m "feat(jung): … [loop]" && git -c rebase.autoStash=true pull --rebase --no-edit -q && git push`（**與平行 mueller/gnostic session 搶 push 用此 autostash-rebase 串**；race 被拒就再跑一次 pull-rebase+push）。
  3. **每批完更新本行「進度」與「下一批」指標**，另起 commit `docs(jung): … [loop]`。
  4. ⚠️ **絕不碰** `mueller_data/`、`mueller_build.py`、`scripts/gnostic_library.py`（別的 session）；中文一律繁體、中間點用「‧」。
- **✅ 第二部第六章「為脫離母親而戰」(The Battle for Deliverance from the Mother)**：**全章 76 rows**（`ch11.json`，英文 HTML 11982–13147，76 entries / 11 詩節，17,681 繁中字）。森林=聖樹=母親、奇萬托佩爾戲劇法文開場、E6 馬=動物性無意識巨段（諸神坐騎/魔鬼馬蹄足=陽具/閃電=馬）、戴歐尼修斯牛蹄禱辭、馬=風/火/光、四馬戰車=時間、廣林奧義書獻祭之馬、埃永獅頭時間神、馬=死亡之樹/特洛伊木馬、莎翁卡西烏斯=母親認同、阿普列尤斯戰鬥=交媾、約伯記箭靶+尼采〈魔術師〉〈寧錄〉二詩=自獵自縊內傾、霍普特曼《沉鐘》、維濕奴入定生梵天、菲羅克忒忒斯毒蛇咬足、埃及 Rê–Isis 讚歌（毒蟲螫太陽神=母親害死/索真名=力比多回母/退回天牛）、回望渴慕=麻痺毒蛇/參孫大利拉、密特拉負牛+基督背十字架、獻祭=放棄母親=爭取自立、箭傷=交媾象徵=新生即過往之死。抽取腳本 `c:/tmp/_jung_extract_ch11.py`。
  - **🔑 章界映射關鍵（Hinkle 重組）— 已實證更正**：**德文版第二部後段只有兩章** — 德 VI「Der Kampf um die Befreiung von der Mutter」(de 14189–15781) ＝ **英文 Ch VI（≈1:1，已 76 rows 完成）**；德 VII「Das Opfer」(de 15780–22374，至 Register 索引前) ＝ **英文 Ch VII「Dual Mother Role」＋ Ch VIII「The Sacrifice」兩章合併**（Hinkle 把德文 Das Opfer 拆成兩英章；兩者開頭皆「奇萬托佩爾獨白」可驗證）。英文章界：VI=HTML 11982–13147、VII=13147–16443、VIII=16443–18479。
- **🚧 第二部第七章「雙重母親」(The Dual Mother Role)**：建設中（`ch12.json`，英文 HTML 13147–16443，**294 個英文 entries / 59 詩節 — 全書最大章**）。德文＝德 VII「Das Opfer」前半（`jung_ch12_de.txt`，1234 段）。**⏭️ 進度：已建 44 rows（標題＋E1–E43）**：…海華沙前史 Mudjekeewis 奪大熊貝帶/化西風眾風之父/東風 Wabun 求愛/由風與水重生。抽取器 `c:/tmp/_jung_extract_ch12.py`（294 entries / 1234 段）。
  - **⚙️ 寫法定案（user 核可）：en/de 不由模型逐字重打，改由 fill 腳本從來源檔程式帶入；模型只寫中文。** 模板 `c:/tmp/_jung_ch12_h.py`：`ROWS=[(en_tag, is_verse, de_spec, zh),…]`；`de_spec="=en"`（榮格保留英文的海華沙等詩節）或 `["D67",…]`（德文片段 id，腳本 smart-join+去腳註+OCRFIX）；`en` 自 `jung_ch12_en.txt` 抓（verse→blockquote）、`de` 同理。每批只換 ROWS（en_tag/de id 對照＋中文），跑 → build → commit。
  - **fill 模板增強**（`c:/tmp/_jung_ch12_j.py`）：de_spec 新增兩式 — `de_slice("D85","起anchor","止anchor")`（一個德文片段被 OCR 合併成多個 en entry 時，用短 anchor 從來源檔切片）＋`de_verse(["D86",...])`（詩節每片段一行 blockquote）。**整晚自動跑、不停問**（user 指示）。
  - **進度 216 rows（E1–E215）**：餅酒=基督體血=不死食糧=與基督同子宮所生弟兄/聖餐危險=不配領(與厄琉西斯地下聖婚心理關聯/凡俗誤解奧祕=狂歡祕密=惡行)/溫特奈勒褻瀆聖餐(妓院=魔鬼團契吮蛇頭/魔鬼杯桌不義餅邪惡酒)=活出本性論=普里阿波斯神(黑髮俊美口出媚言少女愛慕)。⚠️E212 德文中段OCR缺以[…]標。**下一批 E216**＝溫特奈勒續/聖餐母題回收=力比多昇華橋…德文 D566 起。皆 PD。fill 法續。⚠️ pre-push hook 偶因平行 session race 報測試失敗，`npm test` 綠就再 pull-rebase+push（勿 --no-verify）；push race 被拒也再跑一次。
- **⏭️ 後續章節**：VIII 獻祭（en 16443–18479，建 `ch13.json`，德文＝德 VII「Das Opfer」**後半**，續用同一德文塊 de 15780–22374，新 `_jung_extract_ch13.py` 改 en 行號 16443:18479、德文 block 取 ch12 用剩的後段）。逐章流程同下方「新 session 續傳細則」（ch10 寫法通用，僅改檔名/行號）。

### 穩定的 5 步方法（每章照做）
1. **德文重 OCR**（Gemini 全耗盡 → 用 **Haiku**，user 訂閱制不計費）：
   `python scripts/_jung_ocr_slice.py <firstPage> <lastPage>` → 寫 `c:/tmp/jung_wandlungen_de_1912_ocr.jsonl`（**會覆寫**，做新章前先存舊的或改 OUT）。先 `_jung_ocr_slice.py` 裡的 SRC 指向德文 PDF（見下「要重抓的檔」）。
2. **內容指紋配對 de↔en 章**：**不要信 heading／Ferrero 題詞**（多處重複會誤配）。用獨特內容（人名／關鍵句）grep 英文 HTML 各 section 找真對應。已知：德 `Einleitung` = 英 §8 `INTRODUCTION`（非 §9）。
3. **人工逐段對齊**：每個德文段落，從英文找語意對應段（Hinkle 段界與德文不同，允許一德對多英／反之）。
4. **親譯**：德→繁中，**先查 [jung_glossary.md](jung_glossary.md) 鎖術語**（自性≠本我、無意識≠潛意識、力比多、個體化、共時性…；人名佛洛伊德≠弗洛伊德）。新人名先查 [[translation-glossary]]（已升全領域）。
5. **建三欄**：編 `scripts/_jung_pilot_build.py` 的 `zh/de/en_` 三個 list（每章 = heading + N 段，三 list 段數**必須相等**），跑 `python scripts/_jung_pilot_build.py`。驗證 `zh=de=en` 段數相等。

### 驗證 / 截圖
- 段數對齊：讀 JSONL 比對 `content` / `sources.de` / `sources.en` 的 `\n\n` 段數。
- 視覺：`npm run dev`（會綁 3001 若 3000 被占）→ `node scripts/screenshot_book.mjs --ebook 22222222-… --pages <N> --view parallel --base http://localhost:<port> --out c:/tmp/shot`。**device gate**：tool 已注入 `kgl_device_id=screenshot-bot`（`trusted_devices` 預埋過，勿刪）。截圖 >2000px 要先 crop（PIL）再看。完看 **停掉自己起的 dev server**（只停那個 port）。

### 要重抓的檔（tmp 被清過）
- ❌ **德文 PDF**：`c:/tmp/jung_wandlungen_de_1912.pdf` 已刪 → 重抓：`https://archive.org/download/Jung_1912_Wandlungen/Jung_1912_Wandlungen.pdf`（29MB，426 頁，純圖像 PD）。
- ✅ 還在：`jung_wandlungen_de_1912_ocr.jsonl`(pp1-14)、`de_einleitung.txt`、`en_introduction.txt`、`en_ch1.txt`、`jung_pou_en_1916.html`(Gutenberg #65903 全文)。
- 英文全文若沒了：`https://www.gutenberg.org/cache/epub/65903/pg65903-images.html`（被擋就用 mirrorservice.org 鏡像，見 git log）。

### 待辦（優先序）
1. **下一章＝第三章**：德文 `III. Vorbereitende Materialien zur Analyse der Miller'schen Phantasien`（德文 OCR txt 第 1884 行起）= 英 `CHAPTER II — THE MILLER PHANTASIES`（`jung_pou_en_1916.html` 第 3114–3376 行）。流程：用 `c:/tmp/_jung_extract_ch2.py` 改 SRC 行號重抽 de/en 段 → 配對 → 親譯 → `_jung_ch3_bN.py` append 進 `ch03.json` → build。注意英文章號比德文少 1（Hinkle Ch II = 德文 Kap III）。Miller 章起會大量出現英／法詩引文與 Miller 本人法文原文。
   - 德文全文已在 `c:/tmp/jung_wandlungen_de_1912.txt`（23918 行，djvu 文字層，含 OCR 雜訊與行中頁碼/腳註，需清）；英文全文在 `c:/tmp/jung_pou_en_1916.html`。tmp 被清的話德文重抽見下「要重抓的檔」（或本檔來源紀錄）。
2. **腳註**：目前略過書目腳註（里克林等出版資訊、Ninon 腳註）。要補的話用 reader 的 `(N)` + `———` 腳註機制（見 [[scripture-fathers]] footnote 行為），三欄各自的腳註 by-number 對齊（reader `parallelColumns.footnotes` 已支援）。
3. **正式化**：改掉「試譯」標籤／給正式書名分類／補封面圖／決定正式 `ebook_id`（目前是 test 222…）→ push R2 + 刷 previews（參 `scripts/translate_collected_work.py` 的 `_upload` 或 ebook-pipeline）。
4. （未來）受版權 CW 卷：等 user 給乾淨來源檔，不抓盜版全文。

### 基建現況（都 test-first、已 push，不用重做）
- reader N 欄：`pages/ebook/[id].vue` + `lib/multilang-sources.ts`(27 例) + API passthrough。
- Python 寫入器 `scripts/multilang_chunks.py`(21 例) / 對齊 `scripts/align_editions.py`(20 例) / driver `scripts/translate_collected_work.py`（含 `load_html_sections`，11 例）。full pytest 155+ passed。
- 詞庫 [jung_glossary.md](jung_glossary.md)（心靈工坊/TSAP/《榮格心理學辭典》查證鎖定；辭典是版權書只作術語參考不轉錄）。

### ⚠️ 雷區
- Gemini 4 key 全耗盡（billing），別再排 Gemini OCR/翻譯，一律 Haiku。
- `_jung_*.py`、`c:/tmp/*` 是一次性（`_`/tmp 已 gitignore）；別當正式碼。
- 三欄 build 三 list 段數不等 → reader 會錯位；build 後務必驗段數。
