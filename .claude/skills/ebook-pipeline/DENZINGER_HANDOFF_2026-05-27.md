# Denzinger OCR Handoff (2026-05-27)

公教會之信仰與倫理教義選集 (Denzinger 中譯 PDF) OCR 進度與下一 session 接手指南。

## 0. TL;DR — 接手的 3 件事

1. **檢查 gap-fill 是否完成**（看下面「即時狀態查詢」一節）
2. **若未完成且 quota 卡住** → 等 1-3 小時後 `python -X utf8 -u scripts/_denzinger_gaps_ocr.py`（會 resume）
3. **若已完成** → 跑 consolidate + segment 兩支腳本（見「OCR 完之後的 Pipeline」）

---

## 1. 目標

把 Denzinger 中譯 PDF 完整 OCR → 入 ebook reader、再依 [book-structure-bilingual-parallel.md](./book-structure-bilingual-parallel.md) 切成 DH-indexed chunks → 接到 `/creeds` 一次補 44 份大公會議中譯缺口。

## 2. 已完成

| 步驟 | 狀態 | 詳細 |
|---|---|---|
| Drive ingest | ✅ | ebook_id `568726d3-967e-457a-ab69-7452b21d606f` |
| Drive 路徑 | ✅ | `G:/我的雲端硬碟/資料/電子書/世界宗教/基督教/教會法典與信條/輔仁神學著作編譯會，公教會之信仰與倫理教義選集.pdf` |
| DB category | ✅ | `世界宗教` / sub `基督教/教會法典與信條` |
| Main OCR（10 頁/batch）| ⚠️ | 跑完 240/243 batches 但 `max_tokens=4096` 截斷 → 801 / 2430 頁實際有內容（**fix `08ddff1` 已修為 32000**，僅這本書受影響）|
| Tail OCR pp 2401-2430 | ✅ | 30/30 過，附錄五 新教信條 |
| **Gap-fill OCR**（剩 1629 頁，單頁/call）| 🔄 進行中 | 上次跑到 663/1629（page 948）撞 Anthropic 帳號級 429 |
| Bilingual-parallel spec | ✅ | commit `47f336b`，[book-structure-bilingual-parallel.md](./book-structure-bilingual-parallel.md) |
| Scheduled task 關閉 | ✅ | KGLab-OCR-Daily-10/14/18 全 `Disable-ScheduledTask` |

## 3. 即時狀態查詢（每個 session 開頭跑）

```bash
cd c:/Users/user/Desktop/know-graph-lab

# (a) 看 background task 是否仍跑（Windows process 查詢）
powershell -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'python.exe' -and \$_.CommandLine -like '*_denzinger_gaps_ocr*' } | Select-Object ProcessId, @{N='Started';E={\$_.CreationDate}}"

# (b) gap-fill log latest 5 lines
ls -t scripts/logs/ocr_haiku_denzinger_*_gaps*.log | head -1 | xargs tail -5

# (c) 已存 chunks 數
python -X utf8 -c "
import json
from pathlib import Path
for name in ['.jsonl', '.gaps.jsonl']:
    p = Path(r'G:\我的雲端硬碟\資料\電子書\_chunks\568726d3-967e-457a-ab69-7452b21d606f' + name)
    if p.exists():
        with p.open(encoding='utf-8') as f:
            ok = sum(1 for l in f if l.strip() and json.loads(l).get('content', '').strip())
        print(f'  {name}: {ok} non-empty chunks')
"

# (d) DB row state
python -X utf8 -c "
import requests
env = {}
with open('.env', 'r', encoding='utf-8-sig') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip(chr(34)).strip(chr(39))
key = env['SUPABASE_SERVICE_ROLE_KEY']
r = requests.get(env['SUPABASE_URL'] + '/rest/v1/ebooks?id=eq.568726d3-967e-457a-ab69-7452b21d606f&select=parsed_at,parse_error,chunk_count,total_chars,total_pages',
    headers={'apikey': key, 'Authorization': f'Bearer {key}'})
print(r.json())
"
```

## 4. 若 gap-fill 還沒完成

### 4.1 重新跑 gap-fill (resume from checkpoint)

```bash
LOGFILE="scripts/logs/ocr_haiku_denzinger_$(date +%Y-%m-%d)_gaps3.log"
python -X utf8 -u scripts/_denzinger_gaps_ocr.py 2>&1 | tee -a "$LOGFILE"
```

Script 會：
1. 讀 `_chunks/{id}.jsonl` 找出已完成的 pages
2. 讀 `_chunks/{id}.gaps.jsonl` 找出 gap-fill 已完成的 pages（不重做）
3. 列出 missing pages（PDF 有真實內容、JSONL 沒有的）
4. 單頁 + 4-prompt fallback OCR
5. 結果寫進 `.gaps.jsonl`
6. **新加的 2-strike rule**：2 頁連續 `all_prompts_failed` 就退出（避免 quota 卡住時無限 retry 浪費）

### 4.2 如果 2-strike 連續退出 = quota 真的卡住

Anthropic Max plan 帳號級 burst limit。memory 紀錄：「~5 本/天」對應 token quota 上限。等：
- **每分鐘 burst 限制**：5-10 分鐘
- **每小時/每天 token 配額**：1-24 小時

策略：等 1-2 小時再試。日級 quota reset 一般是 UTC midnight (Taipei 08:00) 或固定鐘點。

### 4.3 background 跑時 — 不要 sleep poll

啟 task 用 `run_in_background=true`，會自動通知完成。不要寫迴圈每幾秒查 — 用 task-notification。

## 5. OCR 完之後的 Pipeline

按 [book-structure-bilingual-parallel.md](./book-structure-bilingual-parallel.md) 跑：

### Phase 1: Consolidate `.gaps.jsonl` → final `.jsonl`

新寫 `scripts/_denzinger_consolidate.py`（**待寫**）：

1. 讀 `_chunks/{id}.jsonl`（current 801 chunks）
2. 讀 `_chunks/{id}.gaps.jsonl`（含新 OCR 的 page）
3. Merge：用 page_number 做 key，gaps 的 content 覆蓋空 chunks
4. Renumber chunk_index 0..N-1
5. 寫 final `_chunks/{id}.jsonl`（覆蓋 + 備份舊版）
6. push R2 (`push_to_r2(book_id, jsonl_path)`)
7. UPDATE `ebooks` row: `chunk_count=N`, `total_chars=sum`

### Phase 2: Segment to DH-indexed chunks

新寫 `scripts/segment_denzinger.py`（**待寫**），按 spec section 4：

1. 讀 consolidated page-level chunks
2. Per chunk content，detect DH boundaries: `^\s*(\d{3,5})\s+(.+)`
3. 拉中分塊（CJK char 比例）
4. Section header 偵測（「第 N 場會議」/ 教宗名 / 通諭名 等）
5. 輸出新 chunks: `section_type ∈ {'header', 'entry', 'commentary'}`
6. Apply mode：dry-run / write-jsonl / apply (寫 DB + 更新 `display_mode='bilingual-parallel'`)

### Phase 3: Reader Vue 改動

- DB migration: `ALTER TABLE ebooks ADD COLUMN display_mode text DEFAULT 'standard'`
- 新增 `components/ebook/BilingualReader.vue`（CSS grid 兩欄 + DH badge + 三段切換 + DH 跳轉 input）
- 改 `pages/ebook/[id].vue` 加 `display_mode` dispatch

### Phase 4: 抽 DH ranges 寫進 /creeds

新寫 `scripts/_denzinger_to_creeds.py`（**待寫**）：

按 `COUNCIL_DH_RANGES` 表（spec section 7）：
- 早期 3-7 → DH 100-605
- 中世紀 8-18 → DH 600-1450
- Trent 19 → DH 1500-1900
- 梵一 20 → DH 3000-3075

對每個 council slug，撈 chunks 內 `dh_number` 在範圍內的 → concat 寫進 `data/creeds/.../{slug}-chinese.txt`。一次補 44 份中譯缺口。

## 6. 重要檔案路徑

| 檔 | 路徑 |
|---|---|
| 原 PDF（Drive）| `G:/我的雲端硬碟/資料/電子書/世界宗教/基督教/教會法典與信條/輔仁神學著作編譯會，公教會之信仰與倫理教義選集.pdf` |
| Final JSONL | `G:/我的雲端硬碟/資料/電子書/_chunks/568726d3-967e-457a-ab69-7452b21d606f.jsonl` |
| Gap-fill log | `G:/我的雲端硬碟/資料/電子書/_chunks/568726d3-967e-457a-ab69-7452b21d606f.gaps.jsonl` |
| Main OCR script | `scripts/ocr_with_gemini.py`（支援 `--book ID --engine haiku` 單本）|
| Gap-fill script | `scripts/_denzinger_gaps_ocr.py`（gitignored 因 _prefix；含 2-strike rule）|
| Tail OCR script | `scripts/_denzinger_tail_ocr.py`（已跑完，留作參考）|
| Bilingual spec | `.claude/skills/ebook-pipeline/book-structure-bilingual-parallel.md` |

## 7. 相關 commits

| Commit | 內容 |
|---|---|
| `01e8053` | Haiku OAuth auto-refresh（8h token 過期不死）|
| `dc72da4` | per-batch retry 5→8 / backoff cap 600s |
| `08ddff1` | `_HAIKU_MAX_TOKENS 4096 → 32000`（修截斷 bug，**新 OCR 都吃得到此修**）|
| `47f336b` | bilingual-parallel spec 新增 |

## 8. 已知問題 / 待測試

- [ ] page 948 是否真 content-filter 擋（之前 2-strike 沒實作前無法區分 rate-limit vs 真 block）— 等 quota 回來重試後就知道
- [ ] OCR 完後 chunk_count 與 total_pages 對比（理想 = 2430，blank/decorative 頁少數預期）
- [ ] Phase 2 segmenter regex 要實際 OCR 完後驗證（spec 內 regex 是草稿）
- [ ] 拉丁原文裡有 footnote ¹ 上標符號要保留還是轉 `[^N]`（spec 未定）

## 9. memory 規則提醒（接手 session 必看）

- `feedback_ocr_strategy.md`：Haiku one-at-a-time，新 session 開頭主動 ingest_new_books.py status
- `feedback_overnight_autonomous.md`：放電腦整晚跑時用 background 而非 sleep poll
- `feedback_zlib_3x_daily_check.md`：daily scheduled task **2026-05-27 已 Disabled**，不要重啟
- `feedback_powershell_full_auth.md`：使用者已授權所有 PowerShell 指令，不必每次問
- `feedback_no_secret_values_in_chat.md`：API key/token 名稱可講，值不可貼

---

**接手 session 第一句問用戶**：「現在跑 Denzinger 進度查到 XXX / 1629，下一步要 (a) 繼續 gap-fill / (b) 跑 consolidate / (c) 寫 segmenter？」
