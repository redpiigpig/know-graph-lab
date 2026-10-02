---
name: scripture-near-east
description: 古近東大藏經（/near-east）的體例與維護 —— 埃及／蘇美／阿卡德（巴比倫與亞述）／赫梯與胡里特／烏加里特／迦南與亞蘭／阿拉伯／埃蘭與高地八藏＋外部記述附錄。按文明分藏（先看文字、再看神廟體系），每藏止於其文字死亡，存世狀態多一級「綴合本」並分成書與抄本兩個年代，編號只用學界標準（ETCSL／CTH／KTU／KAI／館藏號）。Use when 要新增或修改古近東條目、決定某份材料歸哪一藏、補編號、補三欄原文英譯中譯、改 /near-east 頁面，或使用者提到「古近東」「埃及學」「亞述學」「蘇美」「巴比倫」「赫梯」「烏加里特」「腓尼基」「吉爾伽美什」「亡靈書」「埃努瑪‧埃利什」。
---

> 🏺 與 [[hellenika-canon]]（希臘羅馬）、[[scripture-zoroastrian]]（祆教）、[[scripture-manichaean]]（摩尼教）
> 並列於 `/scripture-canon` 宗教層，**體例三家都不同，不互相套用**。

> 🚨 截圖任一邊 >2000px 會炸 session。

## 0. 位置與檔案

`/scripture-canon` → 🏺 古近東宗教 → `/scripture-canon/near-east` → `/near-east`（＋`/near-east/about` 凡例）。

| 檔 | 作用 |
|---|---|
| `data/near-east/types.ts` | 型別、六級存世狀態、三欄狀態。檔頭三條是體例，動結構前先讀 |
| `data/near-east/{egypt,sumer,akkad,anatolia,ugarit,levant,arabia,highlands,testimonia}.ts` | 九藏書目 |
| `data/near-east/index.ts` | `CANONS`、`TERMINUS`、slug 索引（重複擲錯）、統計、搜尋、`relatedOf()` |
| `data/near-east/glossary-candidates.md` | 待定譯名【提】清單 |
| `pages/near-east/index.vue`／`[canon]/[volume].vue`／`about.vue` | 總索引／卷頁（條目以 `#slug` 錨點定位）／凡例 |
| `pages/scripture-canon/near-east.vue` | 宗教層入口 |
| `test/near-east.spec.ts` | 14 條，釘住下面的規矩 |

**現況（2026-10-02 建置）**：9 藏 52 卷約 380 種，**只有書目**。三欄正文尚未上架，`intro` 欄全空。

## 1. 體例（四條，改動前先讀）

1. **這不是一個宗教，是七八個。** 按文明分藏，不調和、不比附，不編「近東神話」綜合版。相似處只用 `seealso`。
2. **分藏先看文字、再看神廟體系**，衝突時以神廟體系為準。例外表在 `about.vue` 第二節（胡里特讚歌出土於烏加里特但歸赫梯與胡里特藏、恩赫杜安娜是阿卡德公主但作品歸蘇美藏……）。新例外要補進那張表。
3. **每藏止於它的文字死亡**，沒有統一下限。每藏的 `terminus` 欄寫依據，測試釘住不得為空。
4. **泥板不是書。** 狀態六級：`whole`／`composite`（綴合本，**不設 status 時的預設**）／`fragment`／`inscription`／`lost-cited`／`lost-listed`；佚書必填 `via`（測試釘住）。年代分 `era`（成書）與 `copies`（現存抄本），蘇美文學兩者差兩三百年，不可混。

### 編號：只用學界標準，查不到留空

| 藏 | 編號 | 核對狀態 |
|---|---|---|
| 蘇美 | ETCSL 分類號 | ✅ 2026-10-02 逐條對過 etcsl.orinst.ox.ac.uk（目錄頁 `cgi-bin/etcsl.cgi?text=c.1*` 可抓） |
| 赫梯 | CTH | ✅ 逐條對過 `hethport.net/CTH/`（舊網址 hethport.uni-wuerzburg.de 已轉走） |
| 烏加里特 | KTU 1.x | 憑 KTU 第三版記憶，未線上核對 |
| 迦南／亞蘭 | KAI、TAD | 憑記憶，未線上核對 |
| 埃及 | 館藏號（BM EA、P. Berlin…）、PT／CT／BD | 憑記憶，未線上核對 |
| 阿卡德 | 館藏號、SAA、ARM、BWL 頁碼 | 憑記憶，未線上核對 |

🚨 **自編號碼比沒有號碼更糟**——版面看起來完全正常，但無法外部查證（同 [[feedback_pdf_page_number]]、摩尼教 skill §1 第四條）。卷頁左側序號只是版面定位，不可當引用號。測試釘住蘇美必為 `ETCSL`、赫梯必為 `CTH`/`RS`、烏加里特必為 `KTU 1.`。

### 聖經對位（`bible` 欄）只是互見

不是收錄或排序的理由。希伯來聖經本身不入藏（屬猶太教，規劃中）；以色列與猶大**銘文**收在迦南與亞蘭藏，測試釘住古希伯來語條目只能是銘文或殘篇。

### 跨典藏互見（`xref` 欄，純文字）

- 基督教大藏經‧前藏已收埃努瑪‧埃利什、吉爾伽美什、阿特拉哈西斯、亡靈書、阿頓頌、烏加列祭文等——**不動那邊資料**，只在本藏標 `xref`。
- 希臘羅馬大藏經的普魯塔克、琉善、達馬斯基烏斯、楊布里科斯，在那邊是本經、在本藏附錄是外部證詞。
- 波斯宗教全歸祆教經典。

## 2. 譯名（使用者 2026-10-02 定）

- **短譯**：省去只譯子音尾的「爾」「斯」——馬杜克（非馬爾杜克）。見 [[feedback_short_transliteration]]。
- **伊絲塔**（Ishtar，使用者先說伊斯塔隨即改定伊絲塔）。
- **例外：需要區別同名時保留「爾」**——神名 Ashur 作**亞述爾**，國名作亞述（使用者 10-02 定）。
- **一般譯名優先於聖經譯名**：烏爾、埃蘭、蘇薩、杜牧茲；**赫梯**（非西台，取其銜接聖經「赫人」）。見 [[feedback_general_over_biblical_names]]。
- 以上七條已回寫 `/translation-glossary`（`deities`／`place_names`），舊譯留在 `name_variants`。測試釘住資料裡不得出現舊譯。
- 詞庫沒有的新名先照短譯原則擬，列在 `glossary-candidates.md` 標【提】，**不自行寫進詞庫**（見 [[feedback_glossary_ancient_name_priority]]）。

## 3. 三欄取源（未實作，按可行度）

| 藏 | 原文 | 英譯 | 備註 |
|---|---|---|---|
| 蘇美 | ETCSL 轉寫 | ETCSL 散文譯本 | 最好做：同一站、同一編號、已對齊到行。非商業學術使用 |
| 阿卡德 | eBL、ORACC（CC BY-SA；SAAo 有新亞述全部） | ORACC 英譯；King 1902《創世七泥板》、Thompson 1928 吉爾伽美什等公有領域 | |
| 埃及 | TLA《埃及語辭典》（CC BY-SA，轉寫＋德譯） | Budge（公有領域，但譯法過時須標註） | |
| 赫梯 | Hethitologie-Portal 轉寫 | 現代英譯全在版權內 | 英欄多半只能空 |
| 烏加里特 | 轉寫可得 | Smith、Wyatt 等在版權內 | 英欄多半只能空 |
| 迦南／亞蘭 | 轉寫可得 | Cooke 1903《北閃族銘文教本》公有領域 | |

中譯走站上引擎鏈（Gemini → NVIDIA → Haiku 救急，見 [[feedback_engine_nvidia_no_haiku]]）。動手前照 [[feedback_collected_works_reference_first]] 先查有無既有中譯本。
做完任何一篇正文，**回頭把該條的 `columns` 改成 `ready` 並在卷頁接上 reader 連結**——希臘羅馬大藏經曾經做完全文卻沒接書目，讀者走不到。

## 4. 加東西的流程

1. 過 §1 第二條定歸藏與卷；過 §1 第四條定狀態與兩個年代。
2. 編號：查得到標準編號才填，並在 §1 表格的「核對狀態」記一筆。
3. 譯名：先查詞庫，沒有就照 §2 擬並補進 `glossary-candidates.md`。
4. `npx vitest run test/near-east.spec.ts`；動到頁面再跑 `npx vue-tsc --noEmit -p .nuxt/tsconfig.json`。
5. 動到體例就同步 `pages/near-east/about.vue`。
6. commit 只加自己改的檔（[[feedback_commit_only_scripted_files]]）＋ push。

## 5. 待辦

1. **使用者定奪**：`glossary-candidates.md` 的短譯候選（尤其吉爾伽美什、烏納姆 vs 城名烏爾、比布魯斯 vs 前藏的比布洛斯）。
2. **補 `intro`**：100–200 字，照 [[hellenika-curate]] 的四要件。
3. **核對未線上驗證的編號**（KTU、KAI、館藏號）。
4. **三欄正文**：建議從蘇美藏 ETCSL 開始（原文英譯同源、編號已核）。
5. ✅ 姊妹工作（2026-10-02 完成）：`/research-data/top-papers/near-east-archaeology`——研究史策展 501 筆＋OpenAlex 引用前 500 篇，
   OA 全文 15 篇與校內下載 CSV 在 Drive `電子圖書館\歷史學\中央界域史\近東考古引用前五百期刊論文\`。見 [[research-data-top-papers]]。
   策展清單的專著尚未進 z-lib 獵表、archive.org 尚未掃（照該 skill「清單之後怎麼拿到」走）。
