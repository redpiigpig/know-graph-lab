---
name: hcu-hcjbs-journal
description: 《玄奘佛學研究》學報**公開官網**的建置與維護 —— 這是使用者在玄奘大學的職務工作（學報編輯），不是弘誓的研究資料。兩處成品：①模擬站 `redpiigpig.com/Hsuan_Chuang_Studies`（本 repo `pages/Hsuan_Chuang_Studies/`，封面牆＋各期篇目＋五個章則頁）②正式站＝**玄奘校網「臺灣佛教研究中心」底下既有的《玄奘佛學研究》**（後台帳密見 `.env` 的 `HCU_WEB_CMS_*`；2026-09-20 已補上 44、45 期與五個章則頁）。章則內容一字不自撰，正本是編輯室交來的「英網-N」docx。🚨 只動這個中心站：**宗教與文化學系站（也有一份 1–45 期）不是我們的、帳號也進不去**，中心站其他單元除了建連結一律不動。Use when 要更新投稿指引／編輯委員／審查流程／學術倫理／AI 使用規範任一頁、編輯室給了新版 docx、要補抓新一期篇目與封面、要把模擬站搬上校網後台、或使用者提到「學報網站」「玄奘佛學研究官網」「英網」「臺灣佛教研究中心的網站」。與 [[research-data-hongshi]] 的分工：那邊是需登入的研究資料層 `/research-data/yinshun-hongshi/xuanzang`（全文語料、給論文用），這邊是對外的學報門戶。
---

## 學報在校網有**兩個**家，加上我們的模擬站共三處

| | 網址 | 誰能改 | 現況 |
|---|---|---|---|
| **中心站（正式站）** | `www.hcu.edu.tw/buddhism/buddhism/zh-tw/43C51435…/B975569C…/` | **我們**（`.env` 的 `HCU_WEB_CMS_*`） | 1–45 期＋五個章則頁（2026-09-20 補齊） |
| 宗教與文化學系站 | `www.hcu.edu.tw/ird/ird/zh-tw/religious-journal/`（**結尾斜線不可省，否則 404**） | 系上帳號，**我們沒有權限** | 1–45 期，PDF 都在那；45 期有五篇連結是壞的 |
| 模擬站 | `redpiigpig.com/Hsuan_Chuang_Studies`（`pages/Hsuan_Chuang_Studies/`） | 我們 | 定版面與內容用，給使用者先看 |
| 研究資料層 | `/research-data/yinshun-hongshi/xuanzang`（需登入） | 我們 | 45 期 304 篇全文語料，論文用，見 [[research-data-hongshi]] |

🚨 **只動臺灣佛教研究中心這個站。** 宗教系站不是我們的（帳號也進不去）：那邊 45 期五篇
PDF 被貼成編輯者的 `file:///C:/Users/…/學報核銷/45期玄奘學報/…pdf` 本機路徑、抓不到，
**我們不修、也不繞過去改它**，要修得找系上的網頁管理人。
中心站上別的單元（中心簡介／顧問／專案活動／相關法規…）同樣不動，除了替我們的頁面建連結。

🚨 **維護兩份目次的代價已經現形**：中心站原本停在 43 期、系站到 45 期，而系站那五個壞連結
沒人發現。結論是**正本只留一份、另一邊放連結**；真要兩份，那第二份必須由腳本生成
（`hcjbs_issue_harvest.py` → `hcjbs_cms_issue_html.py`），不可手抄。

## 頁面結構（模擬站現況）

```
/Hsuan_Chuang_Studies              index.vue        封面牆，每期一張封面（400×560）
/Hsuan_Chuang_Studies/issue/[n]    issue/[n].vue    該期篇名／作者／頁數／官方 PDF
/Hsuan_Chuang_Studies/editorial-team               編輯委員（名單表＋逐位簡歷收折）
/Hsuan_Chuang_Studies/submission                   投稿指引（徵稿啟事＋格式要點全文）
/Hsuan_Chuang_Studies/review-process               審查流程（含雙審查決策矩陣）
/Hsuan_Chuang_Studies/ethics                       學術倫理聲明
/Hsuan_Chuang_Studies/ai-policy                    生成式 AI 使用規範
```
共用版頭版尾：`components/HcjbsHeader.vue`（含導覽列 `nav` 陣列與中英切換）、`HcjbsFooter.vue`。

**字體規則**：**英文字與數字一律 Times New Roman**。作法是把 Latin 放在字體堆疊最前、
中文字體放後面（瀏覽器逐字元回退），例如
`font-family:'Times New Roman',Times,'Microsoft JhengHei',sans-serif`、
內文容器 `'Times New Roman',Times,DFKai-SB,標楷體,KaiTi,serif`。
🚨 **不要再寫 `Arial`**——2026-09-19 全站掃過一次改掉了，新頁別又帶回來。

## 🚨 各篇 PDF 的取源順序：先看本機，最後才去爬頁面

**本機就有全部 304 篇**（45 期逐篇），不要一開始就去爬宗教系頁面：

| 順位 | 來源 | 說明 |
|---|---|---|
| ① | Drive `G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\玄奘佛學研究\` | **304 個 PDF**，檔名 `玄奘佛學研究-v<期號兩位>-<10位雜湊>.pdf` |
| ② | `public/content/research-data/yinshun-hongshi/xuanzang-index.json` | 期→逐篇的對照表（`title`／`author`／`pdfKey`／`hasFulltext`），`pdfKey` 就是上面那個檔名 |
| ③ | `public/content/Hsuan_Chuang_Studies/issues.json` | 模擬站用的那份，裡面存著**早先抓到、仍然有效的** hcu 連結 |
| ④ | 宗教系該期頁面 | 最後才用；**它的連結會壞** |

🚨 **「頁面上沒有連結」不等於「檔案不存在」。** 第 45 期七篇裡有五篇，宗教系頁面現在寫的是
編輯者本機路徑 `file:///C:/Users/…/學報核銷/45期玄奘學報/…pdf`，我因此回報「五篇拿不到」——
**錯的**：檔案都在伺服器上，只是檔名跟頁面上那串不一樣，`issues.json` 裡的舊網址七篇全部
200 下載得到（另外 Drive 也有）。下次遇到非 http 連結，照上表往前一順位找，不要直接宣告缺件。

## 各期資料層：`scripts/hcjbs_journal.py`

資料同源 hcu.edu.tw（非 Cloudflare，純 requests 即可）。逐期解析篇目
（`strip_en` 裁尾端英譯、封面升 400×560 存 `public/Hsuan_Chuang_Studies/covers/`）→
`public/content/Hsuan_Chuang_Studies/issues.json`，頁面直接 `import`（SSR 友善；PDF 熱連 hcu 官方）。

重跑：`python -X utf8 scripts/hcjbs_journal.py`（封面已存則跳過）。

## 章則五頁：正本是編輯室給的「英網-N」docx

章則內容**一字不許自撰**。正本 Word 放 `stores/玄奘佛學研究/`（`stores/*` 不進版控），
頁面下方下載鍵走 `server/api/xuanzang/download.get.ts` 的 `FILES` 對照表：

| 頁面 | `?file=` | 正本檔（2026-09-19 這批） |
|---|---|---|
| `submission` 投稿指引 | `submission` | 英網-1 投稿指引(徵稿函).docx |
| `editorial-team` 編輯委員 | `editorial` | 英網-2 編輯團隊資訊.docx |
| `ethics` 學術倫理 | `ethics` | 英網-3 草擬學術倫理聲明**260425** |
| `ai-policy` AI 使用規範 | `ai` | 英網-4 學報AI使用規範**260904** |
| `review-process` 審查流程 | `review` | 英網-5 期刊審查流程260213 |

換新版的動作：新檔複製進 `stores/玄奘佛學研究/`、改 `FILES`、刪掉舊日期那份、
再逐頁把頁面內容對齊新檔（**逐段點名，不是掃一眼**）。

### 四個踩過的坑

🚨 **檔名編號會整批位移。** 2026-09 新增的 AI 規範佔了「英網-4」，原「英網-4 期刊審查流程」
被推成「英網-5」——只按編號對檔會讓審查流程頁改去下載 AI 規範。**對照要認檔名的內容詞，
不要認編號。**

🚨 **章則頁會出現「看起來像官方文件、其實抄錯」的表。** 審查流程頁的雙審查決策矩陣曾有兩列
與正本相反（「修改後再審 × 不推薦刊登」正本是**不推薦刊登**、頁面寫成第三位審查；
「不推薦刊登」那一列前三格整排錯位）。**正本矩陣沿對角線對稱，錯的那版不對稱**——
改完拿 docx 的表逐格點名，別只確認「有那張表」。

🚨 **docx 的名單表與個人簡歷會互相打架。** 林朝成、葉海煙的服務機構兩處不同。
表格欄位**一律以 docx 的名單表為準**（那是學報版權頁印出去的那一份），簡歷內文照原文保留。

🚨 **docx 的措辭改不改，問老師、不要自己決定。** AI 使用規範原文寫「⋯學生使用相關工具時⋯」，
讀起來像從校內規章沿用過來的。第一輪使用者要求照原樣保留，隔天老師指示**改成「作者」**
（2026-09-19 已改，中英兩版）。所以這類「讀起來怪但寫在正本裡」的字，做法是**標出來問**，
既不自行修順、也不當它一定不能動。

### 內容規格備忘

- 徵稿啟事的專輯表隨期次滾動：已出刊的期次要**刪掉**，新公告的期次要補上
  （2026-09 這次刪 45／46 期、補第 56 期 劉宇光教授／當代東南亞上座部佛教）。
- 投稿信箱 `hcu10@hcu.edu.tw`＋副本 `part55410@gmail.com`；聯絡人堅意法師。
- 每年兩期，上半年 3 月 30 日、下半年 9 月 30 日出刊。
- 編輯委員：總編輯釋昭慧＋委員 13 位（依姓氏筆畫），機構與專長見 `editorial-team.vue` 的
  `members` 陣列；簡歷只做中文，英文版僅名字與機構。

## 上稿到校網後台：整條路徑與四個坑（2026-09-20 走通）

後台 `https://www.hcu.edu.tw/backend/login.aspx`，帳密在 `.env`：
`HCU_WEB_CMS_URL`／`HCU_WEB_CMS_USER`／`HCU_WEB_CMS_PASS`（原本鍵名是 `path`／`accuant`／
`password`，2026-09-19 改名）。這是 ASP.NET 的「節點管理／內容管理」型 CMS，**沒有「網站」這種
單位**：每一頁都是節點或節點底下的一篇內容，靠 nav 一層層點下去。學報各頁都掛在同一個節點：
`rid=B975569CC2F04819892552ADE1A9090E`（公開網址裡那段 GUID 就是 rid，可直接拼後台網址）。

整套腳本（都在 `scripts/`，一律只動點名的那一篇／那個檔）：

| 腳本 | 做什麼 |
|---|---|
| `hcu_cms_login.mjs` | 登入並把 cookie 存到 `c:/tmp/hcu-cms/state.json`。**登入頁有圖形驗證碼**，所以它把驗證碼存成 `captcha.png` 後等 `captcha.txt`——讀圖、把答案寫進去，腳本自己續跑 |
| `hcu_cms_browse.mjs <後台URL>` | 只讀：把某頁的表格／連結／下拉選單撈出來 |
| `hcu_cms_article_dump.mjs <id｜NEW> <rid>` | 只讀：某篇的表單欄位與內文 HTML 原稿（拿既有一期當範本） |
| `hcu_cms_upload_files.mjs <資料夾>` | 上傳 PDF 到中心站檔案庫；`--list` 列現有檔；`--delete "<檔名>"` 只刪點名的 |
| `hcjbs_issue_harvest.py N…` | 從系站讀某幾期的**中英篇目**並下載 PDF（模擬站的 issues.json 把英譯裁掉了，不能用） |
| `hcjbs_cms_issue_html.py N…` | 產生各期頁 HTML（照 43 期版面） |
| `hcjbs_cms_rule_pages.py` | 產生五個章則頁 HTML（內容正本＝英網-N docx） |
| `hcu_cms_publish.mjs --node <rid> --title … --html … --date … --publish` | 新增或修改一篇並發布（`--id` 改既有、`--dry` 不存檔） |
| `hcjbs_cms_verify.py` | 稽核：抓公開頁逐項點名關鍵字、逐個下載 PDF 驗 `%PDF` |

**表單欄位**：`Title`／`DisplayDate`／`PublishDate`（生效）／`ArchiveDate`（過期）／
內文 `ucArticle$ctl07$Modify$Content$1`（新增時是 `…$Add$Content$1`，要先按
`#ucArticle$ctl07 a.bottom-add`「增加內容」才長出來）。發布是頁面的 JS `PublicEditor(id, rid)`。

🚨 **CKEditor 的 instance key 是欄位 `name`，不是 `id`**——這些 textarea 根本沒有 id。
用 id 找會找不到 instance、於是退回塞裸 textarea，**送出時 CKEditor 拿它自己的（空）內容
覆蓋回去，存出來一片空白**。灌完一定要 `getData().length` 讀回來確認。

🚨 **儲存鈕有兩顆同名的**：`#btnSubmit`（type=submit，被 CSS 藏起來）與 `#btnSubmit2`
（type=button，看得見、會先跑前端驗證）。點前者會卡在 element is not visible 直到逾時。

🚨 **生效時間沒到＝公開端 404，而後台看起來一切正常。** 第一次上稿把 `PublishDate` 設成當天
08:00，當時才凌晨，後台狀態是「等待」、五個頁面公開端全 404——不回頭抓公開頁根本看不出來。
設成已經到的時刻（`T00:00`）就轉「生效」。`ArchiveDate` 預設「一年後」，要改 9999 年，
否則一年後整頁自己消失。

🚨 **檔案庫上傳會把檔名裡的英文字母轉小寫**（`Loka…`→`loka…`、`Could AI-…`→`could ai-…`），
連結要照**檔案庫列出的實際檔名**寫，照本機檔名寫會 404。檔名清單是 ajax 畫進 `#content` 的縮圖、
檔名在 `<p class="caption">`；用 `a[href]` 去撈會得到 0 個——而「0」看起來很像「檔案庫是空的」。

🚨 **英文與數字要 Times New Roman 就得逐段切 run**（`hcjbs_cms_rule_pages.py` 的 `runs()`），
整段給標楷體的話英文會用標楷體的西文字形。切 run 的字母類**不能只寫 `A-Za-z`**：
`Günzel` 的 `ü`、梵巴轉寫的 `ā ṃ` 會被當成非英文而掉進標楷體 span，畫面上就是一個字母突然
換字體（發生過一次，範圍已擴到 Latin-1／Extended-A/B／Extended Additional）。

### 2026-09-20 上稿結果（八頁，全部發布並稽核全綠）

**節點結構**（都在「資料庫 › 玄奘佛學研究」底下）：

| 頁面 | 型別 | id／rid |
|---|---|---|
| 玄奘佛學研究（首頁＝封面牆） | 列表節點 | `B975569CC2F04819892552ADE1A9090E` |
| 第四十四期 | 該節點的內容 | `DE09FA1EDAB748D7A8FAE8E8CA57EE7B` |
| 第四十五期 | 該節點的內容 | `34BD6FE105FA42A583802ACC00D32151` |
| 編輯委員 | 子節點（單頁） | `28DBE4BB84354651ADB043FED6A1FAAE` |
| 投稿指引 | 子節點（單頁） | `963E07CC70054A9191713195B7E233A5` |
| 審查流程 | 子節點（單頁） | `25E6418CEC0E4A69AF569743EA6FDF43` |
| 學術倫理 | 子節點（單頁） | `3D19104FF4CE46AC8F619F4F110BB884` |
| 生成式人工智慧（AI）使用規範 | 子節點（單頁） | `430E878E0E0E409B96DBB8361E9FE95E` |

🚨 **章則頁一定要是「子節點」，不能當成各期清單裡的內容。** 第一版把五個章則做成
「玄奘佛學研究」節點底下的**內容**，結果它們跟 45 期期刊混在同一份清單裡（被退）。
改成子節點後，nav 上各自一項、清單只剩 45 期。

🚨 **兩種節點的內容編輯器不一樣，走錯就找不到欄位。**
- **單頁節點**（`Template=~/template/SingleData.aspx`）：`NodeContent.aspx?rid=…`，
  用 `hcu_cms_node_publish.mjs`。用 ArticleEditor 會因為沒有 `Title` 欄位而逾時。
- **列表節點**：`NodeContent.aspx` 會被轉回 `ArticleList.aspx`；它的節點內容在
  `NodeContentDialog.aspx`，而且要從清單頁的「節點內容」連結點開，用 `hcu_cms_node_dialog.mjs`。

**建節點**：樹上右鍵 →「建立」→ `NodeEditor.aspx?rid=<父節點>`（**rid 不是 id**，
而且直接打網址會被轉回 NodeList，一定要走 UI）。單頁節點填 `Title`、`IsList=false`、
`Template=~/template/SingleData.aspx`。腳本：`hcu_cms_node_create.mjs`。

## 版面：一律照模擬站（`hcjbs_cms_style.py`）

使用者的要求是「除了校網母頁的 nav，底下全部照模擬站的 UI」。共用元件在
`scripts/hcjbs_cms_style.py`，三條硬規則：

1. **全白底**。照舊期 Word 表格抄來的 `#DBE5F1` 淺藍列底被退過一次。
2. **英文與數字 Times New Roman**：外框 div 給
   `'Times New Roman',Times,DFKai-SB,標楷體,KaiTi,serif`，靠瀏覽器逐字元回退即可，
   不必逐段切 span。
3. **每頁帶區內導覽**（研究學報｜編輯委員｜投稿指引｜審查流程｜學術倫理｜AI 使用規範）：
   母頁 nav 只到「資料庫」，這五頁在第三層，頁面上看不到彼此。

🚨 **不要自己再印一次頁面標題**：CMS 的樣板已經把節點名稱／篇名與日期印在內容區上方，
再印一次就是同一個標題連著出現兩遍（各期頁與封面牆都犯過）。

🚨 **各期頁不放「玄奘大學原始頁」連結**——那是模擬站連回校網用的，正式站上沒有意義。

### 首頁封面牆與「圖片列表」版型

封面 45 張上傳到**圖片庫**（`hcu_cms_upload_files.mjs --images`，公開路徑
`/upload/userfiles/<rid>/Images/cover-NN.jpg`；檔案庫是 `…/files/`，兩個不同端點）。
封面牆 HTML 由 `hcjbs_cms_issue_html.py --wall` 產生，放進列表節點的節點內容。

該節點原本 `ListTemplate=~/template/URLList.aspx`（純文字連結清單），封面牆放上去後
文字清單會在下面重複一次。處置是把 `ListTemplate` 改成 `~/template/Images.aspx`
（圖片列表）：因為 45 篇都沒掛圖片，那份清單就整個不顯示，首頁只剩封面牆。

🚨 **`ListTemplate` 不可清空**——清空會讓整個節點頁 404（試過，已還原）。
🚨 **改完版型頁面會 404 一兩分鐘**（伺服器重建），不是壞掉，別急著回滾。
🚨 **副作用：以後新增一期，CMS 清單不會自動顯示它**（圖片列表只畫有圖的文章）。
   新增一期就要重跑 `--wall` 並更新節點內容，否則首頁上點不到新那期。

### 頁尾的 Word 附件

五個章則頁的頁尾都掛一份 Word（`hcjbs_cms_docx.py` 產生）：用最新版內容、但檔名改成
正式文件名稱（去掉「英網-N」批號與日期），AI 規範那份的「學生」依老師指示改成「作者」。
上傳走節點內容的「附件」區（`hcu_cms_node_publish.mjs --attach`）。

🚨 **附件的「描述」是必填**，空著的話後台看得到檔、公開頁的「相關附件」區卻是空的。
🚨 **公開頁的附件連結是 `/buddhism/Download.aspx?aid=…`，不是 `.docx` 網址**——
   稽核拿 `.docx` 去比會把五頁全報成「缺附件」（誤報過一次）。

待補：45 期那五篇 PDF 要向編輯室（使用者本人）拿原檔，上傳後重跑 `hcjbs_cms_issue_html.py 45`
再覆蓋該篇。

## 版面規格（使用者逐條定下來的，改頁前先看這裡）

元件都在 `scripts/hcjbs_cms_style.py`，**六個頁面共用**（封面牆／45 期／五章則）：

1. **不寫背景色**：站上本來就是白底；填色（淺藍／灰列底）一律不要。
2. **英文與數字 Times New Roman**：外框 div 給 `'Times New Roman',Times,DFKai-SB,標楷體,KaiTi,serif`。
3. **區內導覽**（研究學報｜編輯委員｜投稿指引｜審查流程｜學術倫理｜AI 使用規範）每頁都要，
   **沒有下邊線**、每格之間與**最左最右兩端**都有直線、線寬一律 **2px**，
   而且**目前所在那一項也要能點**（否則各期頁點「研究學報」沒反應）。
4. **敘述段落首行空兩格**（`text-indent: 2em`）；粗體小標、置右行、條列子項不加。
5. 投稿指引的「＊聯絡人⋯堅意法師」**置右**。
6. **頁內不要自己再印一次頁面標題**：CMS 樣板已經印過節點名稱。
   例外是各期頁與封面牆——見下一節。

### 各期頁的三個藏標題招數

CMS 的內容樣板在我們的內容**之前**印三樣東西，順序改不了，所以用 CSS 藏掉、由我們自己印：

| 藏掉 | 為什麼 |
|---|---|
| `.news_detail_container h2` | 它印的節點名稱「玄奘佛學研究」**不是連結**；我們要能點回封面牆 |
| `.news_detail_container .news_title` | 篇名要排在區內導覽**下面**（使用者指定） |
| `.news_detail_container .datetime` | 出版日期我們自己排在篇目表尾 |
| `.photo_list_container`（封面牆那頁） | 裡面是再印一次的節點名稱＋空清單＋分頁條 1 2 3 4 5 |

🚨 **分頁條關不掉，只能藏。** 節點設定沒有「不要清單」的選項：`ListTemplate` **清空會整頁 404**，
`Extra1` 改 999 也沒用；把 `Template` 改成 SingleData 更糟——各期頁會全部變成顯示封面牆
（做過、已還原）。可行的組合是 `Template=~/template/URL.aspx` ＋
`ListTemplate=~/template/Viedo.aspx`（影片列表不畫沒有影片的文章，清單就空了）＋ 上面那段 CSS。
🚨 **改完版型頁面會 404 一兩分鐘**（伺服器重建），不是壞掉。

## 既有 45 期全部換新版面：`hcjbs_cms_restyle.py`

資料不外求——**舊稿裡就有**中英篇名／作者／頁數／PDF 連結：

    node scripts/hcu_cms_dump_node_articles.mjs --node <rid> --ids c:/tmp/hcu-cms/issue-links.json
    python -X utf8 scripts/hcjbs_cms_restyle.py 1 2 3 … 43      # 解析舊稿→新版面
    python -X utf8 scripts/hcjbs_cms_issue_html.py 44 45         # 這兩期用 harvest（舊稿已是新版面）

🚨 **PDF 連結沿用舊稿的 href，不要照檔名規則重算**：舊期檔名五花八門
（`1-1.pdf`／`11-1(2).pdf`／`43-1應用倫理學的新視野…pdf`），重算一定對不上。
🚨 **連結有相對與絕對兩種**：舊期指向宗教系檔案庫的絕對網址
（`https://www.hcu.edu.tw/upload/userfiles/37837C6F…`），新上的兩期是站內相對路徑。
稽核只認相對路徑會把 11–29、41、42 期誤報成「一個 PDF 都沒有」。
🚨 **清單頁是 JS 表格（paramquery）**，`?page=N` 沒用、永遠只給第一頁 20 筆；
要全部 45 期就餵 `--ids`（用公開清單頁抓的 `issue-links.json`）。

## 節點順序：`api/move-node.ashx`

後台把樹的拖拉排序關掉了（`check_move` 回 false），但 API 還在：
`POST api/move-node.ashx {id: 要搬的, rid: 參考節點, p: first|last|before|after}`，
從後台頁面裡 fetch 才帶得到 cookie。腳本 `hcu_cms_node_move.mjs`（`--list <父rid>` 先看順序）。
子選單現況：研究學報（URL 型，外連回封面牆）／編輯委員／投稿指引／審查流程／學術倫理／AI 使用規範。

🚨 **稽核要驗「樣式有沒有套上」，不只驗字。** 五個章則頁曾經關鍵字全中、內容全對，
但外框 div 漏了沒套上、字體還是校網預設黑體——只驗關鍵字驗不出這種錯。
現在 `hcjbs_cms_verify.py` 每頁都檢查字體堆疊、無填色、導覽列六項、研究學報可點。

## See also

[[research-data-hongshi]]（需登入的研究資料層、弘誓各刊）、[[research-data-airiti]]（華藝那側的
篇目與卷期頁碼）、[[feedback_hcu_cms_new_pages_only]]、[[feedback_no_secret_values_in_chat]]。
