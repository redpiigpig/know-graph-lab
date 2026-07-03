# 創生哲學 15 卷「逐節對話地圖」全量補完 — 交接（2026-06-26）

## ✅ 零之四、2026-07-03 全 15 卷「章首故事引子」工程（完成）
使用者定案：**每一卷每一章都以一則相關故事開場再進行探討**（定錨：愛的公式→小王子、陰影/個體化→聖誕頌歌、召喚→佛陀出家）。
- **總表**＝`scripts/genesis_research/fable_map.md`（122 章每章一故事＋鐵則＋插入格式）。格式＝`<div class="chapter-fable"><p>故事2-4段</p><p class="fable-bridge">橋接段</p></div>` 插在該章 `</h2>` 緊後（新章 editor-note 之前）；**不動任何 h2/h3**，clean_inv／DB 不受影響。reader 樣式在 pages/works/[slug]/book/[bid].vue `.chapter-fable`（琥珀卡、斜體敘事＋橋接段）。
- **2026-07-03 全數完成：15 卷 122 章、章＝引子＝橋接一一對應，sec 平衡、無「四然」、無星號，全卷驗證通過。**
- 施工紀錄：前 55 章由 per-卷子代理完成；其後 API 連線反覆中斷（session limit＋ECONNRESET），改由主迴圈以 `fable_insert.py + batch_{a,b,c,d}.json`（scratchpad，一次性）批次插入其餘 67 章。⚠️ 教訓：斷線代理可能留下**無 `</div>` 的殘塊**（O1 第三章曾出現無橋殘塊，誤刪修復時吃掉後文）——正確做法＝搶救完整塊→`git restore`→重插，勿直接刪殘塊。
- 使用者要換某章故事：改該章 `<div class="chapter-fable">` 區塊＋同步 fable_map.md 該列即可，其他一概不動。

> 接續：把**全 15 卷每一小節**都掛上「盟友(支持/補充)/foil(反例)/旁證」當代文獻（仿 E2 對話地圖），
> 並把**既有 ref-DB 條目逐節分類**。瓶頸＝Claude **session 額度**：每個配額窗口約只能跑 **~18 章**研究子代理，
> 全部 105 章要橫跨數個重置窗口。記憶見 [[project_genesis_reference_db]]、[[project_genesis_epistemology_trilogy]]。
> 前一份 E1/E2/E3 收尾交接見 `genesis_trilogy_handoff.md`（五項已完成）。

## ⚠️ 零之三、2026-07-03 第二波調整（使用者追加定案，已完成）
1. **意欲純化＋四象限回 V1（第三、四章）、愛＋主體回 V2（第六、七章）**——四象限本來就在討論生與死之間的意義。**V1=9章／V2=8章／V3=5章**（V3 剩：在場世界論／工畫師／意想界工程學／住世者修養／結語）。
2. **V1/V2 巡禮章不得是中性哲學史**：一律以意欲、願然、四象限向度討論（V1 三個巡禮章各加「四象限讀法」節）。
3. **現象學方法＝三種態度**：直觀態度／現成態度／遍執態度（使用者定名，出自其與 AI 的對談，**不在原稿與對話庫**，語意對齊 E3「非現成」用法＋唯識遍計所執）。V1 導論第四節＋V2 導論第二節已立節，正文待使用者精修。
4. **O1 新第八章**「創生哲學的本體論自我定位：經驗主義品格與理論的彈性」（生成作為第一哲學／經驗主義品格／形式剛性＋內容彈性／**次大敘事僅簡述互見認識論卷二**，不重複詳介——使用者明示）。原結語→第九章。
5. **O2 改題《從量子到宇宙》**：ch1–5 量子部分不動；新增 ch6 弦論與萬有理論（地景=潛生界物理版）、ch7 古典世界與相對論、ch8 宇宙的本體論意義；**結語改「存在者的有限與無限」**（存在者必有限、生成必無限），舊結語兩節併入。O1=9章、O2=9章。
6. **DB 第二波**：`migrate_v_reorg2.py --apply` 74 筆 V3→V1(38)/V2(36)。**現況 V1=73、V2=116、V3=86、O1=134、O2=93、B1=170，六卷 off-canonical=0。** ledger `c:/tmp/genesis_research/migrate_v_reorg2.jsonl`。
7. clean_inv/worklist/thesis/books.json 已同步（V/O 卷自最終 HTML 重生）。

## ⚠️ 零之二、2026-07-02 價值論三部曲重排＋五然四德移存有論（已完成；章數以「零之三」為準）
使用者定案：**V1《各種生死觀》／V2《美學觀》／V3《世界與生活》**；**五然四德總說移 B1 導論一起說明**。
五然＝實然(本體論)／識然(認識論)／應然(倫理學)／願然(價值論)／默然(存有論)；四德＝實然+識然共證「真」、應然=善、願然=美、默然=聖（無真不成善→美→聖階序）。全 15 卷書稿「四然」已全改「五然」（含 B2/B3/E2 內文）。
- ✅ **HTML 重組**（一次性腳本，舊稿歸檔 `scripts/data/_archive_v_pre_reorg_2026-07-02/`，含 B1/B3/O1/E3/M3 修改前副本）：
  - 舊V1：ch1導論+ch6真善美聖→B1 導論新節；ch2/ch3→新V3 第五/六章；ch4/ch5→新V2 第二/三章。
  - 舊V2：ch1/ch2→新V1 第二/六章；ch3/ch5→新V3 第七/八章；ch4→新V2 第五章；ch6→併入新V3 第九章結語。
  - 舊V3：ch3→新V2 第四章；ch1/2/4 留 V3（ch4 改第三章）；ch5→新V3 第九章（改題「誠實作畫與第二軸心時代」）。
  - 新章（正文=綱要+草記，**待使用者精修**）：V1 導論/軸心×2/現代性/結語、V2 導論/鑑賞力結語、V3 第四章「住世者的修養：演算法時代守住誠實度」。
- ✅ **AI 討論點分配**（源自《世界理論》跨領域討論）：O1 第七章加「三層世界的質性躍升：虛構存有者的本體地位」；E3 第二章加「預測編碼與貝氏大腦：知覺作為受控的幻覺」；M3 第八章加「意想界的強制覆寫：演算法、世界種子與注意力倫理」；價值論端＝新V3 第四章+第九章。
- ✅ **clean_inv/worklist/thesis/books.json 全部同步**（clean_inv 自最終 HTML 重生，B1 ch1=7節、O1 ch7=7節、E3 ch2=5節、M3 ch8=5節）。
- ✅ **DB 遷移完成**：`migrate_v_reorg.py --apply`（確定性規則，非 LLM；ledger `c:/tmp/genesis_research/migrate_v_reorg.jsonl`）。223 筆 book_id/dimension 搬移＋1 筆 Friston 2010 與 V3 同 ref_key 重複→刪(id=954)＋4 筆 B1「默然：四然→五然的最後向度」改名。**現況 V1=35、V2=80、V3=160、B1=170，四卷 off-canonical=0。**
- ⏳ 後續：①新章對話地圖研究尚未跑（V1 新五章、V2 新兩章、V3 ch4，及 O1/E3/M3 新節）— 跑 gen_workflow 前 **必須先把新 clean_inv/worklist 複製到 c:/tmp/genesis_research/**；②搬入 B1 的 38 筆掛在兩個大節上，可再用 reclassify 細分；③轉入章內文殘留舊卷章次引用，各卷序的 editor-note 已註明對照表。

## ⚠️ 零、2026-06-27 認識論卷三重排（進行中）
使用者定案「**主體的生成／誕生屬本體論 O3，不屬認識論**」。見 [[project_genesis_epistemology_trilogy]]。
- ✅ **E3→O3 資料遷移已完成**：`migrate_e3_to_o3.py --apply`（Gemini 引擎，ledger 可還原）。舊 E3《主體的誕生》155 筆：24 筆與 O3 重複→刪、131 筆遷 O3。
- ✅ **蓋提爾/誠實生成論群組再撥 E2**：使用者定案這 39 筆通用認識論(蓋提爾/誠實生成論/強弱認識論/知行合一)歸卷二 E2《認識的形式地基》，非主體本體論。`move_gettier_to_e2.py --apply`（還原原 E3 dimension、display_order 500+，ledger 可還原）：37 筆撥 E2、2 筆(Nagel1961/Worrall1989 E2 已有)刪 O3 副本。
- **現況：E3=0、O3=210（118 原生+92 主體/意識遷入）、E2=214（177 原生+37 蓋提爾群組）。**
- ✅ **M1/M2/E1/E2 off-canonical 重分類**：這四卷參考資料在較早 session 建，dimension 是章級/舊版章節標籤與現行 clean_inv 不一致。`reclassify_offcanon.py`（Gemini 引擎，對齊條件＝off-canonical 不看 display_order，ledger 可還原）已把 M1(45)/M2(48)/E1(48)/E2 原生(15) 全部對齊 canonical。**現況 M1/M2/E1 off=0**。
- ✅ **E2 加「知識的判準：從 JTB 到誠實生成論」章**（clean_inv 第二章後，5 小節：蓋提爾/誠實生成論/誠實是知識的條件/強弱認識論/知行合一）。37 筆蓋提爾群組已歸入該章、**E2 off-canonical = 0**（DB live）。
- ✅ **新 E3《認識你自己》已建並入庫**（2026-06-27）：clean_inv/worklist/thesis 手工建 7 章 27 節（導論反身認識→意識與潛意識→**涂爾幹樞紐**身體儀式集體表徵→符號與詮釋→權力制度慣習→跨物種環境→結語）。research workflow(inline) 7/7 完成 → `ingest_all.py apply E3`，**E3=79 筆、0 off-canonical**，各章 7–13 筆。舊《主體的誕生》報告檔已歸檔 `scripts/data/_archive_e3_zhutide/`。
- ✅ **E3 book HTML 已改寫為《認識你自己》正文初稿**（2026-06-27）：使用者選「連正文一起起草」。header 換書名/副標/thesis；序+7章27節+跋，每章一 subagent 依對話地圖真實文獻起草（Gertler/Durkheim/Peirce/Cassirer/Ricoeur/Foucault/Bourdieu/Berger&Luckmann/Nagel…），`assemble_genesis_book.py epi E3 7` 組裝，books.json nChapters=7。舊《主體的誕生》book 備份 `_archive_e3_zhutide/E3_主體的誕生_book.html`；drafts 在 `c:/tmp/genesis_epi/draft/E3/`。
  - ⏳ **正文待使用者精修**（AI 初稿）＋**回填各節 `<p class="section-source">` C-xxxxx 對話引用**（本次略，需對話語料對應）。
  - 小提醒：book h3「Berger &amp; Luckmann」是正確 HTML escape，與 clean_inv/DB 的「&」渲染相同；日後若用 all_sections.py 從 HTML 重生 clean_inv 需 unescape 才對得上。
- ✅ 舊 E3 檔已全數換掉：舊 dialogue 報告檔歸檔 `_archive_e3_zhutide/`、clean_inv/worklist/thesis 的 E3 已換成《認識你自己》7 章。**本次重排全部完成。**

### 零之尾、下一步（使用者精修，非本工作流）
1. E3《認識你自己》正文精修（AI 初稿在 `public/content/works/genesis/E3.html`）+ 回填 C-xxxxx 對話引用 → 改 `c:/tmp/genesis_epi/draft/E3/*.html` 後重跑 `assemble_genesis_book.py epi E3 7`。
2. （可選）O3 第二章 54 筆偏重，想勻可再分類；(D) 待核 5 筆；M2 曾有 1 筆 null stance 已修。
3. 工具全在 `scripts/genesis_research/`：`migrate_e3_to_o3.py`／`move_gettier_to_e2.py`／`reclassify_offcanon.py`／`reclassify_refdb.py`（皆 Gemini 引擎、ledger 在 `c:/tmp/genesis_research/*.jsonl` 可還原）。⚠️ Workflow 續跑一律用 inline `script`（[[feedback_workflow_inline_script_not_scriptpath]]）。

## 一、已完成（已 push）
- **E1/E2/E3**：原始五項全完成（cite-seq 重整、reader 抽查、逐節分類+跨卷重歸位、重點章對話地圖）。
- **既有 ref-DB 逐節分類**：E1/E2/E3 共 124 筆已細化到 canonical h3 小節並跨卷重歸位（E1=81/E2=50/E3=115）。
- **M1（7 章）、M2（ch1–11）對話地圖**已研究+入庫：M1=162 筆、M2=214 筆（含原 refdb + 對話地圖，去重後 upsert，display-offset 200）。

## 二、DB 現況（lit_review_entries, project_slug=genesis-philosophy；2026-06-27 收尾）
**全 15 卷對話地圖皆已入庫；全卷 off-canonical = 0。TOTAL = 2093。**
```
M1=162 M2=245 M3=156 E1=113 E2=214 E3=79
O1=134 O2=93  O3=210 V1=113 V2=111 V3=90
B1=132 B2=107 B3=134
```
- E3=79（新《認識你自己》7 章）、O3=210（含主體材料 92 遷入）、E2=214（含蓋提爾章 37）。
- 各卷 dimension 全對齊現行 clean_inv canonical 小節。

## 三、待續工作
### (A) 研究剩餘 87 章對話地圖 ← 主工作，吃 session 額度
尚未產報告檔的章（磁碟上無 `scripts/data/lit_review_genesis_<VOL>_dialogue_ch<rc>.md`）：
- **M2**: ch12, ch13
- **M3**: ch1–9（全）
- **E1**: ch1, ch3, ch4, ch8（新章；ch2/5/6/7 已做）
- **E2**: ch1–11（全）
- **E3**: ch1, ch2, ch5, ch10（新章；ch3/4/6/7/8/9 已做）
- **O1**: ch1–7  **O2**: ch1–6  **O3**: ch1–7
- **V1**: ch1–6  **V2**: ch1–6  **V3**: ch1–5
- **B1**: ch1–7  **B2**: ch1–6  **B3**: ch1–7

### (B) 逐卷 ingest（每當某卷所有章報告檔齊）
`python -X utf8 scripts/genesis_research/ingest_all.py apply <VOL> [<VOL>…]`
→ 自動 combine 該卷所有 `*_dialogue_ch*.md`、去重(ref_key)、dry-parse、`ingest_lit_review.py --seed --entries-only --book-id <VOL> --display-offset 200`。冪等。
（先 `… dry <VOL>` 看 DUP=[]/miss/stance/themes 再 apply。）

### (C) 既有 ref-DB 條目逐節分類（M3/O*/V*/B*）✅ 2026-06-26 完成
M3/O/V/B 的原始 410 筆 refdb（display_order<200）「所屬面向」原為章級，**已全部細化到 canonical h3 小節**。
- 工具：`scripts/genesis_research/reclassify_refdb.py`（**走 Gemini→NVIDIA→Haiku Python 引擎，不佔 Claude 額度**）。
  每卷把全卷 canonical 小節清單（編號＋所屬章）+ 既有條目（title/目前章/abstract_zh）丟引擎，回傳每筆最貼切小節編號 → REST PATCH dimension。
- 結果：10 卷 × orig 全部 now-canonical（still-chapter=0）。ledger `c:/tmp/genesis_research/reclassify_refdb.jsonl` 存 {id,old,new} 可還原。
- 不做跨卷搬移（dimension 已隱含該 book 的章；主題單一）。canonical 標籤＝`clean_inv.json`。

### (D) 子代理標「待核」條目複查 — 殘 5 筆（已誠實標記，低風險）
全量僅剩 5 處「（細節待核）」（4 檔）：B2-ch3 Johnston《Encyclopedia of Lacanian Psychoanalysis》無年份、B2-ch3 Panasiuk SSRN working paper、M2-ch1 Buchanan&Powell 2018、M2-ch6 城市起源科普綜述、O1-ch3 Watson/Frette 1996 Nature 署名。皆為真實著作僅單一 metadata 待補，照規格誠實標記，非杜撰；上線前要精修可逐筆查。

### (E) OA 全文抓取（背景、獨立引擎、不佔 session 額度）
`python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project genesis-philosophy --resume --engine gemini --pace 1`（log `c:/tmp/lit_review_genesis_fulltext.log`）。新增 M1/M2 等英文條目的 OA 全文逐筆翻譯入 lit_review_sections。

## 四、工具（已存進 repo `scripts/genesis_research/`，因 c:/tmp 會被清）
- `research_workflow.mjs` — Workflow 腳本（WORK 內嵌剩餘章；每波 6、每章重試；每章一子代理寫報告檔）。
- `gen_workflow.py` — **重生**上面腳本：掃描 `scripts/data/*_dialogue_ch*.md`，把磁碟上**還沒產出**的章重新內嵌成 WORK。⚠️先跑這支再啟 workflow，才不會重做已完成章、浪費額度。
- `ingest_all.py` — 逐卷 combine+dedup+dry/apply（見上 B）。
- `thesis.json` — 15 卷 domain + 核心主張（子代理判斷盟友/foil 用）。
- `clean_inv.json` — 15 卷每章 sections（canonical 小節標籤，去 `一、` 前綴）。`worklist.json`／`all_sections.py` 同源。
- ⚠️ 子代理 prompt 內寫死讀 `c:/tmp/genesis_research/{thesis,clean_inv}.json`。**新 session 若 c:/tmp 已清，先：**
  `mkdir -p /c/tmp/genesis_research && cp scripts/genesis_research/{thesis,clean_inv,worklist}.json /c/tmp/genesis_research/`

## 五、續跑標準循環（每個配額窗口重複）
1. `cp scripts/genesis_research/{thesis,clean_inv,worklist}.json /c/tmp/genesis_research/`（若 tmp 被清）
2. `python -X utf8 scripts/genesis_research/gen_workflow.py`（重生 WORK＝磁碟上尚缺的章）
3. 啟 Workflow 背景跑；通知回來看 done/failed。
   - 🚨 **用 inline `script` 參數，別用 `scriptPath`**：本機 permission hook 讀檔會把 UTF-8 中文誤判成「control characters」而擋下（"script contains control characters"）。把 `c:/tmp/genesis_research/research_workflow.mjs` 內容整段貼進 `script` 即可（meta.description 與 RULES 內的 en-dash `–` 先換成 ASCII `-`，WORK 標題保持原樣以對得上 clean_inv.json）。
4. 對「該卷所有章都齊」的卷：`ingest_all.py apply <那些卷>`。
5. `git add scripts/data/lit_review_genesis_<VOL>_dialogue_*.md && git commit && git push`（pre-push 跑 vitest 要綠；遇 remote 並行 push 衝突就 `git fetch` 後重 push，**別 force**）。
6. failed 多半是 `session limit · resets <時間>`：等該時間過後回到步驟 2。每窗口約 ~18 章。
- 🚨 別 16 並發猛打（會觸發伺服器端 429 過載）；wave=6 已內建。
- 🚨 別 force-reset master；repo 有並行 session 在動（jung/panikkar/gnostic 等未暫存變更不是本工作，別碰）。
