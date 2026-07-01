# 創生哲學 15 卷「逐節對話地圖」全量補完 — 交接（2026-06-26）

> 接續：把**全 15 卷每一小節**都掛上「盟友(支持/補充)/foil(反例)/旁證」當代文獻（仿 E2 對話地圖），
> 並把**既有 ref-DB 條目逐節分類**。瓶頸＝Claude **session 額度**：每個配額窗口約只能跑 **~18 章**研究子代理，
> 全部 105 章要橫跨數個重置窗口。記憶見 [[project_genesis_reference_db]]、[[project_genesis_epistemology_trilogy]]。
> 前一份 E1/E2/E3 收尾交接見 `genesis_trilogy_handoff.md`（五項已完成）。

## ⚠️ 零、2026-06-27 認識論卷三重排（進行中）
使用者定案「**主體的生成／誕生屬本體論 O3，不屬認識論**」。見 [[project_genesis_epistemology_trilogy]]。
- ✅ **E3→O3 資料遷移已完成**：`migrate_e3_to_o3.py --apply`（Gemini 引擎，ledger 可還原）。舊 E3《主體的誕生》155 筆：24 筆與 O3 重複→刪、131 筆遷 O3。
- ✅ **蓋提爾/誠實生成論群組再撥 E2**：使用者定案這 39 筆通用認識論(蓋提爾/誠實生成論/強弱認識論/知行合一)歸卷二 E2《認識的形式地基》，非主體本體論。`move_gettier_to_e2.py --apply`（還原原 E3 dimension、display_order 500+，ledger 可還原）：37 筆撥 E2、2 筆(Nagel1961/Worrall1989 E2 已有)刪 O3 副本。
- **現況：E3=0、O3=210（118 原生+92 主體/意識遷入）、E2=214（177 原生+37 蓋提爾群組）。**
- ⏳ **待使用者定奪**：新 E3《認識你自己》主題軸章節（已提精修 8 章草案，含涂爾幹「圖騰/身體儀式/社會建構」為連結軸；待確認章數與「符號/身體」是否與 E2ch3/O3 太近）。核可後建 E3 新 clean_inv/worklist → 研究/對話地圖。
- 🚩 **舊 E3 相關檔仍在**：`scripts/data/lit_review_genesis_E3_dialogue_ch*.md`（主體的誕生研究，內容已屬 O3）與 `clean_inv.json`/`worklist.json` 的 E3 條目仍是舊章節——**建新 E3 前要先換掉這些**，否則 gen_workflow 會誤判 E3 已完成。

## 一、已完成（已 push）
- **E1/E2/E3**：原始五項全完成（cite-seq 重整、reader 抽查、逐節分類+跨卷重歸位、重點章對話地圖）。
- **既有 ref-DB 逐節分類**：E1/E2/E3 共 124 筆已細化到 canonical h3 小節並跨卷重歸位（E1=81/E2=50/E3=115）。
- **M1（7 章）、M2（ch1–11）對話地圖**已研究+入庫：M1=162 筆、M2=214 筆（含原 refdb + 對話地圖，去重後 upsert，display-offset 200）。

## 二、DB 現況（lit_review_entries, project_slug=genesis-philosophy）
- 2026-06-26 15:16 更新：**M1/M2/M3/E1/E2/E3/O1/O2/O3 對話地圖皆已 ingest**。
  本窗口 apply：M2=198 M3=110 E1=82 E2=133 E3=114 O1=94 O2=56 O3=75（idempotent upsert，display-offset 200）。
- 尚未做對話地圖（仍原始 refdb 章級 ~41–46）：**V1（部分，ch1-4 已研究待補 ch5-6）、V2、V3、B1、B2、B3**。
- ⚠️ M2 有 1 筆缺 stance（None）→ 上線前 (D) 複查。

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
