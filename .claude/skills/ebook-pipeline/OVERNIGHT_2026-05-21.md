# Overnight 2026-05-21 進度報告

## ✅ 今晚已完成

1. **v2 resplit oversized chunks**（2 段跑完）
   - 37/67 books 切開 → +1,468 new chunks
   - 30 本 v2 切不動（Schaff Apostolic Fathers / Plato collected works / 中文連續散文）
   - 已 commit + push（`59a9138`）

2. **節級 chunking 工具寫好**（[scripts/resplit_to_sections.py](../../../scripts/resplit_to_sections.py)）
   - 5 種節級 pattern：h3 / 第N節 / Aquinas 題-條 / Question N / Section N
   - is_already_section_chunk 修正：Aquinas 神學大全 `### 第N題` 內含 `第N節` 可繼續切
   - dry-run 印度哲學通史：43 chunks → +116 chunks ✓
   - 32 本 section-rich 候選理論 +2,980 chunks

3. **宗師全集 canonical list**（570 行，[master-scholars-todo.md](master-scholars-todo.md)）
   - 7 學科 × 86 學者 × 322 代表作
   - 神學 26/52、現象學 22/46、近代哲學 30/56、人類學 5/31、心理學 13/44、社會學 18/40、宗教學 38/53
   - **152/322 已 ingest（47%）**
   - **170 本 ⬜ 待下載** — 你 review 後 batch drop / z-lib
   - 已 commit + push（`bcb8a9b`）

## 🔄 仍在跑 / 等待結果

| Task | 狀態 |
|---|---|
| **reclassify Haiku judge** (468 本歷史學) | ✅ 468/468 完成（0 error） |
| **sections dry-run** (32 本) | ✅ 跑完 27/32，+2,602 chunks |
| **yanyo Haiku judge** (162 chunks) | ✅ 跑完 161/162（EPUB 結構壞，不可拆 33 本） |
| OCR worker (PID 5264) | 持續跑 overnight |

### Reclassify 結果分布（覆查命令：`python scripts/_reclassify_history_via_gemini.py review`）

| 應移出歷史學 | 書數 |
|---|---|
| **世界宗教/基督教** (教會史/十字軍/宗教改革/抄本學) | 10 本 |
| **世界宗教/伊斯蘭教** (吉哈德/哈里發/穆斯林史) | 3 本 |
| **世界宗教/猶太教** (Josephus / 猶太人三千年) | 2 本 |
| **世界宗教/佛教 + 印度教 + 東亞宗教** (敦煌/觀音/甘地/儒教) | 5 本 |
| **哲學** (倫理學/古希臘/形上學/各哲學家著作) | 15 本 |
| **宗教學** (跨宗教/神話學) | 8 本 |
| 留在歷史學 | ~425 本 |

明早一鍵 apply：
```bash
"C:\Users\user\AppData\Local\Python\bin\python.exe" -u scripts/_reclassify_history_via_gemini.py apply --dry-run
# 然後 --confirm 跑 actual move
```

### Sections dry-run 結果（驚人成功）

27/32 candidate 全部成功，+2,602 new chunks。亮點：

| 書 | +chunks | 模式 |
|---|---|---|
| **Aquinas 神學大全 第 1 冊** | +252 | chinese_jie:36 |
| **Aquinas 神學大全 第 3 冊** | +288 | chinese_jie:26 |
| **Aquinas 神學大全 第 2 冊** | +48 | chinese_jie:15 |
| 中國儒學史 | +281 | chinese_jie:60 |
| 舊約背景 | +254 | chinese_jie:3 |
| 印度哲學通史 | +116 | md_h3:25 |
| 幽靈帝國拜占庭 | +118 | md_h3:11 |
| 大歷史 | +110 | md_h3:14 |

明早一鍵 live：
```bash
"C:\Users\user\AppData\Local\Python\bin\python.exe" -u scripts/resplit_to_sections.py run --all
```

## 📋 明早接續任務

1. **看 sections dry-run log**：`scripts/logs/resplit_sections_dryrun_2026-05-21.log`
   - 確認 Aquinas 神學大全 1/3 冊 +172/+288 boundary 是否切對
   - 確認沒過度切碎
   - OK → `python scripts/resplit_to_sections.py run --all`（live）

2. **看 reclassify judge 結果**：
   - `python scripts/_reclassify_history_via_gemini.py review`
   - 確認 ✓ 標記合理 → 跑 apply

3. **鹽野七生決議**：
   - Haiku judge 證實 EPUB 內 96 chunks 是「海都物語+君士坦丁堡」混排
   - **建議放棄拆 33 本，改用 z-lib 拿單本重 ingest**
   - 或保留現狀 ~22 個粗類 cluster split
   - User 決定

4. **OCR body 救援 37 本**（>50% tiny chunks，PDF body 沒被 extract）
   - 包含：現代性與後現代性十五講 / 尼采到底說了什麼 / 阿維斯塔 / 走向十字架上的真 / 文化與帝國主義 / 民主與城邦的衰落 / 政治觀念史稿(五) 等
   - 重 OCR 用 Gemini Vision（明天 Gemini quota reset 後）

5. **Master-scholars 待補 170 本下載**：
   - 用 Anna's Archive (annas-archive.li) wget — 不用登入
   - 寫腳本：`scripts/_download_anna_archive.py` 對 ⬜ 書名 search + 抓 download URL
   - 或者 user 手動 batch drop z-lib

6. **歷史學 → 世界宗教 reclassify apply**（reclassify judge 完成後）：
   - 跑 `python scripts/_reclassify_history_via_gemini.py apply --dry-run`
   - 預期會把 N 本 (含基督教史/十字軍/猶太教史/伊斯蘭) 移到 世界宗教/{宗教}
   - 同時搬 Drive 檔案 + UPDATE file_path

## 🚫 今晚發現的「不解決也不影響」問題

- **1190 本書有 <100 字 chunk** — 主要是 PDF body 沒 extract（OCR body failure）
- **劍橋中國史(11冊) DB chunk_count 已修同步**（38 → 81）

## Background tasks 監控指令

```bash
# Reclassify 進度
"C:\Users\user\AppData\Local\Python\bin\python.exe" -u -c "
from pathlib import Path; import json
p = Path(r'c:\tmp\history_reclassify_judgements.jsonl')
print(f'judged: {sum(1 for l in p.read_text(encoding=\"utf-8\").splitlines() if l.strip())}')"

# Sections dry-run log
tail -50 scripts/logs/resplit_sections_dryrun_2026-05-21.log
```
