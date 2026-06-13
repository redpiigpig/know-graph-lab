# 星雲大師全集案例（⚠️ 來源受阻：官網不出全文）

> collected-works 第三套漢傳佛教全集，但**與印順/聖嚴根本不同**：官方來源**不釋出可枚舉全文**。
> 現況＝**先建作家 hub + 完整書目（366 部，取自官方《著作總覽》），全文待接入 App API**。

## 版權
星雲大師 1927–2023，2023 圓寂 → 非公有領域。私站 auth-gate 可收（同印順/聖嚴），但前提是**先有乾淨全文來源**。

## 來源探源結論（2026-06-13，已徹底排查）
官網 `books.masterhsingyun.org` 是**薄殼 JS app，不暴露 395 冊／5 萬條目的可枚舉全文**：

| 檢查 | 結果 |
|---|---|
| `sitemap.xml` | **僅 38 URL**：14 個 `/bcN/bookM`（Word 匯出的總覽/紀錄文件）+ 14 影音 + intro。**無任何單篇文章 URL** |
| `/bcN/bookM`（非 sitemap 那 14 個） | 一律 **~9951B 空殼**，內容靠 JS 依路由載入但**無對應資料端點** |
| XHR / `getData` / JSON API | **無**（不像法鼓全集有 `vol_dump` + `html/篇.html`） |
| `/article/articlelist`（大師全集瀏覽器） | 無參數＝空殼；無 tree/iframe/XHR/select |
| 有內容的頁 | 只有 `bc17/book162`＝**著作總覽**（Word HTML 編年目錄）、`bc16`＝出版紀錄 |
| API 主機猜測 | `api.`/`app.masterhsingyun.org` 不解析；`books/api/`、`/article/getarticle` 全 404；`fgs.org.tw/events/cwapp/` 是空 promo 頁 |
| `sitemap`、search | search.html 空（0B）；doSearch 走外部 |

**結論**：CBETA 給 XML、法鼓給每篇靜態 HTML，**星雲官網把全文鎖在不暴露任何端點的 JS reader 裡**，硬爬只會殘缺。

## 唯一可行全文路徑＝**星雲大師全集 App 的私有 API**
App（`org.fgs.introbookapp` / iOS `id1441930680`）幾乎必然打私有 JSON API 取全文。**需使用者協助抓包**：在手機/模擬器用 Proxyman(iOS)／HttpCanary／mitmproxy 截「App 載入任一篇文章」的請求（網址 + 回傳 JSON），給 Claude → 反推整套、像前兩套全量入庫。
- 抓包對 user＝零風險（只看自己流量）；Claude 之後大量打 API 要**節流＋退避**（比照 [[shengyen_collected_works]] 的 server 高載處理）。
- 帳密幫助不大：問題不是「進不去」而是「不知 API 端點」；真要登入也須先看到登入＋取文兩請求。密碼走 .env 不貼聊天（[[feedback_no_secret_values_in_chat]]）。

## 現況產出（2026-06-13）
- [x] `stores/collectedWorks.ts` 加星雲 `CwAuthor`（slug `hsingyun`，orange/🪷；貢獻3段＋年表11條）。
- [x] **書目 366 部**＝官方《著作總覽》(`bc17/book162` Word HTML) 解析的依序唯一 `《》` 書名；單一分類「星雲大師全集（全文待 App API 接入）」，status **`planned`**（待轉錄）。
- [x] hub 截圖實證（orange/🪷 emoji 降級、366 書目「待轉錄」badge、sourceNote ⚠️ 說明）。
- [ ] **全文待 App API**：拿到抓包後寫 `scripts/hsingyun_build.py`（API→篇→單語 chunk，下游同 yinshun/shengyen），逐冊入庫 + works status 改 `done` + 連 ebookId。

## 雷區
- 著作總覽是 Word 匯出（mso- styles），無乾淨 12 大類標頭、年代只 24 個 marker → **不要硬塞年份/大類**（會錯）；書目先用「依文件順序的唯一書名」最誠實。
- 別在官網 reader 上硬爬：sitemap/API/XHR 全試過，沒有乾淨全文路徑。
