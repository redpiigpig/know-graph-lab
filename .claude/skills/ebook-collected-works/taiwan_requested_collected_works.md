# 台灣處境神學與當代佛教七位全集（2026-08-10）

本批依使用者指定建立：黃彰輝、宋泉盛、王憲治、黃伯和、釋太虛、釋昭慧、釋性廣。
網站有登入保護、僅供使用者私人研究；使用者已明示取得 CBETA 等相關權利方授權。
不得把本批的私用授權推論為公開授權，也不得移除各來源的版本與權利說明。

## 完成度定義

| 作者 | hub 書目邊界 | 本次全文狀態 |
|---|---|---|
| 黃彰輝 | 5 種書／報告、7 篇核心文章、3 場 Princeton 講座 | 已建目錄；底本待逐項取得 |
| 宋泉盛 | 15 種本人專著／論文、5 種編輯文集 | 已修正生卒與學歷；底本待逐項取得 |
| 王憲治 | 15 筆可核專著、論文、編著與身後文集 | CCA 一篇有官方全文，其餘待底本 |
| 黃伯和 | 舊單行本、英文專著、十卷現行文集、官方文章 | 官方文章可直接取用；十卷文集為 canonical edition |
| 釋太虛 | 四藏二十編＋編纂說明，40 個 TX XML 合併為 21 部 | 40/40 XML 已下載並解析，準備上架 |
| 釋昭慧 | 36 種專書表現形＋2 編著＋1 代撰＋官方文章 | 已建目錄；官方 PDF 可優先匯入 |
| 釋性廣 | 6 冊專書＋2 篇學位論文＋官方文章 | 已建目錄；官方 PDF 可優先匯入 |

「已建全集」在本專案中意指作者 hub、可核書目、來源、權利狀態與可續跑匯入路徑均已建立；
只有有 `ebookId` 且資料庫／R2 實際有 chunks 的作品才可標 `done`。

## 主要權威來源

- 黃彰輝：[PCT 官方小傳](https://www.pct.org.tw/article_peop.aspx?strASP=article_peop&strBlockID=B00007&strCTID=CT0005&strContentID=C2007032200006&strDesc=&strSiteID=)、[WCC 文集頁](https://www.oikoumene.org/resources/publications/shoki-coe-an-ecumenical-life-in-context)、[Wheeler 選擇書目](https://journals.sagepub.com/doi/10.1177/239693930202600205)。
- 宋泉盛：[PCT 紀念專文](https://newmsgr.pct.org.tw/Magazine.aspx?strISID=201&strMAGID=M2025041506041&strTID=1)、[WCC 紀念](https://www.oikoumene.org/news/wcc-gives-thanks-for-the-life-of-choan-seng-song)、[愛丁堡大學訃聞](https://divinity.ed.ac.uk/news-and-events/obituaries/rev-professor-choan-seng-song-1929-2024)。
- 王憲治：[PCT 人物誌](https://www.pct.org.tw/article_peop.aspx?strASP=article_peop&strBlockID=B00007&strCTID=CT0005&strContentID=C2007041200005&strDesc=&strSiteID=)、[台南神學院期刊索引](https://www.ttcs.edu.tw/images/ckfinder/7/files/%E7%A5%9E%E5%AD%B8%E8%88%87%E6%95%99%E6%9C%83%E7%99%BC%E8%A1%8C%E7%B4%80%E9%8C%84%28%E8%87%B32023_6%29%281%29.pdf)、[CCA 全文](https://cca.org.hk/ctc/ctc95-03/1.wang.htm)。
- 黃伯和：[United Board 履歷](https://unitedboard.org/about-us/leadership/board-of-trustees/rev-dr-huang-po-ho/)、[ACTT 十卷文集](https://www.actt.org.tw/publications/)、[CJCU 作者成果](https://eweb.cjcu.edu.tw/cjcur/LiteratureList.aspx?author=P%2Bpl6VoA7TmD6ZoDr5gm4w2&page=4)。
- 釋太虛：[CBETA 專題](https://archive2.cbeta.org/en/node/6547)、[TX 目錄](https://cbetaonline.dila.edu.tw/mulu/TX)、[CBETA 權利聲明](https://cbeta.org/copyright)、[XML P5](https://github.com/cbeta-org/xml-p5/tree/master/TX)。
- 釋昭慧：[玄奘大學著作表](https://www.hcu.edu.tw/buddhism/buddhism/zh-tw/6B5F522110EA4A1D9C5D563196197126/031688DABF8540CC9F01F49423C5B19D/CE8A9DFC02EA46FA9196BF3EDA79992D)、[臺大佛學作者索引](https://buddhism.lib.ntu.edu.tw/DLMBS/author/authorinfo.jsp?ID=64856)、[弘誓法印學報](https://www.hongshi.org.tw/archive/journal/)。
- 釋性廣：[玄奘大學著作表](https://www.hcu.edu.tw/ird/ird/zh-tw/7EF2E04CB38648218F4CDF93F5931D0F/388A3F71437545C89203F80683B1B33B/F2042CAD0715407280267A2960B95702)、[弘誓研究資料](https://www.hongshi.org.tw/admin/upload/file/20241231-journal15-9.pdf)。

## 關鍵消歧義與版本規則

- 王憲治（1941–1996）不可與王獻之（344–386）合併；「王憲冶」為誤字。
- 黃彰輝、Shoki Coe、C. H. Hwang、Huang Zhanghui 為同一人；1970 Princeton 項目是錄音。
- 宋泉盛正確生卒為 1929–2024；博士是 1965 年 Union Theological Seminary ThD，不是 Edinburgh 博士。
- 黃伯和十卷現行文集是全集層；舊單行本用 `contained_in` 概念連結，不重複建 reader。
- 昭慧新版、英譯／德文合著版與原作須保留 manifestation 關係；《性別倫理與社會關懷》是官方教師頁漏列補件。
- 性廣《佛教養生學》採 2017；玄奘頁的 2016 與 ISBN／弘誓出版資料不一致。
- 太虛原著、1948 編本與 CBETA 數位文本是不同權利層；每部 reader 封面保留 CBETA／印順文教基金會說明。

## 太虛匯入器

- registry：`taixu_registry.json`（21 部、40 個來源 XML、固定 UUID）
- parser：`scripts/taixu_build.py`
- tests：`scripts/tests/test_taixu_build.py`
- 本機來源快取：`.cache/taixu-tx-xml/`
- 本機 reader JSONL：`.cache/taixu-chunks/`

解析器保留 prose、verse、list、dialogue、table；去除校注重複與頁行標記；每 chunk 上限 12,000 字。
上傳時寫入 `collection='collected-works'`，並同步 R2 全文與 Supabase preview rows。
