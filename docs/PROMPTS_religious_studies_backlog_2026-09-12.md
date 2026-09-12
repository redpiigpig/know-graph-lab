# 未完成項的可執行 prompt（2026-09-12 盤點）

這一輪做完《基督宗教譜系學》全書六章、新開「當代神學研究」與「當代佛學研究」兩張卡、
建了四個語料庫與佛學辭典查詢介面之後，剩下的事整理成下面這些 prompt。

**用法**：開一個新 session，整段貼一個 ``` 區塊進去就好。每一則都寫成自足的——
背景、要做什麼、已知的坑、驗收條件都在裡面，不必先讀這份文件的其他部分。

**排序原則**：A 組不需要任何外部條件，隨時可做；B 組要等外部條件（到校、拿到檔案、
別人修完）；C 組要使用者本人裁定。

---

## A1. IxTheo 神學索引（不需校網，優先度最高）

```
在 know-graph-lab 這個 Nuxt 3 專案裡，替「當代神學研究」卡片（/research-data/contemporary-theology）
接上 Index Theologicus（IxTheo，德國圖賓根大學圖書館的神學期刊索引）。

先讀 .claude/skills/research-data-theology/SKILL.md 全文，那裡有這張卡的架構、
欄位規格、以及「已入館／缺」比對的兩個相反壞法。

為什麼這一項優先：這張卡的期刊論文層目前只有兩個來源——華藝（華語，1,073 筆候選）
與 DOAJ（開放取用，313 刊 104,491 篇）。IxTheo 收德語神學最完整，**而且本身免費開放、
不綁機構 IP**，所以不必等使用者到玄奘校內就能做。玄奘沒訂 ATLA（宗教研究的標準索引庫），
IxTheo 是目前能補上這個缺口的唯一一條。

要做的事：
1. 先確認取得方式。IxTheo 有 OAI-PMH 介面與 API，先探，不要一開始就爬 HTML。
   把實測結果（端點、可用欄位、有沒有速率限制、授權條款）寫進腳本檔頭。
2. 寫 scripts/ixtheo_harvest.py，架構比照 scripts/doaj_harvest.py：
   --journals / --articles / --index 三段，可中斷續跑，狀態落盤。
3. 篇目存 Drive G:/我的雲端硬碟/資料/知識圖工作室/_corpus/ixtheo/，
   索引存 public/content/research-data/contemporary-theology/ixtheo.json（進版控）。
4. 接進 pages/research-data/contemporary-theology/index.vue，比照 DOAJ 那一區的呈現。

🚨 已知的坑（doaj_harvest.py 踩過，這支很可能一樣）：
- 分頁 API 常有「深分頁上限」。DOAJ 是一個查詢最多 1000 筆、第 11 頁直接 400，
  照分頁抓到出錯就停會寫出一個剛好 1000 筆的檔案——數字整齊、不報錯、看起來完全正常。
  解法是用年份區間遞迴二分把查詢切小，**寫檔後一定要與整刊總數對帳**。
- 寫 Python 檔一律用 Write 工具，不要用 bash heredoc：heredoc 會吃掉一層反斜線，
  \\b 會變成退格字元寫進檔案，正則從此永遠不命中而且不報錯。

驗收：
- 跑得起來且數字合理；如果某一刊的篇數剛好是某個整數上限，先當成截斷去查，別當成事實。
- 抽查三筆的卷期與起訖頁，與 IxTheo 網站上該篇對照。
- npx vitest run 沒弄壞既有測試。

commit 訊息用繁體中文，結尾加 Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>。
```

---

## A2. 佛學卡的外文期刊層

```
在 know-graph-lab 裡，替「當代佛學研究」卡片（/research-data/buddhist-studies）
補上**外文**期刊論文層。華語那半已經做好了（1,487 筆候選），現在缺外文。

先讀 .claude/skills/research-data-buddhology/SKILL.md，
再讀 scripts/buddhist_studies_articles.py（華語那半，七區關鍵詞粗篩的作法）
與 scripts/doaj_harvest.py（外文期刊的抓法範本）。

目標刊物，按優先度：
1. Journal of Buddhist Ethics —— 全開放取用，1994 創刊，優先做。
2. Journal of the International Association of Buddhist Studies (JIABS) —— 舊卷開放。
3. Buddhist Studies Review —— 要先確認授權，可能綁訂閱。
4. 順手檢查 DOAJ 那 313 刊裡佛教類只有 2 種（LCC "Buddhism"），
   但可能有刊掛在 "Religion (General)" 底下其實是佛學刊——用刊名關鍵詞複查一遍。

要做的事：把篇目（題名／作者／卷期／起訖頁／年份／全文連結）抓成
Drive _corpus/buddhist-journals/ 底下的 jsonl，並產出
public/content/research-data/buddhist-studies/journals.json，接進該卡片頁面。

🚨 坑：
- 各刊的網站結構完全不同，不要寫成一支通用爬蟲，一刊一個 parser 更好維護。
- 授權要逐刊記在索引裡。開放取用 ≠ 可再散布，CC 也要看是哪一種（NC／ND 有差）。
- 別用 bash heredoc 寫 Python（會吃反斜線）。

驗收：每一刊抓回的篇數要與該刊網站自報的卷期數對得上；抽查近年與最早年份各一筆。
```

---

## A3. 兩張卡的中譯欄回填

```
在 know-graph-lab 裡回填兩張研究卡書目的「中譯本」欄位（zh）。

現況：
- data/research-data/contemporary-theology/bibliography.jsonl —— 186 筆，zh 只填了確知的幾筆
- data/research-data/buddhist-studies/bibliography.jsonl —— 248 筆，zh 只填了 7 筆

先讀 .claude/skills/research-data-theology/SKILL.md 與
.claude/skills/research-data-buddhology/SKILL.md 的「書目的欄位」一節。

作法：
1. 佛學那邊最大宗的來源是台灣華宇出版社「世界佛學名著譯叢」（100 冊），
   那一整套幾乎涵蓋了日文與西文佛學名著的中譯，整套比對一次效率最高。
2. 神學那邊查校園書房、道聲、光啟、基督教文藝、天道、漢語基督教文化研究所這幾家的書目。
3. 查不到就**留空**，不要填「可能有」或猜測的譯名。

🚨 這一項最重要的規矩：**寧可漏報不可誤報。** zh 欄一旦填了，
contemporary_theology_index.py 的比對與 z-lib 獵表都會據以判斷「這本有中譯可找」，
填錯會讓獵表去找一本不存在的書，而且不會有任何錯誤訊息。
不確定的一律留空並在 note 欄記下你查過哪裡。

🚨 譯名要過《翻譯定名》詞庫（/translation-glossary，theologians 等表）。
詞庫的 name_recommended 是絕對權威：若詞庫作「約翰‧史托得」，就不可以寫「斯托得」。

驗收：跑 python scripts/contemporary_theology_index.py --wanted 與
python scripts/buddhist_studies_index.py --wanted，確認獵表筆數合理下降；
jsonl 每行都能 json.loads，(author_zh, title_zh) 零重複。
```

---

## A4. 華藝候選篇目的人工複核

```
在 know-graph-lab 裡複核兩張研究卡的華語期刊論文候選清單。

現況：這兩份是**關鍵詞粗篩的候選，未經人工複核**——
- public/content/research-data/contemporary-theology/articles.json（1,073 筆，十二區）
- public/content/research-data/buddhist-studies/articles.json（1,487 筆，七區）

產生方式見 scripts/contemporary_theology_articles.py 與 buddhist_studies_articles.py 的檔頭。
一篇可以同時落在多區（刻意的），也必然有假命中。

要做的事：
1. 先量假命中率。每區隨機抽 20 筆，人工判斷是否真的屬於該區，算出各區的精確率。
2. 找出假命中集中在哪些關鍵詞上。已知可疑的：
   - 神學卡：「敘事」（〈《創世紀》第二章敘事賞析〉不是敘事神學）、「性別」、「公共領域」
   - 佛學卡：「女性」、「教育」、「政治」
3. 依量測結果調整 TERMS 詞表——**但不要把詞表改成只留高精確率的詞**，
   那會犧牲召回率而且看不出來。正解是把低精確率的詞移到一個 `weak` 清單，
   命中 weak 詞的篇目在 JSON 裡標 `"weak": true`，頁面上分開呈現。
4. 頁面上把各區的精確率抽查結果寫出來，讓讀者知道這份清單多可信。

🚨 判準：這一項的成果不是「清單變乾淨」，而是「**讀者知道這份清單有多不乾淨**」。
把假命中悄悄刪掉是最糟的結果——那會讓人以為剩下的都是真的。
```

---

## A5. 《基督宗教譜系學》的 ⚠️ 註腳升級

```
在 know-graph-lab 裡處理《基督宗教譜系學》（/works/christian-genealogy）書稿中
標了 ⚠️ 的註腳。

先讀 .claude/skills/works-christian-genealogy/SKILL.md 全文。

背景：全書 136 條註，其中一批標了 ⚠️（「依通行版本著錄，未逐頁核對」或
「該書未入館」）。第6章與第1章第四節佔最多，因為二十世紀的二手研究館內幾乎全缺——
烏斯諾、亨特、貝賓頓、拉森、安德森、莫特曼、巴特、齊齊烏拉斯、阿薩德查館皆為 0 筆。

要做的事：
1. 先跑一次盤點：把 CG.html 裡所有含 ⚠️ 的註列出來，分成三類——
   (a) 書已入館只是沒核頁碼 →直接用 scripts/genealogy_research.py 查全文補頁碼
   (b) 書不在館但已在 data/zlib-wanted/denominational-genealogy.jsonl（76 筆）→等抓到
   (c) 書不在館也不在獵表 →補進獵表
2. (a) 那一類逐條補。⚠️ genealogy_research.py 回傳的頁碼是 chunk 起始頁不是該句所在頁；
   長篇著作改標章名，別硬掛頁碼（Schaff 那幾卷分段細，頁碼可用）。
3. 改完跑 python scripts/christian_genealogy_build.py，並複查註釋三方對齊。

🚨 這條線特有的坑（全在 SKILL.md 的「看起來成功的失敗」一節）：
- 註腳可以「數量對、內容錯」——改過稿就抽查中間幾節，別只看頭尾。
- 節檔裡的註釋條目順序是書寫順序，改動後會與引用順序錯開；連號與三方對齊照樣通過，
  只有清單變成 1、2、8、5、6⋯⋯。build.py 的 sort_fn_items() 已會在連號後排序。
- 正文裡**不可以寫死註碼**（「見註 12」），全書連號時會失效；要寫「見第六節」。
```

---

## A6. 辭典查詢介面的授權逐部複核

```
在 know-graph-lab 裡複核佛學辭典查詢介面（/research-data/buddhist-studies/glossaries）
各部辭典的授權狀態。

現況：data/research-data/dila-glossaries.json 裡十五部各有一個 rights 欄，
四類：public-domain / cc / by-permission / unstated。這是腳本從法鼓網頁抓的字樣自動判的，
**unstated 那幾部要人工看過**：

- PLC 巴利—漢語辭典（10,599 條）
- PLGE 巴利文法語尾變化數位索引
- SKME 梵語手冊語尾變化數位索引
- NSL 釋智諭《南山律學辭典》（3,218 條）
- SHH 蘇慧廉—何樂益《中國佛教術語辭典》（16,792 條）—— 1937 年出版，
  Soothill 卒 1935、Hodous 卒 1959，原書在台灣可能已過保護期，但法鼓那個數位版的權利要另外看

要做的事：逐部去法鼓網頁（https://glossaries.dila.edu.tw/glossaries/<code>）與
出版方確認，把 rights 改成確定的值，並在 license 欄寫下依據。
頁面 pages/research-data/buddhist-studies/glossaries.vue 頁尾的授權說明要跟著改。

🚨 規矩：**抓不到授權字樣不等於沒有限制，不可以預設「沒寫就是自由」。**
辛嶋靜志那五部與霍普金斯、Tibskrit 寫的是「經作者同意由法鼓數位化」——
那是授權法鼓建資料庫，不等於授權我們再散布。這個區分要保住。
```

---

## A7. /tripitaka 與佛學研究卡的互指

```
在 know-graph-lab 裡把《佛教大藏經》（/tripitaka）與「當代佛學研究」卡片
（/research-data/buddhist-studies）互相連起來。

先讀 .claude/skills/scripture-tripitaka/SKILL.md 與
.claude/skills/research-data-buddhology/SKILL.md。

現況：兩邊完全沒有連結。一位讀者在讀《法華經》時，看不到站上有辛嶋靜志的
《正法華經詞典》《妙法蓮華經詞典》（各 3,356／2,409 條，已在辭典查詢裡），
也看不到華藝那 1,487 筆候選論文裡與法華相關的幾十篇。

要做的事：
1. 經 → 研究：某部經的 reader 頁側邊加一區「相關研究」，
   用經名去比對 articles.json 的篇名與 bibliography.jsonl 的 note。
2. 研究 → 經：辭典查詢與書目那邊，提到某部經時連回 /tripitaka 的該部。
3. 古代辭書那一塊要指路：《一切經音義》《翻譯名義集》《翻梵語》《釋氏要覽》
   本來就在大正藏事彙部（合計約 4.9 萬段），不在法鼓那批裡——
   讀者常以為辭典只有近現代那些。

🚨 坑：經名比對不能只用全名。《妙法蓮華經》《法華經》《正法華經》是三個不同的譯本
但常被混用；配錯的呈現會「頁面完全正常而內容張冠李戴」，是這個 repo 最常見的
一類錯（見 feedback_reader_silent_failures）。先做一張經名別名對照表，別靠字串包含。
```

---

## B1. 到玄奘校內之後：訂閱庫實測與第一支抓取程式

```
在 know-graph-lab 裡，處理玄奘大學訂閱資料庫的實測結果。

**前提：這一項要在連上玄奘校內網路時做**，或先確認
scripts/state/campus_probe.json 裡已經有校內實測的結果。

先讀 .claude/skills/research-data-theology/SKILL.md 的「校內訂閱庫：先探測再動手」一節，
與 data/research-data/hcu-harvest-plan.json（分級計畫）。

要做的事：
1. 跑 python scripts/campus_probe.py，讓它把 hcu-harvest-plan.json 裡每個 tier B
   目標的 access 欄從 unknown 換成實測值（granted / partial / denied / unclear / error）。
2. 看結果決定先寫哪一支抓取程式。對神學最有價值的順序是：
   ProQuest Arts & Humanities → Project MUSE → De Gruyter → Cambridge Companions。
3. 寫第一支。架構比照 scripts/press_airiti.py（那支已經在跑，含機構身分探測、
   6 秒節流、每日額度上限、帳本）。

🚨🚨 最重要的一條：**只抓篇目索引與人工速率的選擇性全文下載，不做整庫鏡像。**
訂閱庫的大量下載會被當成異常流量，而處置是停**整個機構**的權限——
華藝那條管線已經記過這件事。節流秒數是對機構的承諾，不是可調參數。

🚨 排程的四條硬規矩（全都踩過，全在 SKILL.md）：
.ps1 必須純 ASCII（PowerShell 5.1 遇中文註解會解析崩且行號對不上）、
-AllowStartIfOnBatteries（人在學校時筆電正在用電池，預設的「使用電池時不啟動」
會讓排程從設計上就跑不到）、觸發器要 Daily 不能 Once＋重複（重複期用盡後再也不觸發
而 State 仍是 Ready）、python 要走 Start-Process 拿自己的隱藏主控台
（共用 console 會被別人的 Ctrl+C 帶走，而排程器回報成功）。
```

---

## B2. 佛光大辭典：拿到資料檔之後

```
在 know-graph-lab 裡把《佛光大辭典》收進佛學辭典查詢介面。

**前提：使用者已取得佛光山授權，並且拿到了資料檔**（XML／資料庫／app 詞庫／掃描 PDF
任一種）。若還沒有檔案，先不要動——理由見下。

先讀 scripts/fgs_dictionary_fetch.py 的檔頭，那裡記了目前的狀況與已解決的技術細節。

現況：已從官網抓到 1,997 條（共約 22,600 條），然後停手了。停的理由不是技術問題——
分頁機制已經解開（ASP.NET GridView，__EVENTARGUMENT=Page$N，而且**翻頁必須把查詢字
一起送回去**，少了它伺服器會拿空字串重查、回 0 條，於是每個字都剛好收到 20 條，
看起來像「這個字只有 20 個詞目」）。停的理由是**官網沒有詞目索引頁**，
只能用「字集閉包」枚舉（約 3,800 字、估計 8,000 次請求），而站方在重負載後
持續回 URLError——單一個「法」字就要翻 63 頁。在別人伺服器上敲八千次請求，
既慢又不禮貌，而授權持有者通常可以直接要到資料檔。

拿到檔案之後要做的事：
1. 解析成 Drive _corpus/fgs-dictionary/entries.jsonl，欄位比照法鼓那批：
   {"term": ..., "variants": [...], "domain": [...], "definition": ...}
2. 在 server/utils/glossaries.ts 的 GLOSSARY_NAMES 加一筆，並確認它被
   loadGlossaries() 讀進來（那支是 file-backed，首次查詢才載入記憶體）。
3. 授權狀態寫進 data/research-data/dila-glossaries.json（或另開一個索引），
   註明「經佛光山授權」與授權範圍。

🚨 驗收時**不要只看條數**。這一輪在法鼓那批上踩過：條數全對而近兩萬八千條的釋義
是空字串，因為各部放釋義的標記不同（<def> / <sense> 混合內容 / <p>）。
抽查一定要看「有釋義的比例」。佛光大辭典官方自報約 22,600 條、360 餘萬字，
用字數對帳比用條數對帳可靠。

若最後仍拿不到檔案而使用者要求續抓：腳本可中斷續跑（state.json 記已查字與已收詞目），
但請把 DELAY 調大到 4 秒以上，並改成每輪只跑 100 個字、靠排程分很多天跑完。
```

---

## B3. 教父三欄那個紅測試（別人的線，先確認沒人在動）

```
在 know-graph-lab 裡修 test/fathers-original-render.spec.ts 的失敗案例。

**先確認沒有別的 session 正在改這條線**（git log 看最近的 fix(fathers) commit 時間，
並看 docs/ 底下有沒有相關的 SESSION_HANDOFF）。這條線 2026-09-11 當天有多個 session
在動，貿然介入會互相蓋掉。

失敗案例：「居普良 論述集 第195章」→ 沒有原文欄（sources.la 是空字串）。
查證過的範圍：ebook 0e08c662-540b-4186-b250-9bca0cfe1002（居普良＋諾瓦提安，428 段）
**只剩 3 段有拉丁欄，全是諾瓦提安**；居普良那 59 段的拉丁欄全空。
而前一筆 commit 的訊息寫的是「重切要對『起點相同的段』去重，十九本全綠」——
居普良顯然不在那個「全綠」裡，或是那次重切之後才掉的。

先讀 .claude/skills/scripture-fathers/SKILL.md 與
docs/ 底下最新的 fathers 交接文件。

🚨 這個測試讀的是 Drive 的 _chunks/*.jsonl，不是 repo 裡的程式。所以它紅不代表
程式壞掉，可能是資料層的狀態——但 pre-push hook 分不出這個差別，會擋住所有人的 push。

驗收：npx vitest run test/fathers-original-render.spec.ts 43 例全過，
且不是靠把那個案例從 CASES 移除。
```

---

## C1. 十五個人名要不要立條（使用者裁定）

```
（這一則不是給新 session 的 prompt，是等使用者回覆的問題。）

《基督宗教譜系學》第6章與第1章新增的人名，有一批《翻譯定名》詞庫（/translation-glossary
的 theologians 表，496 筆）裡還沒有條目。書裡暫用的譯名如下，要照這些立條，
還是有哪幾個要換？

烏斯諾（Robert Wuthnow）／亨特（James Davison Hunter）／拉森（Timothy Larsen）／
貝賓頓（David Bebbington）／安德森（Allan Anderson）／葛理翰（Billy Graham）／
麥金泰爾（Carl McIntire）／阿法納西耶夫（Nicholas Afanasiev）／
維瑟特‧霍夫特（W. A. Visser 't Hooft）／勒菲弗（Marcel Lefebvre）／
沙努達（Shenouda III）／丁克哈（Mar Dinkha IV）／杜里安（Max Thurian）／
維舍爾（Lukas Vischer）／特爾慈（Ernst Troeltsch）

⚠️ 為什麼不自己立：詞庫的 name_recommended 是絕對權威，拿我的草稿去灌它，
等於把權威來源倒過來。使用者定奪之後再寫入。

另外，宗教改革以後的新教人物（施本爾、親岑多夫、懷特菲爾德、愛德華茲⋯⋯）
詞庫多半也還沒有條目，同一批處理。
```

---

## C2. 全書配圖（使用者裁定）

```
（等使用者裁定的問題。）

《基督宗教譜系學》送印前要決定配圖。現況：

- 雜誌原稿有 28 張圖，多為 OpenAI 生成的示意圖。
- 改寫稿**一張圖也沒有**——組稿時刻意不引原稿的 figure。
- 其中 11 張在雜誌 DB 裡是佔位符（第10期那篇的 [[圖片N]] 沒有對應的 media_data，
  Drive 第10期圖片夾也沒有 10-14-*），圖說仍留在原稿裡可從 DB 取回。

書裡最需要圖的幾處，按優先度：
1. 第1章第六節的四事件／四單位表 → 已是表格，可能不需要圖
2. 第4章的七個大公傳統分化圖 → 這是全書的核心圖，一定要有
3. 第5章的新教八大宗派系統圖 → 原稿有，但是生成圖
4. 第6章第八節的三層地圖 → 概念圖，值得專門畫
5. 第1章第六節新增的四條譜系延續圖 → 縱向的線，適合畫

要決定的是：自己畫（可以寫成 SVG 進版控）、找人畫、還是沿用生成圖。
⚠️ 生成圖用在學術書裡要考慮兩件事：授權，以及圖裡常有無法察覺的錯字與錯誤細節。
```

---

## 這一輪已完成、不必再做的事

寫在這裡是為了避免下一個 session 重做：

| 項目 | 現況 |
|---|---|
| 《基督宗教譜系學》六章 | ✅ 116,866 字、136 註，含第6章 2.3 萬字與現象學那一節 |
| 術語全書統一 | ✅ 兩套事件名說破、補上第四層「教派」、四處交叉引用修好 |
| 當代神學研究卡 | ✅ 186 筆／12 區＋吉福德 210 場＋華藝 1,073 篇＋DOAJ 313 刊 |
| 當代佛學研究卡 | ✅ 248 筆／7 區＋華藝 1,487 篇（外文期刊層待做，見 A2） |
| 佛學辭典查詢 | ✅ 12 部 103,019 條，/research-data/buddhist-studies/glossaries |
| 普世運動語料 | ✅ 1,451 份／4.02 億字 |
| 洛桑運動語料 | ✅ 109 份／1,009 萬字 |
| 愛丁堡 1910 語料 | ✅ 137 份／8,918 萬字（已登記進 CORPORA，查得到） |
| DOAJ 篇目 | ✅ 313 刊／104,491 篇，每週一 05:00 自動刷新 |
| 玄奘訂閱庫盤點 | ✅ 150 筆分三級，KGL_Campus_Probe 排程已上線待到校 |
| 聖經原文辭典 11 本 | ⏳ 已在 OCR 佇列（日排程 10/14/18 會自己處理），不必手動介入 |
