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

### 2026-09-20 上稿結果（七篇，皆已發布並稽核全綠）

| 頁面 | article id | 備註 |
|---|---|---|
| 第四十四期玄奘佛學研究 | `DE09FA1EDAB748D7A8FAE8E8CA57EE7B` | 7 篇，PDF 全數可下載 |
| 第四十五期玄奘佛學研究 | `34BD6FE105FA42A583802ACC00D32151` | 7 篇，**只有 2 篇有 PDF**（其餘五篇原檔只在編輯者電腦上） |
| 投稿指引 | `96A76E3B3AE547809089C47BAAD28B98` | 專輯表 47–56 期＋格式要點全文 |
| 編輯委員 | `03652C8EB3C8477D9D0808D33B6F96D9` | 名單 14 位＋逐位簡介 |
| 審查流程 | `B52674BF2BF74D1EB3DA5E306F0DC4C3` | 含雙審查決策矩陣 |
| 學術倫理聲明 | `4A70840CEA124E2D92F5D71D219E8658` | 260425 版 |
| 生成式人工智慧（AI）使用規範 | `FD5F7F987CDD435393B68B0B6BAF7C5F` | 「學生」已依老師指示改「作者」 |

待補：45 期那五篇 PDF 要向編輯室（使用者本人）拿原檔，上傳後把 `issue-45.html` 重生再覆蓋該篇。

## See also

[[research-data-hongshi]]（需登入的研究資料層、弘誓各刊）、[[research-data-airiti]]（華藝那側的
篇目與卷期頁碼）、[[feedback_hcu_cms_new_pages_only]]、[[feedback_no_secret_values_in_chat]]。
