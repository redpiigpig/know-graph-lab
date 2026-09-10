---
name: ebook-scan-transcribe
description: >
  把**紙本掃描檔**轉錄成站上可讀、可引用的一卷 —— 拆 2-up 頁、轉正、比對印刷頁碼
  去重補洞、Gemini Vision 逐頁 OCR、每一段掛原書頁碼當引用號、腳註（含跨頁註）
  照收。與 [[ebook-collected-works]] 的分工是：那支管全集的下游（hub／三欄
  reader／入庫／狀態對帳），本 skill 管上游那一段「一疊掃描 PDF → 帶真頁碼的
  chunks」。Use when 使用者丟來一份（或一疊）掃描 PDF 要上架、要處理 2-up
  上下兩頁的掃描、要判斷有沒有重複頁或缺頁、要合併去重出一份乾淨 PDF、
  要保留原書頁碼供引用、要收腳註、或提到「掃描檔」「合併」「重複」「缺頁」
  「頁碼」「註腳」。首案＝昭慧法師全集（《心靈的交會：山間對話》《初期唯識思想》）。
---

# 掃描本轉錄 Skill

> ⚙️ **引擎**：Gemini Vision 為主（`gemini-2.5-flash`；新申請的 key 對這個模型回
> **404 "no longer available to new users"**，`ocr_pdf_to_text` 已把這種 404
> 當成「這把 key 不能用這個模型」而輪替，不會整輪中斷）。2.5-flash 的日額度
> 用完就改 `--model gemini-flash-latest`（配額獨立，但常回 503 overloaded，
> 靠內建退避重試撐過去）。**Haiku Vision 不要用來做逐字 OCR**——它會整段編造
> （[[feedback_ocr_repetition_hallucination]]）。

## 三步管線

| 步驟 | 腳本 | 做什麼 | 吃 LLM？ |
|---|---|---|---|
| ① prep | `scripts/scan_prep.py split` | 來源 PDF → 每頁一個書頁、方向轉正的**工作 PDF** | 否 |
| ② ocr | `scripts/scan_ocr.py` | 工作 PDF → 逐頁 JSON（頁碼／頁眉／段落／註腳） | 是 |
| ③ build | `scripts/chaohwei_build.py` | 頁碼帳 → 分章 → chunks → R2＋DB；`scan_prep.py build` 出成品 PDF | 否 |

書籍設定集中在 **`scripts/scan_books.py`**（純資料）。新增一本＝加一筆，不改邏輯。

```bash
python -X utf8 scripts/scan_prep.py split --book <slug>
python -X utf8 scripts/scan_ocr.py  --book <slug> --batch 6 --resume
python -X utf8 scripts/chaohwei_build.py --audit          # 先看頁碼帳
python -X utf8 scripts/chaohwei_build.py --keep-out c:/tmp/<slug>/keep.json
python -X utf8 scripts/scan_prep.py build --book <slug> --keep … --out "G:/…/成品.pdf"
python -X utf8 scripts/chaohwei_build.py --upload
```

---

## ① prep：掃描檔長什麼樣，先看清楚再動手

館藏掃描檔最常見的形態是 **2-up**：一個 PDF page 其實是**一張橫躺的紙，上下疊著
兩個書頁**。動手前一定要先渲染幾頁看，三件事各自獨立、不能互相推論：

1. **要轉幾度**。`show_pdf_page(rotate=)` 與 `fitz.Matrix()` **方向相反**，實測
   `rotate=270` 才是把躺著的頁轉正。別靠 `page.rotation`（掃描檔一律 0）。
2. **半頁順序**。轉正後是「下半頁在前」還是「上半頁在前」？**兩種都存在**：
   《心靈的交會》橫排，頁碼 b 在下、c 在上（下半先）；《初期唯識思想》直排，
   頁碼 130 在上、131 在下（上半先）。所以 `half_order` 是設定欄位，不猜。
3. **中線在哪**。兩頁之間是掃描機留下的深色帶，`find_split_y()` 取中央 ±18%
   最暗的一列；整區都不夠暗就退回正中間。

> 🚨 **文字層的座標也不可信。** 這類掃描檔常帶一層掃描機自己做的 OCR，字元是亂碼
> ——而且**連 line bbox 的方向都是錯的**。我用它判方向，四個檔全判成同一個方向，
> 實際上不是。判方向只能看渲染出來的**影像**。

### 成品 PDF 一定要 `garbage=4`

拆頁時每個半頁都引用了整張來源掃描圖，`insert_pdf` 會**給每一頁複製一份**：
253 頁的書從 8 MB 漲成 **214 MB**，而且看起來完全正常。`save(garbage=4, clean=True)`
做跨物件去重後回到 8.1 MB。

---

## ② ocr：輸出格式做成「結構化的行」，不要事後再猜

`scan_ocr.py` 要求模型嚴格照這個格式吐：

```
【頁 130】
【眉 ‧初期唯識思想】
正文第一段……（一個自然段一行，不按印刷換行斷句）
正文第二段……
[^13]: 《攝大乘論》卷中（大正三一‧一三九上）。
[^續]: 二支緣起，是名分別愛非愛緣起。」（大正三一‧一三四下）
```

四件事各佔各的位置，build 就不必在字串裡認來認去。設定會依書自動加上：
直排說明（`vertical`）、發言人格式（`speakers`）、忽略前手的鉛筆畫線與眉批
（`ignore_marks`）。

**頁碼規矩**：讀不到就寫 `【頁 ?】`，**絕不用前後頁推算**。中文數字頁碼（一三〇）
請模型換算成 `130`。

**腳註規矩**（[[feedback_transcribe_notes_and_bibliography]]）：
- 正文註號 `[^13]`，用**書上印的號碼**，不從 1 重編；看不清寫 `[^?]`。
- 註文 `[^13]: …`，出處原樣照抄。
- 跨頁註：下一頁那半條寫 `[^續]: …`，build 會接回原註，anchor 留在註**開始**的頁。
  不接的話註釋會斷成兩半、後半沒有號碼，等於引不回去。

**每一批各自落地**。整段跑完才寫檔的話，配額一斷就前功盡棄；`--resume` 讓被打斷
的重跑只補沒跑到的頁（[[feedback_laptop_sleeps_design_for_resume]]）。

---

## ③ build：頁碼帳是這條線的品質閘

`--audit` 印五件事，**每一項都要看過**：

| 欄位 | 意思 |
|---|---|
| 重複 | 同一個印刷頁碼出現在多個掃描頁 → 保留一份 |
| 章末空白頁 | 頁碼序列有洞，但掃描序上那個位置確實有一張空白頁 → **不是缺頁** |
| 🚨 真缺頁 | 洞的位置連空白頁都沒有 → 真的漏掃，要回頭補 |
| 空白頁 | 整頁沒有正文 |
| 裝置頁 | 封面／書名頁／目次／章名頁，不進正文 |

### 分章靠「章名表 × 掃描序」，不靠比對標題文字

章名與起訖頁**照抄書上的目次頁**寫進 `CHAPTERS`；分派段落時拿章的起始頁碼
**原字串**去掃描序上找那一頁，從那裡換章。序的標題常是自訂散文句
（〈在這交會時互放的光芒〉），任何 regex 或字串比對都會連正文一起誤判。

起始頁碼被 OCR 讀錯時往後找兩頁當切點——少了這道保險，一個讀錯的頁碼會讓整章
靜靜地併進前一章。

### 頁碼進 chunk 的方式

- 每一段的原書頁碼進 `chunk.anchors[i]`（＝ reader 左欄的引用號，可點擊複製）。
- `chunk.page_number` 存該章第一個**阿拉伯數字**頁碼；序（頁碼是 a/i）留 `null`。
- `total_pages` 取**全書最後一個印刷頁**，不是最後一章的起始頁。
- 🚨 讀不到真頁碼時留 `null`，**絕不拿 chunk_index+1 充數**
  （[[feedback_transcribe_page_numbers]]）。

---

## 🚨 這條線特有的「看起來成功的失敗」

五個都踩過，共同點是**頁面照常出現、audit 照常說沒問題**，只有真的去讀內容才看得見
（[[feedback_reader_silent_failures]]）。

| 症狀 | 真正的原因 |
|---|---|
| 某一章整個不見，前一章莫名變長 | 前言頁碼 `c`／`d` **也是羅馬數字 100／500**。把頁碼轉成數字再比大小，序的頁就掉出區間。改用掃描序找切點，不解讀頁碼語意 |
| 某一頁整頁消失，但 audit 說「真缺頁 0」 | OCR 把頁眉和正文吐成同一行，頁眉清理把整行（454 字）刪光。audit 看的是**原始**文字所以沒察覺。加長度上限＋只削前綴，並對「有正文卻被清成空白」告警 |
| 去重留下的是模糊的那一份 | 被掃描機黑邊吃掉半行的那一份，OCR 反而**更長**（多吐亂碼）。先比影像品質（`page_quality`，暗像素佔比）再比字數 |
| 憑空多出「頁 75 重複」 | 模型把章名頁的「Dialogue.4」讀成頁碼。章名頁一律不參與頁碼帳 |
| 註釋消失在段落裡 | 頁末註文被接行邏輯黏到正文最後一段的尾巴。註文要在接行**之前**先抽出來 |

另外兩個非內容的坑：
- 半形逗號：Gemini 轉錄中文書常把全形「，」吐成半形。`to_fullwidth_punct` 只在
  **前一個字元是 CJK** 時才換，英文引文與 `1,000` 不受影響。
- dev server 截圖時 OOM：`NODE_OPTIONS=--max-old-space-size=8192`，另起
  `--port 3200`（別動別人的 :3000，[[feedback_no_kill_other_tasks]]）。

---

## 下游：接 collected-works

轉錄完接 [[ebook-collected-works]]：`collection='collected-works'`、hub 加 work
（`genre` 依文體，對談錄用 `dialogue`、段首寫 `〔辛格〕`）、導讀寫進
`data/collectedWorksIntros.ts`、收工跑 `scripts/collected_works_status.py` 對帳。

**reader 的腳註呈現**（2026-09-10 新增於 `pages/collected-works/[slug]/[work].vue`）：
`md()` 把 `[^4]` 渲染成上標、`[^4]: …` 渲染成灰底小字註文列，網址自動連結；
`rows` 用 `isNote` 分辨註文列。這是全集 reader 第一次支援註腳，之前只有粗體斜體。

## 案例

- [chaohwei_collected_works.md](chaohwei_collected_works.md) —— 昭慧法師全集
  （《心靈的交會：山間對話》✅ 上架、《初期唯識思想》轉錄中）

## See also

- [[ebook-collected-works]] — 下游（hub／reader／入庫／對帳）
- [[ebook-pipeline]] — 一般 ebook 的 parse/OCR/standardize
- [[feedback_transcribe_page_numbers]] / [[feedback_transcribe_notes_and_bibliography]]
- [[feedback_reader_silent_failures]] — 這條線的失敗模式全屬這一類
