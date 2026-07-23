# 交接：教父著作獨立子站 + 排版修復（2026-07-20）

新 session 從這裡接。分三塊：**① 已完工** / **② 待續（吞字修復）** / **③ 待辦（T11 漏譯）**。

---

## ① 已完工並上線 ✅

### /fathers 獨立子站（commit `e4eebb09`，229 測試綠、已 push）

使用者要求：「/fathers 跟電子圖書館分開，做獨立網址和 UI/UX」。定調＝**羊皮紙古典風**，**入口不動**（仍從 `/scripture-canon/christianity` 進，不加首頁卡片）。

| 檔案 | 內容 |
|---|---|
| `pages/fathers/[id].vue` | **新** 專屬羊皮紙 reader（非共用 `/ebook/[id]`）|
| `pages/fathers/index.vue` | listing 改羊皮紙；卡片改連 `/fathers/[id]` |
| `lib/ebook-render.ts` | **新** 兩個 reader 共用的純渲染核心 |

**reader 有**：中／對照／單一來源切換、卷→書→段三層目錄側欄、朗讀（`useReaderTts`）、字級行距主題（`EbookDisplaySettings`）、封面頁、腳註雙向錨點。
**reader 刻意沒有**：annotations／書籤／編輯 modal／原頁下載／閱讀狀態 —— 這些是「圖書館」功能，拿掉以強化區隔。

**架構決策**：資料仍走共用 `ebooks`／`ebook_chunks` + `/api/ebooks/[id]`，**沒有做 schema 遷移**（沒必要、成本高）。只有 UI/UX 與網址獨立。

> ⚠️ `lib/ebook-render.ts` 是從 `pages/ebook/[id].vue` 逐字抽出的純函式（escapeHtml / inlineFmt / renderMarkdown / renderTocPage / buildParallelColumns）。目前**只有 fathers reader 匯入它**；`pages/ebook/[id].vue` 仍保有自己那份 inline 副本（怕動到全站圖書館 reader）。要動渲染邏輯**兩邊都要改**，或擇日讓 ebook reader 也改吃這支 lib。

---

## ② 待續：教父書「標題吞內文」排版修復 🔧

### 問題長怎樣

翻譯時 LLM 把 `## 小節標題` 和緊接的內文段落**黏成同一行**，於是 reader 把整段 900 字當成一個「置中＋雙線」的巨大標題來排。

```
## I.— 導論聖耶柔米之重要性在於下列事實：(1) 他是聖經拉丁文譯本…（共 959 字全在標題行）
```
英文原文本來是分開的（`I.— Introductory.` 空行後才是內文），所以**英文 source_text 就是分界的 ground truth**。

### 真實規模（重要！別再相信 228 這個數字）

| | |
|---|---|
| **1,455 個 chunk**，共 **5,776 個吞字標題**，橫跨 **全部 37 卷** | ← 正確 |
| ~~228 處／29 卷~~ | ← **錯的**，別用 |

**為什麼會錯**：我原本從稽核報告的 T2 命中推算，但 `scan_translated_book.py` 的 T2 規則**每個 chunk 只回報第一個標題**，嚴重低估。腳本已改成**整本掃 JSONL**（`load_targets()`），不再依賴稽核 JSON。

### 工具：`scripts/fix_fathers_heading_swallow.py`

```bash
# 先看樣本（不寫入）
python scripts/fix_fathers_heading_swallow.py --sample 10

# 實際修（寫 JSONL → R2 → DB previews），一次 3 本
python scripts/fix_fathers_heading_swallow.py --apply --no-gemini --limit 3
```

**運作方式**：拿英文 heading + 內文開頭當參考，請 LLM 只在正確分界切開、**逐字不得改動**；寫入前一律驗證 `norm(title)+norm(body) == norm(原文)`，不過就略過該處並記錄。書是**整本原子寫入**（跑完一本才寫），所以中斷不會留半寫壞檔。**冪等**，可反覆續跑。

**已知狀態**：先前跑過幾輪，每個 chunk 各修掉 1 處（當時有「只修第一個」的 bug，已修正為迴圈修到沒有為止）。已修的部分**有保留**，沒有資料遺失。

### 踩過的坑（別重蹈）

1. 🚨 **靜默跳過 = 假成功**。舊版路徑失效時 `fn.exists()` 為 False 就 skip，腳本印出「books still needing work: 0 ✓ DONE」看起來完美，其實**一本都沒處理**。已加 **fail-fast**：`CH` 不存在直接 `SystemExit`。任何回報「0 需要處理」時，**務必另外掃檔案確認**。
2. **Gemini 額度用罄**時每次呼叫會先耗時輪完所有 key 才 fallback。加了 `--no-gemini` 直接走 NVIDIA（切分品質相同，樣本 9/10 通過逐字驗證）。
3. **背景任務會隨 session 結束被砍**（這次被砍 3 次）。5,776 處是數千次 LLM 呼叫、數小時的工作 —— **建議掛成排程**（仿 `KGL_Fleet_Keeper`）分批跑，不要靠對話中的背景任務。用 `--limit N` 分批。
4. 一個 chunk 常有**多個**吞字標題（合併多章的 chunk，如「第1-10章」）。必須迴圈修到沒有為止。

---

## ③ 待辦：T11 漏譯核查

稽核發現 **537 處** 中英段落數落差 >25%（INFO 級），是「漏譯／漏段」的軟訊號，尚未逐案查。

```bash
python scripts/scan_translated_book.py <ebook_id> --gate   # 產重譯待辦
```
使用者已同意這輪一併處理，但因吞字修復規模暴增而未開始。

---

## 稽核結論（37 卷全掃，供參考）

**翻譯品質：合格。** 實讀內文流暢、術語正確。最關鍵的 **T9 跨作品污染＝0（全 37 卷）**，精修結構完整性達標。

| 規則 | 命中 | 判定 |
|---|---:|---|
| T9 跨作品污染 | **0** | ✅ 全乾淨 |
| T2 標題／卷名分歧 | 719 | 其中約 491 是**誤報**（導論／信件標題本來就跟卷名不同）；其餘才是吞字 |
| T10 腳註 ref/body 對不上 | 1036 | 多為 CCEL 章末孤兒註，雜訊為主 |
| T11 中英段落數落差 | 537 | 🟡 見 ③ |
| T4 chapter_path 含 markdown 控制字元 | 4 | 小、可安全修 |

重跑稽核：
```bash
python scripts/scan_translated_book.py <ebook_id> --json
```

---

## 🚨 全站注意：Drive 改版打斷了 pipeline 路徑

2026-07-20 「知識圖工作室」重整已執行（使用者有意為之）：

```
舊：G:\我的雲端硬碟\資料\電子書\_chunks        ← 已不存在
新：G:\我的雲端硬碟\資料\知識圖工作室\_chunks   ← 2,174 個 jsonl 在這
```

repo 內 **91 支腳本、102 處**仍寫舊路徑（`scan_translated_book.py`、`translate_ebook_to_zh.py`、OCR、`parse_worker.py`、jung 系列…）。這些多半**失敗時不報錯只跳過**，過夜排程（艦隊 keeper／OCR／翻譯）可能正在無聲空轉。

```bash
grep -rn "資料.電子書" scripts/ --include=*.py   # 102 處
```

**尚未統一修**（使用者說路徑改動是他要的，先寫交接）。建議：全部改吃 `EBOOK_CHUNKS_DIR` 環境變數 + 新預設值，並加 fail-fast，避免再出現靜默假成功。`fix_fathers_heading_swallow.py` 已照此改好，可當範本。

> ✅ **2026-07-20 稍晚已處理**（commit `a06381f6`）：整個 repo 111 檔的舊路徑一次改完，現在 `grep -rn "資料.電子書" scripts/` = 0 處；排程與翻譯艦隊已停機搬檔後重接，並確認新 `_chunks` 有即時寫入（不是空轉）。
> ✅ **吞字修復已掛排程**：`KGL_Fathers_Fix`（每 30 分）→ `scripts/fathers_fix_keeper.ps1` → 沒有 worker 在跑就續跑 `fix_fathers_heading_swallow.py --apply --no-gemini --limit 3`（冪等，中斷不留半寫壞檔）。log：`scripts/logs/fathers_fix_keeper.log`。
> ⏳ **③ T11 漏譯核查（537 處）仍未開始**。
