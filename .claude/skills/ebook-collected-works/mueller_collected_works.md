
> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（`https://integrate.api.nvidia.com/v1`，`deepseek-ai/deepseek-v4-flash`，4 key 輪流＋間隔節流避 429）→ Haiku（最後救急）**。視覺／OCR 走 Gemini Vision／Haiku Vision。見 [[feedback_engine_nvidia_no_haiku]]。

# 馬克思‧穆勒全集 — 案例盡職調查（版權 / 卷目 / 來源）

第二個 ebook-collected-works 案例（繼榮格之後）。**先讀本檔再開工。**

## 一句話結論

弗里德里希‧馬克思‧穆勒（Friedrich Max Müller, 1823–1900）是**宗教學（Religionswissenschaft / the science of religion）的開山祖師**。他 1900 年卒 → **全部著作早已進入公有領域（全球 life+70 = 1970 即過期）**，archive.org / Google Books / Project Gutenberg 有大量乾淨合法全文。**這是 collected-works pipeline 最乾淨的一個案例**：無盜版疑慮、無「第三方中譯不入庫」的版權閃避、來源隨手可得。

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

## 📍 新 session 接手（2026-06-09 更新）

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
- **收尾待辦**：(1) 待 15164 自然退出後，下次排程 `--run-queue` 即吃新 code，可停用這兩 pass；(2) origin-growth 的 ~74 死段日後若要補，需換 OCR 源或人工；(3) 兩 pass 用 background task（非排程）→ 跑完或當機後需手動重啟（`--engine … --only …`，resumable）。

### 待辦
- [ ] queue 跑完後：hub 各書 `status` 由 `in-progress`→`done`（`stores/collectedWorks.ts`，目前其餘 12 部在 hub 仍是 `planned`，**未填 ebookId** → 需把 registry 的 ebook_id 填進 hub 各 work 並設 in-progress/done 才會在 hub 可點；ebook_id 對照見 `mueller_auto.py` WORKS）。
- [ ] coarse 書（比較神話學/六派/神話科學論集/德國作坊）首段偶夾 OCR 前言雜訊（1 chunk）— 可加強 `trim_frontmatter`。
- [ ] 有德文版的卷（物質/神智學/語言1&2/印度/神話科學論集，registry `de_id`）日後比照導論升三欄。
- [ ] `mueller_glossary.md` term sweep（跨書術語一致）。
- [ ] 六派 `sixsystemsofindi017601mbp` 早期下載失敗、後來成功（79 章）；若再失敗換源。

## See also

- [SKILL.md](SKILL.md) — 多語對照 pipeline 主文件
- [mueller_glossary.md](mueller_glossary.md) — 穆勒比較宗教學術語表（英/德/繁中）
- [jung_collected_works.md](jung_collected_works.md) — 第一個案例（榮格，對照閱讀方法論）
- [[translation-glossary]] — 跨領域名物中譯權威（吠陀/奧義書/雅利安/祆教等以此為準）
