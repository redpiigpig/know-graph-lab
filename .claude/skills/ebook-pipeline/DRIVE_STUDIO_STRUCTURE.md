# 知識圖工作室 — Drive 結構對照網站入口（分階段遷移）

**目標**：在 Drive 建一個 `知識圖工作室/` 根資料夾，其子結構**對照網站（Know-Graph-Lab）各入口 portal**，讓每種檔案都有對應的家，解決「全集來源檔／館藏／照片／講道混在一起、Drive 上分不出誰是誰」。

**根路徑**：`G:\我的雲端硬碟\資料\知識圖工作室\`

## 入口 → Drive 資料夾對照

| 網站入口（portal） | 工作室/ 子夾 | 檔案來源現況 | 遷移風險 |
|---|---|---|---|
| `/ebook` 電子圖書館 | `電子圖書館/{10 分類}` | 現在 `資料\電子書\{10 類}`（~2260 本） | 🔴 高（全 file_path＋DRIVE_ROOT） |
| `/collected-works` 全集 | `全集/{學科}/{作家}` | 多為 web 源（少檔）；榮格中文書已進 ✅ | 🟢 低 |
| `/fathers` 教父著作 | `教父著作/` | Schaff/ACCS 在 `電子書\神學`、`電子書\世界宗教` | 🟡 中（bounded，~50 本 file_path） |
| `/research-data` 研究資料 | `研究資料/{城中週報,弘誓,大愛道}` | 城中週報／弘誓刊物／大愛道 PDF | 🟡 中 |
| `/photos` 照片 | `照片/{辰瑋,訓練,弘誓}` | 已在 Drive 別處相簿 | 🔴 高（`photos-library` 腳本引用相簿路徑） |
| `/sermons`,`/pong-archive` 講道 | `講道/` | 龐牧師錄音／逐字稿（已在 Drive） | 🔴 高（pong 腳本引用） |
| `/speech` 演講 | `演講/` | 演講錄音／PPT | 🟡 中 |
| 千面上帝讀書會 | `讀書會/` | 音檔／PPT | 🟡 中 |
| （chunks，非入口） | `_chunks/` | `電子書\_chunks\{id}.jsonl` source of truth | 🔴 高（`EBOOK_CHUNKS_DIR`＋跑中翻譯/OCR 正在寫） |

## 受影響的路徑引用（遷移前必須一起改）

- `ebooks.file_path`（每本；搬檔就 UPDATE，reader/OCR 靠它）
- `.env` `EBOOK_CHUNKS_DIR` ＋ `nuxt.config.ts runtimeConfig.ebookChunksDir`（_chunks 搬才動）
- `ingest_new_books.py` / pipeline `DRIVE_ROOT`（新書落點；只影響「未來新書」，舊書用存好的 file_path）
- `photos-library`：`classify_photos.py` / `rename_photos.py` 相簿路徑
- pong 系腳本：講道音檔/逐字稿路徑
- 原檔端點 `server/api/ebooks/[id]/original.get.ts`：`createReadStream(file_path)` 讀本機 → **正式站/別台電腦拿不到原檔**（見 R2 節）

## 分階段計畫（避開正在跑的翻譯/OCR；每階段搬完驗證＋改引用）

- **Phase 1 ✅（2026-07-19 完成）**：建 `知識圖工作室/` 骨架（電子圖書館/全集/教父著作/研究資料/照片/講道/演講/讀書會/_chunks）＋**榮格 11 本試點**移入 `全集/心理學/榮格/`、file_path 更新、舊空夾清掉。
- **Phase 2 ✅（2026-07-20 完成）**：研究資料 →
  - `公事\印順學派與弘誓研究資料\*` → `研究資料\印順學派與弘誓\`（333 件 / 2.1GB）
  - `公事\國北教\碩士論文\{論文資料,口述訪談}` → `研究資料\大愛道革命\`（1,215 件 / 7.9GB）
  - 城中教會週報：原生 Word 原本在 nonchurch-nuxt repo 的 `stores/城中週報`，**2026-07-20 已移入 `研究資料\城中教會週報\`**（1,858 檔 8GB），`scripts/cz_*.py` 路徑同步改指 Drive。
  - 全集其餘來源檔：除榮格外皆為 web 來源，無檔可搬。
- **Phase 3 ✅（2026-07-20 補完）**：教父 Schaff/ACCS 67 本先前已搬且 file_path 已更新；本次補搬 ACCS 英文 vol 12/15 兩本 epub、清掉 `電子書\世界宗教\基督教\IVP - ACCS *` 空夾，並改掉仍指舊路徑的 `accs_volume_config.json`／`accs_*.ps1`／skill 文件。
- **Phase 4 ✅（2026-07-20 完成）**：三相簿整夾搬入 `照片\{辰瑋相片,訓練相片,弘誓相片}`（80,945 件 / ~310GB，資料夾層級 rename，Drive file ID 不變 → 照片索引／R2 縮圖不受影響）；`nuxt.config.ts photosRoot` ＋ photos-library 全部腳本／skiplist／ledger 路徑同步更新。`儲存資料夾\公事`（非 /photos 相簿）留原地。
- **Phase 5 部分 ✅（2026-07-20）**：`創作\千面上帝\宗教史讀書會` → `讀書會\千面上帝宗教史讀書會`（29 件），qiangmian 腳本／skill 已改。**講道**（龐牧師錄音／逐字稿）與**演講**素材不在本 Drive 帳號（My Drive）內，無檔可搬，`講道\`／`演講\` 待日後新素材直接落點。
- **Phase 6 ✅（2026-07-20 完成）**：先停（11 個排程 Disable ＋ 21 個 python 工作程序 kill），再搬 `電子書\{10類}` → `電子圖書館\`（2,193 本）、`_chunks`（2,233 檔）→ `工作室\_chunks`，舊 `資料\電子書\` 已刪；`EBOOK_CHUNKS_DIR`／`DRIVE_ROOT`／`original.get.ts`／111 個檔案的路徑引用同步改完，`ebooks.file_path` UPDATE 1,837 筆（殘留 0），最後回復排程與艦隊。
## `知識圖工作室\學術著作\`（2026-07-20 建立，對照網站 `/papers`）

`/papers`「學術著作」頁的三區原樣鏡射，每篇一夾（`{id} {短標題}`），內含網站全文 `*_全文.txt` ＋ 投稿用 docx/pdf/pptx 原檔（**複製**，正本仍在 `玄奘\`、`公事\國北教\`）。

| 區 | 篇數 | 檔數 |
|---|---|---|
| `期刊論文\`（j1–j3） | 3 | 28 |
| `會議論文\`（c1–c11） | 11 | 66 |
| `報紙社論\`（e1–e3） | 3 | 3（僅網站全文） |

只收自己的稿：檔名含「張辰瑋」或以論文標題開頭；別人的參考文獻（周伯戡／黃慧茹／林秋梧…）與徵稿公告不收。對照清單見 Drive 端 `學術著作\_資料夾說明.txt`。

## 姊妹站：`資料\無境界者\`（2026-07-20 建立）

無境界者（nonchurch-nuxt）是**另一個網站**，不併進知識圖工作室，改在 `資料\` 下開自己的根夾，同樣對照網站結構。原本 12GB 資料散在 repo 的 `stores/`（已 gitignore），使用者拍板 **Drive 當唯一正本**，本機只留小型工作檔（form.md／pong_sermon_input_rules.md／word_to_sql.md／tempArticles.js／pong-photo.jpg）。

| 網站入口 | Drive 資料夾 | 量 |
|---|---|---|
| 雜誌各期（/articles、/publication） | `雜誌\{01-08 期}` | 856 |
| 龐君華檔案 /pong-archive → 1 講道集 | `龐君華檔案\講道集\{講道清單,年議會講道,音檔,逐字稿}` | 38 |
| → 2 著作與專文 /writings | `龐君華檔案\著作與專文\{著作,學位論文,龐牧師網路文章.txt}` | 5 |
| → 3 訪談與演講 /media | `龐君華檔案\訪談與演講` | 8 |
| → 4 三讀三禱 /daily-office | `龐君華檔案\三讀三禱` | 301 |
| → 6 相關報導 /reports | `龐君華檔案\相關報導`（衛報） | 24 |
| → 事工報告 | `龐君華檔案\事工報告\{2008-2022}` | 110 |
| 城中教會週報 | **正本在** `知識圖工作室\研究資料\城中教會週報`（同時是 /research-data 資料源），無境界者夾內只放指路說明 | 1,858 |

Drive 端另有 `_資料夾說明.txt`（對照表）與 `城中教會週報_請看這裡.txt`。兩個 repo 內 23 個檔案的 `stores/…` 路徑引用已同步改指 Drive。

- **附帶（2026-07-20）**：`資料\儲存資料夾\公事` 併回 `我的雲端硬碟\公事\`（拉丁文課／大學／事工／課程／橫山 5 夾），跨夾同名同大小重複 60 檔（時間戳全一致）刪掉搬來的那份、保留原 `公事` 樹內版本，`資料\儲存資料夾\` 整個刪除。

## R2 原檔（選擇性上，user 拍板 2026-07-19）

- 現況：**chunks 在 R2**（任何電腦/正式站讀得到內容）；**原檔只在 Drive**（`original.get.ts` 串本機）→ 別台電腦/正式站**下載不到原檔、開不了 pdf.js 原頁模式**。
- 決策：**選擇性上 R2**——只把「需要跨機下載／原頁模式／全集參考」的書之原檔上 R2，不是全館（省 GB 級空間，見 [[project_db_quota_rescue]]）。
- 待建：`ebook-original` R2 bucket ＋ `original.get.ts` 加「本機不存在則 fallback R2 presign」＋一支選擇性上傳腳本。

## 現況備註（榮格首案）

榮格 11 本（7 epub 已 parse／4 掃描 pdf 待 OCR／榮格自傳 epub 缺圖 parse error 待重試）已在 `全集/心理學/榮格/`。它們是**第三方中譯**，屬全集參考層（[[project_collected_works_multilang]] REFERENCE），目前 `collection=NULL`（仍在 /ebook 心理學 可讀）；日後可設 `collection='collected-works'`＋掛進榮格 hub 當參考版。
