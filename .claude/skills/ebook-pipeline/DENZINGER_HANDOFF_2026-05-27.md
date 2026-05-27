# Denzinger OCR Handoff (2026-05-27)

公教會之信仰與倫理教義選集 (Denzinger 中譯 PDF) OCR 進度與下一 session 接手指南。

## 0. TL;DR — 接手的 3 件事

1. **檢查 gap-fill 是否完成**（看下面「即時狀態查詢」一節）
2. **若未完成且 quota 卡住** → 等 1-3 小時後 `python -X utf8 -u scripts/_denzinger_gaps_ocr.py`（會 resume）
3. **若已完成** → 跑 consolidate + segment 兩支腳本（見「OCR 完之後的 Pipeline」）

**2026-05-27 更新（session 2，本 session 做完不交棒）**:
- ✅ consolidate + segment scripts 寫好 + TOC 過濾改善
- ✅ DB migration applied (`display_mode` + 5 bilingual chunk columns)
- ✅ Reader Vue 改好（DH badge / DH 跳轉 / breadcrumb chip） + dev server boot 過編譯
- ✅ `_denzinger_to_creeds.py` 也寫好（Phase 4 待 segment 完）
- ⏳ OCR @ 80.9% (1967/2430)，rate-limit 把 ETA 拖到 ~5h 後
- ⏳ Wrapper `_denzinger_wait_then_pipeline.ps1` 背景跑，OCR 完自動接 consolidate + segment write-jsonl，再 ping 我做 segment --apply + verify

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
| **Gap-fill OCR**（剩 1629 頁，單頁/call）| 🔄 進行中 | 2026-05-27 17:00 status: 1934/2430 pages = 79.6% (1133 gap pages + 801 main)；process 仍跑、~3h ETA |
| Bilingual-parallel spec | ✅ | commit `47f336b`，[book-structure-bilingual-parallel.md](./book-structure-bilingual-parallel.md) |
| Scheduled task 關閉 | ✅ | KGLab-OCR-Daily-10/14/18 全 `Disable-ScheduledTask` |
| Consolidate script (Phase 1) | ✅ | `scripts/_denzinger_consolidate.py`（gitignored, `_`-prefix）；dry-run 驗證 OK |
| Segmenter script (Phase 2) | ✅ | `scripts/segment_denzinger.py` commit `766ef09` + TOC-fix；dry-run 出 1136 entries / 49 headers / 35 commentary |

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

**✅ 已寫**：`scripts/_denzinger_consolidate.py`（gitignored, `_` prefix）

跑法：
```bash
python -X utf8 -u scripts/_denzinger_consolidate.py --dry-run   # 報告 merge 計畫
python -X utf8 -u scripts/_denzinger_consolidate.py             # 真寫 + R2 + DB
python -X utf8 -u scripts/_denzinger_consolidate.py --no-db     # JSONL + R2 但不動 DB（除錯用）
```

行為（自動 idempotent，重跑 no-op）：
1. 讀 main `.jsonl` + gaps `.jsonl`
2. Merge by page_number；gaps 補空、新增 main 沒有的
3. Sort by page_number、renumber chunk_index
4. 備份舊 main → `{id}.jsonl.preconsolidate.bak`
5. 原子寫新 main、push R2
6. `insert_chunk_previews` + `update_book_done(chunk_count=N, total_chars=sum, total_pages=max_page)`

Dry-run 預期輸出（2026-05-27 17:00 狀態）：
```
Main JSONL    : 801 chunks (801 non-empty)
Gaps JSONL    : ~1900 pages with content (跑完後)
  fills blanks: 0
  new pages   : ~1900
Consolidated  : ~2400 non-empty chunks, ~5M chars, max page_number=2430
```

### Phase 2: Segment to DH-indexed chunks

**✅ 已寫**：`scripts/segment_denzinger.py`（commit `766ef09` + 後續 TOC fix）

跑法：
```bash
python -X utf8 -u scripts/segment_denzinger.py --dry-run --report    # 統計 + 樣本
python -X utf8 -u scripts/segment_denzinger.py --write-jsonl         # 寫 .bilingual.jsonl
python -X utf8 -u scripts/segment_denzinger.py --apply               # DB + R2 + display_mode
```

實作要點：
- TOC page 短路（content 開頭 `詳細目錄` 或 ≥20% 行有 dot leader） → 整頁變一個 'header' chunk
- DH 條目 dot-leader 過濾（content 含 `\.{5,}` 視為 TOC 殘餘，drop）
- Cross-page merge：entry-entry 同 DH / commentary / 同 chapter_path header 自動串接
- Latin/Chinese pairing：CJK ratio ≥0.4 → zh；<0.1 → lat；其餘 mixed → line-by-line split fallback

**DB migration 必要**（apply 時若欄位缺會報錯印 DDL）：
```sql
ALTER TABLE ebooks ADD COLUMN display_mode text DEFAULT 'standard';
ALTER TABLE ebook_chunks ADD COLUMN section_type text;
ALTER TABLE ebook_chunks ADD COLUMN source_text text;
ALTER TABLE ebook_chunks ADD COLUMN source_lang text;
ALTER TABLE ebook_chunks ADD COLUMN dh_number int;
ALTER TABLE ebook_chunks ADD COLUMN page_numbers int[];
```

**已知待調 regex（dry-run 後 iterate）**：
- 部分 body 頁是兩欄拉中並列 OCR 在同一行（多 spaces 分隔），language line-split 會產生雜亂的 source_text。需要 column-aware OCR 重跑或加 heuristic 切欄
- 仍有 ~29 個 duplicate DH numbers（同條目分布在多頁、未相鄰時不會 merge）
- 仍有 ~40 個非單調遞增 DH（front matter 提及 + 後面 appendix 引用）
- ~198 pages 0 emissions（部分合理空白、部分可能 regex 漏 — 跑完後 spot-check 確認）

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

**Session 接手指引**：第一步跑 §3「即時狀態查詢」，看 OCR 是否仍跑。若已完成、wrapper 也跑完，直接跑 DB migration + `segment_denzinger.py --apply`。

**Session 2 自我管理筆記**（2026-05-27）：使用者明確指示這 session 做完才結束，不交棒。OCR 跑完到 segment apply 期間 wrapper 自動串連，期間可改善 reader Vue / DB migration 等可平行的工作。
