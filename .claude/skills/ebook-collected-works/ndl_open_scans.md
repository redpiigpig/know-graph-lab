> ⚙️ **引擎政策**：OCR 走 Gemini Vision（主）→ Haiku Vision（**須明確下令**，
> 見 [[feedback_ocr_strategy]]）。NVIDIA 那一層是純文字，不能做 vision。

# NDL デジタルコレクション 取源管線（2026-09-07 試點）

無教會譜系裡戰前那批是公有領域，卻**不在青空文庫、也不在 libgen**——只有國立國會
圖書館的掃描本。這一檔記管線本身；書目與版權判斷見
[mukyokai_collected_works.md](mukyokai_collected_works.md)。

> ⚠️ 這個檔名先前被 `scripts/ndl_build.py` 的 docstring 引用，但**檔案一直不存在**
> （上一輪只寫了引用沒寫檔）。本檔補上。下面的 33 部普查數字來自上一輪的交接紀錄，
> **本輪只逐一驗證了試點那一部**，其餘尚未逐 pid 複驗。

## 🚨 判公開範圍只有一個可靠辦法

    curl -s -o /dev/null -w "%{http_code}" https://dl.ndl.go.jp/api/iiif/{pid}/manifest.json
    # 200 ＝ インターネット公開（可用）
    # 404 ＝ 館內限定／個人送信（不可用）

目錄 metadata **不帶**這個欄位，別想從書誌判斷。
「圖書館‧個人送信」看起來可用，但**居住在日本境外者不能使用**，不要算進來。
不要繞過存取控制。

## 兩個 API 的分工

| 用途 | 端點 | 備註 |
|---|---|---|
| 書誌＋**目次**（分章靠它） | `lab.ndl.go.jp/dl/api/book/{pid}` | `page` 偶爾回 0，那時回頭數 IIIF canvas |
| 影像＋公開範圍探針 | `dl.ndl.go.jp/api/iiif/{pid}/manifest.json` | 也是唯一可靠的公開範圍判準 |

## 普查（上一輪交接數字，未逐 pid 複驗）

| 作者 | 可直接下載 | 備註 |
|---|---|---|
| 畔上賢造 | 16 | 全球 PD（卒 1938） |
| 矢內原忠雄 | 9 | 日本 2012 起、台灣皆 PD |
| 藤井武 | 7 | 全球 PD（卒 1930） |
| 內村鑑三 | 1 | 全球 PD |
| **合計** | **33** | |

黒崎幸吉（28 部）、塚本虎二（35 部）、南原繁（23 部）數位化了但**全是館內限定**
（卒後 70 年未過），不可取用。

## 管線（`scripts/ndl_build.py`，`scripts/tests/test_ndl_build.py` 23 例綠）

    python scripts/ndl_build.py --probe 1099766              # 書誌＋分章
    python scripts/ndl_build.py --fetch 1099766              # 影像 → c:/tmp/ndl_cache/{pid}
    python scripts/ndl_build.py --ocr   1099766              # Gemini Vision，一頁一個 checkpoint
    python scripts/ndl_build.py --build 1099766 --slug ...   # → ndl_data/{slug}/secN.json

輸出與 uchimura／howes **同形**（`heading`／`title_zh`／`src`／`zh`），
才接得上 `uchimura_auto.py` 的 checkpoint／翻譯／上架那一段。

### 本輪加的兩道保險

- **`refuse_empty_build()`**：所有 section 都沒有正文就拒絕寫檔。不擋的話會產出
  一整套結構正確、目錄齊全、每章卻都沒有字的 `secN.json`——**頁面看起來完全正常**。
  這道閘在本輪真的擋下了一次（OCR 因額度沒跑成，接著 build 就被擋）。
- **`_client_for()`**：`genai.Client` 一定要綁在變數上。寫成
  `genai.Client(...).models.generate_content(...)` 那個 client 是暫時物件，
  請求還沒回來就可能被 GC 關掉，報
  `RuntimeError: Cannot send a request, as the client has been closed.`
  ——錯誤訊息完全看不出是這個原因，踩過一次。

## 試點：畔上賢造《無教会主義》1934（pid 1099766）

| 步驟 | 狀態 |
|---|---|
| IIIF manifest | ✅ 200（インターネット公開） |
| 書誌 | ✅ 東方書院 1934，影像 18 頁 |
| 目次分章 | ✅ 9 章全部解析成功（見下） |
| 影像下載 | ✅ 18 張 → `c:/tmp/ndl_cache/1099766` |
| OCR | ⛔ **未完成——Gemini 免費層當日額度已用盡** |
| build／翻譯／上架 | ⏳ 等 OCR |

分章結果（影像號範圍）：

    3–3    第一　教派ではない          10–10  第六　聖書的基督教の提唱
    4–4    第二　起源                  11–11  第七　信仰第一主義の提唱
    5–5    第三　現状                  12–14  第八　日本的基督教の提唱
    6–7    第四　教會に對する抗議      15–18  第九　無教會主義の傳道法
    8–9    第五　無教會主義についての誤解

**目次分章這一段完全不用改**——`parse_toc_entry` 把 NDL 那三種寫法都吃下來了，
9 章一次到位。

### ⛔ OCR 卡在哪

`gemini-2.5-flash` 免費層是 **20 requests／day／key** 的**日額度**（當天不恢復，
見 [[reference_gemini_free_tier_quotas]]）。本輪開跑時當日額度已被其他工作用完，
兩把 key 連續 429 → 依 [[feedback_ocr_two_strike_quota]] 自動退出，**0 頁完成**。

**接手時的選項**：
1. **等隔日額度重置**再跑 `--ocr 1099766`。18 頁＝18 requests，一天的額度剛好夠一本。
   checkpoint 是逐頁的，中斷再跑會從沒做的那頁接下去。
2. **改用 Haiku Vision**——但依 [[feedback_ocr_strategy]] 這需要**使用者明確下令**，
   且嚴格一次一本。本輪沒有這個授權，所以沒有自行切換。

## 接手清單

1. 額度重置後跑 `--ocr 1099766` → `--build 1099766 --slug muky-shugi`。
2. 校 OCR：直排舊字舊假名是這批的難點，`clean_ocr_text` 只處理了振り仮名與頁碼，
   **舊字體有沒有被 Gemini 偷偷轉成新字體要抽查**（prompt 已明令禁止，但要驗）。
3. 接 `uchimura_auto.py` 翻繁中、上架，並在 store 的畔上賢造 hub 把該部
   `status` 由 `planned` 改為 `done` 並填 `ebookId`。
4. 其餘 32 部逐 pid 複驗 IIIF manifest 後再排隊。
