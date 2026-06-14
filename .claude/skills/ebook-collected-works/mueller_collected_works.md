
> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（`https://integrate.api.nvidia.com/v1`，`deepseek-ai/deepseek-v4-flash`，4 key 輪流＋間隔節流避 429）→ Haiku（最後救急）**。視覺／OCR 走 Gemini Vision／Haiku Vision。見 [[feedback_engine_nvidia_no_haiku]]。

# 馬克斯‧穆勒全集 — 案例盡職調查（版權 / 卷目 / 來源）

第二個 ebook-collected-works 案例（繼榮格之後）。**先讀本檔再開工。**

## 一句話結論

弗里德里希‧馬克斯‧穆勒（Friedrich Max Müller, 1823–1900）是**宗教學（Religionswissenschaft / the science of religion）的開山祖師**。他 1900 年卒 → **全部著作早已進入公有領域（全球 life+70 = 1970 即過期）**，archive.org / Google Books / Project Gutenberg 有大量乾淨合法全文。**這是 collected-works pipeline 最乾淨的一個案例**：無盜版疑慮、無「第三方中譯不入庫」的版權閃避、來源隨手可得。

唯一架構性差異：穆勒雖是德國人，但學術生涯在牛津，**幾乎所有學術著作以英文寫成** → 預設來源語言是**英文**，非德文。少數著作有他自己監修的**平行德文版**（如起手卷《宗教學導論》），才做真三欄；其餘卷走英＋繁中雙語（仍以 collected-works 的多卷 corpus + 專屬詞庫管理）。

## 語言策略（2026-06-04 user 拍板）

**英＋德＋繁中三欄，僅限有平行德文版的卷**；其餘卷英＋繁中。

- reader 主欄永遠是**我的逐段繁中譯文**；對照欄依該卷可得來源排（有德文版：`source_order=["en","de"]` 或 `["de","en"]`；無德文版：`["en"]`）。
- 起手卷《宗教學導論》**恰好有平行德文版**（見下），首卷即可驗證三欄 pipeline。

## 版權狀態（極簡）

| 項目 | 卒年/出版 | 地位 | 備註 |
|---|---|---|---|
| 穆勒本人全部著作（英文原文 + 德文版）| 卒 1900 | **全球公有領域**（life+70 = 1970 過期）| 無任何限制 |
| Longmans《Collected Works》編輯本（1898–1903）| 出版 ≤1903 | **公有領域**（出版逾百年）| 編輯體例可直接沿用 |
| 既有第三方中譯（若有）| — | 不論版權，**一律不入庫** | 沿用本 skill 姿態；只當校對 transient 參考 |

> 跟榮格相反：榮格卡在「德文 GW / 英文 CW 多數到 2031 仍受版權、網路全文多盜版」；穆勒**全清**，可全自動跑，**比照教父 Schaff/CCEL 公有領域那種乾淨度**。

## 《Collected Works of the Right Hon. F. Max Müller》卷目（Longmans, Green, 1898–1903）

Longmans 把穆勒生前著作重排成統一版式的《全集》，習稱 18 卷（部分目錄計到 19–20，含後出補卷）。核心構成：

| 群組 | 著作 | 年 | 卷數 | 語言 | 宗教學相關度 |
|---|---|---|---|---|---|
| **Gifford 四講** | Natural Religion（自然宗教）| 1888 | 1 | en | ★★★★★ |
| | Physical Religion（物質宗教）| 1890 | 1 | en | ★★★★★ |
| | Anthropological Religion（人類學宗教）| 1891 | 1 | en | ★★★★★ |
| | Theosophy, or Psychological Religion（神智學／心理宗教）| 1892 | 1 | en | ★★★★★ |
| **宗教學奠基** | **Introduction to the Science of Religion（宗教學導論）** | 1873 | 1 | **en＋de** | ★★★★★ **← 起手卷** |
| | Lectures on the Origin and Growth of Religion（宗教起源與發展講座，Hibbert 1878）| 1878 | 1 | en | ★★★★★ |
| **語言／神話學** | Lectures on the Science of Language（語言科學講座）| 1861/64 | 2 | en | ★★★ |
| | Contributions to the Science of Mythology（神話科學論集）| 1897 | 2 | en | ★★★★ |
| **文集** | Chips from a German Workshop（德國作坊雜記，全集重排）| 1867–75 | 4–5 | en | ★★★★ |
| | Last Essays（末年論集 I、II）| 1901 | 2 | en | ★★★★ |
| **印度學** | India: What Can It Teach Us?（印度能教我們什麼）| 1883 | 1 | en | ★★★ |
| | The Six Systems of Indian Philosophy（印度哲學六派）| 1899 | 1 | en | ★★★ |
| **回憶** | Auld Lang Syne / My Autobiography: A Fragment | 1898/1901 | — | en | ★★ |

> 另有他**主編**的巨著《Sacred Books of the East》（東方聖書，50 卷，他譯其中數卷如《奧義書》《法句經》）— 那是**譯本集**不是「穆勒著作集」，性質不同，先不納入本全集 corpus（將來可獨立做）。

### 繁中暫定卷名（corpus 命名用）

宗教學導論／自然宗教／物質宗教／人類學宗教／心理宗教（神智學）／宗教起源與發展講座／語言科學講座／神話科學論集／德國作坊雜記／末年論集／印度能教我們什麼／印度哲學六派。

`parent_volume` 用「群組」欄（Gifford 四講 ⊃ 各卷；宗教學奠基 ⊃ 導論＋Hibbert…），`volume` 用單卷繁中名。

> **排序建議（宗教學優先）**：導論（起手）→ 宗教起源與發展 → Gifford 四講 → 神話科學論集 → 其餘。語言科學講座宗教學味淡，可後排。

## 起手卷：《宗教學導論》Introduction to the Science of Religion (1873)

**為何選它**（user 拍板）：宗教學作為一門獨立學科的**奠基之作**；名言「He who knows one, knows none（只知其一，便一無所知）」出處；最具象徵意義的起點。**且恰有平行德文版** → 首卷即驗三欄。

**結構（英德兩版幾乎同構，極利對齊）**：兩版都是
- 1870 年於倫敦 Royal Institution 的**四場講座**（Four Lectures）
- ＋兩篇附論：《On False Analogies in Comparative Theology（論比較神學中的假類比）》、《The Philosophy of Mythology（神話的哲學）》

→ 同一部作品、同一章節骨架、兩種語言，**比榮格 pilot（Hinkle 重組結構）更易逐段對齊**。德文《Einleitung》是穆勒監修的德文本，分段大致對應英文講座。

> **⚠️ 並存的他人專業中譯本（2026-06-11 user 拍板）**：圖書館另有一本 1988 年**陳觀勝、李培榮譯本**（上海人民出版社，西方學術譯叢，ebook `9ee5147d-21cd-4dae-bdd1-a26f7c5d0333`，掃描 OCR）。此本是「第三方中譯一律不入庫」原則的**明確例外**：user 指示**兩本並存、明確區分**——`/ebook` 圖書館那本標 subtitle「陳觀勝、李培榮譯本（上海人民1988）」；`/collected-works` 三欄本 note 標「英德繁中三欄自譯本」並互相點名。**勿當重複刪除**。（檔名也已 馬克思‧謬勒→馬克斯‧穆勒 正名，Drive＋DB＋inventory 同步。）

## 來源紀錄

| 版本 | 來源 | 狀態 | 備註 |
|---|---|---|---|
| 英文 1873（含兩附論全本）| archive.org `introductiontosc00ml` | ✅ 公有領域 | 有 djvu 文字層；`_djvu.txt` 可直抽 |
| 英文 替代 | archive.org `introductiontos00mlgoog`（Google/Harvard 掃描）| ✅ | 備援 |
| 德文 1874《Einleitung in die vergleichende Religionswissenschaft》| archive.org `einleitungindie00mlgoog`（Google/Harvard）| ✅ 公有領域 | Trübner, Straßburg；四講＋兩附論（über falsche Analogien／über Philosophie der Mythologie）|
| 德文 替代 | MDZ `bsb11184164`（巴伐利亞邦立圖書館 digitalisat）| ✅ | 高品質掃描備援 |

下載點：
- 英文 djvu txt：`https://archive.org/stream/introductiontosc00ml/introductiontosc00ml_djvu.txt`
- 德文 djvu txt：`https://archive.org/stream/einleitungindie00mlgoog/einleitungindie00mlgoog_djvu.txt`

> 兩版都有 djvu 文字層 → **可能不必重 OCR**（比榮格 1912 純圖像掃描好太多）。先抽 djvu txt 評估雜訊；若標題行散掉再考慮 Gemini 重 OCR 開頭幾頁取章節錨點。德文哥德體（Fraktur）若 OCR 差才走 Gemini Vision。

## 對齊策略（本卷）

1. **章節錨點對齊優先**：英德兩版都是 `Lecture I–IV` / `Erste–Vierte Vorlesung` + 兩附論 → 章標題即可靠錨點（比榮格的 epigraph 指紋法穩）。走 `scripts/align_editions.py` 的 anchor join（`parse_chapter_number` 已支援 DE/EN/羅馬數字）。
2. 章內**逐段順序＋長度比**對齊；穆勒德英兩版是同一講稿，段落順序應大致一致，比 Hinkle 改寫好對。
3. 對不齊的段落沿用本 skill「整段塞、不硬切」原則；中文跟我自己的分段走。
4. 起手仍**先 1 講 smoke test**（`--limit`）→ 確認譯名／三欄效果再全跑。

## 詞庫焦點

穆勒不是心理學、是**比較宗教學／比較語言學／印度學**，術語自成體系 → 專屬 [mueller_glossary.md](mueller_glossary.md)：
- 學科名：the science of religion / vergleichende Religionswissenschaft（比較宗教學）、comparative theology（比較神學）、comparative mythology（比較神話學）
- 招牌概念：henotheism（單一主神教／交替神教，穆勒自創）、「nomina/numina（名與神）」「a disease of language（語言的疾病）」、the Infinite（無限者）、Dyaus/Devas、Aryan/Turanian/Semitic 語族三分
- 文獻：Veda/Rig-Veda（吠陀／梨俱吠陀）、Upanishad（奧義書）、Brahmana、Avesta、Zend
- 跟 `/translation-glossary` 重疊處（吠陀、奧義書、雅利安、祆教…）→ 以 `/translation-glossary` `name_recommended` 為權威（[[feedback_glossary_strict_authority]]）

## 🚀 新 session 接手清單

> 基建（reader N 欄、`align_editions.py`、`multilang_chunks.py`、`translate_collected_work.py`）全部就緒、test-first、已 push — **不用重做**，直接接真語料。見 [SKILL.md](SKILL.md) 待辦區。

**穩定 5 步（每講照做）**：
1. **抽文字**：英德 djvu txt 各自抽 → 清行內頁碼/腳註雜訊 → per-語言 sections（先評估是否需 Gemini 重 OCR 章節頁）。
2. **章節錨點配對 de↔en**：本卷用 `Lecture N` / `N. Vorlesung` 標題即可（不必像榮格走內容指紋）。
3. **逐段對齊**：同講內按順序＋長度比；對不齊整段塞。
4. **親譯**：英→繁中（有德文版時德文交叉校對消歧義），**先查 [mueller_glossary.md](mueller_glossary.md) 鎖術語**；新人名地名先查 [[translation-glossary]]。
5. **建三欄**：`content=繁中`、`sources={en,de}`、`source_order` 排序、`source_text` 鏡像 primary → 走 `scripts/multilang_chunks.py` 寫 JSONL → 驗 zh/en/de 段數相等 → R2 + previews。

**ebook_id**：起手 pilot 用測試 id（建後填回本檔）；正式化時換正式 id + 移除「試譯」標籤、配封面、分類「世界宗教／宗教學」。

### ⚠️ 雷區
- 德文是 **1874 Fraktur（哥德體）掃描**；djvu OCR 對 Fraktur 常出錯（ſ↔f、ß、變母音）→ 抽出來先抽查，差就 Gemini Vision 重 OCR。
- 穆勒英文是 19 世紀學術散文，**長句多、拉丁/梵/希臘原文夾注多** → 譯時保留原文夾注（括號），術語鎖死。
- 段數對齊閘照跑（zh/en/de row 數不等 → reader 錯位）。

## 自動化轉錄（2026-06-05 上線）

兩條 pipeline：

1. **`scripts/mueller_build.py`** — 起手卷《宗教學導論》**三欄（英/德/繁中）**。手調 6 段 line range（4 講＋2 附論），DE→EN 逐段對齊，NVIDIA EN→繁中，cover chunk 0 + JSONL + R2/DB。已實證上架（ebook `33333333-…`）。
2. **`scripts/mueller_auto.py`** — 其餘 13 部**雙語（英→繁中）連續 queue**。registry 內建各書 archive.org `_djvu.txt` 源（已驗證）+ ebook_id + 章節策略。每書：下載→OCR reflow→章節切分（lecture heading 偵測＋TOC/前言過濾＋去重；否則 coarse「第N節」）→ NVIDIA 逐段翻→ cover+JSONL→R2/DB。**resumable**（per-work + per-section cache 在 `mueller_data/<slug>/secN.json`）；lock（每段 touch）防排程重入。
   - `--list` 看 queue／`--dry <slug>` 看切分／`--work <slug> --upload` 單書／`--run-queue` 全跑／`--init-rows` 建所有 ebook row。
   - **排程**：Windows 排程任務 `MuellerAutoTranscribe`（登入時＋每 4h，無時限，resumable）跑 `scripts/mueller_auto_queue.bat` → `--run-queue`。session 關掉後靠它續跑、重開機也續。
   - **引擎**：此環境**無 Gemini key** → NVIDIA deepseek（4 key 輪流）主、Haiku 救急。13 部約 25,000 段，連續跑需數日（與 /coach 共用 NVIDIA，互相節流）。
   - **德文平行版**（registry `de_id`）：物質宗教/神智學/語言科學1&2/印度/神話科學論集 有德文版，**先雙語、之後可比照導論升三欄**。
   - **已知限制**：coarse 書首段偶夾 OCR 前言雜訊（1 chunk）；六派 `sixsystemsofindi017601mbp` 無 `_djvu.txt`（下載失敗自動跳過，待換源）。

## 🆕🆕 精修進度（2026-06-12 下午，最新，新 session 從這裡看）

> **一句話**：**精修 step 1/2/4 完成 → 全 14 本 100%（28852/28852 段）、對齊閘 0 flagged、詞庫術語一致、殘段全補。** 只剩 **step 3（A+B+C 全量校對）** 與 **step 5（德文升三欄，日後）**。

- **step 1 對齊閘**：14 本 `scan_translated_book.py --gate` 全 0 flagged（逐段翻譯本就保段落對齊）。
- **step 2 詞庫 term sweep**：收斂 111 處變體（婆羅門書→梵書×105、宗教科學→宗教學×3、交替神教→單一神教、亞利安→雅利安、黎俱吠陀→梨俱吠陀）。**已逐一驗上下文避開同音陷阱**——比較宗教（修飾語）/閃族（族群義非語族）/米勒（多為米勒托斯 Miletus）/杜蘭（人名）/韋陀（韋馱天/vadh 字根）/宗教的科學（穆勒刻意對比修辭）**全部不改**。
- **step 4 殘段補譯**（`scripts/mueller_fill_residuals.py`）：原 143 個 zh-empty **全補完 → 0 殘段**。**根因**：Haiku 把短標題格式化成 markdown heading、舊 `_clean` 整行刪→MAX_FAIL 空段；`--heading-safe` 剝 `#` 不刪行解決。所謂「~144 終態 OCR 垃圾」**其實全是可譯的邊註標題/索引/正文片段**，非垃圾。
- **step 3（全量逐段重校）= user 拍板暫緩（2026-06-12）**：文本已 100% 可讀/對齊/術語一致，全量 A+B+C 28k 段重校屬數日級 token 重投資，user 決定先收工、留日後。**非未完成項，勿自行重啟全量重校**；日後若做，建議先 deterministic 離群掃描（未譯拉丁/希臘/梵文殘留、zh/en 長度比異常、亂碼長句）只校高風險段，而非盲掃全量。
- **step 5 德文升三欄**（日後）：有 `de_id` 的卷（物質/神智學/語言1&2/印度/神話科學論集）比照導論升 EN/DE/繁中三欄。

---

## 🆕 監督接手（2026-06-12 09:27，已被上方精修進度更新）

> **一句話**：**全集 14 部「機翻初稿」全數完工 = 99%（28708/28852 段）；hub 各卷已 status=done＋ebookId、`/collected-works` 馬克斯‧穆勒頁全可點。翻譯 pass 全結束、auto-committer 已停。** ~~剩 ~144 段是補不上的眉批/OCR 雜訊~~（**已證實全可譯、step 4 已補完**）。

### ⚡ 背景進程現況
- **翻譯 pass：全部結束**（`Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? {$_.CommandLine -like '*mueller_haiku*'}` 應為空）。若要補翻某本殘段，自己 launch：`python scripts/mueller_haiku_pass.py --loop --engine haiku --only <slug>`（resumable；NVIDIA 龜速，收尾一律 `--engine haiku`）。
- **auto-committer**：上個 session 的每 10 分 commit while-loop **已於完工時停掉**（翻譯結束、無 mueller_data 寫入需保護）。新 session **不需重啟它**；只要在自己改動後正常 commit 即可。

### 監督/收尾前的健康檢查（可選）
1. **先 commit**：`git commit -q -m "data(mueller): checkpoint [autostash-guard]" -- .claude/skills/ebook-collected-works/mueller_data && git push`（autostash 隨時會吞未 commit 的翻譯）。
2. **看進度**（per-book + total）：
   ```bash
   python -c "import json,glob,os;root='.claude/skills/ebook-collected-works/mueller_data';g=gd=0
   for d in sorted(os.listdir(root)):
    p=os.path.join(root,d);  secs=glob.glob(os.path.join(p,'sec*.json'))
    if not os.path.isdir(p) or not secs: continue
    t=dn=0
    for s in secs:
     j=json.load(open(s,encoding='utf-8'));zh=j.get('zh')or[];en=j.get('en')or[]
     t+=max(len(zh),len(en));dn+=sum(1 for i in range(len(zh)) if (zh[i]or'').strip())
    g+=t;gd+=dn;print(f'{d:28s}{dn*100//t if t else 0:3d}% {dn}/{t}')
   print('TOTAL',gd*100//g,'%',gd,g)"
   ```
3. **警覺 %回退**：若某本已 99% 的書突然掉回低值 = 又被 autostash → `git stash list`，`git show "stash@{N}:<path>"` 比對挑飽滿版，`git checkout "stash@{N}" -- <book dir>` 撿回再 commit（**勿 drop stash／勿碰 non-mueller 檔**，內含並行 jung session 資料）。完整教訓見下方 🚨。

### ✅ 已完成的收尾（2026-06-12，勿重做）
- **hub 全可點**：`stores/collectedWorks.ts` 馬克斯‧穆勒 works[] 12 卷 status→`done`＋ebookId（已填）；4 卷未翻（古代梵文文學史/往日時光/自傳片段/東方聖書，無 ebookId）維持 `planned`。
- **auto-committer 已停**；mueller_data 全 commit+push。

### 🔧 精修（= 新 session 的主要工作；機翻初稿 → 出版品質）
14 部是 **NVIDIA deepseek／Haiku 機翻初稿**，未校對。精修是品質層、與 hub 「done」狀態無關（done = 可讀上架）。建議順序（仿 [[anf_vol1_golden_template]] A+B+C 三層、串 [[project_alignment_gate]]）：
1. **逐段對照品質閘**：`python scripts/scan_translated_book.py --gate <ebookId>`（[[project_alignment_gate]]）抓 zh/en 段數對不齊的 chunk → 重譯該段。先掃 14 本列出壞 chunk 清單。
2. **詞庫 term sweep**：跨 14 書統一術語，鎖 [mueller_glossary.md](mueller_glossary.md)（henotheism→單一神教、the Infinite→無限者、a disease of language→語言的疾病、Aryan/Semitic/Turanian 語族…）；與 `/translation-glossary` 重疊者（吠陀/奧義書/雅利安/祆教…）**以 name_recommended 為權威**（[[feedback_glossary_strict_authority]]）。批次 Haiku 校對可 backfill。
3. **A+B+C 三層校對**：通讀修順（機翻長句生硬）→ 術語鎖定（依詞庫）→ 漏譯/誤譯修正。可按書、按 NVIDIA(較粗) 先於 Haiku(較順) 排優先。
4. **殘段親譯**：各書 1-3% 補不上的眉批/OCR holdout（`fail≥MAX_FAIL` 被 skip 的，reader 現顯英文）→ 人工親譯補，或確認英文 fallback 可接受。查殘段：上方健康檢查腳本看 `dn<t` 的書/節。
5. **德文版升三欄**（日後）：有 `de_id` 的卷（物質/神智學/語言1&2/印度/神話科學論集）比照導論升 EN/DE/繁中三欄。
> 補翻/重譯單段或單本一律 `python scripts/mueller_haiku_pass.py --loop --engine haiku --only <slug>`（resumable；NVIDIA 龜速、收尾別用）。改完 `git push`（pre-push 會跑測試）。

### 命名（2026-06-11 已正名，勿退回）
作者一律 **馬克斯‧穆勒**（Max≠Marx；馬克思留給卡爾‧馬克思）。另有他人專業中譯本《宗教學導論》（陳觀勝/李培榮，上海人民1988，ebook `9ee5147d-…`）與三欄自譯本**並存**，已各自標示、**勿當重複刪**（詳見上方 ⚠️ 並存區塊）。

---

## 📍 舊接手快照（2026-06-09，已被上方取代）

### 目前進度
- **《宗教學導論》三欄（英/德/繁中）= 100% 完成、已上架**。ebook `33333333-3333-4333-8333-333333333333`，7 chunks，~21.5 萬繁中字，hub 已標「已轉錄」。pipeline = `scripts/mueller_build.py`（手調 6 段 line range；cache 在 `mueller_data/isr/`，已 commit）。
- **其餘 13 部 = 自動 queue（`scripts/mueller_auto.py`），English-first 進行中**。全部已 ingest（英文可讀上架）；繁中翻譯進度（2026-06-09）：
  | 書 | 繁中 % | 節數 |
  |---|---|---|
  | 宗教起源與發展 origin-growth | 96% | 83 |
  | 自然宗教 natural-religion | 5% | 20 |
  | 物質/人類學/心理宗教、比較神話學、神話科學論集1&2、語言科學1&2、印度、六派、德國作坊雜記 | 0%（已 ingest 英文） | 各見 registry |
  - 總量約 25,000 段，連續跑需數日。

### English-first 機制（user 指示，[[feedback_jung_nonpd_english_first]]）
- 私人站、**非公有領域來源也可**（穆勒全 PD 無妨）；**英文先輸入**、翻譯可慢。
- queue 兩階段：**Phase 1** 無 LLM 把 13 本英文全 ingest 上架（秒級可讀）；**Phase 2** 逐段翻繁中，未譯段主欄 **fallback 顯示英文**（`section_chunk` 內 `zh[i] or en[i]`），每 12 節 re-upload 讓中文漸進浮現。

### 怎麼接手 / 操作
- **看進度**：`python scripts/mueller_auto.py --list`；或讀各 `mueller_data/<slug>/secN.json` 數 `zh` 非空段。
- **手動續跑**（排程也會自動跑）：`PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/mueller_auto.py --run-queue`（resumable，從 cache 續）。**先確認沒有別的 queue 在跑**（lock 會擋）。
- **單書**：`--work <slug> --upload`；**看切分**：`--dry <slug>`。
- **排程**：Windows 工作 `MuellerAutoTranscribe`（登入時 + **每 30 分**，resumable）跑 `scripts/mueller_auto_queue.bat → --run-queue`。**lock 自癒**：`mueller_data/_queue.lock` 超過 25 分未更新 = 持有者已死，自動接管（健康 run 每 ~3 段 touch 一次）。當機/睡眠/斷網都能 30 分內自己爬起續跑。
- **引擎**：此環境 NVIDIA deepseek（4 key 輪流）主、Gemini/Haiku 救急；與 /coach 共用 NVIDIA 互相節流。`translate_para` 有 **retry-on-empty ×4**（引擎偶爾回空被當譯文的自癒）。

### 🚨 autostash 吞進度（2026-06-11，已修復一次）
**症狀**：總進度從 49%→24%，natural/physical/anthropological/psychological 等已 99% 的書突然掉回原始 ingest 值。
**根因**：**並行的 jung `[loop]` session 跑 `git pull --autostash`**，把本 session **未 commit** 的 mueller_data 翻譯全 stash 起來；因為翻譯 pass 還在寫檔，autostash 的 pop **衝突**→ stash 留滯不還（`git stash list` 見多筆 `autostash`），working tree 被還原成上次 commit 的舊值。
**復原**：翻譯在 stash 裡沒丟。`git show "stash@{N}:<path>"` 比對 zh 充填度，挑「stash 比 working tree 飽滿」的書 `git checkout "stash@{N}" -- <book dir>` 撿回，**勿動並行 session 的 non-mueller 檔、勿 drop stash**（內含 jung 資料）。撿回後**立刻 git commit mueller_data**。
**預防**：**每次抽查都 `git add mueller_data && git commit`**（pass 持續寫檔→隨時有未 commit，唯有勤 commit 才能把 autostash 損失壓在一個 tick 內；就算被 stash 也撿得回）。

### ⚠️ 雷區（務必知道）
- **reader page 1 永遠當封面**（`isCoverPage = currentPage===1`，[pages/ebook/[id].vue](../../../pages/ebook/[id].vue) ~L1792）→ **cover chunk 0 必備**，內容從 chunk 1 / page 2 起。
- **chunk 內容第一段是 heading row** → JSONL 段號 = cache zh 索引 **+1**（off-by-one，查空段時小心）。
- 三欄/雙欄都要 **content / sources.* 段數（`\n\n`）相等**，reader 才逐段對齊。
- 多任務並行：**只動自己啟動的 process**（[[feedback_no_kill_other_tasks]]）；commit 用 pathspec 只提交自己的檔（並行 session 在改 coach/jung）。

### 🩹 2026-06-10 livelock 修復 + Haiku 平行 pass
- **症狀**：排程 `--run-queue`（PID 15164，08:31 啟）連 4 窗淨 +5/+3/+9/+2，origin-growth 反覆重掃、其餘 13 本 2.5h 零推進。
- **根因**：`is_done()` 要求**每段**有 zh，但每節約 1 個補不上的眉批/OCR running-head 永遠回空 → origin-growth 永不達 100% → Phase 2 loop 每趟卡它、餓死後書。
- **修復**（commit `a4ee465`）：`mueller_auto.py` 加 per-segment `fail` 計數，連 `MAX_FAIL=3` 趟回空 → exhausted；`translate_work` 跳過、`is_done` 視為已解決 → 書能完成、queue 前進。reader 本就 fallback 英文，死段仍可讀。
- **生效方式**：15164 載舊 code 且非本 session 啟（[[feedback_no_kill_other_tasks]]）→ **不停它**。改跑 `scripts/mueller_haiku_pass.py`（FIXED code，免 lock，跳過 origin-growth）翻其餘 12 本。
- **效果**：3h 內 12%→33%（自然宗教/物質宗教翻竣）。後段 Haiku 撞 Claude Max 429/401 變慢 → **改雙引擎切分**：`--engine {haiku,nvidia} --only <slugs>` 兩 instance 翻**不重疊**書集並行（互不撞檔、抗單引擎節流）。21:30 分工：
  - **Haiku**：anthropological / psychological / comparative-mythology / contributions-mythology-2
  - **NVIDIA**（mb.make_engine）：contributions-mythology-1 / science-language 1&2 / india-teach / six-systems / chips-1
- **收尾待辦**：(1) 待 15164 自然退出後，下次排程 `--run-queue` 即吃新 code，可停用這兩 pass；(2) origin-growth 的 ~74 死段日後若要補，需換 OCR 源或人工。
- **2026-06-11 早**：15164 已自然退場（origin-growth 97%）。隔夜 Haiku pass **01:28 靜默死亡**（疑 OAuth token 過期逃出 per-book guard）→ 進度卡 49% 6h 沒人發現。**加 `--loop`**（commit）：retry 整套 --only 書直到 `is_done`，連 BaseException 都接，引擎死就自動重啟不再卡死。**兩 pass 用 lock-touch 擋住排程 --run-queue**（避免三方撞檔），跑完 lock 失效排程自動接手收尾。
  - 現行 background task（07:17 起，`--loop`）：**Haiku** `bdh81v70x`（psychological/comparative-mythology/contributions-mythology-2）+ **NVIDIA** `bqjfp6sto`（contributions-mythology-1/science-language 1&2/india/six-systems/chips-1）。當機/重開機後手動重啟同指令即可（resumable）。
  - ⚠️ 早上 NVIDIA+Gemini 都易 429/503 throttle，Haiku 是穩定主力；若 NVIDIA set 長期near-zero，把它改丟第二個 `--engine haiku` instance。

### 待辦
- [ ] queue 跑完後：hub 各書 `status` 由 `in-progress`→`done`（`stores/collectedWorks.ts`，目前其餘 12 部在 hub 仍是 `planned`，**未填 ebookId** → 需把 registry 的 ebook_id 填進 hub 各 work 並設 in-progress/done 才會在 hub 可點；ebook_id 對照見 `mueller_auto.py` WORKS）。
- [ ] coarse 書（比較神話學/六派/神話科學論集/德國作坊）首段偶夾 OCR 前言雜訊（1 chunk）— 可加強 `trim_frontmatter`。
- [ ] 有德文版的卷（物質/神智學/語言1&2/印度/神話科學論集，registry `de_id`）日後比照導論升三欄。
- [ ] `mueller_glossary.md` term sweep（跨書術語一致）。
- [ ] 六派 `sixsystemsofindi017601mbp` 早期下載失敗、後來成功（79 章）；若再失敗換源。

## 🆕🆕🆕 2026-06-12 晚：補 3 卷 + 東方聖書獨立 portal（最新）

- **補入 registry 3 卷**（user「都放進去」）：`ancient-sanskrit-literature`（古代梵文文學史 1859, `historyofancient00mluoft`, eid `4444444e`）、`auld-lang-syne`（往日時光 1898, `auldlangsyne00mluoft`, eid `4444444f`）、`my-autobiography`（自傳片段 1901, `myautobiographyf00mluoft`, eid `44444450`）。皆 coarse 切分，英文已 ingest 上架可讀，hub 標 `in-progress`＋ebookId。**繁中翻譯背景跑**：`python scripts/mueller_haiku_pass.py --loop --engine haiku --only ancient-sanskrit-literature,auld-lang-syne,my-autobiography`（resumable；當機重啟同指令）。→ 全集自動 registry 現 **16 卷**。
- **東方聖書 = 獨立 corpus/portal**（user 拍板，不塞全集卡）：`/sacred-books-east`，`stores/sacredBooksEast.ts`（穆勒原版 50 卷權威編號，按 7 大宗教傳統分組：吠陀/佛教/耆那/祆教/中國儒道/伊斯蘭/索引；譯者中英並列；全 `planned`）＋ `pages/sacred-books-east/index.vue`（簡介＋傳統 chips＋分組卷目卡，轉錄後連 `/ebook`）。穆勒 hub「東方聖書」row 用新欄位 `CwWork.externalUrl` → 點此進專屬目錄（hub `linkTarget()` 優先 externalUrl）。**下一步**：逐卷找 archive.org 源、填 archiveId/ebookId、比照雙語 pipeline 轉錄（這 50 卷是*他人英譯*的東方經典，非穆勒著作）。
- **⚠️ DB ebook_chunks 預覽列不全**：導論/自然/比較神話/語言科學1 的 `ebook_chunks` 表 0 列（其餘部分）；**reader 不受影響**（讀 R2 JSONL，內容完整），但圖書館搜尋預覽缺。日後可重灌預覽列補齊。

## See also

- [sacred_books_east.md](sacred_books_east.md) — **東方聖書 50 卷獨立 corpus 交接文件**（從穆勒分出；6 代表卷轉錄中，新 session 接手看這份）
- [SKILL.md](SKILL.md) — 多語對照 pipeline 主文件
- [mueller_glossary.md](mueller_glossary.md) — 穆勒比較宗教學術語表（英/德/繁中）
- [jung_collected_works.md](jung_collected_works.md) — 第一個案例（榮格，對照閱讀方法論）
- [[translation-glossary]] — 跨領域名物中譯權威（吠陀/奧義書/雅利安/祆教等以此為準）
