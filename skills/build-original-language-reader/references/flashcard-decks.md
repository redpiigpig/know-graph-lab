# Printable flashcard decks

The reader's vocabulary masters also drive printed decks: Hebrew 1,000 cards,
Greek volume 1 and volume 2 at 1,000 each, Latin volume 1 and volume 2 at 1,000
each. They follow the household's existing
English tutoring deck (`家教單字卡.pdf` on the desktop) so the same guillotine
and the same printer settings work for all of them.

## State, 2026-08-30

| Deck | Cards | Pages | With picture | Part of speech blank | File |
|---|---:|---:|---:|---:|---|
| 聖經希伯來文 | 1,000 | 252 | **1,000 (100%)** | 0 | `output/flashcards/hebrew-flashcards-1000.pdf` |
| 通用希臘文・上冊 | 1,000 | 252 | **1,000 (100%)** | **0** | `output/flashcards/greek-flashcards-volume-1.pdf` |
| 通用希臘文・下冊 | 1,000 | 252 | **1,000 (100%)** | **0** | `output/flashcards/greek-flashcards-volume-2.pdf` |
| 教會拉丁文・上冊 | 1,000 | 252 | **996 (99.6%)** | **0** | `output/flashcards/latin-flashcards-volume-1.pdf` |
| 教會拉丁文・下冊 | 1,000 | 252 | **1,000 (100%)** | **0** | `output/flashcards/latin-flashcards-volume-2.pdf` |

All five are built, rendered, verified and pushed. DOCX sits beside each PDF.
2026-08-31 全部依審過的配圖帳本重出一次；覆蓋率不變（刪掉的圖只是退回原本的
OpenMoji 圖，不是變成空白）。

**轉檔有兩個會讓人以為轉好了的坑，兩個都踩過：**

1. `render_and_check_reader_pdfs.py` 的 `--only` 是 `nargs="*"`，所以
   `--only a --only b --only c` **只會跑 c**——後面的旗標把前面的整個蓋掉，而且
   不會有任何警告。要跑多個就寫成 `--only a b c`。
2. 它**寫到 `output/print-masters/`，不是 `output/flashcards/`**。`output/flashcards/`
   那份 PDF 是工作副本，由 `sync_reader_artifacts.py` 從 masters 拉齊。只看
   `output/flashcards/` 的 PDF 會看到三天前的舊檔而以為重轉過了。

這兩個加起來的結果是：build 全綠、render 報 `✔`、頁數尺寸全對，而五份 PDF 有四份
根本沒重轉。抓到它的方法是 silent-failures.md 那條「打開頁面找你剛做的那個改動」
——去看那張「創造」卡，剪刀還在。`ls -l` 比對 docx 與 pdf 的 mtime 一秒就確認。

### Appendix decks, added 2026-08-27

| Deck | Cards | Pages | Dropped (no Chinese) | File |
|---|---:|---:|---:|---|
| 聖經希伯來文附錄 | 255 | 64 | 0 | `output/flashcards/hebrew-flashcards-appendix.docx` |
| 通用希臘文附錄 | 511 | 128 | 114 | `output/flashcards/greek-flashcards-appendix.docx` |
| 教會拉丁文附錄 | 745 | 188 | 191 | `output/flashcards/latin-flashcards-appendix.docx` |

The reader appendices hold the material that never enters the fifty lessons:
proper names in nine categories, numerals and measures, kinship terms, the
calendar and its feasts, church offices and liturgical vocabulary. The owner
asked for cards for all of it. These share the sheet, the card size and the
duplex rule with the five lesson decks and differ in exactly three ways: the
frame colour cycles by **section** rather than by lesson (so one section is one
colour), the footer prints the section name instead of a lesson number, and
**there are no pictures** — no emoji honestly denotes 伯特利, 猶斯定 or 第十七.

Section order is `PRINT_ORDER` from `scripts/proper_name_categories.py` for the
proper names, then each remaining table's own `group` field in first-appearance
order. The printed appendix and the web page use the same order.

A row with no Traditional-Chinese rendering is not printed and the build reports
how many it dropped. Latin's 191 are all proper names the Studium Biblicum
alignment could not settle; its numerals, kinship, calendar, offices, liturgical
year, document-genre and scholastic tables are at 100% since
`gloss_latin_appendices_zh.py` ran. Greek's 114 are the appendix names no
register covers.

**Two Latin tables are deliberately excluded.** `principalParts` (841 rows) is a
morphology reference whose headwords largely repeat the lesson verbs, and
`modernNames` (400 rows) has no Chinese at all and has swept up abbreviations and
common nouns (`Psal`, `Joan`, `Latine`, `Cardinalis`, `Redemptoris`); that table
needs rebuilding at source.

**Hebrew numerals are stored as a masculine/feminine pair**, with no single
`pointed` field. One card per form, with 「（陽性）」/「（陰性）」 on the Chinese
face — a combined card would make the reader memorise two forms at once. Check
any new language's numeral table for the same shape before assuming one row is
one card.

### What the owner has decided

- **Every card should carry a picture.** Their reasoning: a physical deck only
  earns its keep if the picture aids memory, otherwise study online. Hebrew
  reached that on 2026-08-26 (419 blanks picked by hand), and Greek on the same
  day: 925 hand picks in four passes took the two volumes from 50% to 100%, so
  the Greek `OVERRIDES` now carries 1,493 entries. Latin went 802 → 1,361 on 2026-08-27 without a single hand pick, by fixing two things in the borrowing rule rather than by picking pictures — see 「借圖只看第一個義項」 below. The remaining 639 were then hand-picked on 2026-08-28, which took all five decks to 1,996／2,000. The four left blank are 拿撒勒的、加里肋亞的、猶太的、羅馬的: 族屬形容詞, which in the other three readers live in the appendix, and appendix cards carry no picture — 沒有一個 emoji 誠實地代表得了「伯特利」.
- **Cartoon style**, one consistent look.
- **No cutting lines.** A hairline printed a millimetre off leaves every card
  with a crooked edge.
- **The Divine Name takes the God picture.** יְהוָה and יְהֹוִה use the same 🤲 as
  אֱלֹהִים / אֵל / אֲדֹנָי: one concept, one picture. Not a star of David or a
  menorah — those are symbols of later Judaism read back onto the Hebrew Bible,
  which is a different claim.

### Where the pictures come from, and what was ruled out

OpenMoji 17.0.0 (CC BY-SA 4.0), 4,565 consistent cartoon SVGs, cited on each
cover. The 44 MB artwork is not in git;
`scripts/match_flashcard_images.py` downloads it on demand.

Ruled out, so nobody spends the time again:

- **Canva** has no usable programmatic route. The Connect API is partner-gated
  and its content licence does not cover bulk export into your own teaching
  material.
- **AI image generation** was unreachable on 2026-08-25: all seven Gemini keys
  returned 429 on `gemini-2.5-flash-image` and `gemini-3.1-flash-image` (image
  generation is effectively a paid-tier feature), and NVIDIA's `ai.api.nvidia.com`
  image endpoints returned 500/404/timeout. If the owner ever supplies a paid
  Gemini key this is the route to 100% coverage with a better-matched style than
  emoji, and it is worth revisiting first.
- **Openclipart** (CC0, would have been ideal for coverage) has a dead JSON API
  — the search endpoint returns HTML. Scraping it would also mix dozens of
  artists' styles in one deck.

## 一圖一卡：規則、現況與那條擋住它的天花板

owner 2026-08-29：「同一種語言的圖，我嚴格禁止用同一張圖，即使是眼睛的單數或
複數，也要用不同眼睛的卡通圖。」規則從「不相干的詞不共用」收緊成**同一語言內
一張圖只出現在一張卡上**（跨語言仍可共用——πῦρ 與 אֵשׁ 都用火是刻意的）。

### 現況：2,938 張全部審完（2026-08-30）

owner 在三條路裡選了**①先清錯圖，共用暫時照舊**：只做一個判斷「這張圖對不對」，
對的放行，錯的從帳本刪掉、那張卡退回原本手挑的 OpenMoji 圖，不強求一圖一卡。
理由是 owner 自己定過的「錯圖比共用圖更糟」——共用只是兩張卡指向同一個意思，
錯圖是背進一個不存在的意思，而且背了改不掉。

| | 判過 | 放行 | 判錯刪掉 |
|---|---:|---:|---:|
| 聖經希伯來文 | 438 | 125 | 313 |
| 通用希臘文 | 1,184 | 300 | 884 |
| 教會拉丁文 | 1,316 | 407 | 909 |
| **合計** | **2,938** | **832（28%）** | **2,106** |

**放行率只有 28%，遠低於原先估的「約三分之一是錯的」——實際是約七成是錯的。**
五副卡的配圖覆蓋率不變（仍是 1,000／1,000），因為刪掉的那張只是退回原本的
OpenMoji 圖，不是變成空白。

### 天花板在哪

OpenMoji 扣掉旗幟與膚色變體只剩約 2,185 張可用，而希臘與拉丁各要 2,000 張
不重複——靠它本身做不到。第二層走 Iconify 四庫（game-icons／Phosphor／MDI／
Tabler，25,059 個概念，`scripts/iconify_card_images.py`），比對分三層：

1. 圖示本名與英文詞義**完全相符**；
2. 同概念的其他畫法（`eye` → `eye-off`、`eye-closed`），只認以連字號分隔的
   整詞，`ear` 不可以命中 `search`／`earth`；
3. 前兩層都沒有時，用它現在共用的那張圖的 OpenMoji 概念名再走第 2 層。

### 為什麼第 2、3 層的結果一律要人看過

接觸表（`flashcard_contact_sheet.py --audit-icons`）第一頁就有：

| 卡 | 配到 | 實際是 |
|---|---|---|
| 弟兄 | `mdi:point-of-sale` | 刷卡機 |
| 永遠；久遠 | `mdi:delete-forever` | 垃圾桶（命中 forever） |
| 中間；裡面 | `ph:finn-the-human` | 卡通《探險活寶》主角 |
| 生命；一生 | `game-icons:life-bar` | 電玩血條 |
| 軍隊 | `game-icons:swiss-army-knife` | 瑞士刀（命中 army） |
| 頭；頂；首領 | `game-icons:top-hat` | 高禮帽（命中 top） |

**錯圖比共用圖更糟**：共用只是兩張卡指向同一個意思；錯圖是把一個不存在的意思
背進去，而且背了改不掉。所以 `*-card-icons.json` 分兩區：`cards` 是放行的
（本名完全相符），`pendingReview` 是待審的 2,507 張，逐張看過才可以搬進 `cards`。

### 放行的那 431 張也不是自動安全的（2026-08-30 查出）

放行的判準是「圖示本名與候選詞完全相符」——但**相符在第幾個義項上，判準沒有
問**。Strong's 與 Whitaker 的釋義把引申義、冷僻義並列，於是：

| 卡 | 中文 | 配到 | 命中的是 |
|---|---|---|---|
| בָּרָא | 創造；砍伐 | `tabler:cut` | 第二義「砍伐」——剪刀在教創造 |
| מִקְנֶה | 牲畜 | `mdi:water` | 釋義裡的 watering |
| רֹעֶה | 牧人 | `ph:dog` | 牧羊犬不是牧人 |
| מִצְוָה | 誡命 | `ph:spiral` | 螺旋 |
| עָרֵל | 未受割禮的 | `game-icons:razor` | 剃刀，方向相反 |
| εἰ／licet | 如果／雖然 | `ph:shuffle` | 洗牌 |
| βελτίων | 更好的 | `game-icons:chart` | 長條圖 |
| πρᾶξις | 行為 | `ph:function` | 數學的 f(x) |

`scripts/audit_card_icons.py` 把「候選詞不在第一個義項」的挑出來排在前面：
431 張裡有 **245 張**是這種，逐張看過大多是同義（多數／群眾、看見／眼睛）沒問題，
確實錯的約兩成。**所以要人看的不是 2,507 張，是 2,938 張**（431 放行＋2,507 待審），
只是放行那批錯得比較稀。

    python scripts/audit_card_icons.py                      # 三語言的放行區，只列可疑的
    python scripts/audit_card_icons.py --lang hebrew --all  # 連沒疑點的也列
    python scripts/audit_card_icons.py --section pending    # 待審那一區

中文欄一律讀 `build_flashcards.py` 讀的那份（希伯來與希臘各有審過的 by-lemma
詞義檔，拉丁在詞表自己身上）。**不要讀詞表的 `glossZh`**：希伯來詞表那一欄一千筆
全是空的，拿它當中文欄會印出一張空表，而表本身看起來跑完了。

### 帳本會被重跑洗掉——已經擋住（2026-08-30）

`cards`／`pendingReview` 這個分區是人工審圖的帳本，沒有任何程式讀得懂它：
`build_flashcards.py` 只讀 `cards`（讀到什麼就印什麼），而
`iconify_card_images.py --write` 舊版**無論哪一層配到的都寫進 `cards`**。也就是
說任何人再跑一次 `--write`，那 2,507 張沒人看過、約三分之一是錯的圖就整批進了
印卡流程，沒有錯誤訊息、沒有警告。這正是 silent-failures.md 第 18 條。

現在該腳本會先把舊帳本讀回來，帳本裡已有的卡不重配（保住人工判斷），舊帳本
佔用的圖示也算進 `taken`（否則重跑會把同一張圖再發給第二張卡），新配到的只有
「本名完全相符」那一層自動進 `cards`，其餘一律進 `pendingReview`。三種語言重跑
都是 0 增 0 減，可以安全地反覆跑。

### 審圖怎麼做的，與四條可以整批判的規則

`scripts/review_card_icons.py`：`--sheet` 把下一批排成樣張（12 欄 × 11 列 = 132 張，
**整張圖任一邊不可超過 2,000 px，否則會炸掉 session**）、`--list` 印出對應的中文
與圖示名、`--record` 記下判決、`--apply` 寫回帳本。判決存在
`icon-review-decisions.json`，**連「判的是哪一張圖」一起存**：帳本裡的圖換了，
舊判決就自動失效重審——判決是對某一張圖的判決，不是對某張卡的。

判斷一定要看圖，不能只讀名字：`ph:finn-the-human` 是卡通《探險活寶》主角、
`game-icons:life-bar` 是電玩血條、`mdi:dog-service` 是導盲犬、`mdi:pi-hole` 是
一套軟體的標誌。但有四類**判準寫在圖示本名裡**，不必一張一張看（`--filter` 各自
可列出來，每一類都抽了樣張確認過無例外）：

| 規則 | 張數 | 為什麼 |
|---|---:|---|
| `stopword` | 573 | 命中理由是功能詞或單字母（of／to／at／i／go／it）。第三層備援拿現有圖的概念名再找圖，切詞後功能詞也算候選，於是 `eye-of-horus` 的 `of`、`pokemon-go` 的 `go`、`power-socket-it` 的 `it` 都成了命中理由 |
| `negated` | 93 | 名字帶 `-off`／`-disabled`／`no-`／`not-`，畫的是打了叉的那個東西。`gift-off` 是被劃掉的禮物、`food-off` 是被劃掉的食物——教的是相反的意思 |
| `brand` | 40 | 商標、電玩、動漫、塔羅。`death-star` 是星際大戰、`death-note` 是死亡筆記本、`tarot-*` 是塔羅牌 |
| `software` | 103 | 介面元件與檔案格式。`file-word` 是 Word 檔、`http-put` 是 HTTP 動詞、`git-fork` 是版本控制、`subset-of` 是集合論 |

規則裡**刻意不收** `keyboard`／`letter`／`mail`：`musical-keyboard` 是鋼琴鍵盤、
`love-letter` 是插著心的信封，都是真實名物，「愛」配 `love-letter` 是好圖。字母框
那一類改用字首比對（`letter-a`、`alpha-i`、`square-letter-i`）才不會連帶掃掉真名物。

### 逐張看才抓得到的那些

規則之外的 2,129 張是一張一張看的。錯得最有代表性的幾類，寫在這裡是因為它們
只有看圖才看得出來：

- **命中了詞義裡的冷僻義**：בָּרָא「創造；砍伐」配到剪刀、מִקְנֶה「牲畜」配到
  水滴（釋義裡的 watering）、`missa`「彌撒」配到 `fleshy-mass` 一團肉（命中 mass）、
  `officium`「職責」配到 `stapler-heavy-duty` 釘書機（命中 duty）。
- **命中了同音的專有名詞**：`salutatio`「問安」配到 `weather-hail` 冰雹、
  `pater`「父親」配到 `vitruvian-man` 達文西人體比例圖、`regina`「女王」配到
  `bed-queen` 雙人床、`spiritus`「聖神、氣息」配到 `bad-breath` 口臭。
- **畫的是相反的意思**：`thumbs-down` 配「好」、`love-song` 配「恨」、
  `progress-down` 配「進步」、`unfold-less` 配「展開」、`ph:pause` 配「連續不斷」。
- **異教或別的宗教的符號**：`eye-of-horus` 荷魯斯之眼、`hades-symbol` 冥王雙叉戟、
  `star-crescent` 伊斯蘭星月、`greek-sphinx` 人面獅身、`hedjet-white-crown`
  埃及白冠、`holy-hand-grenade` Monty Python。同 [[feedback]] 的時代錯置規矩：
  不是風格問題，是內容錯誤。
- **畫的是現代器物**：`briefcase` 配「工作」、`test-pipe` 配「試探」、
  `chess-bishop` 配「主教」（那是西洋棋子）、`gas-station-in-use` 配「使用」。

錯圖清乾淨之後，才輪得到 owner 那條原始規則——見下一節。

## 一圖一卡：用九套 emoji 做到 97.8%（2026-08-31）

owner：「那就不要圖重複，去找幾種不同的來源。」清完錯圖後仍共用 2,650 張
（希伯來 350、希臘 1,164、拉丁 1,136）。

### 來源：九套彩色 emoji，命名互通

Iconify 上有 237 個圖庫，其中十二套是 emoji。**它們用同一套名字**——`dog`、
`folded-hands`、`prohibited` 每一套都叫同一個名字——所以同一個概念可以拿到九種
不同繪者的畫法。這正是這條規則要的東西：「眼睛的單數與複數也要用不同的眼睛圖」。

| 圖庫 | 張數 | 授權 |
|---|---:|---|
| openmoji | 4,544 | CC BY-SA 4.0（本專案原本就在用） |
| twemoji | 3,988 | CC BY 4.0 |
| noto | 3,710 | Apache 2.0 |
| fluent-emoji-flat | 3,145 | MIT |
| noto-v1 | 2,162 | Apache 2.0 |
| emojione | 1,834 | CC BY 4.0 |
| emojione-v1 | 1,262 | CC BY-SA 4.0 |
| fxemoji | 1,034 | Apache 2.0 |
| streamline-emojis | 787 | CC BY 4.0 |

**`fluent-emoji`（3D 那套，3,126 張）驗過之後剔除。** 它的 SVG 用漸層與內嵌點陣，
PyMuPDF 一律 render 成全黑剪影，五個概念抓下來全是黑影。不會報錯，會安靜地印出
一張純黑的卡。新增任何圖庫都要先 `--probe` 排樣張看圖再收。

### 兩層，只有第二層要人看

| 層 | 做什麼 | 張數 | 要不要審 |
|---|---|---:|---|
| 同概念換畫法 | `folded-hands` 換成 twemoji 的 `folded-hands` | 2,010 | **不用**——概念沒動，twemoji 的狗還是狗 |
| 同語意場換符號 | `folded-hands` 換成 `prayer-beads`、`prohibited` 換成 `cross-mark` | 529 | **要**——概念動了，跟 Iconify 那層同一個風險 |

這個分界是這一輪最重要的一件事：上一輪 Iconify 那層七成是錯的，是因為它去找
「名字碰巧對得上的另一個概念」；換畫法這層完全沒有那個風險，所以兩千張不必看。

家族表（`FAMILIES`，64 個概念、327 個兄弟）逐條列出來看過，改掉七處，其中兩處
是真的會教錯：`right-anger-bubble` 配「提醒、記得」教的是生氣，`waving-hand` 配
「允許、容許」是道別（skill 早就記過「釋放」借到揮手是錯的）。表裡刻意**不收
膚色變體**（`folded-hands-dark` 那一類）：拿膚色去區分兩張卡，學的人什麼也沒多
學到。也不收會帶進錯值的：`input numbers` 那一團的卡是「五十、十二、二十」，
給它 `keycap-7` 就是在教 7。

### 結果與剩下的 111 張

    希伯來  990 張不同的圖，仍共用 10 張（7 團）
    希臘  1,948 張不同的圖，仍共用 52 張（28 團）
    拉丁  1,947 張不同的圖，仍共用 49 張（28 團）

2,650 → 111（2.2%）。剩下的多半是數字（`keycap: 1`／`4`／`6`／`8`／`10`、
`abacus`、`input numbers`）——「六百」跟「一千」之間沒有第二張誠實的圖可換，
硬換就是在教一個錯的數目，所以留著共用。

### 三個坑，每一個都會安靜地毀掉結果

1. **分組要讀「原本的 OpenMoji 配圖表」，不能讀 `load_cards` 解出來的圖。**
   印卡端已經會讀換圖帳本，所以第二次跑會看到「幾乎沒有重複」，然後把帳本重寫
   成只剩十幾筆——前一輪的兩千張無聲消失。
2. **佔用表的鍵是（圖庫, 概念名），不是檔名。** OpenMoji 本地下載的 `link` 叫
   `1F517.png`，同一張圖從 Iconify 抓來叫 `openmoji-link.png`：檔名不同、畫面
   相同。照檔名比會回報「零重複」，而卡片上明明有兩張一樣的。
3. **要分兩趟發。** 一趟做完，`end arrow` 那一團會循家族借走 `top-arrow` 的各套
   畫法，等輪到 `top arrow` 自己那一團時它自己的畫法已經被借光，只好整團維持
   共用。先把所有團的同概念換畫法發完，第二趟才發家族借圖：希臘 81→52、
   拉丁 92→49。

### 一個誠實的但書：簡單符號換了套也還是很像

九套的狗、皇冠、房子明顯不同，但**紅心、叉叉、箭頭這類簡單符號，換一套仍然幾乎
一模一樣**——一個叉就是一個叉。規則在「圖檔層級」是達成了（`--verify` 比概念身分
過關），但學的人翻到那兩張卡，看到的差別很小。這是這條路的天花板，不是實作沒做好。

    python scripts/emoji_variant_images.py --probe dog folded-hands   # 各套畫法對照
    python scripts/emoji_variant_images.py --lang grc                 # 只算不下載
    python scripts/emoji_variant_images.py --lang grc --write
    python scripts/emoji_variant_images.py --lang grc --review        # 只看家族層樣張
    python scripts/emoji_variant_images.py --lang grc --verify        # 驗收同語言重複

### 下一層還沒審過：手挑的 OpenMoji override

這一輪只審了第二層（Iconify）。**退回去的那張 OpenMoji 圖本身沒有經過同樣的
檢查**，而它至少有一張是錯的：רֹעֶה「牧人」的 override 是 🐕（`1F415`，一隻狗）。
`source` 欄寫著 `override`，也就是這是**人挑的**，不是自動配的——所以「手挑過」
不等於「對」。這一層有 2,303 筆（希伯來 810、希臘 1,493），從沒被逐張看過。
刪掉 `ph:dog` 只是讓那張卡退回另一隻狗。

要做的話走同一套：`review_card_icons.py` 的樣張與判決帳本可以照搬，只要把來源
從 `*-card-icons.json` 換成 `*-card-images.json`。

## Sheet

| | |
|---|---|
| Page | A4 landscape, 297 × 210 mm |
| Grid | 4 columns × 2 rows, 8 cards a sheet |
| Card | 71.25 × 98 mm |
| Margins | 6 mm left and right, 7 mm top and bottom — **symmetric on all four sides** |
| Cuts | vertical 6 / 77.25 / **148.5** / 219.75 / 291 mm from the left; horizontal 7 / **105** / 203 mm from the top |
| Duplex | long-edge flip; the back sheet mirrors the column order 4-3-2-1 |

**The two middle cuts land on the paper's own centre lines** (148.5 = half of
297, 105 = half of 210), which is what makes a guillotine stack cuttable: the
operator folds or measures to the centre once and the rest follows. The previous
sheet could not be cut evenly — 74.25 × 94 with 0 side margins and 5 mm top left
17 mm at the bottom, so the middle horizontal cut sat at 99 mm against a 105 mm
centre line, and the cards ran to the paper edge where no home printer can print.
Measured on the rendered page: now 8.9 mm top and bottom, 7.9/8.1 left and
right; before, 6.9 top against 18.8 bottom and under 2 mm at the sides.

**Declaring symmetric margins is what pushes the second row onto its own page —
not the card height.** A symmetric declaration means `top + 2×height + bottom`
equals the page exactly, and the renderer needs a little slack it never asked
for; an 86 mm card fails just as an 98 mm one does when both margins are
declared. The fix is to declare the top and left margins at their real value and
the bottom and right at **zero**: the block still ends at `margin + 2×height`,
so the leftover *is* the visual bottom margin and the page stays centred, while
the renderer keeps its slack. Setting `row.height` and then appending a second
`w:trHeight` leaves two competing rules in the XML and produces the same symptom.

`HEADWORD_MAX_MM` follows the card width rather than being written out: it was
hard-coded to 54 mm for the 74.25 mm card, and a hard-coded limit silently
overflows the moment the card changes width.

## Card faces

Front carries the headword and the lesson. Back carries the picture (when there
is one), the Traditional-Chinese meaning, the part of speech and the lesson. The
meaning line is sized from its own length — the glosses run from two characters
to twenty-seven — rather than set once and allowed to overflow.

**The Greek cards print a citation form only when it cannot be worked out.** The
reader prints the full dictionary form; the card does not need to, because for a
first- or second-declension noun the genitive follows from the ending plus the
gender — `θεός` is a masculine `-ος`, so the genitive can only be `θεοῦ`, and
printing it spends space that the headword's own size ladder would otherwise use.
What is kept is what cannot be derived: a third-declension stem
(`σῶμα, ατος, τό`), a gender that contradicts the ending (`ὁδός, οῦ, ἡ`;
`προφήτης, ου, ὁ`), or an impure alpha (`δόξα, ης, ἡ`). The decisive case is
`γένος, ους, τό` — its nominative is indistinguishable from `λόγος` and its
genitive is nothing like it.

259 of the 729 noun cards keep the form and 470 print the headword alone
(volume 1: 128/231, volume 2: 131/239). `scripts/greek_citation_form.py` decides;
the genitive and article come from the vocabulary's own `printedEntry` where
Mounce supplies one and from Dodson otherwise. The 80 nouns neither source
covers print the headword alone — **never a derived genitive**.

Latin prints the full citation form on the front — four principal parts for a
verb, nominative-genitive-gender for a noun — because that is what has to be
known, and it gets its own size ladder: the longest run past forty characters,
where the Greek ladder would shrink them to nothing. They are allowed to wrap.

Hebrew and Latin read their part of speech from the vocabulary master; Latin's
comes from the reader's own `short_pos`, which reads the gender abbreviation and
the principal parts rather than an explicit field, because Collins labels
neither. Greek has none, so
`scripts/flashcard_pos.py` works it out, strongest evidence first:

1. hand lists for the function words and the irregular verbs;
2. the citation form — an article makes a noun, three terminations an adjective,
   a first-person form a verb;
3. **the SBLGNT's own tags.** MorphGNT labels every New Testament word, so for
   anything the New Testament uses the part of speech is a recorded fact rather
   than an inference. This alone settled 603 of the 723 Greek cards that the
   first two rules left blank;
4. the Chinese gloss where the form is silent — `（配屬格）` marks a preposition,
   a gloss whose senses all end in 「的」 an adjective;
5. `EXTRA_LEXICON`, 116 Septuagint and patristic words read one at a time. Nouns
   dominate it because a bare Septuagint headword carries no article, which is
   exactly the cue rule 2 needs.

Together they settle all 2,000. **A blank line costs nothing; a wrong label is
learned as fact** — the list in rule 5 was written by reading the words, not by
guessing from endings, precisely because -ος is a noun and an adjective alike.

The adverb pattern must allow accents: `καλῶς` carries a circumflex, and a
pattern written `ως` silently never matches it.

### 借圖只看第一個義項，是 2026-08-27 才發現的漏

拉丁那副卡停在 40% 不是因為 OpenMoji 沒圖，是因為借圖只拿整串詞義、第一個
「；」段、第一個「、」段去對。拉丁詞義多半是三四個義項並列，於是
`libero`「解放、釋放」借不到已經有圖的「釋放」，`canticum`「聖歌、讚美詩」借不到
「讚美詩」。改成**逐義項依序比對**（第一義仍有優先權），一次撿回 333 張。

同時發現第二層：拉丁那本的中文用思高本，希伯來與希臘那兩本用《和合本修訂版》，
所以同一個概念兩邊寫法不同，圖借不過來——宗徒／使徒、聖神／聖靈、盟約／約。
`CATHOLIC_TO_PROTESTANT` 這張小表只放兩邊確實同指一物的對子。

代價要照規矩付：借來的圖記下 `borrowedVia`（循哪一個義項借的），非首義借來的
354 張逐張看過，錯配八張已覆蓋——「釋放」借到揮手（那是道別）、「歸還」借到站著
的人、「創建」借到錨（那是望德）、`ut` 借到 🔚（跟當初 `itaque` 一樣，目的的箭頭
不是終點，改成與希臘 ἵνα 同一個 🎯）、「洗禮」借到浴缸（同冊 `baptismus` 早就是
💧）。

## Picture matching

Strictest-first, and it refuses to guess:

1. **Hand-picked overrides**, named by the emoji's own name rather than a
   hexcode so a bad entry fails loudly. This is where the frequent core
   vocabulary lives, and where function words get their symbol —
   לֹא🚫, עַד🛑, אֲשֶׁר🔗, אֵין🕳️, לְמַ֫עַן🎯, ἵνα🎯, καί➕. 2,303 entries so far
   (Hebrew 806 by Strong number plus 4 by pointed form, Greek 1,493).
2. **Chinese-meaning transfer**, both ways and transitive. All five decks share
   one Traditional-Chinese gloss vocabulary, so a word whose meaning another deck
   has already pictured takes that picture: πῦρ and אֵשׁ are both 「火」 and both
   want the flame. Greek reads the Hebrew map, Hebrew reads the Greek map, and
   the Greek matcher runs a second pass over its own results so volume 2 inherits
   volume 1. Latin came third and reads both earlier maps, which is where 444
   of its 802 pictures came from — more than its 279 hand-picked overrides. Run
   the matchers alternately until the counts stop moving — two rounds is enough.

   A borrowed picture can still be wrong for the borrower. `itaque` 「因此、所以」
   arrived carrying 🔚 from whichever card shares that gloss; a conclusion is an
   arrow forward, not a stop. Overrides run first precisely so a deck can correct
   an inheritance without touching the deck it inherited from.

   Keep the loop variable out of the way here. Naming it `key` shadows the
   card's own `strong|pointed` and silently writes entries under their Chinese
   meaning instead, which the deck builder then cannot find. The matcher now
   asserts every key in the map resolves against the vocabulary.
3. **Exact match on the emoji's name**, never on its tag list.
4. **Nothing.** The card prints without a picture.

Rule three is not fussiness. Matching on tags scored 72% and produced בַּיִת
"house" as a potted plant, דֶּרֶךְ "way" as an exploding head and מַיִם "water" as
sweat droplets. `AMBIGUOUS_EN` additionally blocks English words whose senses
split — "watch" the verb against the wristwatch, "bear" the verb against the
animal — because Strong's glosses are English and English is full of them.

A wrong picture on a printed card teaches a sense the word does not carry, and
the learner cannot undo it. Blank beats wrong, every time.

### Filling the last 419 by hand, and what that taught

Picking a picture for every remaining word — including the abstract ones — is a
different job from matching, and it has its own failure modes:

- **Look at the artwork before trusting the name.** OpenMoji's `tap` is a finger
  tapping a screen, not a water tap; `wedding` is a church with a cross, which
  is a Christian building on a Hebrew Bible card; `assembly group` is an adult
  with a child. Render a contact sheet of every new pick (`PIL`, 110 px cells)
  and look at it before rebuilding the deck. Four wrong pictures were caught
  that way and none of them were catchable from the name.
- **Repeats are fine within a root, fatal across an opposition.** The deck has
  always let synonyms share a picture (門/出去/入口 all take the door), and a
  verb and its noun sharing one is a feature — רָעֵב and רָעָב both take 🤤,
  שָׁבָה and שְׁבִי both take the padlock. But 饑荒 must never take the same
  🍴 as 吃, and 管教 must never take the same ☝️ as 你: the card then teaches the
  opposite or an unrelated word. After each round, group the map by picture and
  read the glosses that share one.
- **Anachronism is a content error, not a style one.** Same rule as the Divine
  Name: no church for 新婦, no synagogue for 聖所 (`place of worship` 🛐 is the
  neutral one), but מְנוֹרָה does take the menorah — there it is the object
  itself, not a later symbol read back.
- **Function words take a symbol, not a scene.** 疑問助詞 ❓, כְּ ＝, לְ →,
  בְּ 🚩, מְעַט 🤏, עַד ♾️, בְּלִי 🪹.
- **Some OpenMoji names have no artwork.** `white square` (U+25A1) ships as a
  pink box with a cross through it — the set's own missing-glyph placeholder —
  and it printed on the 四方形的 card until the contact sheet caught it. Hash the
  file against that placeholder before trusting a name; `white large square` is
  the real square.
- **A picture can be wrong in the other direction.** `emergency exit door` shows
  a figure running *out*, so on 「領進」 it teaches the opposite; `ogre` is a
  Japanese oni and has no business illustrating 「蠻族人」; `passport control` is
  an officer checking papers, not a 「皈依者」; `bellhop bell` is room service,
  not 「關切」. All four were caught by looking, none by reading the name.
- **Four prefixes have no Strong number.** בְּ / כְּ / לְ / הֲ are keyed by their
  pointed form in `OVERRIDES_BY_FORM`, which the matcher consults when
  `entry["strong"]` is empty. Copy the form out of the vocabulary master rather
  than typing it: בְּ and כְּ carry a dagesh after the shva, and a hand-typed
  key silently matches nothing.

## Commands

```
python scripts/match_flashcard_images.py --write        # Hebrew picture map
python scripts/match_greek_card_images.py --write       # Greek picture map
python scripts/match_greek_card_images.py --uncovered 50  # what is still blank
python scripts/match_latin_card_images.py --write       # Latin picture map
python scripts/classify_proper_names.py --language all --write  # categories, before the appendix decks
python scripts/build_flashcards.py --deck hbo           # or grc1, grc2, lat1, lat2,
                                                       # hbo-appendix, grc-appendix, lat-appendix
python scripts/build_flashcards.py --deck hbo --limit 16   # proof sheet
```

`scripts/render_and_check_reader_pdfs.py --only <stem>` renders and checks page
geometry, embedded fonts, U+FFFD and blank pages in one step, for the decks and
the readers alike. To drive LibreOffice by hand instead, clear
`PYTHONHOME`/`PYTHONPATH` first: leaving them set makes `soffice` exit 0 having
written nothing.

```
env -u PYTHONHOME -u PYTHONPATH -u PYTHONIOENCODING \
  "C:/Program Files/LibreOffice/program/soffice.com" --headless --norestore \
  -env:UserInstallation=file:///<系統暫存>/lo-profile-cards \
  --convert-to pdf --outdir …/output/flashcards …/output/flashcards/<deck>.docx
```

## Checks worth running on a new deck

- Page count is `2 + 2 × ceil(cards / 8)`. Anything larger means the row spilled.
- No font falls back: every headword glyph should report the deck's own face, not
  Tahoma or Calibri. `pdfplumber` reports the font per character.
- The back sheet's leftmost card matches the front sheet's rightmost.
- Every key in the picture map resolves against the vocabulary master.
- Every back page carries exactly eight images once the deck is at full
  coverage: `len(page.images)` over the odd pages should be 8 for all 125 of
  them. A page with seven means one card lost its picture in the rebuild.
- Two Hebrew cards report Tahoma and that is expected, not a regression: the
  gloss lines 「弟兄；兄弟（אָח 的複數）」 and 「誡命（מִצְוָה 的不規則複數）」
  embed Hebrew inside the Chinese meaning run, which is set in the UI face.
  Headwords themselves never fall back.

## Next, if the owner asks for more

1. **Hebrew and Greek are both at 100%** and need no more overrides — the
   matchers' uncovered reports print empty. What is left in both is refinement:
   a picture that is merely adjacent to its word (肩膀 takes the prosthetic arm,
   下冊's abstract 樣式／形狀／組成 all take the puzzle piece) could be improved,
   but none of them is wrong.
2. **A paid Gemini key** would let image generation fill the rest with a style
   matched to the deck rather than to the emoji set. Check quota before promising
   anything; the free tier gave nothing.
3. **Latin coverage.** Both Latin decks are built. What they still lack is
   pictures: 46% and 35%. The uncovered head of the list is almost entirely
   abstract adverbs and particles — quasi, modo, scilicet, potius, ceterus,
   prius — which have no picture that is theirs rather than an illustration of
   some sentence they might appear in. Adding overrides for those would break
   the rule the decks are built on. The concrete nouns and verbs among the
   blanks are the ones worth a second pass.

### A gate that rejected good Chinese

The gloss checker called any text simplified if OpenCC's `s2t` changed it, and
`s2t` rewrites several characters that are already Traditional. 台 becomes 臺, so
「讀經台」 was refused eleven times running and `ambō` sat unglossed while the deck
refused to build. Worse, **祢 becomes 禰** — and 祢 is the Catholic second-person
honorific for God, which appears in nearly every prayer this project translates;
one of the readings is titled 《願祢受讚頌》. Every translation using it was being
thrown away and retried for ever.

Variants now pass individually while the line is otherwise clean, so 皇后 and
公里 are accepted and 以后我们 is still refused. 号 is deliberately not on the
list: that one really is simplified. Watch for this anywhere a
Traditional-Chinese gate is written as a round-trip comparison.
