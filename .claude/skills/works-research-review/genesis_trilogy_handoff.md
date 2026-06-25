# 創生哲學‧認識論三部曲 重建交接（genesis epistemology trilogy）

> 給新 session：讀完即可接續。記憶見 [[project_genesis_epistemology_trilogy]]、[[project_genesis_reference_db]]。
> 本檔記錄 **2026-06-25 三卷重排已完成上線** 的狀態，以及五項待續工作。

## 一、三卷現狀（已完成、已 push、vitest 206 綠）

| book_id | 書名 | 章數 | 部署檔 | reader |
|---|---|---|---|---|
| E1 | 本質的幽靈 | 8 | `public/content/works/genesis/E1.html` | `/works/genesis-philosophy/book/E1` |
| E2 | 後後現代思潮宣言 | 11 | `…/E2.html` | `…/book/E2` |
| E3 | 主體的誕生 | 10 | `…/E3.html` | `…/book/E3` |

`public/content/works/genesis-philosophy-books.json` 的三卷標題/subtitle/nChapters 已同步更新。

### 各卷章節
**E1 本質的幽靈**（經驗 vs 本質橫貫全哲學史 + 現象即本質第3-4章立為新方法）
1 認識論的歪斜與本質的幽靈 2 幽靈的誕生：希臘兩源頭與更古老的根(先蘇/古近東) 3 現象即本質:認識論的新方法(上) 4 柏拉圖的棺材板:方法論的刀(下) 5 應用一·中世紀三教(基督教共相/伊斯蘭伊本西那/佛教自性vs中觀空唯識) 6 應用二·近代經驗論(洛克→休謨) 7 應用三·笛卡兒/康德/胡塞爾(epoché只擱置) 8 結語:驅魔之後

**E2 後後現代思潮宣言**（乙地基→丙為何能認識宇宙→甲宣言，把典範轉移放最後當高潮）
1 亞里斯多德邏輯的限制與重構:不二論三律 2 不二論作為後設邏輯 3 語言與意向性:知識的條件 4 數學作為認識:哥德爾與公理的選擇 5 範疇論 vs 集合論:關係性認識 6 科學與人文學科作為認識:方法與準科學性 7 物理為何能描述宇宙:共構【新寫】 8 我們為何能認識宇宙:本體論與認識論同構【新寫】 9 知識範式五階段 10 現代的困局與後現代思潮的解構 11 碎形次大敘事聯盟(終章/宣言高潮)

**E3 主體的誕生**
1 認識的主體:強弱認識論 2 知行合一與蓋提爾問題的重構 3 意識的認識論 4 意識的誕生【新寫:自指漩渦/開放自指/共構】 5 具身認識論 6 他心問題與感質的可知性(感質=認識論非存有論) 7 AI認識論一:機器能認識嗎 8 AI認識論二:如何認識AI的心 9 記憶、複製人與「我是個怪圈」【新寫:與侯世達對話】 10 結語:主體的誕生與認識的謙卑(三部曲總收束)

## 二、來源與組裝
- 草稿源真相：`c:/tmp/genesis_epi/draft/{E1,E2,E3}/NN.html` + `_preface.html` + `_coda.html`。
- 組裝：`python -X utf8 scripts/assemble_genesis_book.py epi <E1|E2|E3> <N章>`（header 由 assemble 沿用部署檔，改書名要先改 E?.html `<header>` + books.json）。
- 備份：`c:/tmp/genesis_epi/draft/{E1,E2,E3}_old_backup/`（原始章節）。⚠️**E2_old_backup 的張辰瑋集(07)、張氏黎曼球(08) 是作者原創數學構作、已徹底排除，勿復用**。

## 三、用詞鐵則（全 corpus）
後現代/後後現代去中心 → 一律「**思潮**」不用「主義」；現代主義保留「主義」。「棺材板原則」→「**柏拉圖的棺材板**」。卷一概念引用標「（卷一）」，卷二標「（卷二）」，卷三標「（本卷第N章）」。

## 四、研究回顧（參考資料庫 lit_review_entries）
- 每卷四領域（自然科學/心理學/哲學/宗教與神話）書目，`book_id` 逐卷 scope，project=`genesis-philosophy`。
- 本輪新增：E2 哲學領域 16 筆「當代後後現代/實在論對話地圖」(`scripts/data/lit_review_genesis_E2_dialogue.md`)：Barad行動實在論/enactivism/Griffin建設性後現代=盟友；OOO撤退本質/Meillassoux反相關主義/Bhaskar認識論謬誤=對立；含兩硬詰問(Harman新異與抵抗、太古化石)。
- ingest：`python -X utf8 scripts/ingest_lit_review.py --seed --entries-only --book-id <BID> --project genesis-philosophy --report <md>`。dry-parse 與格式見 `genesis_refdb_handoff.md`。
- 全文逐段轉錄(OA only)背景任務：`scripts/ingest_lit_review.py --fetch-fulltext --project genesis-philosophy --resume --engine gemini`（log `c:/tmp/lit_review_genesis_fulltext.log`）。本輪修過 abort 邏輯：401/403/404/410 付費牆標 unavailable 不計連續中止。

## 五、待續五項（給新 session）
1. **檢查 OA 進度**：`lit_review_entries.fulltext_status` 各狀態統計（translated/fetched/pending/unavailable），背景抓取是否還在跑、是否該 `--resume` 續排 501 筆 pending。
2. **C-xxxxx 對話編號回填，可能要重新分**：新章(E2 ch7/8、E3 ch4/9)目前標「對話編號待回填」無 cite-seq；且**遷建章是從舊結構搬來的，其 section-source 的 C 編號是按舊章節脈絡指派的，重排後可能對不上新章主題**——需重新核對哪些對話真正支撐新章/新節，重新分派 cite-seq。
3. **reader 抽查**：三卷 `/works/genesis-philosophy/book/<BID>` 顯示（章節徽章、本章摘要、論證分析圖、跨卷引用是否成立、有無斷裂）。
4. **最新研究以「每一節」分類**：目前研究回顧的 `所屬面向` 多為章級；要細化到**每一小節(h3)**逐節掛文獻，並補齊 E1、E3（目前對話地圖只做了 E2 哲學域）。
5. **每節找「對話/相反/支持」文獻**：仿 E2 對話地圖，為三卷**每一節**找出可對話、對立、支持的當代文獻（盟友/foil/旁證），逐筆入 `lit_review_entries`（立場=補充/反例/支持），尤其補 E1（中世紀三教、休謨、胡塞爾 epoché）與 E3（意識難問題、他心、AI意識、人格同一性/Parfit、怪圈）。
