---
name: hcu-hcjbs-journal
description: 《玄奘佛學研究》學報**公開官網**的建置與維護 —— 這是使用者在玄奘大學的職務工作（學報編輯），不是弘誓的研究資料。兩處成品：①模擬站 `redpiigpig.com/Hsuan_Chuang_Studies`（本 repo `pages/Hsuan_Chuang_Studies/`，封面牆＋各期篇目＋五個章則頁）②正式站＝**玄奘校網後台「臺灣佛教研究中心」底下新建的網站**（`.env` 的 `HCU_WEB_CMS_*`）。章則內容一字不自撰，正本是編輯室交來的「英網-N」docx。🚨 正式站**只准新建網頁**，中心底下既有頁除了建立連結一律不得改動。Use when 要更新投稿指引／編輯委員／審查流程／學術倫理／AI 使用規範任一頁、編輯室給了新版 docx、要補抓新一期篇目與封面、要把模擬站搬上校網後台、或使用者提到「學報網站」「玄奘佛學研究官網」「英網」「臺灣佛教研究中心的網站」。與 [[research-data-hongshi]] 的分工：那邊是需登入的研究資料層 `/research-data/yinshun-hongshi/xuanzang`（全文語料、給論文用），這邊是對外的學報門戶。
---

## 兩處成品，不要搞混

| | 網址 | 原始碼／位置 | 用途 |
|---|---|---|---|
| **模擬站** | `redpiigpig.com/Hsuan_Chuang_Studies` | `pages/Hsuan_Chuang_Studies/` | 先在這裡把版面與內容做定，給使用者確認 |
| **正式站** | 玄奘校網「臺灣佛教研究中心」底下（新建） | 校網後台，`.env` 的 `HCU_WEB_CMS_URL`／`HCU_WEB_CMS_USER`／`HCU_WEB_CMS_PASS` | 對外正式公開 |
| 研究資料層 | `/research-data/yinshun-hongshi/xuanzang`（需登入） | 見 [[research-data-hongshi]] | 45 期 304 篇全文語料，論文用 |

🚨 **正式站只准新建網頁。** 那是校方正式官網，中心底下還有別人在用的頁面：不得改內容、
不得改版面、不得刪除——**唯一例外是替新網頁建立連結**（在中心選單或既有頁面加一條連結）。
動手前先確認自己在新建的那一頁上，不要在既有頁的編輯器裡改東西。

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

🚨 **docx 的措辭不要自己「修順」。** AI 使用規範原文寫「⋯學生使用相關工具時⋯」，讀起來像從
校內規章沿用過來的，但使用者要求照原樣保留。要改措辭得由編輯室出新版。

### 內容規格備忘

- 徵稿啟事的專輯表隨期次滾動：已出刊的期次要**刪掉**，新公告的期次要補上
  （2026-09 這次刪 45／46 期、補第 56 期 劉宇光教授／當代東南亞上座部佛教）。
- 投稿信箱 `hcu10@hcu.edu.tw`＋副本 `part55410@gmail.com`；聯絡人堅意法師。
- 每年兩期，上半年 3 月 30 日、下半年 9 月 30 日出刊。
- 編輯委員：總編輯釋昭慧＋委員 13 位（依姓氏筆畫），機構與專長見 `editorial-team.vue` 的
  `members` 陣列；簡歷只做中文，英文版僅名字與機構。

## See also

[[research-data-hongshi]]（需登入的研究資料層、弘誓各刊）、[[research-data-airiti]]（華藝那側的
篇目與卷期頁碼）、[[feedback_hcu_cms_new_pages_only]]、[[feedback_no_secret_values_in_chat]]。
