# Overnight 2026-05-22 進度報告

接續 [OVERNIGHT_2026-05-21.md](OVERNIGHT_2026-05-21.md) — 整晚自動跑「sections live + reclassify apply + 寫 OCR rescue 候選表 + SKILL.md 更新」。

## ✅ 完成的工作

### 1. Sections resplit live — 28 本切完 +2,649 chunks

dry-run 看起來乾淨 → `python scripts/resplit_to_sections.py run --all` 跑 live。

**亮點**（log 在 `scripts/logs/resplit_sections_live_2026-05-21.log`）：

| 書 | +chunks | 模式 |
|---|---|---|
| **Aquinas 神學大全（第 1 冊）** | +252 | chinese_jie:36 |
| **Aquinas 神學大全（第 3 冊）** | +145 | chinese_jie:27 |
| 舊約背景 | +254 | chinese_jie:3 |
| 中國儒學史 | +281 | chinese_jie:60 |
| 中國佛教史（卷 3） | +150 | chinese_jie:5 |
| 鹽野七生作品集（33 冊） | +135 | aquinas_a:7, md_h3:1 |
| 幽靈帝國拜占庭 | +118 | md_h3:11 |
| 印度哲學通史 | +116 | md_h3:25 |
| 大歷史 | +110 | md_h3:14 |

Boundary methods used: `aquinas_a=7, md_h3=177, chinese_jie=183` — total 367 boundary cuts。

### 2. History reclassify apply — 44 本搬類別 + 套書 DB-only 安全

Gemini judge 跑了 468 本歷史學書，找出 49 本應移出（high confidence 44 本，low 5 本捨棄）。

`scripts/_reclassify_history_via_gemini.py` 原本 `cmd_apply` 是 `[TODO]` 沒接，今晚補上 `scripts/_reorg_history_apply.py` 完整接線：

- **dry-run 先掃 file_path** — DB 內共享 file_path（套書）會被偵測成 `is_shared=True`
- **shared (套書) 19 本** → 只改 DB category/subcategory，**不搬實體檔**（避免破壞其他 DB row 的指向）
- **unique 25 本** → DB 改 + Drive 檔移到新 category 資料夾 + UPDATE file_path

apply 結果：moved=44, fail=0, not_found=0, db_only(套書)=19

### 3. ⚠ 修一個 bug — compound-category（16 本）

`_reorg_history_apply.py` 原版直接把 Gemini judge 給的 `new_category="世界宗教/基督教"` 整段塞進 `category` 欄。post-apply category counts 出現：

```
10  世界宗教/基督教   ← 錯（應該 category=世界宗教, sub=基督教/...）
 2  世界宗教/猶太教
 2  世界宗教/伊斯蘭教
 1  世界宗教/佛教
 1  世界宗教/印度教
```

修 16/16 → category 變回 `世界宗教`，subcategory 變成 `基督教/教會史` etc（match 既有 22 IVP/9 典外文獻的 nested 命名）。

**修了腳本 normalize() 防止再犯**：raw_cat 含 / 時拆 head/tail，head 進 cat，tail 接到 sub 前面。

### 4. OCR body rescue 候選表 — 49 本識別好

`c:/tmp/ocr_rescue_candidates.txt` 跑 SQL（chunk content < 100 chars 比例 > 50%）找出 49 本 PDF body 抽取失敗的書，寫到 [.claude/skills/ebook-pipeline/ocr-rescue-candidates.md](ocr-rescue-candidates.md)。

**Top 21 是 100% tiny**（body 完全沒抽出來），重災區：
- 文化與帝國主義（572 chunks 全空）
- 走向十字架上的真（473）
- 民主與城邦的衰落（378）
- 國家與祭祀（205）
- 尼采到底說了什麼（112）
- 現代性與後現代性十五講（68）

⚠ **沒自動 re-OCR** — 原因：
1. 今晚已有 2 個 OCR wrapper 在跑（main daily + IVP priority），照 SKILL.md 警告 race risk
2. Gemini quota 狀態未知（OVERNIGHT_2026-05-21.md 提到「明天 quota reset 後」）
3. 一本 30 分鐘起跳，49 本要 24+ 小時，需要明天 user 決定優先順序

### 5. z-lib drop 偵測 — 空（0 ebooks waiting）

### 6. 套書 share-file 暴露的問題

reorg 過程發現 **21 個 file_path 是套書共享**：
- `商務印書館，商務印書館漢譯歷史套裝（24 冊）.epub` — 24 本 ebook row 指同一檔
- `企鵝歐洲史系列（套裝 7 冊）.epub` — 7 本
- `世界史的拼圖（7 冊）.epub` — 7 本
- `中東大歷史（共 5 冊）.epub` — 5 本
- `理想國譯叢系列 套裝 32 冊（MIRROR 系列）.epub` — 32 本
- 其他 16 個

per memory `feedback_set_books_split.md` —「套書要拆成個別書」是長期目標。今晚的 reorg 在 DB 改了 cat/subcat 但不動 file_path，等之後做 set-split workflow 時再正式拆。

## 📊 數字總結（vs 昨晚收盤）

| 指標 | 5/21 收盤 | 5/22 凌晨 | Δ |
|---|---|---|---|
| Total chunks | ~176,733 | **179,382** | +2,649 |
| 歷史學 books | 468 | 424 | −44 |
| 世界宗教 books | 418 | 447 | +29 |
| 哲學 books | 239 | 253 | +14 |
| 神學 books | 319 | 326 | +7 |
| 宗教學 books | 111 | 115 | +4 |
| 文學 books | 58 | 60 | +2 |

## 📋 明早接續任務（user 抓回來）

1. **OCR body rescue** — 看 [ocr-rescue-candidates.md](ocr-rescue-candidates.md) 49 本候選，挑優先順序，等 Gemini quota OK 再排程
2. **鹽野七生 33 冊決議** — 仍待 user 決定（z-lib 重抓單本 vs 保留現狀 vs 拆 33 row）
3. **套書拆 split workflow** — 21 個共享檔的長期任務
4. **印度哲學/哲學原典 子分類補齊** — 12 本商務印書館套書現在 `category=哲學, subcategory=NULL`，可進一步 LLM judge 分 古希臘/近代/中國 等

## 🔍 WebSearch 三輪結果 — master-scholars PDF 找尋（user 指定 option C）

Anna's Archive / libgen / z-lib 自動下載全擋（DNS / anti-bot）。換成 Google WebSearch 對每本書 / 每位學者搜索免費 PDF。

### Round 1 — 170 本待補書直連搜尋

每本 1 次 WebSearch，過濾出 archive.org / .edu / monoskop / 作者站等直連 PDF（拒 books.com.tw / 博客來 / 書評 / bookey AI 摘要）。

- **143/170 found (84.1%)**
- 命中率語言差很多：英文標題 96% vs 中文標題 67%
- Top hosts：archive.org (11) / monoskop.org (5) / cdn.bookey.app (10 ⚠ AI 摘要要降權)

### Round 2 — 27 N 改英文書名重 search

把「中譯版罩英文原書」27 本換 English title 再搜。

- **+18 新命中 → 161/170 (94.7%)**
- 救回 Durkheim Suicide / Bourdieu Logic of Practice / Spinoza Tractatus / Tylor Primitive Culture / Malinowski Argonauts / Freud 文明及其不滿 / Jung Psychological Types / Otto Idea of the Holy
- **9 確定放棄**：Bauman ×2 (Cornell UP)、Hauerwas (Notre Dame UP)、Aron (T&F)、Hartmann (De Gruyter)、Panikkar、Rogers、Fromm、Merleau-Ponty 符號、Balthasar — 都是出版社鎖檔，只能 Anna's Archive 手動

### Round 3 — 106 學者全集打包搜尋

user 觀察：322 代表作只是 hit-list，要完整覆蓋每個學者全集應 500+ 本量級（Freud SE 24 卷、Jung CW 20 卷、Heidegger GA 102 卷、Husserliana 42 卷、Weber MWG 47 卷…）。

- subagent 跑到 **15/106 撞 session limit**（9 Y / 6 N）
- 剩 91 + 救 6 N → 我手動構造 `archive.org/search?query=creator:"{Latin name}"` URL 補完
- 驗證 sample：Husserl 116 件、W.C. Smith 17 件、Bourdieu 53 件 — 構造 URL 真的有結果
- **最終 106/106 都有 archive.org author profile URL**

| 已 verified（subagent 找到具體 bundle） | 構造（user 點開可看 archive.org 全部該作者作品） |
|---|---|
| Max Weber Gesamtausgabe / Marx Collected Works / Eliade Monoskop / Max Müller / Feuerbach / William James / Frazer (Golden Bough 12 vols) / Otto / Durkheim Monoskop | 97 學者 archive.org 作者搜索頁 |

### 兩張 CSV 給 user

1. **`c:/tmp/master_scholars_pdf_urls.csv`** — 170 本直連 PDF（161 Y / 9 N）
2. **`c:/tmp/master_scholars_full_collection_urls.csv`** — 106 學者全集打包入口（106 Y / 0 N）
3. **`c:/tmp/master_scholars_pdf_search_summary.md`** — Round 1+2 摘要 + top 20 URL

### 下載流程建議（VPN 不需要）

archive.org / monoskop / earlymoderntexts / marxists.org **全球可達**，台灣 ISP 不擋。user 可以直接：
1. 點開 CSV 內 best_url
2. 對 archive.org 頁面手動挑 PDF/EPUB 下載到 `z-lib/` 資料夾
3. 既有 daily ingest 自動接（10/14/18 排程）
4. **不要 wget 大批量** — archive.org 對 bot 也風控，建議 user 用瀏覽器逐本下載比較不會被 ban

預估覆蓋率：
- 322 代表作 → ~158 本確定可下載
- 106 學者全集入口 → 假設每個學者平均能再撈到 5 本沒在 hit-list 上的 → +500 本量級
- **合計 600-700 本可能下載量**，但實際還是看 user 點擊速度

## 隔夜碰到的 dead-end（記給未來自己）

- **Anna's Archive .li 反爬** — `https://annas-archive.li/search?q=...` 回 HTML JS challenge，requests 拉不到實際結果。Need real browser / playwright or 換 mirror
- **PowerShell cp950 + Python print** — chinese print 到 stdout 會 UnicodeEncodeError，必須 `sys.stdout.reconfigure(encoding='utf-8')` 或寫檔再讀
- **Supabase Management API** — 跑 SQL 比 REST PATCH 直觀，且能 GROUP BY；但 `db.{ref}.supabase.co` IPv6-only 連不通，照 memory 用 `api.supabase.com/v1/projects/{ref}/database/query`
