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

**現況（2026-10-02）**：9 藏 52 卷約 380 種。蘇美藏 69 條已有轉寫＋英譯（ETCSL），其餘各藏只有書目；中譯全空，`intro` 欄全空。

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
- **已有通行譯法者照通行**（使用者 10-02 定：吉爾伽美什、涅伽爾、尼努爾塔、庫瑪爾比、帕爾米拉……全表見 `glossary-candidates.md`，已入詞庫）。短譯只用在**沒有通行譯名**的新名上。
- 詞庫沒有、也沒有通行譯法的新名才照短譯擬，列在 `glossary-candidates.md` 標【提】，**不自行寫進詞庫**（見 [[feedback_glossary_ancient_name_priority]]）。

## 3. 三欄取源

### 現況（2026-10-02）

| 路 | 涵蓋 | 狀態 |
|---|---|---|
| ① 線上開放語料 | 蘇美藏 69 條（ETCSL 轉寫＋英譯） | ✅ **已上架**，5,429 段，`/near-east/text/<slug>` |
| ① 線上開放語料 | 新亞述先知 SAA 9（11 篇）、王子冥府夢 SAA 3 32 | ✅ 已上架（`scripts/near_east_oracc.py`）。其餘 ORACC 專案（RINAP 以撒哈頓等）未做。🚨 ORACC 的 json 下載包**只有轉寫**，英譯要逐篇抓 `oracc.museum.upenn.edu/<project>/<P號>/html` |
| ② 公有領域舊譯 | 古騰堡九部（Thompson 吉爾伽美什 1928、Budge 亡靈書／創世傳說／諸神傳說、King 1918、Smith 1876、Erman 1927 英譯、Harper 1901、Wilson 1901） | ✅ 已下載到 Drive `經典對照與註釋\古近東大藏經－公有領域英譯底本\`（txt＋epub），**尚未切段對齊** |
| ③ 現代標準譯本 | 赫梯、烏加里特、埃及、阿卡德、ANET、COS 與各卷專門校譯本共 75 部 | ✅ **66 部到手**（10-03；LibGen 自動＋人工挑、z-lib 四帳號），落 z-lib/ 收件夾由每日入庫上 Drive。缺 9 部見獵表 `data/zlib-wanted/near-east-translations.jsonl` 未下載者 |
| ② 補 | archive.org 1930 年前公有領域英譯與校本 37 部＋分卷（Breasted、Luckenbill、King、Thompson、Budge、Griffith、Cowley、Cory…） | ✅ 同存 Drive 英譯底本夾（104 PDF／2 GB，含同書不同掃描本）|

🚨 sacred-texts.com 對腳本一律回 403，公有領域舊譯改走古騰堡。赫梯與烏加里特**沒有**公有領域英譯，只能靠第③路。

### 正文資料形狀

- `data/near-east/sources/text/<slug>.json`：`{slug, source, siglum, source_url, license, compositions:[{num, title_en, segments:[{ref, orig, orig_lines, en, zh?}]}]}`
- 合集條目（戀歌集、諺語集、王頌集）一條含多篇 composition，reader 以篇名分節。
- `data/near-east/sources/manifest.json` 由取源腳本寫；書目頁的三欄色塊與「可點進 reader」都以它為準（`effectiveColumns()`／`hasText()`），**不要手改書目的 columns 欄來標「已上架」**。
- `data/near-east/sources/index.ts` 用 `import.meta.glob` **非 eager** 惰性載入。

### ETCSL 取源（`scripts/near_east_etcsl.py`，不用 LLM）

對齊鍵是 ETCSL 自己的：英譯頁每段 `<a name='t111.p3'>`，轉寫頁每行帶 `lineid=t111.p3` 指回所屬段。段號照抄英譯段的行號範圍（「11–16」）。快取 `output/near-east/etcsl/`，重跑只補沒抓過的。
每條印「轉寫 X/Y 行（Y＝頁上實際行數）、無轉寫段、無歸屬行」，**任何一個不是 0 都要查**。踩過的四個坑：

1. **ETCSL 不論 `charenc` 參數，轉寫一律輸出 ASCII**：c＝š、j＝ĝ、h＝ḫ。腳本整欄轉回；英譯欄不可套用。
2. **哀歌的段落標記（「第一 kirugu」）在 `<p>` 與 `<a>` 之間夾 `&nbsp;`**：第一版沒認到，烏爾哀歌 21 行轉寫無歸屬，十四條出現「無歸屬行」。
3. **合集範圍展開成 0 篇卻不報錯**：分類頁的 regex 寫錯，五個合集默默沒有正文。另外範圍要取兩端編號的**共同前綴**去抓分類頁（6.1.01–6.2.5 → `c.6*`），只取前兩節會漏掉跨節的那一半。
4. **古代書目（0.x）只有轉寫頁，行號沒有連結**：第一版用 enumerate 自編流水號，還把網頁其他表格的格子算進去（537 段，實為 508）。改讀原頁行號並以頁上行數驗。

## 4. 加東西的流程

1. 過 §1 第二條定歸藏與卷；過 §1 第四條定狀態與兩個年代。
2. 編號：查得到標準編號才填，並在 §1 表格的「核對狀態」記一筆。
3. 譯名：先查詞庫，沒有就照 §2 擬並補進 `glossary-candidates.md`。
4. `npx vitest run test/near-east.spec.ts`；動到頁面再跑 `npx vue-tsc --noEmit -p .nuxt/tsconfig.json`。
5. 動到體例就同步 `pages/near-east/about.vue`。
6. commit 只加自己改的檔（[[feedback_commit_only_scripted_files]]）＋ push。

## 5. 待辦

1. ✅ 譯名候選 2026-10-02 全部定案（照通行），已入詞庫。
2. **補 `intro`**：100–200 字，照 [[hellenika-curate]] 的四要件。
3. **核對未線上驗證的編號**（KTU、KAI、館藏號）。
4. **三欄正文**：蘇美藏 ✅；下一步 ORACC（新亞述）→ 古騰堡舊譯切段（埃努瑪‧埃利什、吉爾伽美什、亡靈書）→ 等 z-lib 到書。中譯全藏未動。
5. ✅ 姊妹工作（2026-10-02 完成）：`/research-data/top-papers/near-east-archaeology`——研究史策展 501 筆＋OpenAlex 引用前 500 篇，
   OA 全文 15 篇與校內下載 CSV 在 Drive `電子圖書館\歷史學\中央界域史\近東考古引用前五百期刊論文\`。見 [[research-data-top-papers]]。
   策展清單的專著尚未進 z-lib 獵表、archive.org 尚未掃（照該 skill「清單之後怎麼拿到」走）。
