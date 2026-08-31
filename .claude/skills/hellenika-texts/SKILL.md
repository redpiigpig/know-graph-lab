---
name: hellenika-texts
description: 希臘羅馬大藏經（/hellenika）的**文獻**全文取源與逐段對照 —— 與 [[hellenika-epigraphy]]（石頭上的東西）分工，本 skill 管「書上的東西」：赫西俄德《神譜》、荷馬詩頌、《俄耳甫斯讚歌》、荷馬兩部史詩這類傳世文本，取希臘文原文與公有領域英譯，按詩行號切段，再逐段譯成繁中，出成 reader 的三欄對照。含 Perseus 標準 TEI 的抓法、沒有 TEI 時改走 Wikisource 的作法、史詩的分卷與散文里程碑、切段對齊原則、各篇取源現況。Use when 要新增一篇文獻的全文轉錄、要補某篇的中譯、要處理沒有公有領域英譯的篇目、要調切段粒度、或使用者說「把某某書的原文放上去」。體例底層見 [[hellenika-canon]]。
---

# 希臘羅馬大藏經 — 文獻全文取源與逐段對照

書目卡只告訴讀者這部書存在。這個 skill 管的是**把書本身放上去**：原文一欄、
公有領域英譯一欄、我的繁中一欄，逐段對齊。

三支取源腳本的分工，記牢別走錯：

| 腳本 | 取什麼 | 切段單位 | 產物 |
|---|---|---|---|
| `hellenika_cgrn.py` | 祭儀規範銘文 | 石面行號 | `sources/cgrn/` |
| `hellenika_phi.py` | 其餘銘文與紙草 | 案號或石面行號 | `sources/phi/` |
| **`hellenika_text.py`** | **有 TEI 的傳世文獻** | **詩行號** | **`sources/text/`** |
| **`hellenika_orphic.py`** | **《俄耳甫斯讚歌》**（無 TEI） | **一首一段** | 同上 |

後兩支寫同一個 schema、落同一個目錄、走同一支翻譯腳本，差別只在**哪裡取原文**。
再遇到沒有 TEI 的篇目，照 `hellenika_orphic.py` 的樣子另寫取源函式即可，不要為它
另立一套 schema。

---

## 1. 取源：Perseus 標準 TEI，不走 API

🚨 **不要用 Scaife 的 CTS API**（`scaife-cts.perseus.org`）。2026-08-28 實測整個
API host 連不上（curl 回 000），而 reader 頁面是 JS 驅動的，抓下來沒有正文。

改抓上游的標準 TEI 原始檔：

```
https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/{群}/{作}/{urn}.xml
```

例：`data/tlg0020/tlg001/tlg0020.tlg001.perseus-grc2.xml` ＝ 赫西俄德《神譜》希臘文。

好處：公有領域、無節流、行號完整、不必解析 JS。

**版本後綴要試不要猜。** `perseus-eng1` 常常不存在而 `perseus-eng2` 存在
（《神譜》就是這樣）；`tlg0013.tlg001.perseus-eng1` 也是 404。腳本對 404 回 `None`
並印出「TEI 不存在」，不要當成程式壞掉。

---

## 2. 切段：以英譯的里程碑為邊界

希臘文 TEI 每行一個 `<l n="N">`；Evelyn-White 的英譯**每五行才下一個里程碑**
（`<l n="1">`、`<l n="5">`、`<l n="10">`…），中間是連續散文式的詩行。

所以切段邊界一律取**英譯的里程碑**，再把落在該區間的希臘文行併起來：

```
段 = 連續 4 個英譯里程碑（MILESTONES_PER_SEG）≈ 20 行
```

這樣兩欄的邊界永遠對得上。反過來若以希臘文行號切，會切在英譯句子中間，
出來就是半句對半句——那正是 [[feedback_reader_silent_failures]] 那類「印得出來
但配錯」的錯法。

英譯不存在時退回「每 5 行一個假里程碑」，並把 `pivot` 標成 `'none'`、填
`pivot_note`——與治癒銘文同一套處理（見 [[hellenika-epigraphy]] §11）。

**兩個例外，各有各的理由：**

- **散文英譯**（荷馬兩部史詩的 Murray Loeb 本）沒有 `<l>`，里程碑改埋成
  `<milestone unit="line">`。原則不變，只是里程碑換個抓法，見 §5b。
- **英譯根本沒有里程碑**（《俄耳甫斯讚歌》的 Taylor 1792，兩行壓成一行）時，
  這條原則失效。此時**不切段**：一首即一段，邊界取在篇界，見 §5a。
  短篇（10–30 行）可以這樣做，長篇不行——長篇沒有里程碑就得另想辦法，
  不要為了「有東西上架」而硬切。

---

## 3. 產物 schema

`data/hellenika/sources/text/{slug}.json`：

```jsonc
{
  "source": "perseus",
  "siglum": "Hes. Th.",          // 學界引用縮寫
  "slug": "theogony",
  "url": "…raw.githubusercontent…",
  "title_zh": "神譜", "title_en": "Theogony", "author": "赫西俄德",
  "volume": "A",                  // 所屬卷 key
  "licence": "…",
  "pivot": "perseus-eng",         // 'perseus-eng' ＝經由英譯；'none' ＝直譯自原文
  "pivot_note": null,
  "lines_total": 1022,
  "names": {},                    // 本篇專名定譯表，翻譯前先填
  "segments": [
    { "line_from": 1, "line_to": 19, "greek": "…", "en": "…", "zh": "" }
  ]
}
```

`zh` 一律先留空，翻譯是獨立的第二步。**取源與翻譯分開跑**，因為翻譯要吃
Gemini／NVIDIA／OpenRouter 的額度，而整夜驅動器
（`hellenika_overnight.py`）也在用同一批 key——兩邊同時跑必然互撞 429。

---

## 4. 🚨 整夜驅動器會把 `data/hellenika` 整個 git add

`hellenika_overnight.py` 的 commit 是 `git add data/hellenika`（無白名單）。
所以**驅動器在跑的時候，不要把半成品寫進 `data/hellenika/`**，否則會被它
連同簡介一起 commit＋push，訊息還寫著「補簡介」。

作法：取源時加 `--out c:/tmp/hellenika/text`，等驅動器停了再搬進去。

---

## 5. 現況（2026-08-30）

### 三欄對照（希臘原文／英譯／繁中）

| 篇 | 卷 | 段數 | 繁中 |
|---|---|---|---|
| 赫西俄德《神譜》 | Α | 53 | ✅ 53 |
| 赫西俄德《工作與時日》 | Β | 44 | ✅ 44 |
| 荷馬詩頌 第 1–33 首 | Ο | 138 | ✅ 138 |
| **《俄耳甫斯讚歌》序詩＋87 首** | **Ο** | **88** | **✅ 88** |
| **《伊利亞特》廿四卷** | **Γ** | **735** | ⏳ 0 |
| **《奧德賽》廿四卷** | **Δ** | **680** | ⏳ 0 |

合計 **1,738 段／33,000 餘行**，其中 **323 段有繁中**。翻譯走
`hellenika_text_align.py`，引擎 Haiku（`HELLENIKA_ENGINE=haiku`）。

兩部史詩是 user 2026-08-30 交辦「荷馬史詩和神譜也要優先放進內容」的結果：
**原文與英譯先全部上架，中譯分批慢慢補**（user 定調）。1,415 段是既有量的六倍，
不要想一次跑完。

**長度比校準**：中譯字元數 ÷ 英譯字元數，《神譜》一系實測中位數 **0.307**、
全距 0.18–0.41；俄耳甫斯那批 **0.328**、全距 0.28–0.38。拿 0.25 當下限會誤報
十幾段（實查都是完整的，只是中文較密）。要設閘門就用**低於 0.15 或高於 0.60**。

### 🚨 兩個實際卡住過的坑（翻譯端）

1. **模型把 JSON 的鍵回成「第3段」而不是「3」。** 嚴格比對會把整批好譯文丟掉，
   `homeric-hymn-03` 就這樣卡在 19/28 而看起來像「額度不夠」。修法是抽出鍵裡的
   數字再比對（`re.sub(r'\D', '', k)`），逐段對應的保證不放寬。
   **不要看到「整批丟棄」就以為是引擎問題，先看它回了什麼鍵。**
2. **OAuth access token 每幾小時滾一次。** 長跑的 worker 抓著舊 token 會一路 401，
   而 401 是 `anthropic.AuthenticationError`，不會被 429／連線錯誤的 except 接到，
   於是被當成「引擎全乾」放棄。`ask_haiku` 現在接 401 後丟掉 client 並清空 mtime
   記憶，下一次呼叫強制重讀 `.credentials.json`。

### 沒有 TEI 的篇目

- **《俄耳甫斯讚歌》87 首** —— ✅ **2026-08-30 已解決**，見 §5a。
  Perseus 與 First1KGreek 確實都沒有（`tlg1815` 兩邊皆 404）、Bibliotheca Augustana
  舊網址 404、sacred-texts 回 403 —— 但**希臘文 Wikisource 有**，而且是 Abel 1885
  的現成校對本。**日後再碰到「查無 TEI」的篇目，Wikisource（希臘文版、拉丁文版）
  要先查過再說沒有。**

### PHI 現況（供 [[hellenika-epigraphy]] 參照）

`/text/{id}` 仍可取（實測 28551 回 200），但 **`/search` 已回 403**，skill 裡
「站上 /search?patt= 可查編號」那條作法失效。找編號改走已刊概覽：
TAM V,1 452 ＝ PHI 263861、TAM V,1 535 ＝ PHI 263959，同一部書內編號大致遞增，
可據此推算並以 `expect` 驗證。

---

## 5a. 《俄耳甫斯讚歌》：沒有 TEI 的那一篇怎麼取（2026-08-30 完成）

`scripts/hellenika_orphic.py`。取源路線是 user 在三條裡挑的：

| | 取什麼 | 為什麼 |
|---|---|---|
| **希臘文** | 希臘文 Wikisource《Ὀρφικοὶ ύμνοι》 | 該站逐頁校對後 transclude 自 **Abel 1885《Orphica》**（頁面自陳「Προέλευση κειμένων: Eugen Abel επιμ. (1885)」）。等於拿到公有領域底本的**現成校對成果**，不必自己跑 Vision OCR |
| **英譯** | theoi.com 的 Taylor 1792 | 公有領域，乾淨 HTML |

被否決的兩條記在這裡，免得日後有人重走：**hellenicgods.org** 排版最省事，但希臘文
底本是 Quandt 1941，版權灰色；**archive.org 的 Abel 掃描本**明確公有領域，但要逐首
Vision OCR——而 Wikisource 拿的正是同一個底本。

### 🚨 三個坑，每一個都會「印得出來但配錯」

1. **兩站的編號差一號。** Taylor 把〈致赫卡忒〉併進序詩〈致穆賽俄斯〉裡不另立篇，
   所以 **Taylor I（Prothyraia）＝ Abel／Quandt 第 2 首**，一路差到底。照號碼對接，
   87 首會整批錯開一格。腳本因此不靠編號，靠 `HYMNS` 那張人工核對過的表，每列自帶
   `en_check`，抓下來的英譯標題對不上就中止不寫檔。
   **第二道獨立證據**：希臘文標題自帶焚香指示（`θυμίαμα στύρακα`），可與英譯的
   `The Fumigation from Storax` 交叉驗證——88 篇只有 2 篇不符，查下來都是 Taylor
   版本自身的異文，不是錯位。
2. **一首讚歌可能橫跨掃描本兩頁，那頁就有兩個以上 `<div class="poem">`。**
   起初用 `<div class="poem">(.*?)</div>` 只吃到第一個，序詩 44 行靜默剩 22 行。
   現在用 lxml 收齊全部，並**把 Wikisource 自己的行號標記（`<span id="vN">`，每 5 行
   一個）換成哨兵**，抽完核對「標為第 N 行的那一行確實排在第 N 行」——跨頁沒收齊、
   收重、順序錯亂都會當場現形。
   容許值是 `top ≤ 行數 ≤ top+5`：末行剛好逢五時該標記偶爾漏標（第 29 首
   Φερσεφόνης 即 20 行而只標到 v15）。

   > 🚨 **哨兵一開始用 ` `，而 lxml 會把 NUL 直接吃掉**——哨兵全數消失，
   > 於是整套行號核對一路空轉，88 篇「全部通過」。這比沒有檢查更糟：它讓人以為
   > 查過了。現在哨兵改用私有使用區的 **U+E000**，並且**先數頁上原有幾個
   > `id="vN"`，抽完對不上就報錯**——檢查本身失效必須是個錯誤，不能是沉默。
   > 同一個教訓也適用於 `hellenika_text.py` 的 `prose_lines()`。
   > **凡是「驗證器」，都要有一個讓它自己失效時會叫出來的機制。**
3. **Taylor 對八首沒有焚香的讚歌只寫「A Hymn.」佔位。** 當成焚香收進來，模型會在
   中譯欄頂上生出**憑空捏造的「（焚香：蘇合香）」**——來源三方都沒有這個字。
   現在取源端就把非 `Fumigation` 的佔位丟掉。

### 切段：一首一段

讚歌多半 6–30 行，而 Taylor 把希臘文的兩行壓成英譯的一行，兩邊行號**根本對不
起來**。故不切段：一首即一段，邊界取在篇界——這是唯一保證對得上的切法。序詩
44 行同樣不切，與其在 Taylor 的連綿神名表裡猜邊界，不如整段送。

`pivot` 用新值 `'taylor-eng'`（＝經由 Taylor 英譯，屬「有學術英譯把關」那一層，
見 [[hellenika-canon]] §11），`pivot_note` 說明「一首一段、不逐行對照」。

### 定名

站上詞庫的 `deities` 只有六條合用（宙斯、赫拉、波塞頓、雅典娜、阿波羅、阿瑞斯），
其餘全查無。依規矩不自行寫進詞庫，62 條【提】列在
`data/hellenika/glossary-candidates-orphic.md` 待 user 校可。
該檔末尾另記一條**待裁示的既有不一致**：詞庫作「蓋亞」而本藏經一路作「蓋婭」，
兩者不在 `CORPUS_OVERRIDES` 裡。

### 節流

Wikisource 的 API 在 1.5 秒間隔下連抓十頁就回 429。`_get()` 已加逐次退避重試，
`DELAY` 拉到 3 秒。**429 不是程式壞掉，不要靠縮短間隔硬闖。**
重抓一律加 `--force`，且重抓會**沿用既有繁中**（希臘文一字未改才接回去）。

---

## 5b. 荷馬兩部史詩：分卷與散文里程碑（2026-08-30）

走 `hellenika_text.py`（Perseus TEI），但比赫西俄德那批多兩件事：

1. **行號逐卷從 1 重來。** 一部史詩是一個 TEI 檔、內含 24 個
   `<div subtype="book">`，行號各自從 1 起算。不分卷就會把廿四卷的第 1 行疊成同
   一行。故 TARGETS 多一個 `book` 欄，**一卷一個檔**（`iliad-01`…`24`、
   `odyssey-01`…`24`），與詩頌同慣例。grc 寫 `Book`、eng 寫 `book`，比對不分大小寫。
2. **英譯是散文，沒有 `<l>`。** 取 A. T. Murray 的 Loeb 本（伊 1924–25、奧 1919，
   皆公有領域，`perseus-eng3`），行號以 `<milestone n="N" unit="line"/>` 埋在段落
   中間，故走 `prose_lines()`：把里程碑換成哨兵再切開，回傳格式與 `<l>` 那條路
   相同，下游不必分辨。Loeb 的 `<note>` 是編者註不是譯文，先 `strip_elements` 剝掉。
   `perseus-eng4`（Butler 經 Power 與 Nagy 修訂）里程碑較疏且修訂本年代晚，不取。

🚨 **上游 TEI 自己有行號筆誤。**《奧德賽》十六的 275 與 285 之間夾了一個
`n="580"`（顯然是 280 之誤）。放著不管，切段會排出 `line_from 580 → line_to 299`
這種倒置的段，而且希臘文那欄整段空掉，頁面照樣渲染。`prose_lines()` 現在會把
「比前一個大、卻又比後一個大」的尖刺剔除、文字併回前一段，一個字都不丟，並印警告。

**收工前的稽核值得照抄**：逐段檢查 ①兩欄都不空 ②`line_from` 接續前段的 `line_to`
③末段止於 `lines_total` ④英／希字元比在 0.5–3.0。這四項當初就是靠第 ① 與第 ④ 項
把那個上游筆誤揪出來的。

🚨 **哨兵不可用「空格＋數字＋空格」。** 中途曾因為巢狀腳本的跳脫把哨兵寫成那樣，
那會把譯文裡**每一個獨立數字**都當成行號切開——切錯而不是切不到，看不出來。
現在用 `MARK = '%s'`（私有使用區），原始碼裡寫跳脫序列，不留控制字元。

---

## 5c. 已接進 reader（2026-08-29；2026-08-30 改惰性載入）

`data/hellenika/sources/index.ts` 原本只認 `cgrn` 與 `phi` 兩種來源，現已認第三種
`perseus`，`pivot` 也多一個 `'perseus-eng'`。三處要一起改，漏一處就是靜默失效：

| 檔 | 改了什麼 |
|---|---|
| `sources/index.ts` | `AlignedText.source` 加 `'perseus'`；多 `slug`／`author`／`lines_total` 三欄；加 `./text/*.json` 的 glob；`normalise()` 收第三種 source |
| 同上 `alignedSlug()` | **文獻沒有庫編號，路由改用檔名** —— `/hellenika/text/theogony`，不是「庫-編號」 |
| `pages/hellenika/text/[slug].vue` | 篇首標籤依來源分「文獻」（綠）與「銘文／紙草」（藍）；文獻另顯作者與詩行總數 |

排序：同來源時 `perseus` 依 slug 字典序，銘文仍依數字編號。

### 🚨 2026-08-30：`import.meta.glob` 不可再用 `{ eager: true }`

加進兩部史詩之後，`sources/` 是 **5.9 MB**（光史詩就 4.2 MB）。eager 會把全部 JSON
打進 `/hellenika/text` 這條路由的 chunk，讀者點開任何一首詩頌都得先下載整套藏經。

現在改成惰性，介面隨之換掉：

| 舊 | 新 | 說明 |
|---|---|---|
| `ALIGNED_TEXTS`（含正文） | `ALIGNED_REFS`（只有 `source`／`slug`／`path`） | **篇目清單只從檔名推導，不載內容** |
| `findAligned(slug)` 同步 | `loadAligned(slug)` 回 Promise | reader 用 `useAsyncData` 取單篇 |
| `alignedInVolume()` | 已刪 | 從來沒有人用 |

`[slug].vue` 的篇目導覽因此只拿得到 slug，拿不到標題——那一列本來就只顯示編號，
把 `:title` 的 tooltip 拿掉即可。**日後要在清單上顯示標題，不要退回 eager**，
另出一份輕量索引。

順帶修掉一個既有的錯：英譯欄的標題寫死「英譯（CGRN）」，文獻篇目全標錯，
現在依 `pivot` 顯示 CGRN／Perseus／Taylor 1792。

### 逐首一頁的篇目導覽

荷馬詩頌 33 首、俄耳甫斯詩頌 88 篇、史詩各 24 卷，都是**逐首（卷）一頁**，而書目
那邊一條 works 只掛得住一個 `link`。沒有導覽列，讀者從書目點進去就只看得到第一首、
走不到其餘。`[slug].vue` 因此對 slug 形如「前綴-數字」者列出同組全部篇目
（俄耳甫斯第 0 首是序詩，標「序」不標 0）。

---

## 6. 加一篇的流程

0. **先確認有沒有 TEI。** Perseus → First1KGreek → **Wikisource（希臘文版／拉丁文版）**。
   前兩者沒有不等於沒有電子文本，俄耳甫斯那篇就是栽在這一步（§5a）。
1. 在 `TARGETS` 加一筆（slug／中英題／作者／所屬卷 key／siglum／grc 與 eng 的 urn；
   分卷的作品另加 `book`）。無 TEI 者另寫取源函式，schema 照 §3 不變。
2. `--fetch {slug} --lines 1-115` 先試跑一小段，肉眼確認兩欄對得上。
3. 確認後 `--fetch {slug}` 全篇，**先寫到 `--out c:/tmp/...`**（§4：整夜驅動器會
   把 `data/hellenika` 整個 git add）。
4. **稽核後才搬進 repo**：兩欄都不空、行號接續、末段止於 `lines_total`、
   英／希字元比在 0.5–3.0。這一關不能省——本輪四個靜默錯誤全是它抓到的。
5. 填 `names`（專名定譯先過 [[translation-glossary]]；查無者列
   `glossary-candidates-*.md` 標【提】，**不自行寫進詞庫**）。
6. 翻譯（另跑）：`python scripts/hellenika_text_align.py --file {slug}`。
   引擎鏈 Gemini → NVIDIA → OpenRouter → Haiku；要只走 Haiku 就設
   `HELLENIKA_ENGINE=haiku`。先加 `--limit 1` 跑一批肉眼看過再全開。
7. **譯文稽核**：長度比（§5 的 0.15–0.60）、中間點是否為「‧」、
   **中譯有沒有生出來源沒有的東西**（那批捏造的「（焚香：蘇合香）」就是這樣抓到的）。
8. 書目條目補 `link` 指向 reader。逐首一頁者連到第一首即可，其餘靠篇目導覽走。
9. 收工：`npx vue-tsc --noEmit -p .nuxt/tsconfig.json`（`scripts/run-biblical-*.mjs`
   那 48 個錯是既有噪音，不是你弄壞的）、`npx vitest run`、`npx nuxt build`。
