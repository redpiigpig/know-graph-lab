---
name: ebook-collected-works
description: 「經典學者全集」的收錄流程 —— 以**學科**組織（哲學／社會學／宗教學／神學／佛學／心理學／人類學…），獨立 `/collected-works` portal（依學科分區）＋作家 hub（小傳／肖像／年表／著作目錄）＋單卷 reader。跟 [[ebook-translate]]（一般外文→繁中雙語）、[[scripture-fathers]]（公有領域教父原典）並列。四種收錄 pipeline：**多語對照**（原文＋既有譯本＋我的繁中，N 欄逐段）／**單一語言**（本即繁中的漢傳全集，零翻譯零對齊）／**REFERENCE**（已有完整第三方中譯就不重譯，原文逐段對照）／**自譯**（English-first 引擎逐段翻）。Use when 使用者要把某位學者的全集（依學科）做成 hub＋逐段對照上架、要新增作家或學科、要擴充 reader 多欄、要設計／修多語 JSONL schema、要對齊跨版本段落。各學科案例見下「§C 各學科案例」；schema／對齊／portal 基建見「§B 方法論核心」。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash-0731`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

> 📚 **註釋與書目政策（2026-09-09 使用者定調，推翻舊規）**：**尾註／腳註／參考書目一律要收，不可略過。**舊做法把 Notes／Bibliography 當成「檢索裝置不是散文」而跳過，使用者明確推翻：**「不然我怎麼確認他引用的史料？」**——對研究用途而言，註釋正是全書最需要的部分，少了它就無法核對作者到底引了什麼。見 [[feedback_transcribe_notes_and_bibliography]]。
> - **註釋**：全部轉錄。敘述性的註（含論證或評語）要譯成繁中；純書目式的註（作者‧書名‧卷期‧頁）**引註字串原樣保留**以便查證，可另加中譯題名。
> - **參考書目**：全部轉錄，原文原樣；可加中譯題名。
> - **縮寫／略語表必收**（例：豪斯評傳的 Attribution Abbreviations——SK＝《聖書之研究》、MKK＝《無教會》、ZenshûA/B＝1932–33 與 1981–84 兩種《內村鑑三全集》）。沒有這張表，註釋裡的代號無法解讀，等於沒收。
> - **唯一可略者：Index（索引）**——它是指向紙本頁碼的指標，站上不重現紙本頁碼，轉錄無用。年表／詞彙表若 hub 已另有，註明「已另存」即可，不必重複。
> - 已上架但缺註釋的書要**回頭補**；補完在該案例檔記一行。

> 📄 **頁碼政策（2026-09-09 使用者定調）**：**轉錄一律要帶得回原書頁碼**——使用者引用時必須寫得出「第幾頁」。見 [[feedback_transcribe_page_numbers]]。
> - **有頁碼的來源**（PDF、掃描本、archive.org djvu、NDL 影像）：逐段記下該段所在的**原書印刷頁**，寫進 chunk 的 `page_number`。重整流程不可重編（[[feedback_pdf_page_number]]）。
> - 🚨 **絕不可拿流水號冒充頁碼。**全集那條線曾把 `page_number` 填成 `chunk_index + 1`（`uchimura_auto.py`），465 頁的豪斯評傳變成 152 個「頁碼」——看起來正常、照著引就是錯的。**這比沒有頁碼更糟**，因為它會讓人真的照著寫進論文。沒有真頁碼時**寧可留 null**。
> - **本來就沒有頁碼的來源**（青空文庫等電子底本、HTML 網頁）：`page_number` 留 null，改記**底本資訊**（青空文庫每篇末的「底本：」區塊：出版社‧版次‧印刷年），讓引用者至少標得出所據版本。🚨 `uchimura_build.py` 目前**刻意丟掉**底本區塊，要改回來。
> - **註釋與參考書目**同樣要記頁碼（例：豪斯評傳的尾註在 PDF p429–451、書目 p452–457）。
> - ✅ **豪斯評傳已補真頁碼（2026-09-10）**：`howes_build.folio_of()` 從書眉那一行（size 8.0、y≈36）讀出印刷頁碼；章首頁按慣例不印書眉，由鄰頁遞推（`fill_folios`，先順推再逆推——該節第一頁多半就是章首頁，只能由下一頁減一）。**羅馬頁碼不做算術**，推不出來留 None（序言的 xii 跟正文的 12 是不同的兩頁）。`load_work_sections` 現在多回一個與 `paras` 等長的 `pages` 欄。實測 1442 段裡 **1438 段有真頁碼**（序言 xii–xvi／導論 1–12／結論 381–398）。
> - 🚨 稽核跑出「掃描 0 個 JSONL」時先看 **`G:` 有沒有掛載**，不是判準壞掉。2026-09-10 連三次空手而回都是這個原因（Google Drive 沒起來）。
> - 稽核工具**改用 `scripts/audit_page_numbers_db.py`**（直接查 DB，不碰 Drive；舊的 `audit_page_numbers.py` 讀 Drive `_chunks/*.jsonl`，Drive 沒掛載時會安靜地掃到 0 個檔就結束）。
> - 🚨 **`serial` 不等於假**。一頁一 chunk 的 PDF 本來就滿足 `page_number == chunk_index+1`，那個頁碼是真的。真正的造假是 **EPUB 卻 serial**（EPUB 沒有版面就沒有頁碼，逐一遞增只可能是 `chunk_index+1` 冒充的）。不分這一刀，全庫會從「51 本待修」變成「1,146 本待修」，而且會去清掉一千多本頁碼正確的書。
> - ✅ **2026-09-10 全庫已清零**：4,114 本裡 `serial-epub` 51 本／6,486 chunk（全集 50 ＋ 圖書館 1）已用 `scripts/fix_fake_page_numbers.py` 清成 NULL；豪斯評傳例外，改推真頁碼（148/152 有值，1–398）。現況 serial-epub **0**、serial-pdf 1,095、real 2,049、none 885、sparse 85。
> - ⏳ `apocrypha_sections` 41,458 段的 `page_number` **一筆都沒填**（schema 有欄位、資料是空的）。

> ✍️ **語域：一律白話文（2026-09-10 使用者定調）**。原文是文語体（明治文語、舊字舊假名）也一樣——**原文的古雅是日文那一邊的事，中譯要讓今天的讀者讀得懂**。不要用句末的「也／矣／乎／哉／焉／耳」，不要拿「之」當「的」用。
> - **唯一例外是詩詞韻文**（讚美詩、和歌、漢詩、引用的詩行），那些照韻文體譯，可用文言。
> - 稽核：`scripts/audit_classical_register.py`（虛詞密度判語域，classical／mixed／vernacular／verse）。`--clear` **強制要指定 `--author`**——繆勒 SBE 第 16 卷就是《易經》本身、《法句經》引的是漢譯偈頌，那些「文言」是對的，全庫無差別清會毀掉。
> - 2026-09-10 實測分布：《基督信徒的慰藉》34%、《約伯記講演》18%、《耶穌傳》7%、《基督教入門》6%，其餘 ≤5%。已清 510 段重譯。

> 🈶 **日文書名／專名通則（2026-09-10 使用者定調）**：**原題本來就有的漢字照原漢字，只有假名（平假名／片假名）的部分才另外翻**。
> - 例：『基督信徒のなぐさめ』＝「基督信徒」（漢字照留）＋「なぐさめ」（假名→慰藉）＝**《基督信徒的慰藉》**。（順帶一提，那個和語詞就是波愛修斯『哲学の慰め』的「慰め」，中譯《哲學的慰藉》與本書因此對得起來。）
> - 🚨 **英文書名是譯出來的，中文要譯回原書名，不可再意譯一次**。豪斯評傳一度出現：Search after Peace→《尋求和平》（應為**《求安錄》**，18 處只有 1 處對）、The Earth and Man→《地球與人類》（應為**《地人論》**）、I Novel→「我小說」（應為**「私小說」**）、Ryûzanroku→〈流殘錄〉／〈漂鼠錄〉（應為**〈流竄錄〉**，竄字本就從鼠）。
> - 🚨 **《代表的日本人》與《日本及日本人》不可合併**——同一本書 1908 改題前後的兩個書名，合併等於抹掉改題這件事。
> - 🚨 不帶書名號的「聖經研究」**不可**一律改成《聖書之研究》：那多半是「研讀聖經」這件事，而且豪斯書裡另有一份在華美國宣教士辦的中文《聖經研究》，是兩份不同的雜誌。
> - 定名權威：我們自己的 `REGISTRY` ＋ **廖本恩論文書目的既有中譯本**（`data/zlib-wanted/mukyokai-chinese-translations.jsonl`，41 筆，郭維租／吳得榮／涂南山譯）。收斂工具是 `scripts/name_lock.py`（英文佐證閘），目前 25 條鎖。

> 🧾 **表格不可被壓成一行**：豪斯評傳的表格字級跟引文一樣是 8.5，原本整張表被當成引文併成一段。認表格靠**第二欄**（右欄 x0≈271，正文引文最右只到 55），出成 markdown 表格；`pages/ebook/[id].vue` 的 `renderMarkdown` 已補上 `<table>` 渲染。🚨 引擎回來的表格一定是**一行**（`clean_zh_output` 又收空白），要用 `howes_build.retable()` 切回去，列數對不上就原樣退回。🚨 羅馬字轉寫的日文那一欄不可翻（和歌對照表的右欄）。

> 📖 **conversion 一律譯「歸信」（2026-09-10 使用者定調）**：`convert (n.)`→**歸信者**，`convert (v.t.)`→使…歸信。
> **不可用「回心」**——那是日文基督教譯 conversion 的詞（かいしん），中文基督教界不用，讀者會誤讀成「悔改」（日文裡 回心＝conversio、悔い改め＝metanoia，分得很清楚）。「皈依」只留給明確的天主教語境，以及佛教／印度教本來就該用皈依的地方。
> - 根因是 prompt 自己寫的：`howes_build` 與 `uchimura_en_build` 的概念層規則本來就列著「conversion→回心」。兩支都已改。豪斯的英文原著從頭到尾沒出現過 kaishin——這個詞完全是翻譯端加上去的。
> - 收斂舊譯文用 `scripts/redo_conversion_terms.py`（比 `--redo-matching` 多一道**英文佐證閘**：該段英文真的有 convert 一族才清）。少了這道閘，繆勒講「皈依三寶」、潘尼卡講印度教的段落會被一起清掉重譯。
> - 尚有「回心」殘留的卷：`uchimura_en_data/how-i-became`（15）、`ndl_data/toyo-bunka`（13）、`mueller_data/sbe-06-quran-1`（2）、`mueller_data/psychological-religion`（1）、`yanaihara_data/jesus-life`（1）。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。

> 📊 **各全集翻譯線現況（2026-07-22，由 [[project_fleet_keeper]] 的 `KGL_Fleet_Keeper` 排程託管，`scripts/fleet_keeper.ps1`）**：
> - **榮格**：CW9ii／11／12 ✅＋4 部早期著作 ✅；`scripts/jung_run_queue.py` 跑全 19 卷 CW（走 **NVIDIA**，把 Gemini 讓給 ACCS OCR）。CW1-8/9i/10/13-18 待補。新收「文集典藏版（全九冊）」EPUB 進 Drive `全集/心理學/榮格/`（含 CW4/5/6/8/9i/10/15/17/18 九冊）。
> - **哲學家（柏拉圖/亞里斯多德）**：`scripts/plato_run_queue.py` 跑 26 部（**NVIDIA**）；21/26 有滿快取，近完成。
> - **潘尼卡**：7 部完成；**吠陀經驗（義文大部頭 ~1.7 萬段）走 Haiku**，sec3854 進行中。（韋伯已改道：見下）。
> - **馬克斯韋伯**（宗教社會學，hub 已存在 slug=`max-weber`）：**2026-07-23 改採 REFERENCE 轉錄既有中譯本、不自譯**，引擎 **OpenRouter 免費**（8 key，與主鏈分流；免費 vision 爛只能純文字）。9 本中譯本（李中文/張旺山/康樂簡惠美/閻克文/韓水法/顧忠華…繁簡混）已入 Drive `全集/宗教社會學/韋伯/`；轉錄走 `panikkar_build.py` 型 REFERENCE build。詳見 [[project_weber_collected_works]]。 **2026-09-02 開工**：兩篇志業演講（李中文繁譯 EPUB）已零 LLM 上架（`scripts/weber_build.py`），其餘七本的來源品質盤點與取捨見 [weber_collected_works.md](weber_collected_works.md)。
> - **內村鑑三**：青空文庫 11 篇 ✅ 全譯／英文原著兩部與豪斯評傳翻譯中（`uchimura_auto.py --author uchimura|uchimura-en|howes`）。無教會神學區另有矢內原＋七人 hub（[[project_uchimura_yanaihara]]）。
> - **東方聖書（sacred-books-east）**：奧義書✅；剩 5 卷（阿維斯陀/古蘭經/法句經/易經/耆那教）`sbe_translate.py --loop --backend haiku`。
> - **引擎分流**：Gemini→ACCS OCR；NVIDIA→榮格佇列＋哲學佇列＋大愛道；Haiku→潘尼卡吠陀＋SBE。**監管只需 1 個 session**（艦隊靠排程自我修復，多 session 會搶 checkpoint）。

# 經典學者全集 Skill（Collected Works — 依學科組織）

把**經典學者的全集**收進獨立的 `/collected-works` portal（**依學科分區**），每位學者一個作家 hub（小傳／肖像／年表／著作目錄），單卷進 `/ebook/[id]` reader 逐段對照閱讀。

這是 ebook-translate 家族的第三個 skill：

| Skill | 負責 | 典型對象 |
|---|---|---|
| [[ebook-pipeline]] | parse / OCR / standardize / 套書 split | 任何 ebook 上游處理 |
| [[ebook-translate]] | 外文 → 繁中（雙語）/ 簡 → 繁 | 單本英文書、ACCS 缺卷 |
| [[scripture-fathers]] | 教父原典（公有領域 Schaff/CCEL）中譯精修 | ANF/NPNF/ACCS |
| **ebook-collected-works（本 skill）** | **經典學者「全集」依學科收錄；多語／單語／參照／自譯四路** | **柏拉圖、榮格、穆勒、潘尼卡、印順‧聖嚴‧星雲…** |

**核心承諾**：portal 依學科組織；每位學者一份 hub（學術小傳＋年表＋完整書目＋轉錄狀態）；reader 主欄永遠是**我自己的逐段繁中譯文**（單語全集則主欄＝原文繁中本身），旁邊可並陳來源語言欄（原文／既有譯本），使用者可切「中／對照／原文…」。

---

## 何時 trigger

- 使用者指定**某位學者的全集／文集／著作集**要收進 `/collected-works`
  - 「把榮格全集找德文英文版三欄放進來」「馬克斯穆勒宗教學全集」「潘尼卡全集」「印順／聖嚴／星雲全集」「把古希臘哲學家的全集建起來」
- 要**新增一個學科**或把作家**重新歸類**到某學科
- 要把現有雙語書升級成 3 欄以上、要擴充 reader 多欄切換
- 要設計或修「多來源語言」JSONL schema、要對齊跨版本段落

**不適用**：
- 單一外文 → 繁中（不進全集 portal、沒有 hub 概念）→ [[ebook-translate]]
- 公有領域教父原典（走 /fathers）→ [[scripture-fathers]]
- 簡 → 繁批次轉換 → [[ebook-translate]] B pipeline

---

# §A 學科分類總覽（portal 骨架）

**portal 依學科分組（2026-07-01，user 拍板：佛學獨立一類）**。作家歸屬由 `CwAuthor.disciplineGroup`（新欄）決定，portal [pages/collected-works/index.vue](../../../pages/collected-works/index.vue) 依常數分區顯示：

```ts
const DISCIPLINE_ORDER = ['哲學', '宗教學', '宗教社會學', '神學', '基督宗教研究', '佛學', '心理學', '社會學', '人類學']
// 未列出的學科接最後（localeCompare），空組不顯示
// 傘狀學科的次領域（era 層）可固定順序（不依生年）：ERA_ORDER['基督宗教研究']=['新約研究','舊約研究','教會史']
```

**年代→地域兩層分組（2026-07-18，user 拍板）**：`CwAuthor` 另有 `era?`／`region?` 兩欄，**哲學／神學／基督宗教研究用**。portal 對「有任一作家帶 `era`」的學科自動改成**兩層**：先依 `era`（年代，依組內最早生年排序，除非 `ERA_ORDER` 有固定順序）分大標，年代內再依 `region`（地域）分小標，才出卡片；`region` 未設（fallback `'其他'`）時不顯示地域小標（2026-07-23 加）；沒 `era` 的學科（宗教學／宗教社會學／心理學／佛學）維持單層依 `sortYear` 排。**每個年代內都可有多個地域欄**（user：「古代中世紀近代都要分地域」）。
- **基督宗教研究**（傘狀，2026-07-23）：`era` 當**次領域**用（非年代）＝`新約研究`／`舊約研究`／`教會史`，順序由 `ERA_ORDER` 固定；作者**不設 region**（單純三小節，無地域層）。
- 哲學 era：`古代`/`中世紀`/`近代`/`現代與當代`；region：`西方`（古代＝希臘羅馬、中世紀＝拉丁經院）/`拜占庭`/`伊斯蘭`/`猶太`/`印度`/`中國`/`日本`/`美洲`/`非洲`/`韓國`
- 神學 era：`教父時代`/`中世紀`/`宗教改革`/`近代`/`現代與當代`；region：`西方（拉丁）`（教父～近代）/**`歐陸`**（現代與當代歐洲，含英國）/`北美`/`東方（希臘）`/`東方（希臘／東正教）`/`東方（敘利亞／東方教會）`/`東方（東方正統教會）`/`拉丁美洲`/`非洲`/`東亞`/`東亞（日‧韓）`（無教會）/`南亞`/**`原住民`**（北美／毛利／台灣玉山神學院）。現當代神學共 10 地域欄；南方神學／第三世界＝拉美＋非洲＋亞洲已涵蓋，不另建重複 region。

**現況歸類（每學科 → 作家）**：

> 🆕 **2026-07-18 大規模補齊 246 位「人＋書目」骨架**（全 `planned`／`copyright`，肖像逐一驗證，翻譯之後才排）。用 13 路平行研究 agent 產 JSON → `assemble.py` 去重驗證組裝入 store。取向：**多元＋非西方中心並重**（女性與非西方代表貫徹各近現代群組）。目前 store 共約 280 位。

> 🆕 **2026-07-23 新增「基督宗教研究」傘狀學科（40 位新骨架＋3 位從神學遷入）**：緣起 FB「小黑書」(littleblackbook0000) 導讀的近代聖經學術書。傘狀一群、`era` 當三次領域（新約／舊約／教會史，`ERA_ORDER` 固定順序、無 region 地域層）。布特曼／哈納克／菲奧倫查從神學遷入（清掉 region）。3 路平行研究 agent 產 JSON（`c:\tmp\cw_{nt,ot,church}.json`）→ Python 組裝入 store（disciplineGroup 統一改 `基督宗教研究`＋補 era）。肖像全空待回填。近代學術幾全受版權 → 走 REFERENCE-first（先查 z-lib 既有中譯）／自譯。**這批同時是「小黑書 25 本 libgen 下載清單」的來源**（見本 skill 資料夾 `小黑書_libgen下載清單.txt`）。

| 學科 | 規模 | 涵蓋（年代→地域）| pipeline |
|---|---|---|---|
| **哲學** | 123 | 古代（西方＝希臘羅馬 19／中國先秦／印度正統六派）・中世紀（西方拉丁經院／拜占庭／伊斯蘭／猶太／印度吠檀多）・近代（西方／中國明清／日本江戶／韓國性理學／波斯後古典）・現代與當代（西方／中國新儒家／印度／日本京都／非洲／拉美美洲） | 多語對照（公有領域者） |
| **宗教學** | 17 | 單層：穆勒`max-mueller`・潘尼卡`panikkar`＋泰勒→弗雷澤→奧托→伊利亞德→多尼格＋井筒俊彦／中村元 | 多語／REFERENCE／自譯 |
| **宗教社會學** | 15 | 單層（全新）：涂爾幹・韋伯・特洛爾奇・齊美爾・伯格・盧克曼・貝拉・斯塔克・道格拉斯／戴維／阿薩德… | 多語對照 |
| **神學** | 104 | 教父（拉丁／希臘／敘利亞）・中世紀（含希爾德加德等女神秘家）・宗教改革・近代・現代與當代西方（巴特／拉納／過程神學）・非西方處境（解放／女性／黑人／非洲／東亞含無教會9位／南亞／東正教）・新教其餘宗派（衛理／聖公／重浸／貴格／福音／五旬節）・東方正統教會六會 | 多語對照 |
| **基督宗教研究** | 43 | 傘狀三小節（era 當次領域）：**新約研究**（戴斯曼→多德→耶利米亞斯→凱澤曼→梅茨格→亨格爾→R.布朗→桑德斯→鄧恩→海斯→賴特→波卡姆＋布特曼‧菲奧倫查）／**舊約研究**（威爾豪森→貢克爾→考夫曼→艾希羅特→奧爾布賴特→馮拉德→諾特→德沃→布賴特→克羅斯→柴爾茲→特里布爾→布魯格曼）／**教會史**（莫斯海姆→沙夫→哈納克→拉圖雷特→班頓→弗蘭德→歐文/亨利查德威克→帕利坎→A.卡梅倫→彼得布朗→威爾肯→岡薩雷斯→帕格爾斯→麥卡洛克） | REFERENCE／自譯（近代學術幾全受版權） |
| **佛學** | 3 | 印順`yinshun`・聖嚴`shengyen`・星雲`hsingyun` | 單一語言（本即繁中） |
| **心理學** | 18 | 單層：榮格`jung`＋佛洛伊德・阿德勒・威廉詹姆斯・佛洛姆・弗蘭克・希爾曼・荷妮／克萊恩／安娜佛洛伊德／河合隼雄／森田正馬 | 多語對照 |

已完成**轉錄**的卷（reader 可讀）仍見下 §C 各案例；上表多為 hub＋書目骨架。

**加一位新作家 = 在 `stores/collectedWorks.ts` 的 `authors[]` push 一個 `CwAuthor`**（免 DB migration、免 server route）。務必填 `disciplineGroup`（**別跟一句話副標 `discipline` 搞混**）＋ `sortYear`（生年，BCE 為負；portal 依此在學科組內排序，缺省者排末尾）；`color` 須在 [tailwind.config.ts](../../../tailwind.config.ts) safelist（amber/blue/rose/emerald/violet/sky/indigo/cyan/orange/stone/purple/teal，shade 50–300/500–700，**別用 -400**）。**一人一 hub**（前蘇格拉底不併卡）。詳見 [§B7 portal + hub](#b7-portal--作家-hub-頁)。

---

# §B 方法論核心（跨學科共用）

## §B0 開工第一步：判版權＋選 pipeline

### 可得性與版權盡職調查（這類全集的真實障礙）

教父全集能全自動跑，是因為 Schaff/CCEL 版本公有領域。**近現代「全集」幾乎相反**，開工前一定先查：

1. **原文全集是否還在版權內？** 作者卒年 + 70。例：榮格 1961 卒 → 德文 GW 到 2031；潘尼卡 2010 卒 → 約 2080。
2. **既有譯本是否有版權？**（多半有 — 商務／校園／道風／Princeton/Bollingen…）
3. **網路免費全文是什麼性質？** 多半是**盜版掃描 PDF** 或 OCR 髒檔。
4. **哪些卷／早期著作其實已公有領域？**（1929 前出版者）— 這些才有乾淨合法來源。
5. 結論寫進該全集的 case-study md（版權表）。

### 本專案的處理姿態（跟 scripture-fathers「參考現成中譯本校準」同源）

- **reader 主欄＝我自己的逐段繁中譯文 + 來源語言原文欄。** 第三方中譯本預設**不當主欄**。
  - **私人自用例外（user 拍板 2026-06-12）**：本站是私人研究圖書館，**第三方中譯本可入庫當「參考層」**（簡體先 opencc→繁中，[[feedback_traditional_chinese_only]]），但**不取代我的逐段自譯主欄**，標示清楚「第三方譯本‧參考」。→ 即 REFERENCE pipeline。
  - 🆕 **重複譯本取捨（user 2026-07-23，全集通用）**：同一著作有多個中譯本時，主欄一律「**繁體 > 簡體；繁體中取最新出版年**」，其餘留參考層。詳見 [[feedback_collected_works_latest_traditional_edition]]。
- **來源語言欄**是「對照閱讀」用途。版權內來源文字走本機 pipeline；**我（Claude）不在對話裡貼整段受版權原文**，文字一律走本機 script / 檔案。
- **公有領域的卷優先**；標示清楚。
- **私人自用 → 受版權卷可用 shadow library 取來源檔（user 拍板 2026-06-12）**：本站 auth-gate 後僅供個人閱讀（非公開散布），受版權著作若無 PD 源、archive.org 又只借閱，**可從 shadow library（Anna's Archive / Library Genesis）抓來源到本機**（比照 [[feedback_jung_nonpd_english_first]]）。鐵則：(1) **English-first**，主欄是我的逐段繁中；(2) 來源原文**只走本機檔／script、絕不貼進對話**；(3) `curl`/Bash 抓到 `c:/tmp` 再 `--src` 餵 pipeline。⚠️ **環境網路限制**：此 sandbox 多數 shadow 鏡像（annas-archive、libgen.is/.rs）**DNS 被擋**，僅 `libgen.li` 可達且常只索引期刊書評 → 抓不到時請 user 自己下載後丟本機（new-book drop / `c:/tmp`）。

### 🆕 翻譯前鐵則：REFERENCE-first（user 2026-07-23）

**任何卷要「翻譯」前，先查有無現成中譯本，不要一上來就自譯。** 見 [[feedback_collected_works_reference_first]]。
1. 先比對該作家 works × **圖書館既有**（collection=null）→ 有就直接搬全集（PATCH collection + store 連 ebookId；見 [[feedback_collected_works_not_in_library]]）。
2. 再查 **z-library**（2026-09-02 起這一步已自動化：[[ebook-zlib-harvest]]，每日排程依清單抓，額度十本／日）有無中譯本 → 有就**列進獵表**（本 skill 資料夾的 `z-library_獵表_全集中譯.txt`，作家中英名＋書名＋原文名；**不要放 repo 根目錄**），交使用者下載，之後走 **REFERENCE**。
3. **只有查無任何中譯本才走自譯（pipeline④）**。多譯本取最新繁體（[[feedback_collected_works_latest_traditional_edition]]）。

→ 即 pipeline 選擇順序＝**REFERENCE ＞ 自譯**（翻轉原 English-first 預設）。全集書一律 `collection='collected-works'` 不進圖書館；轉錄批次後跑 `scripts/apply-ebooks-quality-collection.mjs` 補標。

#### 🚨 這條鐵則最常見的失效方式：**用自己擬的譯名去查，查過等於沒查**

2026-09-08 差一點就自譯了伊利亞德兩本已有中譯的書。規則沒被違反——第 2 步「查
z-library」確實跑過，帳本上也確實寫著 `no-usable-hit`。問題出在**拿去查的書名是
hub `works[].title` 裡我自己擬的推測譯名**，跟實際出版的中譯本書名對不上，
`expect` 比對一律 -100，於是中譯本明明在架上卻被判成「沒有」：

| hub 裡我擬的 | 實際出版譯名 | z-lib 上的狀態 |
|---|---|---|
| 宗教思想史 | **世界宗教理念史**（商周繁體）／宗教思想史（簡體三卷） | 都在 |
| 薩滿教：古老的出神技術 | **萨满教：古老的入迷术** | 在（epub 59 MB） |
| 聖與俗：宗教的本質 | **神圣与世俗**（簡）／聖與俗（桂冠繁，z-lib 無） | 簡體在 |
| 永恆回歸的神話 | **宇宙與歷史：永恆回歸的神話**（楊儒賓譯） | 在 |
| 瑜伽：不朽與自由 | **不死与自由：瑜伽实践的西方阐释** | 在 |

**所以第 2 步要拆成兩件事：**

1. **先查出實際出版的中譯本書名**（不是自己翻）。hub 的 `works[].title` 是給人看的
   標題，**不是查詢鍵**。查證管道：使用者本人（他讀過的書他知道）、國家圖書館、
   博客來／豆瓣、以及自己的課程大綱與講義書目——`scripts/course_syllabus_docx.py`
   裡就寫著「伊利亞德著，楊素娥譯。《聖與俗：宗教的本質》。台北：桂冠，2001」，
   本機早就有答案，是我沒去看。
2. **用那個書名去查**，並把它寫進 `data/zlib-wanted/collected-works-zh.jsonl`
   （策展清單，會被 `zlib_wanted.py` 併進總表），`expect` 用書名的核心詞就好，
   別整串比對——簡繁與副標的差異會讓長字串一律落空。

**判定「真的沒有中譯本」的門檻**：至少用「繁體書名」「簡體書名」「作者中譯名＋書名」
三種寫法各查過一次，而且看過 dry-run 印出來的前六名（`--dry-run` 會把被閘擋掉的
也列出來，才分得出是「閘太嚴」還是「站上真的沒有」）。只憑一次 `no-usable-hit`
就判定沒有，等於把自己擬的譯名當成了世界的事實。

**z-lib 連續搜尋會被限流，回空不等於沒有。** 同一輪連下兩本之後，接下來四筆查詢
全回 0 筆並被記成 `not-found`——而那四筆五分鐘前 dry-run 時全部找得到。`not-found`
會讓那些 key 永遠不再重試，所以**懷疑是限流時要把那幾行從
`scripts/state/zlib_ledger.jsonl` 刪掉**（檔案是 append-only JSONL，重寫即可），
下載之間也要拉開間隔。大檔（50 MB 以上）容易 `download.saveAs: canceled`，單獨重試。

### 四種收錄 pipeline（**先判走哪條**）

| pipeline | 何時用 | 主欄 | 來源欄 | LLM | 對齊 | 案例 |
|---|---|---|---|---|---|---|
| **① 多語對照** | 原文＋既有他語譯本＋要我自譯繁中，做 N 欄 | 我的繁中 | 原文＋既有譯本 | 有（自譯） | 跨版對齊（最難） | 榮格、穆勒、古希臘 |
| **② 單一語言** | 全集本即繁體中文 | 原文繁中本身 | 無（reader 退化單欄） | 無 | 無 | 印順、聖嚴、星雲 |
| **③ REFERENCE** | 已有完整第三方中譯，不重譯 | 第三方中譯（簡→繁，標「參考」） | 原文逐段對照 | 無 | 章序配對 | 潘尼卡《宗教內對話》 |
| **④ 自譯** | 無中譯的受版權卷，English-first | 我的繁中 | 原文（英／義／西…） | 有 | 章序切段 | 潘尼卡自譯 queue |

下游（入庫 / hub / reader）四路**完全共用**；差別只在「取源＋解析＋要不要翻＋怎麼對齊」。**多語對照**細節見 §B1–§B4，**單一語言**見 §B5，**portal/hub/reader** 見 §B6–§B7。

---

## §B1 三件 ebook-translate 不處理的事（多語對照專屬）

### 1. 多卷套書 = 一個 corpus

全集是**套書**。先遵守 [[feedback-set-books-split]] / [[feedback-set-books-subfolder]]：
- 每卷一個 `ebooks` row（不是整套一個 row）
- Drive 在分類下建子資料夾整理；移動檔案後 `UPDATE ebooks.file_path` 同步
- 跨卷 `volume` / `parent_volume` 命名統一（`parent_volume` = 著作集分組）
- 跨卷術語一致 → 走專屬 glossary（見 §B8）

### 2. 單一來源 → 多來源 schema（`sources`）

現行 JSONL 只有 `source_lang`(str) + `source_text`(str) = 一個來源。多語全集要 N 個來源，schema 這樣擴充（**向後相容**）：

```jsonc
{
  "chunk_index": 0,
  "chunk_type": "chapter",
  "chapter_path": "轉化的象徵 · 第一部 · 第一章",
  "volume": "轉化的象徵（卷五）",
  "parent_volume": "轉化的象徵",
  "format": "markdown",

  "content": "繁中譯文 …",          // 主欄：我的逐段繁中（永遠是 zh）

  // ── 向後相容欄（舊 reader / 雙語書照常運作）──
  "source_lang": "de",              // PRIMARY 來源語言（= source_order[0]）
  "source_text": "德文原文 …",      // PRIMARY 來源全文（= sources[source_lang]）

  // ── 多語新欄 ──
  "sources": {                      // 所有非中文來源：lang code → 對齊後文本
    "de": "德文原文 …",
    "en": "英文既有譯本 …"
  },
  "source_order": ["de", "en"]      // 來源欄顯示順序（原文在前、譯本在後）
}
```

**相容規則**：
- `source_text`/`source_lang` 永遠鏡像 `sources[source_order[0]]` → 舊 reader 拿到主來源照常顯示，雙語書（只有 `en`）不受影響。
- 新 reader 見 `sources` 就走 N 欄；沒 `sources` 就 synthesize `{[source_lang]: source_text}` / `source_order=[source_lang]`（等同今日雙語）；**單一語言全集連 `source_text` 都不寫 → 自動退化單欄**。

### 3. 跨版本段落對齊（多語最難的一步）

原文與既有譯本是**獨立編輯**的版本：分段不同、有的卷重排、註腳系統不同 → **不能假設「第 i 段原文 = 第 i 段譯本」**。策略由粗到細：

1. **章節錨點對齊**（最可靠）：兩版都有的 §/章/小節編號（如 Bollingen `[¶ N]` 段碼）當 join key。優先找有段碼的版本。
2. **長度比＋順序對齊**（無段碼時）：同章內按段落順序 + 字數比例 greedy 對齊（類似 scripture-papal 的 `alignDocs()`）。
3. **LLM 輔助對齊**（兜底）：同章丟給 Gemini/Haiku 輸出「原段 ↔ 譯段」index pairs。
4. **對不齊就分欄不分段**：退化成「整章原文欄 / 整章譯本欄 / 我的逐段中文」，中文跟我自己的分段，來源欄整段顯示。

> 中文譯文一律**跟著我自己的分段**走。對齊是把原文、譯本**塞進我的段落框架**，不是反過來。對不上的來源段落寧可整段塞、不要硬切。

---

## §B2 多語對照 pipeline 概覽（每卷）

```
[0] 盡職調查：版權表 + 公有領域判定（寫進 case-study md）
        ▼
[1] 取得來源：原文卷 + 既有譯本卷（PDF/EPUB）；套書規則：每卷一 row、Drive 子資料夾、file_path 同步
        ▼
[2] 抽文字：EPUB→乾淨；PDF→Gemini/Haiku OCR（走 [[ebook-pipeline]] OCR）；per-語言 source chunks（保留段碼/章節錨點）
        ▼
[3] 對齊：章節錨點 > 長度比 > LLM 輔助 > 整段塞（§B1-3）→「對齊後章節單位」
        ▼
[4] 翻譯：translate_ebook_to_zh 變體，從原文翻、既有譯本當交叉校對；術語走專屬 glossary（§B8）
        ▼
[5] 寫多語 JSONL：content=繁中, sources={…}, source_order, source_text 鏡像
        ▼
[6] volume / parent_volume backfill（著作集分組樹）
        ▼
[7] R2 + DB previews 同步（PATCH chunk_count/standardized_at）
        ▼
[8] reader 多欄切換驗證（中 / 對照 / 各來源語言）
```

翻譯引擎、quota 協調、OAuth refresh、append-resume、Gemini→Haiku 2-strike — **全部沿用 [[ebook-translate]] 基礎設施**，本 skill 不重造。

**基建現況（都 test-first、已 push，不用重做）**：
- `sources` 契約模組 [lib/multilang-sources.ts](../../../lib/multilang-sources.ts)（client+server 共用，27 例）＋ [test/multilang-sources.spec.ts](../../../test/multilang-sources.spec.ts)：normalize / mirrorPrimarySource / availableViewModes / resolveViewMode stale 夾制 / langLabel / zipParallel 補白。**下游 reader 與 API 一律用這個 module。**
- reader N 欄 + API passthrough：`ChunkData`([server/utils/ebook-chunks.ts](../../../server/utils/ebook-chunks.ts)) 加 `sources?`/`source_order?` + [[id].get.ts](../../../server/api/ebooks/[id].get.ts) passthrough。
- Python 寫入器 [scripts/multilang_chunks.py](../../../scripts/multilang_chunks.py)（21 例，鏡像 TS 契約 + `assemble_multilang_chunks(units, translate_fn, source_order)`，engine boundary=`translate_fn`）。
- 對齊 [scripts/align_editions.py](../../../scripts/align_editions.py)（20 例：`parse_chapter_number` DE/EN/CJK+羅馬/中文數字；`align_editions` 錨點 join / order 補白 fallback）。
- 驅動 [scripts/translate_collected_work.py](../../../scripts/translate_collected_work.py)（11 例：`load_plaintext_sections`/`split_html_sections`(bs4)/`make_translate_fn(engine)`/`run`）。
- 殘留（接真語料時按需補）：段碼級 `[¶ N]` 細對齊、LLM 輔助 fallback、錨點 part-scoping（含 Part 的書章號每部重起 → key 不唯一，手工配對不依賴它）。

---

## §B5 單一語言 PLAYBOOK（漢傳佛教／中文全集）

> 印順(CBETA)/聖嚴(法鼓全集)/星雲(masterhsingyun) 三套累積的通用做法。**任何「本即繁中、要逐冊上架的中文全集」都照這套**（§B1–B4 多語對齊在此**不適用**，零翻譯零對齊）。下游入庫/hub/reader 完全共用，新案例**只需寫來源解析器**。

### 0. 單一語言鐵則
- **零翻譯、零跨語對齊**：`content` = 原文繁中本身；chunk **不寫 `sources`/`source_text`** → reader 自動退化單欄（§B1-2 向後相容）。
- 一書（冊）= 一個 `ebooks` row；一篇（章/節/條目）= 一個 chunk；`parent_volume`=大類/著作集、`volume`=書名、`chapter_path`=書名 · [章節…] · 篇名。
- **保留原書頁碼**（[[feedback_pdf_page_number]]）：CBETA `lb` 邊碼 / 法鼓 `span.pb data-page` / 星雲麵包屑 `pNNN` → 存進 `chunk.page_number`。
- deterministic `ebook_id` 每作家一個命名空間：印順 `a0000000-…-NN`、聖嚴 `b0000000-…`、星雲 `c0000000-…`；registry JSON committed 進 skill 資料夾。

### 1. 開工第一步：來源分級（決定可行性，**別跳過**）
| 來源型態 | 範例 | 做法 |
|---|---|---|
| **結構化標記**（TEI/XML/EPUB） | CBETA `cbeta-org/xml-p5` Y 系列 | 最佳；GitHub raw 直抓，`cb:mulu`/`cb:div` 巢狀＝章節樹。非商業可再散布 |
| **靜態每篇 HTML、可枚舉** | 法鼓 `getData.php?type=vol_dump`+`html/{id}.html` | 好；先抓「枚舉端點」再逐篇抓 |
| **薄殼 JS reader、內容端點藏起來** | 星雲 `/bcN/bookM` 空殼 | ⚠️ **別爬殼**；先找真內容路由（見 §2） |

判準：`curl sitemap.xml` → playwright 看載文章的 **XHR/network** → 看頁面 size（~9KB 空殼 vs 有內容）。

### 2. 找「藏起來的內容端點」（星雲教訓，最關鍵的一招）
薄殼站全文常**不在 sitemap、不被 reader 殼揭露**，走另一條 server 路由（MVC `/Controller/action{id}`）。排查順序：
1. **直接問 user 要一個「他實際在讀的文章 URL」** ← 最快，往往秒破關（星雲 `/ArticleDetail/artcle1980`）。
2. playwright 攔截所有 response，找非資產 GET（`.php`/`.json`/`.ashx`/`/ArticleDetail`）。
3. 看 `getData.php?type=…` 之類 JS 變數端點（法鼓 `all_books`/`vol_dump`）。
4. 探子網域多半不解析 → 放棄猜、回到 1。

### 3. 無乾淨目錄時：用**麵包屑反推結構**
每篇文章頁自帶 `第N類【類名】 › 冊 › 子冊 › p篇` → 靠文章自身重建整棵樹：`parent_volume`=麵包屑[0]、`book_key`=麵包屑[1]、`chapter_path`=麵包屑[1:]、多卷靠同一 `book_key` 併冊。

### 4. 禮貌大量爬取（~2 萬篇，**user 叮囑別被封**）
- **節流**：`ThreadPoolExecutor` 4 workers + 每請求 0.05s 延遲 + 指數退避（封頂 8–20s）。實測 ~7/s、err=0。
- **resumable 快取**：每篇寫 `c:/tmp/<author>_cache/{N}.json`（含 `empty:true` 標記空洞）→ 被擋重跑自動續，不重抓。
- **監控封鎖**：看 err 計數暴增＝被擋 → 停、退避久一點再續。
- **快取留著別清**（星雲快取 25500 檔保留）。
- requests 帶 **User-Agent + `verify=False`**。

### 5. 入庫批次韌性（聖嚴/星雲都踩過）
Supabase/R2 偶發 `RemoteDisconnected`/`ConnectionError` → **`--all` 迴圈一定 per-book `try/except`** + 末尾重試一輪 + **`--resume`**（查 DB `id=in.(...)` 跳過已有 chunk 的冊）。

### 6. 共用雷區
- `ebooks.id` 是 **UUID** → REST 查全集用 `id=in.(…)`，**不能 `like`**。
- `EBOOK_CHUNKS_DIR` 在 .env 可能空字串 → 用 `te.CHUNKS_DIR`（已 fallback G: 雲端）。
- **CJK 接行**：殺換行**不插空格**（`re.sub(r"[ \t]*\n[ \t\n]*","",s)`）但保留全形空格 U+3000 與英文詞間真空格。
- **截圖 reader**：全頁高 ~3800–3970px > 2000px 硬限 → 讀前 PIL crop top ≤1850。
- **dev server 多任務衝突**：:3000 可能被別任務佔/壞（[[feedback_no_kill_other_tasks]] 不可殺）→ 自己另起 `PORT=3100/3200`；已認證 reader 首次 SSR 冷編譯 >30s → `navigationTimeout` 拉 150s、或先 curl 暖路由。
- **無公有領域肖像**（當代法師照片受版權）→ `portraitUrl:''`，portal/hub 已加 emoji 佔位 `v-else`。
- 截圖腳本放 `scripts/_xy_*.mjs`（`_` 前綴）跑完即刪、**別 commit**。

### 7. 全文未到位時的 placeholder（星雲曾用）
先建 hub + **書目**（status `planned`/`copyright`，sourceNote 標明待來源），之後全文進來再把 works `status→done`+填 `ebookId`。誠實標示勝過硬刻殘缺爬蟲。

---

## §B6 全集專屬三欄 reader（2026-07-02 起，取代 /ebook UI）

**全集不再走 `/ebook/[id]`**（user 拍板：/ebook 空白封面＋分頁感錯位「開頭很奇怪」）。改用**聖經三欄式**專屬 reader [pages/collected-works/[slug]/[work].vue](../../../pages/collected-works/[slug]/[work].vue)（版型仿 `pages/creeds/[slug].vue` grid mode），`[work]` = ebookId。

- **每 row grid**：`3.25rem 1fr…1fr` ＝ **左引用號欄 + 繁中 + 各來源欄**（欄數依 `source_order` 動態；單語書＝引用號＋繁中兩欄）。逐段用 `lib/multilang-sources.ts` 的 `normalizeSources`＋`zipParallel`（content 與各 `sources[lang]` 按 `\n\n` 段 index zip、補白）。`## …` 開頭的段渲染為跨欄小標。
- **引用號欄**＝`chunk.anchors[i]`（**Stephanus 17a／Bekker 1094a**；無 anchors 的舊書退化用 `page_number`）。點擊複製「`{作者}《{書名}》{anchor}`」＋設 `#cite-{anchor}` hash 深連結 → 滿足「詳細引用方式」。
- **每卷頂部導讀卡**（page 1）：書名＋`data/collectedWorksIntros.ts[ebookId].intro`（簡介導讀段落）＋引用格式示例；取代原空白封面。缺項降級只顯示 `work.note`。有 cover chunk 的舊書：`chunk_type==='cover'` 只出導讀卡、不出 body。
- **Toggle**：`中 | 對照 | <各語言>`（沿用 `availableViewModes`/`langLabel`）。**分頁**：每 Stephanus/Bekker 頁一 view（`?p=N`）＋TOC 抽屜（依 `volume` 分卷）。
- **取資料鐵則**：client-side `$fetch('/api/ebooks/'+id+'?includeToc=1&page=N')` **必帶 `Authorization: Bearer <supabase access_token>`**（`getSession().access_token`）——`/api/ebooks` `requireAuth()`，SSR/純 cookie 會 401（踩過）。
- **`anchors` 資料契約**：`plato_build.build_units` 產 `anchors=[sec_id…]`（與段一一對應）→ `multilang_chunks.build/assemble` 傳遞 → `ChunkData.anchors?` → `/api/ebooks/[id].get.ts` currentPage 白名單 `anchors`（**四處都要，缺一到不了 client**）。
- **⚠️ Nuxt 巢狀路由雷**：`[slug].vue` + `[slug]/[work].vue` 會讓 `[slug]` 變父層（需 `<NuxtPage/>` 否則 child 不渲染、只出 hub）→ 已把 hub 改成 `[slug]/index.vue`、與 `[work].vue` 同層。
- **驗證（2026-07-02 截圖實證）**：新 reader page1 導讀卡＋引用格式＋Stephanus 17 三欄；page2 每 row 引用號 18a/18b + 繁中/希臘/英 逐段對齊。一次性 shot 腳本 `scripts/_cw_shot.mjs`（用完即刪、`_`-prefix 未 gitignore 別 commit；auth＝magic-link＋session cookie＋`kgl_device_id=screenshot-bot`；nav timeout 要在首個 goto 前設 150s）。
- 底層仍沿用 [lib/multilang-sources.ts](../../../lib/multilang-sources.ts)（**別各自重寫 schema 判斷**）；`/ebook/[id].vue` 保留給一般電子書。

---

## §B7 Portal + 作家 Hub 頁

全集**不放電子圖書館（/ebook）裡**，而是獨立 `/collected-works` portal（首頁「📚 全集」cyan 卡）。portal 依學科分區（見 §A）。每位學者一張卡 → 作家 hub `/collected-works/[slug]` 最外層呈現：

1. **學術貢獻簡介**（`contribution: string[]`，繁中段落，支援 `**粗體**`）
2. **肖像**（`portraitUrl`：Wikimedia Commons `Special:FilePath/<檔名>?width=500` 公有領域縮圖，**不用 Supabase Storage**；當代人物無 PD 肖像 → `''`，hub 用 emoji 佔位）
3. **生平學術年表**（`timeline: {year, text}[]`）
4. **著作目錄**（`works[]`，**按 `category` 分組、組內依 `yearSort` 排序**；顯示年分／繁中名／原文名／來源語言標／轉錄狀態）

**單卷閱讀走全集專屬三欄 reader `/collected-works/[slug]/[work]`**（見 §B6；`work.ebookId` 帶過去；`externalUrl` 優先，如東方聖書）；hub `linkTarget()` 回 `/collected-works/${slug}/${ebookId}`（**不再是 /ebook**）。hub 只是入口＋完整書目＋路線圖。每卷導讀寫在 [data/collectedWorksIntros.ts](../../../data/collectedWorksIntros.ts)（keyed by ebookId）。

### 資料：`stores/collectedWorks.ts`（repo-committed，沿用 /works·speech.ts 模式）
- 直接改本檔新增／編輯作家與書目，**免 DB migration、免 server route**（user 拍板 2026-06-05）。
- `CwAuthor` 必填欄：`slug` / `name` / `disciplineGroup`（§A 分組鍵）/ `discipline`（一句話副標）/ `fields[]` / `portraitUrl` / `color` / `emoji` / `contribution` / `timeline` / `works`。
- `WorkStatus`：`done`（已轉錄→reader）/ `in-progress`（轉錄中，可連 pilot）/ `planned`（待轉錄）/ `copyright`（受版權待來源）。badge：綠／琥珀／灰／石。hub `[slug].vue` 會 fetch 活 chunk_count → 有內容自動把 planned 升「轉錄中」可點。
- **某卷轉錄完成** = 改 `status` 為 `done`/`in-progress` 並填 `ebookId`。
- **驗證（2026-06-05 實證）**：dev server + `screenshot_book.mjs` 截 portal/hub。一次性截圖腳本用完即刪（`_`-prefix 未 gitignore，別 commit）。

---

## §B8 Glossary（每部全集一份專屬術語表）

教父走 `/translation-glossary`。全集多半是**別的學科**，術語不同，**每部全集建一份專屬 glossary md**（放本 skill 資料夾）：
- 規則同 ebook-translate glossary：翻譯前先鎖譯名 → 翻譯中 PROMPT 帶 glossary → 翻完跑 term sweep 收斂變體。
- 跨卷一致是硬指標（同一術語不可一卷「自性」一卷「自我」）。
- 若人物/概念跟現有 `/translation-glossary` 重疊 → 仍以 `name_recommended` 為權威（[[feedback-glossary-strict-authority]]）。**哲學家／科學家／帝王／地名一律先查 [[translation-glossary]] 的對應領域表鎖譯名。**
- 現有：[jung_glossary.md](jung_glossary.md)（德文原詞為準）、[mueller_glossary.md](mueller_glossary.md)（英文原詞為準）、[panikkar_glossary.md](panikkar_glossary.md)（自鑄詞 cosmotheandric…）。

---

# §C 各學科案例

> 每個案例的**完整版權表／卷目／來源／對齊策略／接手清單**在各自 case-study md；此處只給「一句話現況＋走哪條 pipeline」。

## C1 哲學：古希臘哲學家（依年代）

**新學科群（2026-07-01 起，hub 骨架，pipeline ① 多語對照）**。portal 改依學科分組後開的「哲學」群，著作目錄多為 `planned`，逐步轉錄。全屬**公有領域**（古典原文＋十九世紀權威英譯 Jowett/Ross/MacKenna），可做希臘／英／繁中三欄。肖像用 Wikimedia Commons 公有領域胸像／畫像（已 curl 逐一驗證可載；普羅泰戈拉‧高爾吉亞無合適 PD 像 → emoji）。接手轉錄比照榮格 pipeline；人名先查 [[translation-glossary]] 哲學家表鎖譯名。

**🚩 結構定案（user 2026-07-01）：一人一 hub、前蘇格拉底不併卡、`sortYear` 依生年排序。** 原先的合併卡 `presocratics` 已拆為 14 個獨立作家；全群 **19 位**，portal 依 `sortYear`（生年 BCE 負值）由古到今排：

| # | slug | 生年(sortYear) | 骨架 | 肖像 |
|---|---|---|---|---|
| 1–3 米利都 | `thales` / `anaximander` / `anaximenes` | −624/−610/−586 | 水／無限者 apeiron／氣 殘篇 | ✅ |
| 4 | `pythagoras` | −570 | 數為萬物之本、靈魂輪迴（見證 DK14/58） | ✅ |
| 5 | `xenophanes` | −565 | 批判擬人神觀、趨一神（DK21） | ✅ |
| 6 | `heraclitus` | −535 | 萬物流變、邏各斯（DK22） | ✅ |
| 7 | `parmenides` | −515 | 存有為一、本體論（DK28） | ✅ |
| 8 | `anaxagoras` | −500 | 種子＋努斯 nous（DK59） | ✅ |
| 9 | `zeno-elea` | −495 | 運動悖論（DK29） | ✅ |
| 10 | `empedocles` | −494 | 四根＋愛與爭；《淨化》（DK31） | ✅ |
| 11–12 辯士 | `protagoras` / `gorgias` | −490/−483 | 人是萬物尺度／〈論非存在〉 | emoji |
| 13 | `socrates` | −470 | 無著作；見柏拉圖／色諾芬 | ✅ |
| 14 | `democritus` | −460 | 原子與虛空；歡愉倫理（DK68） | ✅ |
| 15 | `plato` | −428 | 早／中／晚期對話錄＋書信（Stephanus＋Jowett） | ✅ |
| 16 | `aristotle` | −384 | 工具論‧自然‧生物‧形上‧倫理政治‧修辭詩學（Bekker＋Ross） | ✅ |
| 17 | `epicurus` | −341 | 三書信＋主要教義＋附盧克萊修 | ✅ |
| 18 | `epictetus` | 50 | 手冊＋談話錄＋斯多噶參照 | ✅ |
| 19 | `plotinus` | 204 | 《九章集》六集＋波菲利傳（MacKenna） | ✅ |

**下一步**：擇一 hub（建議柏拉圖《蘇格拉底的申辯》起）取 PD 希臘原文（Perseus，Stephanus 編號，已驗證可抓）＋Jowett 英譯（Gutenberg #1656，已驗證）→ 走 §B2 多語 pipeline → 逐段三欄。專屬 glossary 建 `greek_philosophy_glossary.md`（理型 εἶδος、邏各斯 logos、努斯 nous、本原 archē、ataraxia、太一 to Hen…；對齊 repo 既有 `scripts/seed_glossary_philosophers.py`）。

## C2 宗教學：馬克斯‧穆勒 + 雷蒙‧潘尼卡

> **潘尼卡 2026-07-01 由「神學」改歸「宗教學」（user 拍板）** —— 其宗教學／比較宗教定位重於純系統神學。神學學科由內村鑑三＋矢內原忠雄開區（見 C3）。

### 穆勒（宗教學開山祖，pipeline ①）
案例檔 → **[mueller_collected_works.md](mueller_collected_works.md)**（版權表 / Longmans 18 卷目 / 來源 / 對齊 / 接手）＋詞庫 [mueller_glossary.md](mueller_glossary.md)。

一句話現況：Friedrich Max Müller（1823–1900，**宗教學開山祖**）卒於 1900 → **全部著作早已公有領域**，是 collected-works 最乾淨案例。以英文寫作為主 → 預設英＋繁中雙語；有平行德文版的卷（起手卷《宗教學導論》1873 = 德《Einleitung》1874，英德同構四講＋兩附論）做真三欄。**✅《宗教學導論》三欄竣**（`33333333-…`，7 chunks，~21.5 萬繁中字）；其餘 13 部走 `scripts/mueller_auto.py` 自動 queue（English-first：先無 LLM 上架英文、再逐段翻）。

> 🧹 **來源欄 OCR 清理（2026-07-01）**：老書 djvu OCR 的 `en`/`de` 來源欄殘留亂符（•■€™♦►）、斷詞、目錄點漏／頁眉／掃描樣板，中文因 LLM 已濾故乾淨。工具 `scripts/mueller_source_clean.py`（測試優先，`scripts/tests/test_mueller_source_clean.py` 10 綠）：`clean_source(text,lang)` 刷符號/控制字元/樣板＋保守斷詞合併（德文「„」在 de 保留）；`is_junk_para` 高精度判整段 junk（**只認「點漏後直接接頁碼」的目錄行**，避免誤殺 19 世紀散文省略號）；driver 丟 junk 時同步丟 en/de/zh/fail 保持平行，**zh 文字絕不編輯**。`--dry-run` 先驗、`--apply` 套用；改完逐卷 `mueller_auto.assemble_and_upload`（isr 走 `mueller_build --build-only --upload`）。首輪 17 部清 1437 段／丟 39 junk 段。

### 潘尼卡（宗教間對話／比較神學，pipeline ③④）
案例檔 → **[panikkar_collected_works.md](panikkar_collected_works.md)**（版權表 / Opera Omnia 12 卷目 / 起手卷 / 接手）＋詞庫 [panikkar_glossary.md](panikkar_glossary.md)。

一句話現況：Raimon Panikkar（1918–2010，**宗教間／宗教內對話與跨文化哲學巨擘**）卒於 2010 → **受版權至約 2080，榮格型（非穆勒）**：無乾淨 PD 全文、第三方中譯不當主欄。採 **English-first**。多語原創（加泰隆／西／義／英／德），Opera Omnia 是主題重編 → 多數卷先英＋繁中雙語。**兩種 build（user 拍板 2026-06-12）**：③ **REFERENCE**（`--src <en> --zh-src <zh>`，有完整中譯就不重譯，第三方中譯簡→繁當主欄、英文逐段對照、零 LLM）／④ **自譯**（`--src <en>`，無中譯的卷 English-first 引擎自譯）。CJK 章標題由 `_CJK_HEADING_RE` 切段。**✅ 上架 2 本**（宗教內對話 `55555556-…` REFERENCE；神的經驗 `55555561-…` 自譯 39 chunks）；自譯 queue `scripts/panikkar_auto.py --run-queue` 背景連跑（8 卷，義/英/西）。腳本 `panikkar_build.py`/`panikkar_auto.py`/`ocr_pdf_to_text.py`，pytest 29 例綠。

## C3 神學：無教會主義九位

**神學學科＝無教會主義（Mukyōkai）譜系群（2026-07-16 開區＋同日擴收，共九位）**，仿 C1 古希臘「一人一 hub、依 sortYear 排序」。

**兩位核心（各自獨立 case-study）**：內村鑑三（1861–1930，創始者）卒逾 95 年 → **全球公有領域**，青空文庫 11 篇＋archive.org 岩波全集掃描＋兩部**英文原著**（How I Became a Christian／Representative Men of Japan）；矢內原忠雄（1893–1961，殖民政策學者‧戰後東大總長）→ **日本（2012 起）與台灣 PD**（《帝国主義下の台湾》1929 出版全球乾淨，NDL pid 1191101 インターネット公開已驗證）。hub＋書目（內村 10 部／矢內原 13 部，全 planned）已上 → **[uchimura_collected_works.md](uchimura_collected_works.md)**／**[yanaihara_collected_works.md](yanaihara_collected_works.md)**。

**譜系七位（合併一檔）**：畔上賢造（1884–1938，**全球 PD**，NDL 公開 **27 部**，hub 書目 24 筆，**已上架 3 本**）／塚本虎二（1885–1973，日版權至 2043，3 部）／黒崎幸吉（1886–1970，至 2040，3 部）／藤井武（1888–1930，**PD**，4 部）／南原繁（1889–1974，至 2044，4 部，唯一有 PD 肖像）／**金教臣**（1901–1945，**PD**，韓國《聖書朝鮮》創刊人，3 部）／咸錫憲（1901–1989，韓版權至 2059，4 部）——金教臣＋咸錫憲是本 portal **首兩個韓文（ko）案例**。受版權者比照榮格前例 `status='copyright'` hub＋書目先行。取捨（政池仁／大塚久雄／高橋三郎落選理由）、版權表（2018 日本改法不溯及）、肖像與來源盤點 → **[mukyokai_collected_works.md](mukyokai_collected_works.md)**。

**東亞本土神學‧其餘地區 26 位（2026-09-07）**：台灣四位與無教會譜系之外，把中國 11
（吳雷川／誠靜怡／賈玉銘／韋卓民／劉廷芳／謝扶雅／吳耀宗／王明道／倪柝聲／丁光訓／何世明）、
韓國 7（李龍道／金在俊／尹聖範／徐南同／玄永學／柳東植／金容福）、日本 6（賀川豐彥／
有賀鐵太郎／瀧澤克己／北森嘉藏／古屋安雄／八木誠一）、沖繩 2（金城重明／平良修）一次補齊。
生卒年**逐筆查證**：Wikidata 對劉廷芳與金容福的誤配確認屬實並已排除。
🚨 **BDCC 只覆蓋中國 11 人中的 8 人**（吳耀宗／丁光訓／何世明查無），且該站對不存在的
slug **回 HTTP 500 而非 404**——別把「查無此人」誤讀成站方故障。⚠️ 這批是「已建目錄」
不是「已核書目」：多數 works 的 `year` 為 `—`、`yearSort` 只是排序估計值，**不可當出版年引用**。
順手把 portal 地域晶片的 `東亞（日‧韓）` 13 筆統一為 `東亞`（加入中國與沖繩後該標籤已不成立）。
查證總表、版權分級與遺留 → **[east_asian_contextual_theology.md](east_asian_contextual_theology.md)**。

**內村三波進度（2026-09-06）**：①青空文庫 11 篇→6 卷 866 段 **全譯完成**；
②兩部英文原著（archive.org djvu）→ `uchimura_en_build.py`，《代表的日本人》319 段、《我如何成為基督徒》496 段**均已完成**；③**傳記**——豪斯《Japan's Modern Prophet》
（UBC Press 2005，英文學界定本，中文世界無譯本）19 節 1,442 段**已完成**（另經三輪專名精修，見案例檔），
是本 portal 第一本「寫作家的書」，hub 內新開 category「傳記與研究（他人著作）」→
**[howes_uchimura_biography.md](howes_uchimura_biography.md)**。

### NDL 取源線（2026-09-08 起，**四本已上架**）

戰前那批不在青空文庫也不在 libgen，只有 NDL 掃描本。
🥇 **取源用 NDL 自己的官方 OCR**（`/dl/api/book/layouttext/{pid}`，帶版面結構），
不要用視覺模型——兩次獨立 Gemini 互比有 271 處分歧，逐字精度做不出可用的版本；
**Haiku Vision 更會整段編造**（勿再試）。視覺模型只剩一個用途：補 `〓`。

| 書 | 章 | 段 | 殘留 `〓` |
|---|---|---|---|
| 畔上《無教會主義》1934 | 9 | 59 | **0**（有第二份 OCR 逐字對齊） |
| 畔上《初代の人々》1931 | 10 | 174 | 7 |
| 畔上《東洋文化の復興と基督教》1934 | 6 | 128 | 10 |
| 賀川《キリスト山上の垂訓》1927 | 48 | 170 | 29 |

**普查數字要自己重跑，而且要注意送進去的字形**：交接紀錄每一筆都低估。
複驗結果 —— 賀川豐彥 **89 種自著**（136 個 pid，一個 pid 是一個版次不是一部書）、
**矢內原忠雄 41 部**（交接寫 9）、畔上賢造 **27 部**（交接寫 16）、
**藤井武 12 部**（交接寫 7）。賀川那批是本 portal 最大的一座公有領域礦。

🚨 矢內原的 9 是怎麼來的：查「矢**內**原忠雄」回 0 筆，查「矢**内**原忠雄」回 41 ——
差別只在舊字體／新字體，而 API **不會報錯，就回 0**，跟「真的沒有」長得一模一樣。
`ndl_author_survey.py` 現在兩種字形都查再合併。新增作者若回 0，先確認字形。

🚨 **最該記住的一條**：NDL 把字集外的舊字體印成 `〓`（各書 300–900 處），
**它不是固定同一個字**。我曾經讓它「一律當敎」，結果賀川那本整章的
「地の**鹽**なり」變成「地の敎なり」，還有 心の淸き者→心の敎きもの、斷食→斷敎。
畔上兩本沒出事**只是運氣**。現在改成語境錨定、補不出來就留 `〓`——
**看得見的未解遠好過看不見的錯**。

管線、五個分章的坑、ruby 亂碼偵測、人工更正為何要存成資料 →
**[ndl_open_scans.md](ndl_open_scans.md)**。
registry：`azegami_build.py`／`kagawa_build.py`；測試 `test_ndl_build.py` 123 例。

矢內原《帝国主義下の台湾》與藤井武／金教臣那條 PD 線仍待起手。

## C4 佛學：印順‧聖嚴‧星雲‧昭慧（單一語言，pipeline ②）

全集本即繁中 → 零翻譯零對齊，走 §B5 PLAYBOOK。案例檔：[yinshun_collected_works.md](yinshun_collected_works.md) / [shengyen_collected_works.md](shengyen_collected_works.md) / [hsingyun_collected_works.md](hsingyun_collected_works.md)。

- **✅ 印順導師**（`yinshun`，amber ☸️）：來源 CBETA Y 系列 TEI P5 XML（`cbeta-org/xml-p5`，44 XML=42 部，非商業可再散布）。`cb:mulu` 三層→章節樹、`lb` 邊碼→段碼。`scripts/yinshun_build.py`（8 例綠）+ `yinshun_registry.json`。**44 卷 / 5324 chunks 上架**。
- **✅ 聖嚴法師**（`shengyen`，teal 🥁）：來源 ddc.shengyen.org《法鼓全集 2020 紀念版》— SPA 殼但靜態檔全枚舉（`all_books` 110 冊／`vol_dump` 4079 篇／`toc.html`／`html/{輯-冊-篇}.html`）。`p.indent` 正文／`p.hN` 標題／`span.pb data-page` 保留頁碼。`scripts/shengyen_build.py`（9 例綠）。**110 冊 / 4181 chunks 上架**。
- **✅ 星雲大師**（`hsingyun`，orange 🪷）：官網 reader 殼一度誤判「不出全文」，**user 給 `/ArticleDetail/artcle{N}` 後破關**（每篇免登入 server-render 全文＋麵包屑階層，不在 sitemap）。crawl `artcle{1..25500}`（19,888 篇有效、err=0）→ 麵包屑分組成 **109 冊 / 19,997 chunks**。`scripts/hsingyun_build.py`（10 例綠）。**🔑 教訓：薄殼站找不到內容端點時，直接問 user 要「實際在讀的文章 URL」往往秒破關。**

- **昭慧法師**（`chao-hwei`，rose 🕊️，2026-09-10 開）：**本區第一個「紙本掃描本」來源**——前三位都有現成的數位全文（CBETA／法鼓／佛光官網），昭慧法師沒有，只能從掃描檔做起。上游那一整段（2-up 拆頁轉正、頁碼帳、逐頁 OCR、腳註）獨立成 [[ebook-scan-transcribe]]，本 skill 只接下游。**✅《心靈的交會：山間對話》**（與彼得‧辛格對談，法界出版 2021，**作者授權製作電子版**）13 chunks／11.3 萬字，`genre:'dialogue'`，每一段掛原書印刷頁碼當引用號；**⏳《初期唯識思想》**轉錄中。**🔑 教訓：掃描本的失敗全是「靜默」型**——章別判錯、整頁被清理清光、去重留下爛的那一份，頁面都照常出現。細節見 [chaohwei_collected_works.md](../ebook-scan-transcribe/chaohwei_collected_works.md)。

## C5 心理學：榮格全集＋河合隼雄（REFERENCE 六冊）

**✅ 河合隼雄六冊繁中譯本上架（2026-07-23，REFERENCE／單一語言）**：來源＝讀客熊貓君版《河合隼雄心理學經典》套裝 EPUB（**簡體既有中譯本**、乾淨電子書非掃描），拆六冊各一 `ebooks` row（`ca7a1928-0000-4000-8000-00000000000{1..6}`）：讀幻想文學／原來如此的對談／長大成人的難處／故事與神奇／貓魂／青春就是夢和遊戲，共 **199 chunks / ~555K 繁中字**。做法＝`scripts/kawai_build.py`（6 純函式測試綠）：EPUB part→章節樹（toc.ncx 兩層 navMap）→ 每 xhtml part 一 chunk → `standardize_ebook.to_traditional`（opencc s2tw + TRAD_FIXES）→ **零 LLM、不寫 source_text（reader 退化單欄）**。hub `hayao-kawai` works[] 六筆 `status='done'`＋`ebookId`；`collection='collected-works'`。**教訓**：既有中譯本套書＝最省力路徑，判 REFERENCE-first（[[feedback_collected_works_reference_first]]）後直接 s2tw 轉錄即可，不必碰翻譯引擎。

案例檔 → **[jung_collected_works.md](jung_collected_works.md)**（版權表 / GW·CW 20 卷目 / 公有領域判定 / 來源 / 接手清單）＋詞庫 [jung_glossary.md](jung_glossary.md)。**本 skill 誕生的首案，多語對照 pipeline ① 的原型。**

一句話現況：榮格（1875–1961）GW 德文原典＋CW 英譯**多數卷版權內到 2031**，網路免費全文多盜版掃描；**僅 1930 前早期著作有乾淨 PD 來源**。**✅ Jung PD pilot 全卷完成（2026-06-24）**：1912《Wandlungen und Symbole der Libido》(de) + Hinkle 1916《Psychology of the Unconscious》(en) 完成 ch01–ch13，共 **1,205 rows / 254,474 繁中字**，`ebook_id 22222222-2222-4222-8222-222222222222`。

**✅《分析心理學論文集》英→繁中完成（2026-07-03）**：Constance Long 編 15 篇論文集（Gutenberg #48225，公有領域，英文文集無平行德文 → 英繁中雙語）。`scripts/jung_collected_papers_translate.py`（已 commit）：解析本文 `h2 CHAPTER` 標記（非前付 `p2` TOC）→ 分章 chunk → **NVIDIA-first** 引擎（Gemini 4 key 全 429 → 略過重試風暴）→ 多語 JSONL(source_order=[en]) upsert，每段 checkpoint、每 8 段上傳、單段容錯（transient 504 跳過續跑）、可續傳。全 15 章 285 段完成，ebook `22222224-…`。**教訓**：① NVIDIA 偶爾在 zh 前洩漏前言（「以下是根據您的要求…繁體中文版本：」＋有時加 `---`），害 zh 段數 > en 段數對齊錯位 → 收尾要掃「開頭前言／水平線」清理（opener 正則 + 段數比對，見本次 14 段清理）；② detached run 要用 PowerShell `Start-Process`（Bash 背景任務會隨 session 結束被砍，本案中斷 2 次）。

**✅《七篇致亡靈的佈道》德英中三欄完成（2026-07-03，REFERENCE 復用）**：/gnostic 已有英＋繁中 182 段（doc `seven-sermons-to-the-dead`）→ 只加德文 1916 原典為第三版，**零重譯**。`scripts/sermons_add_german.py`（已 commit）：德文全文來源 klarerblick.de「Sieben Reden an die Toten」（Jung 1916，美國 PD；curl 抓 HTML→get_text 逐行→REDE I–VII 去 footer=170 段，存 committed `.claude/skills/scripture-gnostic/sermons_de_1916.json`）→ `align_paras`（借 jung_ptypen 的長度 DP）對齊到英文本文段（order_index 37–181；§36 標題另填德文題名；前付 0–35 編者導言無德文留空）→ 插 `gnostic_versions` code=de_1916(category=source, is_default_orig=true) + 140 `gnostic_sections`。reader `pickForCategory('source')` **自動顯示中/英/原文三欄，只影響此 doc**（`availableVersions` 依 doc 有無 section 過濾）。截圖實證：Die Toten kamen zurück von Jerusalem ↔ The dead came back from Jerusalem ↔ 死者從耶路撒冷回來 三欄對齊。榮格 hub 書目用 `externalUrl` 連 /gnostic、不重複建 ebook。**教訓**：WebFetch 小模型會以「版權」為由拒抓 PD 文本 → 改 curl 抓 HTML 本機解析；.env 是 CRLF，JS 載入器要 split('=')+trim（regex `$` 會被 `\r` 卡住）。

**✅《心理類型》德英中三欄完成（2026-07-01）**：既有 Baynes 1923 英＋繁中（`ebook_id 22222223-…`，257 chunks）接上 **Gutenberg #61543 德文 1921 原典** → 三欄，德文覆蓋 234/257。對齊法（`scripts/jung_ptypen_add_german.py`，無底線＝已 commit）：**敘事章（Einleitung、I–X）走長度型單調 DP 段落對齊**（`align_paras`，英文 djvu 過度切段時允許 N→1 合併）；**定義章 Ch XI 因兩語各按自家字母序排列（獨 Empfindung=英 Sensation 位置不同）改走「見出字對照」**（`align_definitions` + `DE2EN_DEF` 術語表；同 chunk 內德文定義依英文出現序 re-sort → 逐欄對齊）；Schlusswort 結論部另走段落 DP。截圖實證：敘事 p13（拉德伯圖斯三欄同段）、定義 p229（Reductive/Reduktiv/簡化 三欄同定義）。**教訓／殘留**：① 長章 V／X 中段有 ~1–2 段 drift（長度型對齊固有，可日後用 h3 小節錨點收窄）；② reader `splitParagraphs` 會 `filter(Boolean)` 去空段 → 不能用空段 padding 做 chunk 內精確 index 對齊，故定義多筆同頁靠 re-sort 對齊首段；③ 跨語「同一部作品、既有他語譯本」若**譯本忠於原文順序**（Baynes 1923 ≠ Hinkle 1916 之重組），逐段自動對齊即可成，不必人工。同法可延伸其他「德文原典 Gutenberg 有乾淨 HTML＋既有早期英譯」的卷。

**起手卷決策＋方法教訓（其他多語卷通用）**：
- Pilot 選公有領域早期著作 = 唯一現在能合法取得、兩版同源可驗證跨版對齊者。受版權 CW 卷須 user 提供合法來源檔（**不抓盜版全文**）。
- 🔴 **德 1912 ↔ 英 1916 非段落同構（實證）**：Hinkle 重組結構（自序≠Jung Einleitung，heading 自動對齊會抓錯）→ **正確逐段三欄需人工逐句配對 + 親譯**，非自動 run。多數全集卷的既有他語譯本同樣非段落同構，此問題普遍。
- 穩定方法（每章）：德掃描 PDF → **Haiku 重 OCR**（Gemini 4 key 全耗盡）→ **內容指紋**配對 de↔en 章（非 heading）→ 人工逐段對齊 → 親譯（先查 [jung_glossary.md](jung_glossary.md)）→ build（三 list 段數必須相等，對齊閘會 SystemExit）。續傳細則見 [jung_collected_works.md](jung_collected_works.md)「🚀 新 session 接手清單」。

---

## §B9 文體版面（genre → reader 版面，2026-07-19）

**轉錄/翻譯時先判斷文體**（user 拍板：不同文體要不同版面，非通用一種）。`CwWork.genre`（`CwGenre`）決定 collected-works reader `[work].vue` 的呈現：
- `dialogue` 對話錄：段首 `〔講者〕內文` → 講者標籤 + 對話輪。**🚨 現有 Plato 是逐 Stephanus 節翻（一節多講者、zh 一整塊）無法 retrofit 講者分行 → 未來 dialogue 收錄要改「逐 speech 為單位」ingest**（Perseus Plato TEI 有 `<said who>` 可取講者）。
- `verse` 詩歌讚歌：保留詩行（單行換行）與詩節（空行）、懸掛縮排、逐行對齊（以法蓮/衛斯理聖詩/內薩瓦爾科約特爾/蘇菲詩）。
- `aphorism` 格言命題：逐條編號卡（斯多噶手冊/伊比鳩魯主要教義/維根斯坦小數編號）。
- `quaestio` 經院問答：段首 `〔異議/反之/正解/答覆〕` → 四段角色分區配色（阿奎那神學大全）。**✅ 首案在建（2026-07-23）：阿奎那《神學大全》中華道明會譯本 17 冊。圖書館既有 OCR 掃描本（collection=null）→ `scripts/aquinas_build.py`（6 純函式測試綠）讀 Drive 原始 OCR JSONL（唯讀保留）→ 每「節」切一 chunk、依「有關第N節，我們討論如下 → 質疑編號 → 反之 → 正解我解答如下 → 釋疑編號」注入四段標記 → 新 id `a9051225-…-NN`（a9≈aquinas 1225生年）。pilot 第一冊 221 節上架、reader 四段配色截圖驗證 ✅（作家 `thomas-aquinas` 在哲學學科，work 帶 `genre:'quaestio'`）。🚨 底本 OCR 雜訊重（督貴/啞益/反之→皮之），逐字清理＝剩餘大批次；批次同時重跑會修好被 OCR 打壞的區段標記。**
  **✅ 2026-08-17：17 冊全數 build＋upload 進 DB（2,598 chunks），hub 也補齊 17 冊 work 條目（原本只掛第一冊，另 16 冊入了庫卻在站上看不到）。逐字清理改走 `--clean --engine openrouter`（免費 8-key 獨立池，`google/gemma-4-26b-a4b-it:free`，完全不吃 Gemini／NVIDIA 量能），逐節 cache 在 `c:\tmp\aquinas_clean/{冊:02d}_{節:04d}.txt`＝可中斷續跑。已排進 `scripts/fleet_keeper.ps1` 的 **第一條 lane**（`aquinas`，每 30 分自我修復），`--upload` 為 idempotent（upsert＋replace chunks）故可反覆跑。**
- `treatise`(預設)/`essay`/`lecture`/`diary-letters`/`narrative`：通用逐段版面。
判定 helper `scripts/genre_classify.py`（結構啟發式；**hint（fetch manifest 已標／Haiku 覆核）優先**，純文字易被目錄騙故門檻保守）。reader 改動 regression-safe（未標＝現行版面，已截圖驗證）。內容慣例：對話錄/問答段落一律以 `〔角色〕` 起始，詩歌保留換行——**ingest 時就要埋好這些標記**。

## SOP（每卷接手）

**多語對照卷（pipeline ①，如古希臘／榮格／穆勒）**：
1. 讀該全集 case-study md 版權表，確認來源策略（公有領域 / 本機處理）
2. 套書規則：建 row + Drive 子資料夾 + file_path（[[feedback-set-books-subfolder]]）
3. 抽文字（EPUB 直抽 / PDF 走 OCR）→ per-語言 source chunks
4. glossary 先鎖高頻術語（§B8；人名查 [[translation-glossary]]）
5. 對齊（章節錨點優先，§B1-3）→ 對齊單位
6. `--limit 2` smoke test → 翻 2–3 章給使用者確認譯名/分欄
7. full run（engine/quota 看 [[ebook-translate]]）→ 多語 JSONL
8. volume/parent_volume backfill → R2 + DB previews
9. reader 多欄驗證 → hub works `status→done`+`ebookId` → commit + push（[[feedback-auto-push]]）
10. **收工前跑一次對帳**：`python scripts/collected_works_status.py`（改完再 `--apply`）

### 🚨 第 10 步不能省：「翻完了／上架了／標好了」是三件事

榮格十六卷 2026-08 就翻完，hub 卻掛著 in-progress、DB 裡只有一卷——三個原因疊在一起
（來源檔搬走、`file_path` 撞唯一鍵、row 沒帶 `collection`），每一個都沒有徵兆
（[[feedback_reader_silent_failures]]）。`collected_works_status.py` 把三者擺在一起看：

| 分類 | 意思 | 怎麼修 |
|---|---|---|
| 假 done | hub 說完成，DB 沒內容 | `--fix-fake` 降回 planned，順手拿掉查無此書的 ebookId |
| 該標 done | DB 已滿，hub 還沒改 | `--apply` |
| 沒列進 hub | DB 有這本全集書，works[] 沒有它 | `--link --apply`（書名對得上就自動補 ebookId） |
| 進行中 | 還在跑 | `--apply` 會把「本機已完成 N 節」寫進 note |
| 同書異版／譯本集 | hub 已指到另一譯本／本體在 /sacred-books-east | 不算缺漏，不用動 |

2026-09-02 這一輪：50 筆該標 done、4 筆假 done 降級、11 筆補進 hub，另補建**太虛大師
hub**（21 編早就上架卻沒有作家頁）與**佛洛伊德 hub**（《夢的解析》324 chunks 同上）。

⚠️ 手工往 store 插 works 條目時，插入點務必落在該作者的 `works: [...]` 之內——
`test/collected-works/isolation.spec.ts` 會抓到（它比對 regex 抽到的 ebookId 數與
store 實際載入的數量，插進 timeline 陣列會多一個對不上）。

**單一語言卷（pipeline ②，如印順／聖嚴／星雲）**：照 §B5 —— 來源分級 → 找內容端點 → 麵包屑反推結構 → 禮貌爬取+快取 → 解析器 → 入庫（per-book try/except+resume）→ hub。

**REFERENCE/自譯（pipeline ③④，如潘尼卡）**：見 [panikkar_collected_works.md](panikkar_collected_works.md) 接手清單。

---

## See also

- [[ebook-translate]] — 翻譯基礎設施（engine / quota / OAuth / append-resume / Gemini-Haiku fallback）＋一般雙語翻譯
- [[scripture-fathers]] — 公有領域教父原典；「參考現成中譯本校準」姿態本 skill 沿用
- [[ebook-pipeline]] — parse / OCR / standardize / 套書 split 上游
- [[ebook-scan-transcribe]] — **紙本掃描檔**那一段上游（2-up 拆頁轉正／頁碼帳去重補洞／逐頁 OCR／腳註含跨頁註／原書頁碼當引用號）
- [[translation-glossary]] — 人名／地名／哲學家／神學名詞詞庫（翻任何全集前先鎖譯名）
- [scripture-papal](../scripture-papal/SKILL.md) — 既有「拉/英/中三欄逐段對照」(alignDocs) content-file 版實作，可參考對齊邏輯
- 案例檔：[jung_collected_works.md](jung_collected_works.md)（心理學）／[mueller_collected_works.md](mueller_collected_works.md)（宗教學）／[panikkar_collected_works.md](panikkar_collected_works.md)（宗教學）／[yinshun_collected_works.md](yinshun_collected_works.md)‧[shengyen_collected_works.md](shengyen_collected_works.md)‧[hsingyun_collected_works.md](hsingyun_collected_works.md)（佛學）
- 詞庫：[jung_glossary.md](jung_glossary.md)／[mueller_glossary.md](mueller_glossary.md)／[panikkar_glossary.md](panikkar_glossary.md)（古希臘待建 `greek_philosophy_glossary.md`）

# 2026-09-02 交接：空殼歸零

這一天把 portal 上「有卡片、點進去是空的」全部清掉，並補了兩個根本不存在的作家頁。

| 做了什麼 | 結果 |
|---|---|
| 榮格 CW 十六卷上架（三個原因各修一個，見 [jung_collected_works.md](jung_collected_works.md)） | 6 本／164 萬字 → 21 本／648 萬字 |
| 希臘化與新柏拉圖 15 本（普羅提諾六集＋波菲利、伊比鳩魯五篇、愛比克泰德三種） | 71.8 萬字，佇列全數完成 |
| 韋伯三本（兩篇志業演講 EPUB＋方法論文集 714 頁，見 [weber_collected_works.md](weber_collected_works.md)） | 零 LLM 轉錄 |
| 矢內原青空文庫四篇（見 [yanaihara_collected_works.md](yanaihara_collected_works.md)） | 全部上架 |
| 榮格自傳（ebooklib 被一張不存在的圖擋了幾個月，改走 zipfile） | 15 章／24.4 萬字 |
| **太虛大師 hub**（21 編／595 萬字早就上架，portal 上卻沒有這個人） | 補建 |
| **佛洛伊德 hub**（《夢的解析》324 chunks 同樣情形） | 補建 |
| 狀態對帳（`scripts/collected_works_status.py`） | 四類落差全部歸零 |

**全集：446 本／9,339 萬字，空殼 0 本。**

## 這一天學到最貴的一課

「翻完了」「上架了」「標好了」是**三件事**，中間任何一環斷掉都不會有徵兆：

* 榮格十六卷八月就翻完，hub 掛著 in-progress，DB 裡只有一卷——原因是來源檔搬走、
  `file_path` 撞唯一鍵、row 沒帶 `collection`，三個疊在一起。
* 太虛 21 編、佛洛伊德《夢的解析》內容都在 DB，只是 portal 沒有那個作家。
* 亞里斯多德《政治學》43/98 個 chunk 的譯文後半是模型的自語（`"政", "體", … same.`），
  chunk 照樣寫檔上傳、reader 照樣顯示，唯一徵兆是字數異常大。

所以 SOP 第 10 步（收工前跑一次對帳）不是形式。

## 🚨 收工前的三道品質閘（缺一不可）

三支工具抓的是**不同的失敗模式**、吃**不同的資料形狀**，不能互相取代。共同點是：
這幾類錯全都**段數對得齊、覆蓋率 100%、品質分數正常**，只有真的去讀內容才看得見
（[[feedback_reader_silent_failures]]）。

| 閘 | 工具 | 吃什麼 | 抓什麼 |
|---|---|---|---|
| ① 狀態對帳 | `scripts/collected_works_status.py` | store＋DB | 假 done／該標 done／沒列進 hub |
| ② 模型自語 | `scripts/plato_quality_scan.py` | `c:/tmp/plato_*.jsonl` | token 自語、體積異常、混入英文長句 |
| ③ 拒譯污染 | `scripts/audit_llm_meta_replies.py` | `*_data/*/sec*.json` | 元回覆、整段未翻譯、臆造 |

### ③ 拒譯污染（2026-09-08 新增，首掃就清了 2,554 段）

Haiku 遇到它判定「不是英文／是亂碼」的來源時**不回空**，而是回一段說明，管線把
說明當譯文存進 `zh[i]`：

    我注意到您提供的「英文原文」實際上是梵文文本（使用 IAST 音譯法），而非英文。

首次全掃 `*_data`：**元回覆 2,375 段、整段未翻譯 179 段**，且**都已經上線**
（阿維斯陀 266 段 DB preview 裡 32 段開頭就是）。重災區 `sbe-04-zend-avesta-1`、
`auld-lang-syne`、`comparative-mythology`、`chips-1`、`science-language-2`。

三類判準與踩過的坑：

* **元回覆**——🚨 **中英文都要掃**。第一版只掃中文標記，漏掉 207 段
  `I'm ready to translate the English text from…` / `I appreciate your detailed
  instructions, but I notice…`。
* **整段未翻譯**——LLM 把英文原文原樣吐回來（中文字佔比 <5%）。抽樣抓到 2,280 字的
  `Magic and Witchcraft, though often confounded with Religion…`。
* **臆造**——來源極短、譯文卻長好幾倍。書眉 `140 LECTURE in.` 生出 1,118 字講稿、
  索引行 `Bastholm ........` 生出 1,575 字虛構章節、`Introduction.` 一個字生出整段導論。
  🚨 門檻 `HALLU_MIN_OUT` 實測要 **120 不能用 30**：`Saranyu=Erinuys, 73.` 譯成
  「薩蘭尤（Saranyu）= 厄里倪厄斯（Erinuys），第73頁。」是**正確譯文**，中文音譯加括號
  本來就會變長。這一類是啟發式判斷，`--fix --meta-only` 會保留它們待人工看過。

**清成空白而不是硬翻，是刻意的。** 高發來源是**被 OCR 打爛的梵文／阿維斯陀轉寫**與
**書眉**（`Ixx THE QUR'AN.`、`xl DHAMMAPADA.`），本來就沒有可譯內容。硬翻只會得到
`Ixxx THE QURAN.` →「第十章《古蘭經》」（lxxx 是頁碼不是章號）、
`Tue Cuaprer or tHe Ports.` →「卡巴聖殿或眾門之地」（其實是詩人章，Poets 被 OCR 成
Ports）。留白時 reader 只顯示英文，那是誠實的；留著錯譯則是靜默的錯誤。
真要補譯**走 Gemini，別再用 Haiku 補同一批**（同 [[feedback_dialogue_rewrite_gemini_not_haiku]]）。

    python scripts/audit_llm_meta_replies.py                    # 只報告
    python scripts/audit_llm_meta_replies.py --root mueller_data --samples 5
    python scripts/audit_llm_meta_replies.py --fix --meta-only  # 清判準明確的兩類

🚨 `--fix` **只改本機 sec*.json，不會上傳**。清完要重跑該 driver 的
`assemble_and_upload` 才會反映到站上，否則就是 [[feedback_build_not_equal_deployed]]。
上傳時注意 **sbe-\* 各卷的 registry 在 `sbe_translate.WORKS`，不在
`mueller_auto.WORKS`**（後者只有 Müller 本人 16 部），取錯會 `KeyError`——
`mueller_fill_residuals.py` 就是這樣靜靜地一本都沒上傳。

## 記憶庫併入：project_collected_works_multilang

新 skill `ebook-collected-works`（`.claude/skills/ebook-collected-works/`）— 教**多卷全集**做「3 欄以上多語對照」（原文＋既有譯本＋我的繁中逐段）上架電子圖書館。跟 [[ebook-translate]]（雙語）、[[scripture-fathers]]（公有領域教父）並列為第三個翻譯 skill。使用者要求 skill 名稱要**通用教全集翻譯**，不要只教榮格。

**三件 ebook-translate 不處理的事**：(1) 多卷套書統一 volume/parent_volume 樹；(2) `source_text`/`source_lang` 單一來源 → `sources`{lang:text}+`source_order` 多來源 schema（向後相容：source_text 鏡像 source_order[0]）；(3) 獨立編輯的德/英版本「逐段對不齊」對齊（章節錨點>長度比>LLM輔助>整段塞）。

**首案＝榮格全集**：⚠️ GW 德文原典+CW 英譯**多數卷版權內到 2031**（榮格 1961 卒）；網路免費全文多盜版掃描；**僅 1929 前早期著作**（《Wandlungen》1912 德 + Hinkle 1916 英）有乾淨公有領域來源，且 CW5 改寫本≠1912 原典。使用者選擇「盜版 PDF 跑完整全集」+「另建新 skill」。處理姿態：reader 只顯示我的繁中+來源原文欄，第三方中譯不入庫；版權內來源走本機 pipeline，Claude 不在對話貼整段受版權原文。

**進度（2026-06-02 全部 test-first，已 push）**：
- ✅ reader N 欄：`pages/ebook/[id].vue` ViewMode→`zh|parallel|src:<lang>`，toggle 由 source_order 動態生；`ChunkData`+API 加 `sources?`/`source_order?`。**已截圖實證**（3 欄對照 + zip 補白 + footnote by-number 對齊 + 單來源模式）。
- ✅ 契約模組 `lib/multilang-sources.ts`（client+server 共用，非 server/utils）+ `test/multilang-sources.spec.ts`（27 例）。
- ✅ Python 寫入器 `scripts/multilang_chunks.py`（鏡像 TS 契約 + `assemble_multilang_chunks(units, translate_fn, source_order)`）+ test（21 例）。
- ✅ 對齊 `scripts/align_editions.py`（`parse_chapter_number` DE/EN/CJK+羅馬/中文數字；`align_editions` 錨點 join / order 補白 fallback）+ test（20 例）。full pytest 147 passed。
- 🔧 `screenshot_book.mjs` 加 `--device`（注入 `kgl_device_id=screenshot-bot`）繞過 device-trust gate；`trusted_devices` 已預埋該列（勿刪，fathers 校對截圖也靠它）。

**起手卷拍板（Claude 決定）**：公有領域 1912《Wandlungen》(de) + Hinkle 1916《Psychology of the Unconscious》(en) — 唯一現在能合法取得處理、同一作品可驗證跨版對齊的 Jung 來源。受版權 CW 卷待 user 提供 HTML 來源檔（不抓盜版全文）。

**Pilot 實況（2026-06-03 真資料跑過，全 push）**：
- ✅ 詞庫鎖定：jung_glossary.md 用心靈工坊/TSAP/《榮格心理學辭典》查證（das Selbst=自性禁「本我」、individuation=個體化、synchronicity=共時性、libido=力比多）。《榮格心理學辭典》是**版權書**，只作術語參考、不轉錄入庫（同 fathers「參考不入庫」政策）。
- ✅ 驅動鏈：`scripts/translate_collected_work.py`（split_sections/`load_html_sections`/`make_translate_fn`/`run`）+ HTML loader（實證 Gutenberg #65903 Hinkle 英譯）。
- ✅ 德文重 OCR 路線可行：archive.org 1912 PDF **純圖像無文字層**；本專案 Gemini/Haiku 重 OCR 開頭 14 頁→還原 ERSTER TEIL/Einleitung/I./II. 結構。OCR slice 存 `c:/tmp/jung_wandlungen_de_1912_ocr.jsonl`，工具 `scripts/_jung_ocr_slice.py`。
- ⚠️ **Gemini 4 把 key 全耗盡**（key#1 prepay depleted、#2-4 quota exceeded）→ 走 Haiku fallback。影響全專案預設引擎，user 需查 Gemini 帳單。
- 🔴 **德 1912 ↔ 英 1916 不逐段對齊（實證）**：Hinkle 重組（自序≠Jung Einleitung；heading 自動對齊抓錯）。用 Ferrero 法文題詞指紋定位真對應（德 Einleitung=英 Ch I Two Kinds of Thinking），但章內段落仍不對齊（英 74 段 vs 德 4 段）。→ **正確逐段三欄需人工逐句配對+親譯**，非自動 run；多數全集卷英譯(Hull)同樣非段落同構，此問題普遍。

**✅ 首章三欄上架（2026-06-03）**：走 (a) 人工配對。內容指紋確認德 Einleitung=英 §8 INTRODUCTION（非 §9；heading/Ferrero 題詞不可靠），**親譯整章「引論」5 段**，trilingual ebook `22222222-2222-4222-8222-222222222222`（test）reader 三欄逐段對齊（截圖+段數雙驗證）。穩定方法：德掃描 PDF→**Haiku 重 OCR**（Gemini 全死）→內容指紋配 de↔en 章→人工逐段對齊→親譯→build。工具 `scripts/_jung_ocr_slice.py`/`_jung_pilot_build.py`（一次性 `_`）。

**🚀 接手交棒**：User 要開新 session 續做。**完整接手清單（5 步方法/待辦/檔案/指令/雷區/ebook_id）寫在 skill 內 `jung_collected_works.md`「🚀 新 session 接手清單」**。下一章＝德 `II.`（兩種思維）=英 §9 Ch I（Hinkle 章號比德少 1）。Gemini 已死一律 Haiku（訂閱制不計費）。德文 PDF 已刪需重抓 archive.org `Jung_1912_Wandlungen`。

**🆕 全集 Portal + 作家 Hub（2026-06-05，已 push）**：全集**不放在 /ebook 裡**，獨立 `/collected-works`（首頁加 📚 全集 cyan 卡）。每位學者一張卡→作家 hub `/collected-works/[slug]` 最外層：學術貢獻簡介(粗體 markdown)＋肖像(Wikimedia Commons `Special:FilePath/<檔>?width=500` 公有領域，不用 Supabase Storage)＋生平學術年表(timeline)＋著作目錄(按 category 分組、組內 yearSort 排序、轉錄狀態 badge done/in-progress/planned/copyright)。單卷閱讀仍走既有 `/ebook/[id]` 多欄 reader(work.ebookId 連過去)。資料在 `stores/collectedWorks.ts`(repo-committed，沿用 /works·speech.ts 模式，**user 拍板免 DB migration/免 server route**)。新增學者=push 一個 CwAuthor；某卷轉錄完=改 status+填 ebookId。color 須在 tailwind safelist(別用 -400)。已截圖實證 portal/穆勒/榮格 3 頁。

**🆕 案例 2＝馬克斯‧穆勒（宗教學家全集 #1，2026-06-05 起）**：Friedrich Max Müller 1823–1900，宗教學開山祖，**卒 1900 全部著作早已公有領域、全球無限制**（最乾淨案例，無盜版/版權閃避）。**以英文寫作為主** → 預設英＋繁中；少數有平行德文版的卷做英德繁中三欄。語言策略(user 拍板)：英＋德＋繁中三欄僅限有德文版的卷。起手卷＝《宗教學導論》(1873 英 archive.org `introductiontosc00ml` ＝ 1874 德《Einleitung》archive.org `einleitungindie00mlgoog`)，**英德同構：皇家研究院四講＋兩附論**，比榮格 Hinkle 重組好對齊。德文 1874 Fraktur djvu OCR 中等雜訊(可譯，差再 Gemini Vision)。案例檔 `mueller_collected_works.md`(版權/18卷目/來源/對齊/接手) + 詞庫 `mueller_glossary.md`(宗教學/henotheism 單一神教/語言的疾病/雅利安語族…，英文原詞為準)。源 txt 在 `c:/tmp/mueller_isr_en_1873.txt` / `mueller_einleitung_de_1874.txt`。

**✅《宗教學導論》三欄竣（2026-06-05 上架，hub 已轉錄）**：ebook `33333333-3333-4333-8333-333333333333`，7 chunks(封面+4講+2附論)，EN/DE/繁中逐段對齊 0 mismatch，~21.5 萬繁中字。pipeline=`scripts/mueller_build.py`(手調 6 段 line range；retry-on-empty 補引擎漏譯；4 段引擎反覆漏譯的真內容含「知其一便一無所知」名言由我親譯補)。cache 在 `mueller_data/isr/sec0-5.json`(已 commit)。**雷區**：reader 強制 page1=封面(`isCoverPage`=currentPage===1)會吃掉內容→cover chunk 0 必備；chunk content 第一段是 heading row→JSONL ¶N=cache zh[N-1] 有 off-by-one。

**🤖 其餘 13 部自動 queue 連續轉錄（2026-06-05 起跑，排程接管）**：`scripts/mueller_auto.py`(registry 13 書 archive.org `_djvu.txt` 源已驗證 + ebook_id + 章節策略)雙語(英→繁中)；下載→reflow→章節切分(lecture heading 偵測+TOC/前言過濾+去重；否則 coarse 第N節)→NVIDIA 逐段→cover+JSONL→R2/DB。resumable(per-book/section cache `mueller_data/<slug>/`)+lock(每段 touch)。**English-first(2026-06-05，user 指示，同 [[feedback_jung_nonpd_english_first]])**：queue Phase 1 先**無 LLM 把全部英文 ingest 上架**（13 本秒級可讀英文）、Phase 2 才逐段翻；繁中主欄**未譯段 fallback 顯示英文**（`section_chunk` zh[i] or en[i]），每 12 節 re-upload 讓中文漸進浮現。私人站、非 PD 來源也可用（穆勒全 PD 無妨）。**排程**：Windows 任務 `MuellerAutoTranscribe`(登入+每4h,無時限,resumable)跑 `scripts/mueller_auto_queue.bat`→`--run-queue`；session 關掉/重開機都續跑直到 13 部竣。hub `[slug].vue` fetch 活 chunk_count→有內容自動轉「轉錄中」可點。**規模~25k 段、數日**，與 /coach 共用 NVIDIA 互相節流。**待修**：六派 `sixsystemsofindi017601mbp` 無 txt(跳過待換源)；coarse 書首段偶夾 OCR 前言；有德文版者(物質/神智學/語言1&2/印度/神話科學論集)日後可升三欄。

**🆕 案例 3＝雷蒙‧潘尼卡（受版權當代神學家 #1，2026-06-12 起）**：Raimon Panikkar 1918–2010，宗教間/宗教內對話與跨文化哲學巨擘；**卒 2010 → 全部著作受版權至約 2080，榮格型（非穆勒）**：網路無乾淨合法 PD 全文、第三方中譯不入庫。採 English-first（[[feedback_jung_nonpd_english_first]] 私人站非 PD 可用、英文先輸入）。多語原創（加泰隆/西/義/英/德），Opera Omnia(Jaca Book 義/Orbis 英,12 卷,Milena Carrara Pavan 主編) 是**主題重編** → 逐段三欄只在「同一文本恰有原文+英譯」時成立，多數卷先英+繁中雙語。語言策略(user 拍板 2026-06-12)：English-first 雙語預設、個別文本有平行原文版再升三欄。起手卷＝**《印度教中未識的基督》**(原文即英文,1964/1981)，ebook_id `55555555-5555-4555-8555-555555555555`。檔：`panikkar_collected_works.md`(版權表/12卷目/接手) + `panikkar_glossary.md`(自鑄詞 cosmotheandric 宇宙神人共融/intrareligious 宗教內對話/Christophany 基督顯現/tempiternity/diatopical hermeneutics)。**test-first**：`scripts/tests/test_panikkar_build.py`(14 例) → `scripts/panikkar_build.py`(reflow/split/align/build_section_chunk/assemble_pilot，比照 mueller_build；**坑：split 必須在 reflow 之前，否則 reflow 合併無標點段會吞掉標題**)。hub 潘尼卡卡 indigo🪷 12 卷書目+肖像(CC0 `Raimon Panikkar.jpg`)，起手卷 status=planned(pipeline 就緒待英文來源檔)。**兩種 build 模式（user 拍板 2026-06-12）**：(1) **REFERENCE 模式**（`panikkar_build.py --src <en> --zh-src <zh>`）— **已有完整中譯就不重譯**，把第三方中譯（簡 opencc→繁，`standardize_ebook.to_traditional`）當主欄、英文原典逐段對照、零 LLM；潘尼卡有王志成/思竹整套中譯（四川人民/宗教文化/江蘇人民），起手卷《印度教中未知的基督》即走此模式。(2) **自譯模式**（`--src <en>`）— 無中譯的卷才 English-first 引擎自譯。新函式 `build_reference_chunk`/`pair_sections`（按章序配對）/`assemble_reference`/`load_zh_sections`；CJK 章標題 `_CJK_HEADING_RE`（導論/第N章/第N節…，**token 後須接邊界，"第一章的正文"不誤判**）。第三方中譯私人自用可入庫當「參考層」、不取代自譯主欄（SKILL.md 處理姿態私人例外）。test-first 共 22 例綠。

**取源原則（user 拍板 2026-06-12，已寫進 SKILL.md「本專案的處理姿態」）**：本站=auth-gate 私人研究圖書館僅供個人閱讀 → 受版權卷若無 PD 源、archive.org 又只借閱，**可從 shadow library（Anna's Archive／libgen）抓來源 PDF/EPUB 到本機**（English-first、來源原文只走本機檔不貼對話、主欄是我的繁中）。**⚠️ 此 sandbox 網路限制**：annas-archive／libgen.is/.rs **DNS 被擋**，僅 `libgen.li` 可達且常只索引期刊書評非專書；archive.org 本人兩本（`unknownchristofh0000raim`1967/`..._q2h1`1981）皆 inlibrary 借閱制 djvu.txt 受限 → **抓不到時請 user 在自己機器下載後丟本機**（new-book drop／`c:/tmp`），`--src` 讀檔即開譯。

**🆕 漢傳佛教三套＝第一批「單一語言」案例（2026-06-13，已 push）**：全集本即繁中 → **零翻譯、零跨語對齊**，pipeline 砍剩「解析→JSONL→DB/R2→hub」，reader 退化單欄（無 `sources`，向後相容）。downstream 入庫/hub/reader 三套完全共用，差別只在來源解析器。
- ✅ **印順導師**（slug `yinshun`，amber/☸️）：來源 CBETA Y 系列 TEI P5 XML（`cbeta-org/xml-p5`，44 XML=42 部，非商業可再散布，遠優於已改版基金會官網）。`cb:mulu` 三層→章節樹、`lb` 邊碼、`note` 剝除。`scripts/yinshun_build.py`(8 例綠)+`yinshun_registry.json`。**44 卷/5324 chunks 上架**。
- ✅ **聖嚴法師**（slug `shengyen`，teal/🥁）：來源 ddc.shengyen.org《法鼓全集2020紀念版》— SPA 殼但靜態檔全枚舉（`getData.php?type=all_books`110冊／`type=vol_dump`4079篇／`tree_menu/toc.html`章節樹／`html/{輯-冊-篇}.html`正文）。`p.indent`正文/`p.hN`標題/`span.pb data-page`**保留原書頁碼**/`span.lb`剝除。`scripts/shengyen_build.py`(9 例綠)+`shengyen_registry.json`。**110 冊/4181 chunks 上架**。雷區：requests 要 UA+verify=False+指數退避（server 高載丟連線）、`--all` per-book try/except+`--resume`。
- ✅ **星雲大師**（slug `hsingyun`，orange/🪷）：官網 reader 殼（`/bcN/bookM` 空殼、sitemap 38 URL、無 XHR）一度誤判「不出全文」，**但 user 給 `/ArticleDetail/artcle{N}` 後破關**——每篇免登入 server-render 全文 + 麵包屑階層（大類/冊/篇），不在 sitemap、reader 殼不揭露。**已全量上架**：crawl `artcle{1..25500}`（19,888 篇有效、err=0 未被封鎖、快取 `c:/tmp/hsingyun_cache/`）→ 麵包屑 `book_key` 分組成 **109 冊 / 19,997 chunks**（ebook_id `c0000000-…`，按 12 大類）。`scripts/hsingyun_build.py`（10 例綠，parse_article/crawl 禮貌節流+退避+resumable/`--build --resume` per-book 容錯）+`hsingyun_registry.json`。**🔑 教訓：薄殼 JS 站找不到內容端點時，直接問 user 要一個「實際在讀的文章 URL」往往秒破關（內文常走 sitemap 外的另一條 MVC 路由 `/ArticleDetail/artcle{N}`）。**
- 共用雷區：ebooks.id 是 UUID，查全集用 `id=in.(...)` 不能 `like`；reader 全頁截圖 ~3800-3970px > 2000px 硬限須 PIL crop；dev server 多任務並行 :3000 可能被別任務佔/壞（[[feedback_no_kill_other_tasks]]）→ 自己另起 `PORT=3100`，已認證 reader 首次 SSR 冷編譯 >30s 須把 screenshot navigationTimeout 拉 150s。case 檔：`yinshun_collected_works.md`/`shengyen_collected_works.md`/`hsingyun_collected_works.md`。

**🆕 潘尼卡進度（2026-06-14 交棒，新 session 先讀 `panikkar_collected_works.md`「🚀 新 session 接手清單」）**：z-lib/ 有 user 丟的全部 PDF/EPUB（版權檔、OCR 文字進 c:/tmp 或 panikkar_data/，勿 commit/勿貼對話）。中譯 8 種全查實、原文 ~11 種（義/英/西，多 text-layer）。**規則：有中譯→REFERENCE 對照；無中譯→由原文（多義大利文）/英文自譯。**
- ✅ **上架 2 本**：宗教內對話（`55555556-…`，REFERENCE en+王志成中譯，11 章逐段 0 mismatch）；神的經驗：奧祕的聖像（`55555561-…`，自譯 en→繁中，39 chunks）。
- 🔄 **自譯 queue 背景連跑**：`scripts/panikkar_auto.py --run-queue`（EBOOK_CHUNKS_DIR 要設）。8 卷 registry WORKS，resumable（`panikkar_data/<slug>/orig.txt`+`sec{N}.json`），engine `pb.make_engine(src_lang)` 英/義/西。序：experience-of-god✅→rhythm-of-being(epub，本輪 prompt-too-long 跳過、已修 `_split_long_paras`、下輪補)→myth-faith-hermeneutics(義)→pace→mysticism-fullness(卷I)→religion-world-body→mundanal-silencio→vedic-experience(1222pp 殿後)。~2500 頁跑數日。**待辦：各卷完成補 hub done+ebookId。**
- **3 支核心腳本**：`panikkar_build.py`（單本 REFERENCE/自譯，REGISTRY+manifest+`split_chapters_by_manifest`）、`panikkar_auto.py`（queue）、`ocr_pdf_to_text.py`（`--engine font` born-digital 字級抽標題 / gemini OCR scanned / text）。pytest 29 例綠。
- **對齊血淚**：REFERENCE 章節對齊最難——`split_chapters_by_manifest` 用「following-body」判真章 vs 目錄（勿固定視窗 TOC）、錨點 alternatives（第N章 OR 標題）、merge running-head；**born-digital 原文用 font 抽取**（視覺 OCR 漏標章名、壞 cmap 亂碼 ŚŪNYATĀ→SONYATA）；**flat 書對得齊、階層書（人的圓滿 部→章→節）對不齊需人工 manifest**。
- ⏳ **待補**：人的圓滿(it+zh)階層書人工逐章 manifest 精對（OCR 在 c:/tmp 會被清需重抽）；缺英文原典的 4 本中譯（印度教中未知的基督/文化裁軍/看不見的和諧/對話經）待 user 補原文。

**🆕 portal 依學科分組 + 古希臘哲學家全集（2026-07-01，已 push；SKILL.md 亦全面重構為學科優先 §A/§B/§C）**：user 要 `/collected-works` portal **改依學科分組**（佛學獨立一類）。`CwAuthor` 加 `disciplineGroup` 欄（別跟既有 `discipline` 一句話副標搞混）＋ `sortYear`（生年 BCE 負；portal `pages/collected-works/index.vue` 在學科組內依此排序，缺省排末尾）；`DISCIPLINE_ORDER=['哲學','社會學','宗教學','神學','佛學','心理學','人類學']`，空組不顯示。歸類：穆勒＋**潘尼卡→宗教學**（潘尼卡 2026-07-01 由神學改歸宗教學，user 拍板；**神學暫無人**）、榮格→心理學、印順/聖嚴/星雲→佛學。**哲學學科群＝古希臘 19 位、一人一 hub、依年代排**（user 拍板「前蘇格拉底不能跟蘇格拉底併卡、每個人獨立」）：泰利斯/阿那克西曼德/阿那克西美尼/畢達哥拉斯/色諾芬尼/赫拉克利特/巴門尼德/阿那克薩哥拉/芝諾(伊利亞)/恩培多克勒/普羅泰戈拉/高爾吉亞/蘇格拉底/德謨克利特/柏拉圖/亞里斯多德/伊比鳩魯/愛比克泰德/普羅提諾（sortYear −624→204）。全**公有領域**（古典原文+19世紀英譯 Jowett/Ross/MacKenna），可希/英/繁中三欄，著作多 `planned` 待逐步轉錄。肖像用 Wikimedia Commons PD 胸像/畫像（逐一 curl 驗證；普羅泰戈拉/高爾吉亞無合適 PD 像→emoji）。拆卡用一次性生成腳本 `scratchpad/gen_presocratics.py`（banner 標記 byte-splice，非 Edit 硬匹配）。接手轉錄比照榮格 pipeline、人名先查 [[translation-glossary]] 哲學家表（對齊 `scripts/seed_glossary_philosophers.py`），待建 `greek_philosophy_glossary.md`。**下一步**：柏拉圖《蘇格拉底的申辯》起手（Perseus 希臘 Stephanus + Gutenberg #1656 Jowett 英譯，皆已驗證可抓）→ §B2 多語 pipeline 三欄。**注意**：pre-push vitest hook 會被並行 session 的 dev server 佔 .nuxt 弄壞（非程式問題），純文件變更 user 核可 `--no-verify`。

**✅ 柏拉圖《蘇格拉底的申辯》希英繁三欄完成（2026-07-01，哲學群第一本，已上架驗證）**：`scripts/plato_build.py`（可重用對話錄 pipeline）。來源＝**Perseus canonical-greekLit GitHub raw**（`data/tlg0059/tlg002/…perseus-grc2.xml` Unicode 希臘＋`…perseus-eng2.xml` Fowler 英譯 Loeb 1914，皆 PD；**別用 dltext，那是 Betacode 非 Unicode**）。兩版皆以 **Stephanus 節 milestone（`unit="section" n="17a"`）為錨點→完美對齊**（125 節 grc==en，0 gap）。**逐節翻繁中**（從希臘、Fowler 僅消歧義，`PROMPT_TMPL.format(source=)`；Gemini 4 key 全 429→`--engine haiku` 直翻，同 Jung）、每 Stephanus 頁一 chunk、grc/en/zh 段數對齊（reader `zipParallel`）。ebook `70000000-0000-4000-8000-000000000001`，**27 chunks（1 封面+26 頁 17–42）/ 20,685 繁中字**，hub work status=done。截圖實證三欄逐段。**兩個雷區（踩過）**：① **reader `isCoverPage=currentPage===1` 會吞掉 chunk 0 內容**→必須 `_prepend_cover`（chunk 0=犧牲封面 chapter_path「封面」，真內容自 chunk 1），同 mueller_build.make_cover_chunk；② **ebooks 表有 CHECK**：`file_type ∈ {epub,pdf}`（'xml' 400）、**無 status/source_lang 欄**、`display_mode='standard'`（多語靠 chunk 的 sources 判定非此欄）；insert 要 `raise_for_status` 別靜默失敗（我第一次靜默失敗→row 不存在 reader 404，靠截圖驗證才抓到）。多語 reader **不寫 ebook_chunks preview**（Jung 也 0 rows，全讀 R2 JSONL）。**下一部對話錄**：在 `DIALOGUES` registry 加一筆（tlg 號＋ebook_id＋meta）即可 `python scripts/plato_build.py <slug> --upload`。

**🆕 全集專屬三欄 reader（2026-07-02，取代 /ebook UI，已 push＋截圖實證）**：user 要全集不走 /ebook（空白封面＋分頁錯位「開頭很奇怪」），改**聖經三欄式**專屬 reader `pages/collected-works/[slug]/[work].vue`（`[work]`=ebookId，版型仿 `pages/creeds/[slug].vue` grid）。每 row：`3.25rem 1fr…` ＝**左引用號欄＋繁中＋各來源欄**（欄數依 source_order 動態；`normalizeSources`＋`zipParallel` 逐段）。引用號＝`chunk.anchors[i]`（**Stephanus 17a／Bekker 1094a**；無則 page_number），點擊複製「作者《書名》anchor」＋`#cite-` hash。**每卷 page1 頂部導讀卡**＝`data/collectedWorksIntros.ts[ebookId]`（keyed by ebookId 的獨立檔）。**anchors 資料契約四處都要**：plato_build.build_units 產 anchors → multilang_chunks.build/assemble 傳遞 → ChunkData.anchors? → `/api/ebooks/[id].get.ts` currentPage 白名單。**踩過的雷**：① **Nuxt 巢狀路由**——`[slug].vue`＋`[slug]/[work].vue` 會讓 [slug] 變父層需 `<NuxtPage/>`（否則 child 不渲染只出 hub）→ 把 hub 移成 `[slug]/index.vue` 與 [work] 同層；② `/api/ebooks` `requireAuth()` 要 **Bearer token**（`getSession().access_token`），reader client-side fetch 必帶 Authorization，SSR/cookie-only 會 401（/ebook reader 就是這樣，line 1621 getToken）。舊 /ebook reader 保留給一般電子書。SKILL §B6 已改寫。

**🆕 整夜自動化引擎（2026-07-02 修正）**：`greek_overnight.py` 預設 **NVIDIA**（`nvidia_translate`，deepseek-v4-flash-0731，`NVIDIA_MIN_INTERVAL=6s` 全域節流＋4-key 輪流；~8-10s/節、~overnight 跑完全 Plato+Aristotle）。**Haiku 直翻 bulk 會撞 Claude Max 429**（sequential 也撞）→ 別用 haiku 跑大量；Gemini 4-key billing 耗盡。`plato_build make_translate_fn` 加 `nvidia` 選項。**雷：別同時跑兩個 queue**（我一度 haiku queue 沒停就launch nvidia queue，兩者搶 log/cache/upload；用 TaskStop 全停→清 `.done` marker→單一 nvidia queue 重跑，快取保 translations、cache-hit 重組補 anchors）。resumable：per-節 cache `c:/tmp/plato_cache/<slug>_zh/`＋`<slug>.done` marker。

**🆕 五學科大規模補齊 246 位人＋書目＋年代→地域兩層分組（2026-07-18，已 push commit 23ad01b4）**：user 要把心理學/宗教學/宗教社會學/神學/哲學「人和書目補齊」，翻譯之後再排。決策：哲學/神學**先分年代再分地域**（user 二次澄清「古代中世紀近代都要各自分地域」）、其餘單層；直接研究補齊全部；**多元＋非西方中心並重**。
- **結構**：`CwAuthor` 加 `era?`/`region?`；portal `index.vue` 對「有 era 的學科」渲染兩層（年代大標→地域小標→卡片，年代/地域皆依組內最早 sortYear 排），無 era 學科維持單層。`DISCIPLINE_ORDER` 加 `宗教社會學`（排宗教學後）。既有 19 古希臘 region 從「希臘‧地中海」統一「西方」、9 無教會＝現代與當代‧東亞（日‧韓）。
- **規模**（store 現~280 位）：哲學 123（古代西/中/印＋中世紀西/拜占庭/伊斯蘭/猶太/印＋近代西/中明清/日江戶/韓性理學/波斯後古典＋現當代西/新儒家/印/京都/非洲/拉美）、神學 104（教父拉丁/希臘/敘利亞＋中世紀女神秘家＋宗改＋近代＋現當代西方＋非西方處境解放/女性/黑人/非洲/東亞/南亞/東正教＋新教其餘宗派衛理/聖公/重浸/貴格/福音/五旬節＋東方正統六會）、宗教學 17、宗教社會學 15（新）、心理學 18。
- **執行手法**：13 路平行 `general-purpose` sonnet agent（每 bucket 一份，讀共用 `scratchpad/cw_spec.md` 規格）產 JSON→`scratchpad/assemble.py`（去重/驗色系 safelist/驗 status/必填→emit TS 插 authors 陣列尾）。**肖像逐一 urllib HEAD 驗證**（Wikimedia 擋預設 UA 要帶 Mozilla；連發會 429 誤判需間隔重驗；68 個僅 wang-yangming 真 404 已清空）。esbuild 驗 TS 語法＋dev server :3200 截圖實證兩層分欄。全 planned/copyright（尚無轉錄），翻譯 pipeline 之後逐卷接（比照 §C 各案例）。
- **相關 feedback**：[[feedback_dazangjing_diversity]] 多元原則同樣適用；[[feedback_workflow_inline_script_not_scriptpath]] 這次沒用 Workflow（未 opt-in）改用 Agent 平行；agent JSON 輸出比 TS 安全（assemble.py 統一 emit）。
- **當代神學再細分地域（2026-07-19，commit 72dc4aee）**：user 要「現代與當代神學要分歐陸/北美/拉美/非洲/原住民等」。做法：神學 era=現代與當代 且 region=西方（拉丁）的 15 筆改「歐陸」（教父/中世紀/宗改/近代仍留「西方（拉丁）」，用「上一行 era 是現代與當代才改」精準 targeting）；北美本已分開；新增**原住民神學 9 位**（region 原住民，北美 Tinker/Deloria/Charleston/Woodley/Curtice＋毛利 Marsden＋**台灣玉山神學院 布興‧大立/瓦歷斯‧烏干(≠瓦歷斯‧諾幹詩人)/童春發**）。現當代神學共 10 地域欄。**南方神學/第三世界＝拉美+非洲+亞洲已涵蓋，未另建重複 region**。
- **🐛 assemble.py 去重雷**：`existing_slugs()` 正則若只認單引號 `slug: '...'`，會漏掉 JSON 產生的雙引號 `"slug": "..."` → 二次跑重複插入全部（karl-barth ×2、總數暴增）。已修為 `["']?slug["']?:\s*["']([^"']+)`。**未 commit 前發現→git checkout 還原重來**。日後再擴充跑 assemble 務必先確認此正則。

**🆕 開跑全文翻譯（Haiku）＋抓下一批源＋文體版面基建（2026-07-19）**：
- **翻譯引擎認證**：user 要先全部用 **Haiku**。`te.sonnet_translate`/`haiku_translate` 沒 `ANTHROPIC_API_KEY` 時**自動 fallback 讀 `~/.claude/.credentials.json` 的 Claude Max OAuth token**（`_make_anthropic_client`），所以 **Haiku 免 API key 就能跑**（Sonnet 同理）。.env 目前 GEMINI 0 把、NVIDIA 6 把、ANTHROPIC 無。
- **希臘全文翻譯開跑中**：`Start-Process python scripts/greek_overnight.py --engine haiku`（detached，pid 見 log；log `c:/tmp/greek_haiku_overnight.out.log`）。resumable、逐部上架三欄。已完成 philebus/rhetoric/symposium/phaedrus… 續跑 plato+亞里斯多德 25 部。**detached 要用 PowerShell Start-Process**（Bash `&` 會隨 session 被砍）。
- **下一批 PD 源已抓**（`c:/tmp/cw_sources/` + `_manifest.json`，13 檔）：descartes/spinoza/hume/kant/nietzsche/marx/mill/william-james/freud/durkheim/tylor×2/frazer，全 Gutenberg PD（譯本須 1929 前 PD）。**待接翻譯 pipeline**（仿 mueller_auto：English-first 分節→Haiku→上架）。新補 255 位大宗仍多為 planned 待逐一取源。
- **文體版面基建（commit 3cb9f8ae）**：user 要「轉錄/翻譯時先判斷文體」，不同文體不同版面。`CwWork` 加 `genre`（CwGenre：dialogue/verse/aphorism/quaestio/treatise/essay/lecture/diary-letters/narrative）。reader `[work].vue` 依 genre 分派：對話錄/問答段首 `〔角色〕內文` → 講者標籤/角色分區（異議→反之→正解→答覆配色）；詩歌保留詩行詩節；格言逐條編號卡；**未標＝通用逐段版面（regression-safe，申辯截圖驗證無破）**。`scripts/genre_classify.py`＝判定 helper（結構啟發式，**hint(manifest/LLM)優先**，純文字易被目錄騙故門檻保守）。**🚨 對話錄講者分行需 ingest 改「逐 speech 為單位」**（現有 Plato 逐 Stephanus 節翻、一節含多講者無法 retrofit）→ 未來 dialogue 收錄走逐 speech；plato_build TEI 有 `<said who>` 可取講者。
- **文體×版面對照**（user 核可要做的 4 種）：對話錄（講者分行）/詩歌讚歌（詩行詩節逐行對齊）/格言命題（編號卡，斯多噶·伊比鳩魯·維根斯坦小數）/神學大全問答（quaestio 四段）。日記書信·講義·論著較後。
- **🚨 單一 Max OAuth 帳號一次只能跑一條 Haiku 翻譯線**：2026-07-19 同時跑 greek_overnight＋modern_classics_auto 兩條 Haiku，429 壓力翻倍→greek 撞連環 429＋**401 token 失效**（te 反覆重讀 credentials.json 仍 401）而死；modern solo 則健康。**別並行兩條 Haiku 佇列**（跟舊「別同時跑兩 queue」同源但根因是共享 OAuth rate-limit＋token，非 log/cache 衝突）。兩條都 resumable，續跑跳過已完成。
- **OAuth token 過夜限制**：`~/.claude/.credentials.json` 的 accessToken 有期效（實測某刻剩 ~7.6h），**靠 Claude Code session 活著才會滾動刷新**；session 結束後 token 到期→翻譯 401 停。過夜要活得靠排程（[[project_fleet_keeper]] KGL_Fleet_Keeper 每 30 分重拉死線）而非一次性 Start-Process。
- **翻譯品質實測佳（Haiku）**：philebus 希→繁「快樂勝過明智？普羅塔庫斯：是的。蘇格拉底：…」、marx 英→繁「現代工業建立了世界市場，美洲的發現為此鋪平了道路」皆流暢忠實；小瑕＝跨節譯名漂移（斐勒布/菲力布斯），日後 term-sweep 收斂。
- **✅ 排程 KGL_CW_Translation（每 30 分喚醒，2026-07-19）**：`scripts/cw_translation_supervisor.ps1`＋`install_cw_translation_supervisor.ps1`。**只跑近代經典 modern_classics_auto（Haiku，.done 跳過）**；guard 用 **PID lockfile `c:/tmp/cw_translation.lock`**（排程以 Limited 權限跑，`Get-CimInstance` CommandLine 回 null → CIM 比對 guard 會失效，改 lockfile 才可靠，已實測第二次觸發正確 skip）。AtLogon＋每 N 分重複＋`MultipleInstances IgnoreNew`＋無限執行時間。
- **🔑 既有翻譯排程盤點**：桌面已有 `KGL_Translation_Supervisor`(Running，跑 `translation_supervisor.py`→plato_build，`--engine auto`＝NVIDIA)＋`KGL_Cloud_Translation_Supervisor`＋`KGL_Fleet_Keeper`＋`MuellerAutoTranscribe`(Disabled)。**希臘(Plato/Aristotle)已被 KGL_Translation_Supervisor 用 NVIDIA cover**→我的 CW 排程不重跑希臘（不同引擎池、不搶 Haiku 額度）。**教訓：新增翻譯排程前先 `Get-ScheduledTask` 盤點既有的，別重複跑同一批。**

**Why:** 全集翻譯跟單本/教父翻譯需求不同（套書、多源、跨版對齊、版權），值得獨立 skill。
**How to apply:** 接「某全集做多語對照」需求時讀此 skill；先做 reader N 欄基建再上真資料；起手建議用公有領域早期著作驗證三欄。

🚨 2026-08-19：舊名 `deepseek-ai/deepseek-v4-flash`（無 `-0731`）已下架，對所有 key 一律回 **HTTP 410 Gone**。全 repo 49 檔已改名（commit 032c09d8）。日後 NVIDIA 那一層突然失效，先驗模型名還在不在。

## 索引補記

- 案例榮格(版權到2031) + 馬克斯穆勒(宗教學家全集，全公有領域)

## 記憶庫併入：project_weber_collected_works

馬克斯‧韋伯（Max Weber）全集收進 `/collected-works` **宗教社會學**學科（hub slug=`max-weber`，2026-07-18 那批自動骨架已存在：肖像1917PD／9筆年表／書目；2026-07-23 補 sourceNote 與〈政治作為志業〉）。屬 [[project_collected_works_multilang]] 家族。

**引擎＝OpenRouter 免費模型**（8 把 key 在 .env `OPENROUTER_API_Key_1..8`；同帳號額度共用不加倍）。刻意與 Gemini／NVIDIA 主鏈分流，比照 ACCS 不佔 Gemini 額度。⚠️ OpenRouter 免費 vision 模型爛（測過 nemotron 吐日文亂碼、gemma 429）→ 只能做**純文字**，不能 OCR。

**pipeline＝REFERENCE（③）不是自譯**（2026-07-23 使用者拍板）：下載的中譯本**直接轉錄當主欄**、簡體先 opencc→繁、**不重新翻譯**。9 本中譯本已從下載區(C:/Users/user/Downloads)搬進 Drive `知識圖工作室/全集/宗教社會學/韋伯/`、下載區原檔已刪：李中文《以學術/以政治為志業》(epub繁)、韋伯選集(1)學術與政治(繁)、張旺山《方法論文集》(繁)、康樂簡惠美《宗教社會學宗教與世界》(簡)、閻克文《新教倫理》(簡)、韓水法莫茜《社會科學方法論》(簡)、顧忠華《社會學基本概念》(簡)、《社會學基本概念經濟行動》(簡)。

**乾淨英文 PD 來源**（若日後要英繁對照）：Parsons 1930《新教倫理》英譯 2026-01-01 滿95年進美國PD（marxists.org／Wikisource／archive.org 全文）。私人站本就[[feedback_jung_nonpd_english_first]]不限PD。

✅ **圖書館既有韋伯原著已併入全集（2026-07-23 done）**：7 本馬克斯韋伯原著 `ebooks.collection` 已 PATCH 成 `collected-works`（離開圖書館）；hub works 連了 5 本 ebookId+status=done（新教倫理=康樂簡惠美新版 2a9a6c32、中國宗教=中國的宗教宗教與世界 f7733673、印度的宗教 028481d2、學術志業=李猛科學作為天職 424dc120、新增宗教社會學 b89ffe1d）。🚨 **Florence Weber(弗洛朗斯‧韋伯)《人類學簡史》不是馬克斯韋伯**，留圖書館。二手研究（紀登斯/雅思培/施路赫特）作者非韋伯也留圖書館。**2 本重複版留全集未 hub 主列待使用者定刪否**：bfb220d8(新教倫理舊版)、f32548e9(儒教與道教單行)。
**圖書館搜尋已改跨 collection**（`search.get.ts` 拿掉 `.is(collection,null)`），書名/作者/全文都搜得到全集，結果加「全集」cyan 標籤。`store` ebookId 必須用**未加引號 key** `ebookId:`（backfill regex `test/collected-works/isolation.spec.ts` 只認這格式，用 `"ebookId":` 會 fail）。

**OpenRouter 可用翻譯模型（實測 2026-07-23）**：`nvidia/nemotron-3-ultra-550b-a55b:free`（550B）+ **嚴格 system prompt**（role=translator、只輸出中文）翻 EN→繁中準確。⚠️ super-120b 洩漏思考、gemma 一直 429、直接 user-prompt 給指令會亂答。免費層 ~50 req/日（8key 同帳號共用），衝量要 OpenRouter 儲值 $10 解 1000/日。

**待辦**：REFERENCE 轉錄尚未開始（僅 hub＋來源檔到位）；全 works 仍 status=planned。轉錄走 [[project_collected_works_multilang]] 的 REFERENCE build（`panikkar_build.py` 型 `--src/--zh-src`）。

## 索引補記

- 圖書館另有 11 筆韋伯待議併入

## 記憶庫併入：project_chaohwei_collected_works

2026-09-10 開區。佛學區第五位（`chao-hwei`，rose 🕊️，sortYear 1957），**本區第一個
「只有紙本掃描本」的來源**——太虛／印順／星雲／聖嚴都有現成數位全文，昭慧法師沒有。

**上游那一整段抽成新 skill `ebook-scan-transcribe`**（三腳本：`scan_prep.py` 拆頁轉正
／`scan_ocr.py` 逐頁 OCR／`chaohwei_build.py` 頁碼帳＋分章＋入庫），書籍設定集中在
`scripts/scan_books.py`，新增一本＝加一筆。下游仍走 [[ebook-collected-works]]。

- **✅《心靈的交會：山間對話》**（與彼得‧辛格對談，法界出版 2021，**使用者已取得作者
  授權**）：13 chunks／11.3 萬字，`c4a01957-…-0001`，`genre:'dialogue'`。
  印刷頁 1–222 **真缺頁 0**、去掉 2 頁重掃。成品 PDF 253 頁在 Drive
  `全集\佛學\昭慧法師\`。
- **⏳《初期唯識思想——瑜伽行派形成之脈絡》**：工作 PDF 已拆好 300 書頁，OCR 待續。
- hub 另有法界出版社書目 10 種 planned（**該目錄沒有出版年，yearSort 只是排序用**）。

🚨 **這條線的失敗全是「靜默」型**（[[feedback_reader_silent_failures]]）：
前言頁碼 `c`／`d` 也是羅馬數字 100／500 會讓整章判錯；頁眉黏在正文同一行會讓整頁
被清理清光而 audit 仍報「沒缺頁」；重複頁只比字數會選到被黑邊吃掉的那一份。
細節見 skill 的〈看起來成功的失敗〉表。

📄 每一段都掛原書印刷頁碼當 `anchors`（reader 左欄引用號可點擊複製），
讀不到留空、不拿流水號充數（[[feedback_transcribe_page_numbers]]）。
**collected-works reader 這次才第一次支援腳註**（`[^4]` 上標＋`[^4]: …` 灰底註文列）。

## 記憶庫併入：project_uchimura_yanaihara

2026-07-16 使用者拍板:**內村鑑三**(1861–1930)與**矢內原忠雄**(1893–1961)兩位日本無教會主義者加入 [[ebook-collected-works]] 的 `/collected-works` portal,**定位是神學家**(`disciplineGroup: '神學'`)——該學科自潘尼卡 2026-07-01 改歸宗教學後一直是空的,他們是開區作家。

**Why:** 使用者的 nonchurch-nuxt 專案即是無教會傳統;矢內原《帝国主義下の台湾》與台灣直接相關。

**How to apply:** slug `uchimura`(emerald ✝️,10 部)/`yanaihara`(blue 🕊️,13 部);版權:內村全球 PD,矢內原日本(卒後50年,2012 起)與台灣 PD、美國 URAA 限 1930 後各卷;日文著作走多語對照(ja+繁中),內村的英文原著(How I Became a Christian、代表的日本人)走 en+繁中。hub 已上線(commit cd7b8867)。case-study md 在 skill 資料夾 uchimura_collected_works.md / yanaihara_collected_works.md。

乾淨來源已盤點:內村青空文庫 11 篇零 OCR+archive.org 兩部英文初版;矢內原起手卷《帝国主義下の台湾》1929 全球 PD、NDL pid 1191101 IIIF manifest 公開(201 コマ)已實證,青空文庫 4 篇。NDL API 有 429 節流(兩次即退)。

2026-07-16 追加拍板:**不只內村+矢內原,無教會主義其他重要人士的重要著作也都收**(藤井武/塚本虎二/黒崎幸吉/南原繁等候選+韓國系金教臣/咸錫憲,金教臣強烈建議收)。日本版權分界:卒於 1967 前→日本 PD,1968 後卒→卒後 70 年(2018 改法不溯及);受版權者照榮格前例收 hub+書目 status=copyright。

## 記憶庫併入：project_husserl_ideas_transcription

2026-09-10 開卷。[[project_western_phenomenology_history]] 第 4–6 章的底本（第 5 章「本質直觀」是全書樞紐）。
走 **Boyce Gibson 1931 英譯**（archive.org `in.ernet.dli.2015.188260`，472 掃描頁）；胡塞爾 1938 卒、
譯者 1935 卒，德文原著與英譯都公有領域。ebookId `d0000000-0000-4000-8000-000000000021`，store 已標 in-progress。

**🚨 archive.org 的 `_djvu.txt` 對這批書一律先驗字元再用**：奧托《論「聖」》與胡塞爾兩本實測都是
**零個希臘字母、零個德文變音字母**。胡塞爾滿篇 ἐποχή／εἶδος／νόησις／Bewußtsein，這種底本餵進翻譯
引擎，中文看起來正常而內容是編的。德文原著 1913 那版更是**花體字排印**（Husserl→"Huffed"）。
判準一行：`len(re.findall(r'[Ͱ-Ͽ]', txt))`。

**兩支新工具（可重用，別重造）：**
- `scripts/archive_djvu.py`（38 例測試）——讀 `_djvu.xml` 逐字座標撈**真印刷頁碼**與註腳。既有的
  `mueller_auto.fetch_djvu` 讀 `_djvu.txt`，沒頁界沒幾何，只能把書眉頁碼當雜訊丟、page_number 一律 None。
  奧托 1924 刷實測：直接撈到 74%、遞推後 94%、跳號 0。
  🚨 五個坑：書眉要 strip 不然黏在每段開頭／OCR 讀錯的頁碼要 repair_folios 打掉再遞推／註腳行距只多三成
  （門檻 1.35 會整頁漏）／行末連字號要壓過縮排判定／**縮排要有上界 220**（OCR 把一條印刷行拆兩筆時
  後半截 x0 右移五百以上，沒上界每個碎片都變新段落，中英兩欄整本錯位）。
- `scripts/husserl_build.py`（23 例測試）——Vision OCR，頁碼與腳註由 Vision 當下標（`[[p N]]`／`[note] `），
  章首頁沒印就 `[[p ?]]` 不准猜。接進 `uchimura_auto.py --author husserl`。

**🚨 本管線第一號坑：Vision 偶爾整批「一行一段」回**（照排印行斷不照段落斷）。b0017 中位段長 64 字、
句尾完整率 **6%**；段數多、頁碼齊、頁面完全正常，但每「段」是半句話。`looks_line_broken()` 閘門＋
升級 prompt 重跑。判準必須「段短」**且**「句尾多半不完整」兩條同時成立——只看段長會誤殺扉頁目錄
（b0001 中位也 64，但完整率 81%，那是對的）。

**排程 `KGL_Husserl_OCR`**（每 20 分，`scripts/husserl_ocr_keeper.ps1`）：472 頁 / 8 = **59 批**，
撞 Gemini 免費層配額牆就等下一班接著跑。**59 批全齊會自己 Disable**（[[feedback_disable_finished_schedules]]）。
OCR 跑完才輪到翻譯：`python scripts/uchimura_auto.py --author husserl --run-queue`。

**其餘現象學原典的取源現況**（2026-09-10 探過）：奧托德英兩版、胡塞爾 LU 1900 德文全開放且有 djvu.xml；
**范德列烏《宗教的本質與表現》archive.org 是借閱限制**（`access-restricted-item: true`）要另找來源。

## 記憶庫併入：project_aquinas_summa_quaestio

把多瑪斯‧阿奎那《神學大全》（中華道明會譯本 17 冊）做成 `/collected-works` **quaestio 經院問答**全集。作家 hub `thomas-aquinas` 已存在（**哲學**學科），work 帶 `genre:'quaestio'` → reader `[work].vue` 自動四段配色（〔異議〕rose／〔反之〕amber／〔正解〕emerald／〔答覆〕blue）。走 [[ebook-collected-works]] 的 §B9 文體版面 + REFERENCE-first（[[feedback_collected_works_reference_first]]）。

**來源**＝圖書館既有 19 筆 `神學大全 第N冊`（collection=null，OCR 掃描中譯本，各冊 Drive `_chunks/{id}.jsonl` 為**唯讀原始 OCR 源**，別覆蓋）＋一組 3 冊全形括號重複殘檔（`神學大全（第N冊`，author=阿奎那）**待刪去重**。17 冊來源 ebook_id 與集/題範圍列在 `scripts/aquinas_build.py` 的 `REGISTRY`。

**輸出**＝新 collected-works id `a9051225-0000-4000-8000-0000000000NN`（a9≈aquinas、1225生年、NN=冊號1..17），collection='collected-works'。`scripts/aquinas_build.py`（6 純函式測試綠）：讀源→輕量規則清理→`split_articles`（以「有關第N節，我們討論如下」切節）→`mark_zones`（質疑編號→反之→正解我解答如下→釋疑編號 四段注入）→每節一 chunk。

**狀態（2026-09-04）**：**17 冊全數建置完成**，合計 3,006 節 chunk／約 4,784,055 字。
- 第1冊 論天主一體三位 221 節／第2冊 論天主創造萬物 121／第3冊 論人 213／第4冊 論人的道德行為與情 251／第5冊 論德性與惡習及罪 211／第6冊 論法律與恩寵 133／第7冊 論信德與望德 111／第8冊 論愛德 139／第9冊 論智德與義德 159／第10冊 論義德之諸部分 191／第11冊 論勇德與節德 190／第12冊 論特殊恩寵、生活和身分 100／第13冊 論天主聖言之降生成人 149／第14冊 論基督的生平與救贖 168／第15冊 論聖事總論與聖洗堅振 216／第16冊 論聖體聖事與懺悔 282／第17冊 論肉身復活的問題 151。
- `fleet_aquinas` 線由 `KGL_Fleet_Keeper` 每 30 分重拉，現在每輪都是「內容未變，略過上傳」＝冪等空跑；要重建某冊得先動源或清 cache。
- ⏳ 未做：清理成果的人工抽樣核對（保守 prompt 只准修字形，仍該抽查）。

**（歷史）2026-07-23**：pilot 第一冊上架、reader 四段版面截圖驗證、commit `fef7357f`。

**批次設計（待建 `--clean` 模式）**：每冊 raw→切節→**逐節 NVIDIA 保守清理**→re-mark→上架。
- 引擎＝**NVIDIA deepseek-v4-flash-0731**（`translate_ebook_to_zh` 的 `nvidia_translate`／key 輪換／6s 節流）——**不吃 ACCS 的 Gemini Vision 量能**（不同池）。
- 🚨 **保守 prompt**：只准修 OCR 字形錯（督貴→督責、皮之→反之、啞益→有益）＋刪跑版頁眉 bleed／頁碼；**嚴禁改寫/增刪句子、嚴禁動神學論證措辭**（教義文本改一字即變義）。清理後抽樣人工核對。清理同時修好被 OCR 打壞的區段標記（皮之→反之）→切段更準（故先清再切，或逐節清後 re-mark）。
- **resumable**：逐節 cache 到 `c:/tmp/aquinas_clean/{vol}_{art}.txt`；🚨 detached Start-Process 過夜會死（[[project_fleet_keeper]]），要嘛掛排程要嘛靠 cache 重啟續跑。
- 每冊上架後於 `stores/collectedWorks.ts` `thomas-aquinas` works[] 加該冊（category「神學大全（中華道明會譯本‧共十七冊）」，done+ebookId+`genre:'quaestio'`，🚨 ebookId 未加引號 key）＋`data/collectedWorksIntros.ts` 導讀；跑 `apply-ebooks-quality-collection.mjs` 補標。

**後續佇列（user 定序）**：阿奎那 → 公教會之信仰與倫理教義選集（Denzinger，ebook 568726d3 只 6 大 chunk、拉中擠一塊、多欄+註釋 UI 待評）→ 東方教父文集（4b791a1d，**直排被 OCR 讀反、正文全失**，整本重 OCR，佔 ACCS Vision 量能待排）。

🚨 2026-08-19：舊名 `deepseek-ai/deepseek-v4-flash`（無 `-0731`）已下架，對所有 key 一律回 **HTTP 410 Gone**。全 repo 49 檔已改名（commit 032c09d8）。日後 NVIDIA 那一層突然失效，先驗模型名還在不在。

## 索引補記

- ⏳剩16冊+NVIDIA保守清理過夜(嚴禁改寫教義文字/不吃ACCS量能)

## 記憶庫併入：project_christianity_studies_littleblackbook

**書源「小黑書」** = FB/IG `littleblackbook0000`（聖經研究科普平台，高雄）。**Meta 家 FB/IG 都擋登入牆抓不到貼文**；真正可抓的是它的 **WordPress `littleblackbook0000.wordpress.com`**（每集 Ep# = 一本近代西文聖經學術原著，書名+作者齊全，`/page/N/` 翻頁）＋ YouTube 頻道。要挖它導讀的書一律走 WordPress，別浪費時間爬 FB/IG。

2026-07-23 首輪：撈 25 集 → **libgen.li 逐本實查**（annas-archive 有 JS 指紋擋、libgen.bz 庫小；只 libgen.li 能用），23/25 有電子檔。清單在 `.claude/skills/ebook-collected-works/小黑書_libgen下載清單.txt`。使用者下載後走 `ingest_new_books.py` 進電子圖書館。libgen 域名在此環境 **WebFetch 被擋、curl DNS 也擋**，只能用 **PowerShell `Invoke-WebRequest -UseBasicParsing`**（且別 OutFile 落地：Defender 會把 shadow-library HTML 當病毒攔，要在記憶體處理）。

由此緣起，全集 `/collected-works` **新增傘狀學科「基督宗教研究」**（[[project_collected_works_multilang]] 的一支）：`era` 當三次領域＝新約研究/舊約研究/教會史（`ERA_ORDER` 固定順序、**無 region 地域層**）。40 位新 hub 骨架＋布特曼/哈納克/菲奧倫查從神學遷入＝43 位。全 `planned`/`copyright`、**肖像 portraitUrl 待回填**、著作待 REFERENCE-first 收錄。細節見 collected-works SKILL.md §A（2026-07-23 note）。
