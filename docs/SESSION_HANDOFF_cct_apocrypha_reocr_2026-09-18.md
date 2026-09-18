# 交接：《基督教典外文獻》十冊重 OCR 並逐書入 /apocrypha

給接手的 session。**這份可以整份貼進新 session 當 prompt。**
前一輪做完的部分與所有已知的坑都寫在下面，照著走可以不用重踩。

---

## 一、任務

站上 `/apocrypha` 有 **15 份文獻的文字層是壞的**、**4 份是複合檔**（整冊書擠在一個
`doc_slug` 底下）。原因是當初入庫時直接吃了那幾冊 PDF 內建的文字層，而那層本身是
壞掉的 OCR。

要做的是：**用 MinerU 重 OCR 十冊原書 → 逐部作品切分 → 覆蓋或新建對應的
`apocrypha_documents` / `apocrypha_sections`。**

### 現況（跑一次就知道，不要憑這份文件）

```bash
python scripts/apocrypha_audit_quality.py
```

兩道閘：①複合檔（正文含 ≥2 個「卷N…簡介」標頭）②壞文字層（字形訛誤 > 5／萬字）。
2026-09-18 的結果是 5 份複合（含一份是刻意留的暫存桶）、15 份壞 OCR，最嚴重的是
`protoevangelium-james` 43.8／萬、`joseph-aseneth` 41.5、`pistis-sophia` 25.6、
`gmatthias` 22.9、`infancy-thomas` 16.1。

### 原檔（全部都在，已驗）

`G:\我的雲端硬碟\資料\知識圖工作室\電子圖書館\世界宗教\基督教\基督教典外文獻 (10 冊)\`

| 冊 | 頁 |
|---|---|
| 新約篇 第 1–4 冊 | 320 / 363 / 312 / 299（小計 1,294） |
| 舊約篇 第 1–6 冊 | 326 / 350 / 429 / 427 / 487 / 507（小計 2,526） |
| **合計** | **3,820 頁** |

⚠️ 同一夾裡另有「王曉朝，基督教典外文獻─新約篇─第 N 冊」四本，那是**不同譯本**，
`total_pages` 與 `chunk_count` 對不上（頁 9 / chunks 100），本身也有問題，
**先不要混進來**。

**建議分兩段**：先跑新約篇 4 冊（1,294 頁，CPU 約 3 小時），把整條流程驗通，
再決定舊約篇 6 冊要不要接著跑。

---

## 二、前一輪已經做完的，不要重做

1. **`gthom` 已修**。它原本掛 574 節，其中只有 213 節（ch.11–12）真的是《多馬福音》；
   其餘 361 節橫跨叢書總論、雅各原始福音、嬰孩多馬、拉丁語嬰孩福音、彼拉多文獻、
   十二使徒福音、腓力福音、摩尼派殘片、多馬書。已搬到 `cct-gospels-unsplit`，
   **沒有刪除**。重做時這 361 節是你的對照組。
   修復腳本：`scripts/apocrypha_repair_gthom.py`（一次性，留著當範例）。

2. **兩篇嬰孩福音已經用新管線重做並入庫**，可以當**驗收樣本**：
   - `infancy-latin` 7 節（§68–74，印刷頁 150–154），訛誤 0
   - `infancy-arabic` 56 節（序言＋§1–55，印刷頁 110–132，含 26 條註腳），訛誤 0
   - 腳本：`scripts/ingest_infancy_gospels.py`，**照抄它的結構**
   - MinerU 輸出留在 `output/apocrypha-ocr/`（不進版控）

3. **品質閘已寫好**：`scripts/apocrypha_audit_quality.py`

---

## 三、🚨 必讀的坑（每一條都是踩過的）

### A. MinerU 把頁碼與註腳放在 `discarded_blocks`

`scripts/mineru_ocr.py` 的 `pages_from_middle()` 只讀 `preproc_blocks`（那是為了修
跨頁段落刻意選的，不要改它）。但**頁碼與註腳在 `discarded_blocks`**，型別分別是
`page_number` 與 `page_footnote`。只吃它產的 jsonl 會**把註釋與原書頁碼靜默丟光**，
而且頁面看起來完全正常。

→ **回頭讀 `middle.json`**。實測阿拉伯語那篇有 26 條註腳、22 個頁碼區塊，全在
`discarded_blocks` 裡。範例見 `ingest_infancy_gospels.py` 的 `read_middle()`。

→ 跑 MinerU 時**輸出夾要留著**：`run_mineru()` 用的是 `TemporaryDirectory`，
跑完 `middle.json` 就沒了。直接呼叫 `_mineru_venv\Scripts\mineru.exe` 並指定 `-o`。

### B. 頁碼用頁面上印的那一個，不要推算

`discarded_blocks` 的 `page_number` 就是原書頁碼。只有章首頁（版心不印頁碼）才回退
到頁序推算，而且推完要跟宣告的頁範圍對得上才放行。**假頁碼比沒有更糟。**

### C. 切節只認節號當錨，不要拿段落形狀去猜

前一輪第一版用「這段夠長、開頭不是標點 → 判為新一節」去補被 OCR 吃掉的節號，結果把
**跨頁續段**全判成新節：**55 節照樣連號、字數照樣對得上、閘照樣全過**，但每一節的
界線都往前挪了一段。印出來一切正常。

→ 沒帶號的段落一律併進當前節。真正被吃掉的節號走**寫死的對照表**（只認那一節開頭的
原文），比對不到／比對到多處／位置不在前後兩節之間，一律擋下不寫。

### D. 🚨 chunk 邊界不對齊作品邊界

`gthom` 的 ch.10 第 1 節還是拉丁語嬰孩福音的結尾，第 2 節已經是「卷二 多馬福音 簡介」。
**所以不能照 chapter 切。** 要靠正文裡的「卷N…簡介」標頭定界——而那些標頭在舊 OCR 裡
本身就是壞的（「該斯底主義者」＝諾斯底、「以使徒為名的偽音書」＝福音書）。

→ **順序不能反：先重 OCR，再定界。**

### E. 字數不是好閘，要逐段點名

節號被切掉、段落接合符不同，本來就會差幾十字，差多少都能說成「正常」。
→ 閘要問：**每一個 preproc 段落是不是都在某一節／簡介／序言／版權尾裡找得到**。
前一輪兩篇都是「0 段落外」。

### F. MinerU 走 `--device cpu`，不要搶 GPU

那張卡只有 6GB、同時只能跑一個，而且多半被別條線的夜班佇列佔著。
`scripts/mineru_ocr.py run` 已經支援 `--device cpu`：不佔顯存所以**略過 GPU 鎖**，
也不從別人手上接鎖。實測 28 頁 229 秒。

**不可以** `Stop-Process` 殺掉別人的 MinerU。

### G. PostgREST 靜默截在 1000 筆

伺服器端 `db-max-rows=1000`，`limit` 給再大都沒用。**一定要分頁抓**（見
`apocrypha_audit_quality.py` 的 `fetch_all`）。而且回傳可能是 dict 不是 list
（欄位名打錯時），要擋。

### H. 不要刪，要搬

有些作品站上沒有別的來源，刪掉就真的沒了。舊資料搬到標示清楚的暫存 slug，
在 `apocrypha_documents` 建一列寫明它是什麼、為什麼在那裡。

### I. 「在預期的鍵底下查無」不等於「內容不存在」

前一輪查 `doc_slug=infancy-latin` 得 0 節就認定站上沒有，其實內容躺在 `gthom` 底下
（相似度 0.82／0.66／0.97，是同一段的兩個 OCR 版本）。
→ **入庫前先用模糊比對掃全表**，精確子字串會被壞 OCR 的錯字擋掉。

### J. 訛誤指紋是這一套書專屬的

`apocrypha_audit_quality.py` 的 `BAD_GLYPHS`（「耶蕻」「約慈」「該斯底」…）只驗得出
**這一套書**的壞法，不是通用的 OCR 品質分數。換一套書要另外找它自己的指紋。

### K. 稽核跑了不等於稽核看了

**不要**把「改資料→重生→跑稽核→commit→push」串成一條背景指令——紅燈會混在 push 的
輸出裡被掃過去。**前景跑稽核、讀完綠了再提交。**

### L. push 被擋也會 exit 0

`git push` 被 pre-push hook 擋下或網路斷掉時照樣可能 exit 0。
**推完一定要 `git merge-base --is-ancestor <sha> origin/master` 實地比對。**
GitHub 這幾天 DNS 不穩，多半要重推兩三次。

### M. 這台筆電會休眠

`mineru_ocr.py` 已經有 `keep_awake()`。長跑要設計成可續跑：做完一冊就存檔，
不要全部跑完才寫。

---

## 四、驗收標準

1. `python scripts/apocrypha_audit_quality.py` → **兩道閘皆過**
   （或剩下的未過項目在文件裡有明確說明為什麼不處理）
2. 每一份重做的文獻：**逐段點名 0 段落外**、**頁碼是原書印刷頁**、**註腳有收**
3. 抽驗三份，讀回 DB 比對節數與首尾節文字
4. `node scripts/genealogy_audit_apocrypha.mjs`、`genealogy_audit_tags.mjs`、
   `genealogy_audit_segments.mjs` 三支**前景**跑完全綠
5. `data/christian-genealogy/apocryphal-gospels.json` 與 `nt-apocrypha.json` 的
   `sections` 計數與 DB 實際對得上（前一輪 `gthom` 就是這裡灌水：宣稱 574 實際 213）
6. 完成後更新 `.claude/skills/scripture-canon/SKILL.md`

---

## 五、相關檔案

| 用途 | 路徑 |
|---|---|
| 品質閘 | `scripts/apocrypha_audit_quality.py` |
| 入庫範例（照抄結構） | `scripts/ingest_infancy_gospels.py` |
| gthom 修復（一次性範例） | `scripts/apocrypha_repair_gthom.py` |
| MinerU | `scripts/mineru_ocr.py`（`run --device cpu`） |
| 譜系側的節數 | `data/christian-genealogy/{apocryphal-gospels,nt-apocrypha}.json` |
| 三支譜系稽核 | `scripts/genealogy_audit_{apocrypha,tags,segments}.mjs` |

**解譯器一律寫明路徑**：`C:\Users\user\AppData\Local\Python\bin\python.exe`
（PowerShell 裸 `python` 會中 `_whisper_venv`，管線起來不報錯只卡 import）。
