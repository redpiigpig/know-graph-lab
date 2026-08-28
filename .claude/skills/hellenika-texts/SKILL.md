---
name: hellenika-texts
description: 希臘羅馬大藏經（/hellenika）的**文獻**全文取源與逐段對照 —— 與 [[hellenika-epigraphy]]（石頭上的東西）分工，本 skill 管「書上的東西」：赫西俄德《神譜》、荷馬詩頌、俄耳甫斯讚歌這類傳世文本，取希臘文原文與公有領域英譯，按詩行號切段，再逐段譯成繁中，出成 reader 的三欄對照。含 Perseus 標準 TEI 的抓法、切段對齊原則、各篇取源現況與尚無 PD 電子文本的缺口。Use when 要新增一篇文獻的全文轉錄、要補某篇的中譯、要處理沒有公有領域英譯的篇目、要調切段粒度、或使用者說「把某某書的原文放上去」。體例底層見 [[hellenika-canon]]。
---

# 希臘羅馬大藏經 — 文獻全文取源與逐段對照

書目卡只告訴讀者這部書存在。這個 skill 管的是**把書本身放上去**：原文一欄、
公有領域英譯一欄、我的繁中一欄，逐段對齊。

三支取源腳本的分工，記牢別走錯：

| 腳本 | 取什麼 | 切段單位 | 產物 |
|---|---|---|---|
| `hellenika_cgrn.py` | 祭儀規範銘文 | 石面行號 | `sources/cgrn/` |
| `hellenika_phi.py` | 其餘銘文與紙草 | 案號或石面行號 | `sources/phi/` |
| **`hellenika_text.py`** | **傳世文獻** | **詩行號** | **`sources/text/`** |

---

## 1. 取源：Perseus 標準 TEI，不走 API

🚨 **不要用 Scaife 的 CTS API**（`scaife-cts.perseus.org`）。2026-08-28 實測整個
API host 連不上（curl 回 000），而 reader 頁面是 JS 驅動的，抓下來沒有正文。

改抓上游的標準 TEI 原始檔：

```
https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/{群}/{作}/{urn}.xml
```

例：`data/tlg0020/tlg001/tlg0020.tlg001.perseus-grc2.xml` ＝ 赫西俄德《神譜》希臘文。

好處：公有領域、無節流、行號完整、不必解析 JS。

**版本後綴要試不要猜。** `perseus-eng1` 常常不存在而 `perseus-eng2` 存在
（《神譜》就是這樣）；`tlg0013.tlg001.perseus-eng1` 也是 404。腳本對 404 回 `None`
並印出「TEI 不存在」，不要當成程式壞掉。

---

## 2. 切段：以英譯的里程碑為邊界

希臘文 TEI 每行一個 `<l n="N">`；Evelyn-White 的英譯**每五行才下一個里程碑**
（`<l n="1">`、`<l n="5">`、`<l n="10">`…），中間是連續散文式的詩行。

所以切段邊界一律取**英譯的里程碑**，再把落在該區間的希臘文行併起來：

```
段 = 連續 4 個英譯里程碑（MILESTONES_PER_SEG）≈ 20 行
```

這樣兩欄的邊界永遠對得上。反過來若以希臘文行號切，會切在英譯句子中間，
出來就是半句對半句——那正是 [[feedback_reader_silent_failures]] 那類「印得出來
但配錯」的錯法。

英譯不存在時退回「每 5 行一個假里程碑」，並把 `pivot` 標成 `'none'`、填
`pivot_note`——與治癒銘文同一套處理（見 [[hellenika-epigraphy]] §11）。

---

## 3. 產物 schema

`data/hellenika/sources/text/{slug}.json`：

```jsonc
{
  "source": "perseus",
  "siglum": "Hes. Th.",          // 學界引用縮寫
  "slug": "theogony",
  "url": "…raw.githubusercontent…",
  "title_zh": "神譜", "title_en": "Theogony", "author": "赫西俄德",
  "volume": "A",                  // 所屬卷 key
  "licence": "…",
  "pivot": "perseus-eng",         // 'perseus-eng' ＝經由英譯；'none' ＝直譯自原文
  "pivot_note": null,
  "lines_total": 1022,
  "names": {},                    // 本篇專名定譯表，翻譯前先填
  "segments": [
    { "line_from": 1, "line_to": 19, "greek": "…", "en": "…", "zh": "" }
  ]
}
```

`zh` 一律先留空，翻譯是獨立的第二步。**取源與翻譯分開跑**，因為翻譯要吃
Gemini／NVIDIA／OpenRouter 的額度，而整夜驅動器
（`hellenika_overnight.py`）也在用同一批 key——兩邊同時跑必然互撞 429。

---

## 4. 🚨 整夜驅動器會把 `data/hellenika` 整個 git add

`hellenika_overnight.py` 的 commit 是 `git add data/hellenika`（無白名單）。
所以**驅動器在跑的時候，不要把半成品寫進 `data/hellenika/`**，否則會被它
連同簡介一起 commit＋push，訊息還寫著「補簡介」。

作法：取源時加 `--out c:/tmp/hellenika/text`，等驅動器停了再搬進去。

---

## 5. 現況（2026-08-28）

### ✅ 原文＋英譯＋繁中三欄全數完成（2026-08-29）

| 篇 | 卷 | 段數 |
|---|---|---|
| 赫西俄德《神譜》 | Α | 53／53 |
| 赫西俄德《工作與時日》 | Β | 44／44 |
| 荷馬詩頌 第 1–33 首 | Ο | 138／138 |

合計 **235/235 段**，4,176 行。翻譯走 `scripts/hellenika_text_align.py`，引擎 Haiku
（`HELLENIKA_ENGINE=haiku`）。已接進 reader：`sources/index.ts` 認第三種來源
`perseus`，路由 slug 不是「庫-編號」而是檔名（`/hellenika/text/theogony`）。

**長度比校準**：中譯字元數 ÷ 英譯字元數，實測中位數 **0.307**、全距 0.18–0.41。
拿 0.25 當下限會誤報十幾段（實查都是完整的，只是中文較密）。要設閘門就用
**低於 0.15 或高於 0.60** 才叫可疑。

### 🚨 兩個實際卡住過的坑

1. **模型把 JSON 的鍵回成「第3段」而不是「3」。** 嚴格比對會把整批好譯文丟掉，
   `homeric-hymn-03` 就這樣卡在 19/28 而看起來像「額度不夠」。修法是抽出鍵裡的
   數字再比對（`re.sub(r'\D', '', k)`），逐段對應的保證不放寬。
   **不要看到「整批丟棄」就以為是引擎問題，先看它回了什麼鍵。**
2. **OAuth access token 每幾小時滾一次。** 長跑的 worker 抓著舊 token 會一路 401，
   而 401 是 `anthropic.AuthenticationError`，不會被 429／連線錯誤的 except 接到，
   於是被當成「引擎全乾」放棄。`ask_haiku` 現在接 401 後丟掉 client 並清空 mtime
   記憶，下一次呼叫強制重讀 `.credentials.json`。

### 尚無公有領域電子文本

- **《俄耳甫斯讚歌》87 首** —— 現代希臘多神教儀式實際誦唸最多的一批，但：
  Perseus 與 First1KGreek 都沒有（`tlg1815` 兩邊皆 404）；Bibliotheca Augustana
  的舊網址已 404；sacred-texts（Taylor 1792 英譯）回 403。
  **下一步**：希臘文找 Abel 1885 或 Quandt 1941 的掃描本（Abel 已入公有領域），
  英譯用 Taylor 1792（PD），兩者都可能得走 archive.org 而非現成 TEI。

### PHI 現況（供 [[hellenika-epigraphy]] 參照）

`/text/{id}` 仍可取（實測 28551 回 200），但 **`/search` 已回 403**，skill 裡
「站上 /search?patt= 可查編號」那條作法失效。找編號改走已刊概覽：
TAM V,1 452 ＝ PHI 263861、TAM V,1 535 ＝ PHI 263959，同一部書內編號大致遞增，
可據此推算並以 `expect` 驗證。

---

## 6. 加一篇的流程

1. 在 `TARGETS` 加一筆（slug／中英題／作者／所屬卷 key／siglum／grc 與 eng 的 urn）。
2. `--fetch {slug} --lines 1-115` 先試跑一小段，肉眼確認兩欄對得上。
3. 確認後 `--fetch {slug}` 全篇。
4. 填 `names`（專名定譯先過 [[translation-glossary]]）。
5. 翻譯（第二步，另跑；引擎鏈同 repo 慣例 Gemini → NVIDIA → OpenRouter）。
6. 書目條目補 `link` 指向 reader。
