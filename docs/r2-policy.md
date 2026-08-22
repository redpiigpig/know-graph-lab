# R2 使用規則

## 為什麼有這份規則

2026-08-21 收到 Cloudflare 帳單 $0.52。查下去發現 bucket `knowgraphlab` 已經 **28.0 GB**，
而 R2 免費額度只有 **10 GB**（超出部分 $0.015/GB-月）。其中 18 GB 是「本來就不該放上去」的東西：

| 內容 | 大小 | 問題 |
|---|---|---|
| 燈箱放大圖 `_1600` webp q80 | 15.8 GB | 規格開太大，1024 q65 只要 31% 體積 |
| 福嚴會訊 71 期掃描 PDF | 3.5 GB | 每期 48.7 MB，Drive 有正本 |
| 弘誓雙月刊 117 期掃描 PDF | 2.2 GB | 同上 |
| 國家檔案局卷宗 412 檔 | 1.2 GB | 同上 |
| 孤兒縮圖（原檔已改名／刪除） | 2.0 GB | 沒人清 |

**R2 有 10 GB，Drive 有 5 TB。** 兩者不是同一種東西，不該當成同一種東西用。

## 鐵則

> **Drive 是正本。R2 是雲端部署才需要的小體積衍生物快取，不是儲存空間。**

站主要都在本機跑站，G: 槽掛著 Drive，**檔案系統直接讀得到**。所以「要提供下載」
從來就不是「必須上 R2」的理由 —— 見下面〈下載功能怎麼做〉。

## 可以放 R2

* 網頁縮圖：`photos/thumb/`，只做 **480 q80**（縮圖牆）與 **1024 q65**（燈箱）兩種寬度
* 電子書 chunks：`ebook-chunks/`（gz 壓縮，reader 逐章載入）
* 逐段全文轉錄：`*-fulltext/`（純文字，整批也才 89 MB）
* 簡報／海報等小附件：`qiangmian-ppt/`、`speech-posters/` 這類
* 小體積且是頁面主要入口的下載：單檔 ≲ 5 MB、單一用途總量 ≲ 100 MB
  （例：`dadaodao-materials/碩士文稿/` 那份 2.4 MB 的碩士論文 PDF）

## 不可以放 R2

* 掃描原檔、整本 PDF 檔庫（期刊、會訊、卷宗、學報）
* 影音
* 單檔 > 10 MB 的原始資料 —— 除非說得出「非它不可」的理由
* **任何 Drive 上已有正本、而本機讀得到的原始資料**

## 下載功能怎麼做

不要為了下載把原檔搬上 R2。照 [`server/utils/research-files.ts`](../server/utils/research-files.ts) 的模式：

```
Drive 正本（本機 G: 槽）→ 找不到才退回 R2 簽名網址
```

本機跑站時走第一條，下載體驗完全不變；雲端部署沒有 Drive 才走第二條，
而第二條只在該檔小到符合上面〈可以放 R2〉時才會有東西。

Drive 根目錄走 runtimeConfig（`researchDataRoot` / `photosRoot` / `bibleVersesDir`），
不要在端點裡寫死路徑。

註：站上分類與 Drive 資料夾不一定一致（例如「研究回顧」是站上的歸類，該檔在
Drive 實際放在「作者/林建德/」），所以解析器是**先比對相對路徑、找不到再退回檔名索引**。

## 上傳前先問三題

1. Drive 有正本嗎？（沒有 → 先放 Drive）
2. 本機讀得到嗎？（讀得到 → 就別上 R2）
3. 雲端部署真的需要它嗎？（不需要 → 別上 R2）

三題有任一題答「否 / 不需要」，就不要上傳。

## 定期體檢

```bash
python scripts/r2_reclaim.py all          # dry-run，列出可回收的量
python scripts/r2_reclaim.py all --go     # 確認後執行
```

三批各有驗證閘，過不了就不刪：

| 批次 | 驗證閘 |
|---|---|
| `orphans` | cacheKey 不在 `photos/index.json` |
| `thumbs` | 同 key 的 `_1024` 已存在（沒替身不刪） |
| `research` | Drive 有同名同大小的備份 |

建議每季跑一次 dry-run。照片同步腳本本身也會長孤兒（原檔改名／刪除後縮圖留著），
這是常態，不是異常。

## 2026-08 縮容結果

28.0 GB → **約 7.8 GB**，回到免費額度內：

* 孤兒縮圖 −2.0 GB
* 燈箱圖 1600 q80 → 1024 q65，−9.7 GB（[`scripts/r2_shrink_photo_thumbs.mjs`](../scripts/r2_shrink_photo_thumbs.mjs)）
* 研究資料掃描原檔 −8.5 GB（下架前逐檔核對 Drive 有同名同大小，並補回 304 個只存在 R2 的檔）
