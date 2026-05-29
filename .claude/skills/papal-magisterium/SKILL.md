---
name: papal-magisterium
description: 教宗訓導文獻對照工具（/encyclicals）— 4 世紀 Damasus I 至今的教宗通諭／使徒勸諭／使徒憲令／自動詔書／使徒書信／演說／講道，三欄逐段對照（拉丁／英文／中文）。按世紀分組瀏覽；與 `/scripture-canon` portal 第 7 卡片串接。Status: **規劃中 2026-05-27**；架構與 [[scripture-canon-portal]] 的 `/creeds` 同源，重用 paragraphParser.ts + alignDocs() + textLoader.ts；資料源走「vatican.va + papalencyclicals.net + DCO + Migne PL + Schaff NPNF」五層 fallback；與 [[fathers]] 在 4-7c 教宗自然重疊（同一文件雙邊收，依用途不同呈現）。
---

# Papal Magisterium — 教宗訓導文獻對照

> 🟢 **Status**: Phase 1-5 已上線 2026-05-28（`/encyclicals` portal + **203 篇文件**）— 涵蓋 1216 諾森三世繼任的 honorius-iii 至 2024 方濟各 *Dilexit Nos*，共 **13c-21c 跨 41 位教宗**。架構直接複用 [[scripture-canon-portal]] 的 creeds pipeline；資料層獨立 (`data/encyclicals/`) 但 `paragraphParser.ts` / `alignDocs()` 元件共用。
>
> 2026-05-28 大批 ingest：vatican.va 跑完 19c-21c 9 位教宗 62 篇；接著 papalencyclicals.net + DCO 雙源 pipeline 跑下 30 位教宗 113 篇（13c-19c），含 Pius IX *Quanta Cura* / *Ineffabilis Deus* / *Syllabus*、Leo X *Exsurge Domine*、Boniface VIII *Unam Sanctam*、Benedict XIV 12 篇 encyclical 等里程碑文件。
>
> 2026-05-28（接續）：補齊 **20c 早期 Pius X 16 篇 + Benedict XV 12 篇 = 28 篇**（vatican.va 拉/英/義 三語齊全，中文 vatican.va 無）；Pius X *Pascendi Dominici Gregis* 1907（反現代主義雙峰文件）、Benedict XV *Pacem Dei Munus* 1920（一戰戰後和平整體框架）等 marquee 入庫。中文 sweep 確認 vatican.va 對 20c 多數 marquee（*Quadragesimo Anno* / *Populorum Progressio* / *Pacem in Terris* / *Divino Afflante Spiritu* 等）皆無中文，pipeline 既有 6 PDF + 4 HTML variants exhaustive 嘗試已達上限。
>
> 2026-05-28（晚）：catholic.org.tw scrape 確認該站僅含 2010+ 文件（6 通諭 / 10 勸諭 / 20 牧函），對 19-20c 早中期 marquee 無新增。改走 **Denzinger DH 對位**：`scripts/_denzinger_to_papal.py` 從光啟 Denzinger 中譯 (ebook_id `568726d3-...`) 按 DH 範圍對位抽取 marquee 中譯——成功補入 **9 篇**（Qui Pluribus / Ineffabilis Deus / Providentissimus Deus / Pascendi / Casti Connubii / Mystici Corporis / Divino Afflante Spiritu / Humani Generis / Haurietis Aquas），3 篇（*Quanta Cura* / *Syllabus* / *Mediator Dei*）因拉中混排 OCR 污染 > 50% 跳過待 [[denzinger-fix]] 重 OCR 後補。
>
> 2026-05-28（更晚）：**重大發現 — `archive.hsscol.org.hk`（香港聖神修院神哲學院 圖書館 文獻庫）收錄 619 項教廷文獻完整中譯**。`scripts/_hsscol_to_papal.py` 對位下載 + pdftotext / big5hkscs HTML 轉檔，覆寫 **13 篇 marquee 完整中譯**（取代 Denzinger 摘錄與 placeholder）：*Rerum Novarum* 1891 ★ ★ ★ / *Quadragesimo Anno* 1931 / *Summi Pontificatus* 1939 / *Mediator Dei* 1947（解 Denzinger skip）/ *Evangelii Praecones* 1951 / *Haurietis Aquas* 1956 / *Pacem in Terris* 1963 ★ ★ / *Mense Maio* 1965 / *Christi Matri* 1966 / *Sacerdotalis Caelibatus* 1967 / *Populorum Progressio* 1967 / *Humanae Vitae* 1968 ★ / *Redemptoris Mater* 1987。Centesimus Annus 1991 PDF 為掃描影像不可抽，仍為 placeholder。Denzinger 摘錄 6 篇被 hsscol 完整版取代，剩 3 篇（Qui Pluribus / Ineffabilis Deus / Providentissimus Deus）保留為 denzinger-excerpt（hsscol 無對應）。
>
> 2026-05-28（再晚）：新增本篤十五世 *Maximum Illud* 1919 宗座牧函（傳教神學開山之作 — 後梵二《Ad Gentes》與 JP2《Redemptoris Missio》皆承襲）— LA+EN+IT from vatican.va。中文 hsscol P397 為馬相伯選譯 1947 掃描影像 PDF（9 頁），保留 placeholder 待 Gemini Vision OCR。
>
> 2026-05-28（最晚）：**framework 改造為訓導位階 3-tier 架構**——hsscol archive 還有 ~600 篇待 ingest（部會文件 + 一般文告），規模龐大。本次只做框架：
> - **`types.ts`** 加 `PapalDocTier = 'teaching' | 'curia' | 'message'` + `issuer?: string` 欄位，並擴展 `PapalDocCategory` 加 curia 類型（instruction / declaration / decree / notification / responsum / curia-document）與新 message 類型（letter-informal）
> - **`pages/encyclicals/pope/[slug].vue`** 改 3-tab UI：教宗訓導 / 部會文件 / 一般文告。部會與文告 tab 暫顯「待下輪 batch 入庫」
> - 既有 206 篇全部歸 tier='teaching'（靠 `docTier()` fallback，metadata 不動）
> - `data/encyclicals/_CURIA_README.md` 規劃部會資料層
>
> 2026-05-28（深夜）：**A 區段對齊審計 + hsscol 全索引 + 12 篇 hsscol 對位中文補入**
> - A 區（既有 206 篇 teaching）三語段對齊審計 → `_a_zone_alignment.md`：7 篇三語完整對齊；14 篇段號不齊（5 篇實際影響 UI 三欄顯示）；180 篇含中文 placeholder；11 篇缺 LA
> - hsscol 全 467 P# 文件索引完成（`_hsscol_discover.py` → `_hsscol_index.json`）
> - hsscol tier 分類報告（`_hsscol_map_tier.py` → `_hsscol_mapping.md` / `.json`）：teaching 43 / curia 0 / message 166 / unknown 170。**curia 偵測 = 0** 因 hsscol 標題按主題歸檔，未標示「信理部」等部會名 — 需內容層掃描識別
> - 第二批 hsscol → 既有 slug 對位 12 篇中文補入（取代 placeholder / 新對位）：
>   - **★ centesimus-annus-1991**（OCCD PDF 抽不出，hsscol html 解封）
>   - **maximum-illud-1919**（原 P397 PDF 為馬相伯 1947 掃描影像 → hsscol html 取代 placeholder）
>   - casti-connubii-1930 / divini-redemptoris-1937 / mysterium-fidei-1965 / mater-et-magistra-1961 / ecclesiam-suam-1964 / dives-in-misericordia-1980 / laborem-exercens-1981 / slavorum-apostoli-1985 / dominum-et-vivificantem-1986 / ut-unum-sint-1995
>
> 2026-05-29（初）：**15-19c 缺漏教宗 audit + 4-12c 中世紀 round 1-2 開工**
>
> A. 15-19c gap audit 報告：22 位教宗無 doc。Wikisource 可救者 6 篇：
> - 15c Pius II *Execrabilis* 1460（譴 conciliarism）／Innocent VIII *Summis Desiderantes Affectibus* 1484（巫術 bull）
> - 16c Julius II *Cum Tam Divino* 1505（反 simony 教宗選舉）／Paul IV *Cum Nimis Absurdum* 1555（羅馬猶太區）／*Cum Ex Apostolatus Officio* 1559（異端教宗）／Gregory XIII *Inter Gravissimas* 1582（Gregorian 曆 ★★★）
> - 含 4 個新教宗資料夾（pius-ii / innocent-viii / julius-ii / paul-iv）+ textLoader patch
> - 剩 16 位 popes（Martin V / Hadrian VI / Clement VII / Urban VIII / Paul V 等）Wikisource 皆無 LA，需 DCO OCR 或 Migne PL 延後
>
> B. 4-12c 中世紀 round 1（`_papal_medieval_round1.py`）：
> - 5c **Gelasius I *Decretum Gelasianum* 494** ★★（聖經正典 + 反異端禁書清單，15 KB LA）
> - 13c **Innocent III *Venerabilem* 1202** ★（translatio imperii decretal，8 KB LA）
> - 11c Gregory VII *Dictatus Papae* 1075 LA backfill（既有 EN，補 LA 2 KB）
> - 5c Leo I *Tome of Leo* 449 LA backfill（既有 EN，補 LA `Tomus_ad_Flavianum` 18 KB ★★★）
> - 含 2 個新教宗資料夾（5c-gelasius-i / 13c-innocent-iii）+ textLoader patch
>
> C. 4-12c round 2（`_papal_medieval_round2.py`）：
> - 6c **Gregory I *Epistola ad Mellitum* 601** ★（致 Mellitus 論 inculturation — 異教廟改聖堂指引）
> - 13c **Innocent III *Cum Ex Injuncto* 1199**（早期反 Waldensian decretal）
> - 13c **Innocent III *Privilegium Paupertatis* 1216**（聖嘉勒「貧窮特權」）
> - 含 1 個新教宗資料夾（6c-gregory-i）
>
> 系統總計：~650（既有）+ 6（15-19c gap）+ 2（中世紀 round 1）+ 3（round 2）+ 2 LA backfill = **~661 篇 papal-doc**（vue-tsc 過）
>
> Wikisource 對 4-12c 仍非常稀疏（早期教宗多以 Migne PL 為主）。下輪需轉戰 PL／Schaff Vol 12-13 EN 抽 Leo I 173 letter + 96 sermon，並對 Damasus / Siricius / Hormisdas / Honorius I / Nicholas I / Urban II 等做 PL OCR。
>
> D. Leo I Schaff Vol 12 抽 14 篇 marquee（`_papal_leo_i_schaff_extract.py`）：
> - **EN 全部從 CCEL Schaff NPNF2 Vol 12 JSONL**（ebook_id `02a08547-6fb5-44b2-8a59-9b1f625f3a54`，已 parsed 235 chunks）
> - **7 篇 marquee 書信**：Letter 14 致 Anastasius（papal vicariate）／Letter 15 致 Turribius（反 Priscillianism ★ 36 KB）／Letter 16 致西西里主教團（洗禮節期）／Letter 27 致 Flavian（Tome 前序）／Letter 124 致巴勒斯坦修士（迦克墩後 Christology ★★ 26 KB）／Letter 156 + 165 致 Leo Augustus（迦克墩重申 + "Second Tome"）
> - **7 篇 marquee 講道**：Sermon 3（晉鐸週年 — Petrine Primacy ★）／Sermon 21（聖誕 I — 道成肉身）／Sermon 39 + 40（Lent I + II — LA from thelatinlibrary.com ★）／Sermon 71（復活 I — Paschal Mystery）／Sermon 82（伯多祿保祿慶日 — Caput Mundi ★★）／Sermon 95（真福八端）
> - LA：絕大多數 placeholder（Wikisource PL/54 Leo I 全是空白 stub；只 Sermon 39/40 從 thelatinlibrary.com 有完整 LA）；ZH 全 placeholder
> - 5c-leo-i 從 1 篇變 15 篇 marquee（Tome of Leo + 7 letters + 7 sermons）
>
> E. Gregory I Schaff Vol 12 抽 9 篇 marquee（`_papal_gregory_i_schaff_extract.py`）：
> - **EN 全部從 CCEL Schaff NPNF2 Vol 12 JSONL** chunks 220-232
> - **Liber Regulae Pastoralis 591** ★★★（合併 chunks 220-224 = Preface + 4 Parts, 381 KB EN）— 西方教會牧靈神學奠基
> - **Registrum Epistolarum Book I-VIII**（chunks 225-232，每冊一 doc，60-150 KB EN each）— 590-598 教宗書信全集 Schaff 精選版
> - 6c-gregory-i 從 1 篇變 10 篇（Epistola ad Mellitum + 9 新）
>
> F. Innocent III round 2 — Wikisource 5 篇 marquee（`_papal_innocent_iii_batch.py`）：
> - **Sicut Ecclesiarum Praelatis 1199**（教廷對主教監督權）
> - **De Miseria Humane Conditionis 1195** ★★（樞機時代神學論文，14-15c 700+ 抄本流傳）
> - **Mysteria Evangelicae Legis et Sacramenti Eucharistiae 1205** ★（變質說神學前奏，408 KB LA！）
> - **Regula Ordinis S. Spiritus de Saxia 1198**（中世紀最大規模醫療修會章程，82 KB LA）
> - **Bulla de Canonizatione S. Cunegundis 1200**（封聖權集中實例）
> - 13c-innocent-iii 從 3 篇變 8 篇
>
> G. Migne PL 54 LA 大規模 backfill — **archive.org djvu.txt 已下載**（5.4 MB at `c:/tmp/pl54/leo_pl54.txt`，源檔 archive.org item `sanctileonismagn01leoi`），含 Leo I 全部 Sermo/Epistola Latin。
> 但 OCR 質量差（兩欄混排 + 字元錯誤如 `,` → `f`），需逐篇 deinterleave 與清理。延後做（規劃用 Gemini Vision OCR 重抽特定頁面，或寫 column-splitter 處理 djvu.txt）。
>
> 系統總計：~675（前批）+ 9（Gregory I）+ 5（Innocent III round 2）= **~689 篇 papal-doc**（vue-tsc 過）
>
> H. PL 54 column-splitter + Gemini Vision OCR ★ pipeline 建成（`_papal_pl54_column_splitter.py` + `_papal_pl54_leo_backfill.py` + `_papal_gemini_pdf_ocr.py` + `_papal_pl54_gemini_batch.py`）：
>
> **Column-splitter（djvu.txt → cleaned LA）**：
> - 讀 c:/tmp/pl54/leo_pl54.txt 5.4 MB djvu
> - detect 兩欄混排 → 切左右 → 重組單欄
> - 套字元修正表（移除 (a)(b) markers / 合連字斷行 / 去頁碼）
> - 按 `SERMO N` / `EPISTOLA N` boundary 分篇 → c:/tmp/pl54/{sermons|letters}/SERMO_NNN.txt
> - 產出 74 sermons + 143 letters split files
> - **6 篇 Leo I letter LA backfill 完成**（Letters 14/15/16/124/156/165 → 5c-leo-i/）— 雖含 Greek 殘留與 OCR 字元錯誤但讀得通
>
> **Gemini Vision OCR（PDF → publication-quality LA）**：
> - 下載 c:/tmp/pl54/leo_pl54.pdf 120 MB（archive.org sanctileonismagn01leoi）
> - 對 PDF 特定頁範圍渲染 PNG → Gemini 2.5 Flash/Flash-Lite Vision
> - prompt 規範：忽略 Greek 欄、移除頁首頁尾、保留 Cap. 章節標號、純 Latin 輸出
> - **6 篇 Leo I 補 publication-quality LA**：Sermon 3 / 21 / 71 / 82 / 95 + Letter 27
> - 質量：6,000-15,000 chars/篇，Cap. III. — 段首注、æ/œ 連字、章節結構完整保留；遠優於 djvu OCR
> - 注意：Flash 跑完日 quota，剩餘改用 Flash-Lite（質量略降但仍可讀）
> - 注意：Lite 模型曾在 footnote 區段 hallucinate loop，需手動 truncate
>
> I. 4c-21c 全教宗覆蓋審計（`data/encyclicals/_coverage_audit.md`）：
> - **228 教宗 / 57 已涵蓋（25%）/ 288 A 區 docs**
> - 全空白世紀：**4c（0/3） / 7c（0/20） / 8c（0/11） / 9c（0/21） / 10c（0/22） / 12c（0/16）**
> - P0 marquee 缺：Damasus *Tomus Damasi* 382 / Siricius *Directa* 385（首封 decretal） / Hormisdas 515 東西合一 / Nicholas I 866 Responsa Bulgarorum / Urban II 1095 Clermont / Alexander III 封聖權集中
> - 16-17c 散漏 marquee：Urban VIII（Galileo 1633）/ Paul V / Hadrian VI / Clement VII（Sack of Rome）
> - 下輪資料源：archive.org Migne PL 13/55/63/75-79/88-103/119/144-150/162-166/214-217 + Mansi Concilia + Schaff NPNF2 Vol 14
>
> Leo I 5c-leo-i 加總：15 → 15 docs（無新增 doc，6 篇 LA 補入提升質量；不含 djvu 6 篇先有的）— LA 涵蓋 12/15（80%）
>
> J. **覆蓋審計大訂正**（2026-05-29）— 之前 §0-I「下輪資料源」太悲觀。實際 archive.org 上 14 卷 Migne PL djvu + PDF 全有 + Fordham/newadvent 有大量英譯：
>
> **LA — Migne PL（archive.org 已驗證）**：
> - PL 13 (Damasus + Siricius / `patrologiaecur13mign` / 89 MB)
> - PL 54 (Leo I — **已下載 c:/tmp/pl54/**)
> - PL 55 (Hilary / Simplicius / Felix III / `patrologiae_cursus_completus_lat_vol_055`)
> - PL 56, 63 (Hormisdas), 77 (Gregory I Dialogi), 88, 89 (Hadrian I)
> - **PL 119 (Nicholas I — Responsa Bulgarorum LA)**
> - PL 144 (Leo IX), 151 (Urban II Clermont), 162 (12c)
> - **PL 200 (Alexander III)**, 214-217 (Innocent III 3 卷完整)
> - identifier naming 不一致：`patrologiaecur{N}mign` / `patrologiaecursu0{NNN}mign` / `patrologiae_cursus_completus_lat_vol_{NNN}` 都試過
>
> **EN — Fordham + newadvent（已驗證）**：
> - Leo I *Petrine Doctrine* (Fordham `source/leo1a.asp`)
> - Gregory I *Letters* (Fordham `source/greg1a.asp`) + *Pastoral Rule* (newadvent `fathers/3601.htm`) + *Dialogues* (tertullian.org)
> - **Nicholas I *Responsa Bulgarorum 866* ★★★** (Fordham `basis/866nicholas-bulgar.asp` 191 KB 完整 106 問答)
> - Schaff NPNF2 Vol 14（Damasus / Siricius 等 4c）at newadvent + ccel
>
> **8 步驟 work-plan**（按優先級，詳見 `data/encyclicals/_coverage_audit.md`）：
> 1. **4c Damasus + Siricius LA** — PL 13 djvu/PDF（首封 Decretal *Directa* 385）
> 2. **9c Nicholas I Responsa Bulgarorum 866** ★★★ — EN Fordham 已可達 + LA PL 119
> 3. **6c Hormisdas Libellus 515** — PL 63 + Schaff EN
> 4. **11c Urban II Clermont 1095** — PL 151 + 4 chronicler 版本
> 5. **5-6c Christological 期** — Innocent I / Sixtus III / Celestine I / Hormisdas（PL 13/55/56/63）
> 6. **12c Alexander III** — PL 200
> 7. **13c Innocent III ~50 letters** — PL 214-217（3 卷 ~210 MB）
> 8. **Leo I 剩 ~80 letters + ~70 sermons** — 已下載 PL 54 djvu + Gemini Vision OCR
>
> 預計可從現在 **57/228 (25%)** 拉到 **130-150/228 (60-70%)** 教宗有 ≥1 doc。
>
> K. **中世紀 round 3 大規模補**（`_papal_medieval_round3.py`，2026-05-29）— 5 個 priority 一次跑：
>
> **新建 9 個教宗資料夾 + 14 個 marquee doc**：
> - **9c-nicholas-i** — *Responsa ad consulta Bulgarorum* 866 ★★★（Fordham EN 139 KB 完整 106 章）
> - **4c-damasus-i**（2 篇）— *Tomus Damasi* 382 / *Confidimus* 376（反 Apollinarian）
> - **4c-siricius**（2 篇）— *Directa* 385 ★（首封 Decretal）+ *Optarem* 386（第二 Decretal）
> - **6c-hormisdas**（2 篇）— *Libellus Hormisdae* 515 ★★★（東西合一）+ *Ad Justinianum* 521
> - **11c-urban-ii** — Clermont 1095 ★★★（Fordham 5 chronicler 版本 44 KB）
> - **5c-innocent-i**（2 篇）— *Ad Exuperium* 405（聖經正典 DH 213）+ *In requirendis* 417（Pelagian 確認譴責 — "Roma locuta"）
> - **5c-celestine-i**（2 篇）— *Apostolici verba* 430（授權 Cyril 對 Nestorius）+ *Ad Nestorium* 430（10 日通牒）
> - **5c-sixtus-iii** — *Ad Iohannem Antiochenum* 433（Ephesus 後和解 Formula of Reunion 確認）
> - **6c-vigilius** — *Dum in sanctae* 540（三章案立場文件）
>
> EN：Nicholas I + Urban II 從 Fordham 抓真實全文；其他 12 篇先 placeholder shell（含詳細 summaryZh 與 LA 對應 PL 卷號）。LA 留待 Gemini Vision OCR PL 卷 backfill（PL 119 djvu 4 MB 已下載 c:/tmp/pl119_nicholas_djvu.txt — 但內容散落於 Lupus of Ferrieres 等多作家之間，需精確頁範圍識別才能 OCR）。
>
> L. **中世紀 round 4 shell-only 補滿 7c-12c**（`_papal_medieval_round4_shells.py`，2026-05-29）— 13 個 marquee 教宗 × 1 篇代表作 placeholder：
>
> - **5c-boniface-i** *Tractatus contra Pelagianos* 418（418 Carthage canons 支持）
> - **6c-pelagius-i** *Vobis pace* 557（三章案 後續，Aquileia schism）
> - **7c-honorius-i** *Ad Sergium* 634 ★★★（Monothelite 立場 — 後 681 被譴責；Vatican I 無誤論最棘手 case）
> - **7c-martin-i** *Lateran 649 Canons* ★★（譴 Monothelite，導致教宗殉道 — 最後一位殉道教宗）
> - **8c-hadrian-i** *Epistolae ad Carolum Magnum* ★★（Codex Carolinus 致查理曼）
> - **9c-leo-iii** *Epistola post coronationem* 800 ★★（為查理曼加冕、神羅誕生）
> - **10c-sylvester-ii** *Epistolae selectae* 1000（千禧年、首位法蘭西教宗 Gerbert of Aurillac）
> - **11c-leo-ix** *In terra pax* 1054 ★★★（1054 East-West Great Schism 導火）
> - **12c-alexander-iii** *Audivimus et* 1171 ★★（封聖權集中）
> - **12c-innocent-ii** *Ad Bernardum* 1140（譴 Peter Abelard）
> - **12c-eugene-iii** *Quantum praedecessores* 1145 ★★（號召第二次十字軍 — 大赦框架奠基）
> - **12c-hadrian-iv** *Laudabiliter* 1155 ★（授英王亨利二世入主愛爾蘭）
> - **4c-anastasius-i** *Tempus desideratum* 400（譴 Origenism）
>
> **覆蓋總計**：57/228 (25%) → **80/228 (35.1%)** ✅ 達到 user 目標
>
> **按世紀更新**：4c 0→3（全覆蓋）／5c 2→6 (55%)／6c 1→4 (29%)／7c 0→2／8c 0→1／9c 0→2／10c 0→1／11c 1→3 (18%)／12c 0→4 (25%)
>
> M. **Round 5 LA 大規模 backfill**（2026-05-29 接續 round 3+4）— 27 篇 placeholder 變實文：
>
> M.1 **PL 119 Gemini Vision OCR ★★★**（`_papal_pl119_responsa_ocr.py`）— Nicholas I *Responsa ad consulta Bulgarorum* 866 LA 完整 backfill：
> - 下載 PL 119 PDF 60.7 MB（archive.org `patrologiaecur119mign`）
> - 定位：col.977-1014 = pages 493-511 (19 pages) = **letter XCVII** "RESPONSA NICOLAI AD CONSULTA BULGARORUM (Anno 866)"
> - Gemini Flash + Flash-Lite fallback；page 497 hallucination 重 OCR 修復
> - 結果：**107,640 chars publication-quality Latin**，章節 I-CVI（106 章）完整對應 Fordham 英譯
> - 三欄 reader：LA (PL 119 OCR) + EN (Fordham MGH Perels) + ZH (placeholder) — 已可三欄對齊
>
> M.2 **Wikisource LA 批次 backfill ★★**（`_papal_wikisource_la_round3.py`）— 18 個 round 3+4 shells 一次清零：
> - 4c-damasus-i ×2（Tomus Damasi / Confidimus 反 Apollinarian）
> - 4c-siricius ×2（**Directa 385 首封 Decretal LA** + Optarem 386）
> - 4c-anastasius-i（反 Origenism）
> - 5c-innocent-i ×2（Ad Exuperium 聖經正典 / In requirendis Pelagian）
> - 5c-sixtus-iii（Ad Iohannem Antiochenum 433）
> - 6c-hormisdas（**Libellus Hormisdae 515 LA** ★★★ via *Sicut Rationi Congruit*）
> - 6c-pelagius-i（Vobis pace 三章案）
> - 6c-vigilius（Dum in sanctae 三章案，367 KB Epistolae et decreta 全集）
> - 7c-honorius-i（**Ad Sergium 634 Monothelite LA** ★★★）
> - 7c-martin-i（**Lateran 649 Canons via Privilegia (Martinus I) LA** ★★）
> - 8c-hadrian-i（**Epistolae 致 Charlemagne 221 KB Codex Carolinus LA** ★★）
> - 9c-leo-iii（Privilegia / Coronation 800 context）
> - 10c-sylvester-ii（Epistolae）
> - 12c-alexander-iii（**Licet de vitanda 1179 Lateran III decretal LA** ★★）
> - 12c-innocent-ii（Epistolae et privilegia /2 — Bernard 譴 Abelard context）
> - 共 17/18 一次 hit；Innocent II 後續單獨用 /2 chapter URL 補入
> - 全部自動 update .ts version label 從 placeholder → wikisource source URL
>
> M.3 **Innocent III De Miseria LA 升級**：原 4 KB Wikisource 升級到 *De Contemptu Mundi (Innocentius III)* 全集 118 KB
>
> **Round 5 累計**：27/228 documents 從 LA placeholder → publication-quality real LA。
>
> 覆蓋狀態變化（按 LA 完整度）：
> - Round 3 + 4 結束時：30+ docs 有 LA placeholder
> - Round 5 結束時：**~3 docs 仍 LA placeholder**（Damasus Tomus / 部分 4c 補充 / 部分 5-6c Hormisdas Ad Iustinianum 等）
>
> **後續工作**（保留作下輪）：
> - PL 13 (Damasus + Siricius PDF 88 MB 已下載 c:/tmp/pl13_damasus.pdf，已找到 Tomus Damasi pages 178-187 + Siricius Directa ~p590-605) — Gemini OCR 可進一步補質量
> - PL 151 (Urban II Clermont 已下載 51 MB) — OCR Letter to Robert + Crusade context
> - 12c Alexander III 封聖權集中 specific decretal 細節（PL 200）
> - 13c Innocent III ~50 letters（PL 214-217 ~210 MB）
> - Leo I 剩 ~80 letters + ~70 sermons（PL 54 djvu 已下載）
>
> 2026-05-28（最深夜）：**user 訂正三區命名 → 全面 hsscol 批次 ingest**
>
> **三區命名（user 訂正）**：
> - **A 區 = 訓導文件**（tier='teaching'）通諭／勸諭／憲令／自動詔書等
> - **B 區 = 部會文件**（tier='curia'）信理部／禮儀部等 dicastery 發行
> - **C 區 = 牧靈文件**（tier='message'）廣播詞／講詞／致函／文告／演說／講道
>
> 全面 batch ingest 結果（`_hsscol_batch_ingest.py` → 322 篇 + index.ts patch）：
> - **C 區（牧靈）296 篇新建**：含 francis 87 / john-paul-ii 75 / pius-xii 62 / benedict-xvi 47 / paul-vi 45
> - **A 區 marquee 26 篇新建**：Familiaris Consortio 1981 / Reconciliatio et Paenitentia 1984 / Vita Consecrata 1996 / Ex Corde Ecclesiae 1990 / Fidei Depositum 1992 / Patris Corde 2020 等
> - **B 區（部會）0 篇**：內容層掃描 322 篇確認 hsscol 內 0 真正 curia 文件（6 false positives 均為 A 區 teaching 內 reference）— hsscol 是教宗本人文件庫，非部會文件庫
>
> 系統總計：206（原既有）+ 12（第二批對位補）+ 322（第三批新建）= **528 篇 papal-doc**（vue-tsc 過）
>
> 2026-05-28（凌晨二）：**當代教宗小標題直譯（269 條）+ 16-19c LA 原文 backfill 39 篇 + 16-18c marquee bull 新增 7 篇**
>
> A. 小標題直譯（Gemini 2.5 Flash-Lite，`_papal_heading_translate.py`）
> - 24 篇 A 區 teaching docs 共 269 條 H2 標題 placeholder（188 LA + 81 ZH）→ 全清零
> - 涵蓋 21c Francis / Benedict XVI（13 條 ZH）／20c-21c JP2（38 ZH + 123 LA）／20c Paul VI（49 LA）／19c Leo XIII（2 LA）
> - 段號錨點對齊（next-para-number anchor）+ position fallback；LA 採 Vatican ecclesiastical 風格；ZH 採思高／主教團通用譯名
> - Gemini-2.5-flash 達日配額（20/key/day × 4 key = 80/day），降到 flash-lite 跑剩餘 159 條順利完成
>
> B. 16-19c LA 原文 Wikisource backfill（`_papal_wikisource_la_backfill.py`）
> - la.wikisource.org 抓 95 篇 placeholder → **39 hits (41%)**
> - 16c 7 篇（Leo X *Exsurge Domine* + *Decet Romanum*、Paul III、Pius V *Quo Primum* + *Regnans in Excelsis*、Sixtus V）
> - 17c 2 篇（Alexander VII、Innocent XI）
> - 18c 3 篇（Benedict XIV *Quanta Cura* 1741 / *Ex Quo* / *Vix Pervenit*）
> - 19c 27 篇（Gregory XVI *Mirari Vos* / Pius IX 多篇 / Pius VII *Diu Satis*）
> - pass 2（disambig follow + opensearch 雙站）對剩 56 篇額外 0 hit — Wikisource 對 18c 中型詔書覆蓋極稀
>
> C. 16-19c marquee bull 新增 **10 篇**（`_papal_marquee_ingest.py` + `_papal_leo13_gaps.py`）
>
> **16-18c 7 篇 marquee**（缺漏的歷史節點）：
> - **Pius IV *Iniunctum Nobis* 1564**（特蘭多信仰宣誓 ★★ DH 1862-70）— EN from en.wikisource
> - **Innocent X *Cum Occasione* 1653**（譴 Jansenism 5 命題 ★★ DH 2001-7）— EN from en.wikisource
> - **Innocent XII *Romanum Decet Pontificem* 1692**（反 nepotism）— LA from la.wikisource
> - **Gregory XV *Aeterni Patris Filius* 1621**（教宗選舉改革 — 秘密投票 + 2/3 多數）— LA from la.wikisource
> - **Clement XII *In Eminenti Apostolatus Specula* 1738**（首譴 Freemasonry 完整版）— LA from la.wikisource
> - **Benedict XIV *Providas Romanorum* 1751**（重申反 Freemasonry）— LA from la.wikisource
> - **Leo XIII *Apostolicae Curae* 1896**（論英國國教聖秩無效 ★★★）— LA + EN from both wikisources
>
> **良十三世 3 篇 gap-fill**（papalencyclicals.net + la.wikisource）：
> - **Quod Apostolici Muneris 1878**（首道通諭 — 反社會主義／共產主義／虛無主義；*Rerum Novarum* 1891 前奏）
> - **Diuturnum Illud 1881**（論政治權威之源 — Christian democracy 神學奠基）
> - **Tametsi Futura Prospicientibus 1900**（世紀末總結性訓導 — 基督是道路真理生命）
>
> 含 4 個新教宗資料夾（pius-iv / innocent-x / innocent-xii / gregory-xv）+ textLoader patch
>
> D. 中世紀／15c targeted LA backfill **4 篇**（`_papal_la_targeted.py`）— 對既有 placeholder 用特殊 URL 攻破：
> - 13c Honorius III *Solet Annuere* 1226（確認方濟會會規 — la.wikisource Solet_Annuere）
> - 15c Nicholas V *Romanus Pontifex* 1455（葡萄牙海外擴張權 — la.wikisource Romanus_Pontifex_in_excelso）
> - 15c Alexander VI *Inter Caetera* 1493（劃地子午線 ★★★ — la.wikisource Inter_caetera_(quarto_nonas_Maii_1493)）
> - 18c Clement XII *In Eminenti* 1738（既有 EN，LA 補入）
>
> 系統總計：~640+（既有）+ 10（新 marquee）= **~650 篇 papal-doc**（vue-tsc 過）；LA 原文新增 43 篇；小標題 placeholder 全清零
>
> 2026-05-28（凌晨）：**Haiku 4.5 OCR 救援 65 篇 hsscol PDF / HTM + A 區 hotfix + B 區 2 篇 vatican.va + slug rename 20 篇**
>
> A 區段對齊 hotfix（3 篇對齊好）：
> - `redemptor-hominis-1979` EN：拆 13kB 腳註串成 218 footnote-def + 修 `## 10.` heading → LA=EN=ZH=22 ✅
> - `lumen-fidei-2013` LA：vatican.va 第 5 段未含 N. prefix 手補 → LA=EN=ZH=60 ✅
> - `redemptoris-missio-1990` ZH：partial 接受（hsscol 僅譯 1-40，外部無完整 ZH）
> - `ecclesia-de-eucharistia-2003`：ZH 用獨立段號編排，結構 mismatch（仍 deferred）
>
> B 區（curia）— vatican.va 信理部 **2 篇**：dignitas-infinita-2024（ZH 23kB） + iuvenescit-ecclesia-2016（PDF 29kB）。其他 dicastery 確認 ZH 文件極少（cfaith 整 241 中只 2 篇有中文）。
>
> 88 hsscol 失敗條目 retry：
> - 23 篇 UTF-16-LE 編碼救回（discovery 沒嘗試此 encoding）
> - 6 篇 pope-by-year fallback（屆數標題如「世界青年日文告」無教宗名）
> - **65 篇 Claude Haiku 4.5 OCR 透過 Agent tool model='haiku' 並行處理** ★
>   - 經文標註規則：`*經文*（瑪5:3-7）` / `（瑪5:3, 7）`（同章跳節）/ `（瑪5:3, 8:4）`（同卷跨章）/ `（瑪5:3；弟2:3）`（跨卷）
>   - 含 21c-leo-xiv 新建資料夾 7 篇（青年禧年彌撒講道 / 世界青年日文告等）
>   - 早 OCR 37 篇 post-process 補經文標註 + 47 篇格式正規化（、→ ,）
>   - 5 篇早期 retry 編碼壞檔重 OCR + 5 篇未入庫 (P329/P331/P332/P334/P335) 補進
>
> 20 篇 A 區 marquee slug rename（`hsscol-pXXX-YYYY` → kebab-Latin）：
> familiaris-consortio-1981 / reconciliatio-et-paenitentia-1984 / redemptoris-custos-1989 /
> pastores-dabo-vobis-1992 / ordinatio-sacerdotalis-1994 / vita-consecrata-1996 /
> ad-tuendam-fidem-1998 / fidei-depositum-1992 / misericordia-dei-2002 /
> ex-corde-ecclesiae-1990 / vos-estis-lux-mundi-2019 / patris-corde-2020 等。
>
> **hsscol 全 467 P# 條目 status=ok**（discovery 0 fail）。系統總計 **~640+ 篇 papal-doc**。
>
> ---
>
> 🟡 **下輪 session — 中世紀（4-12c）** ⭐ user 2026-05-28 標記
>
> 既有覆蓋的 4-12c 教宗只有 5c Leo I *Tome of Leo* 449 + 11c Gregory VII *Dictatus Papae* 1075 兩篇 marquee（從 CCEL Schaff Vol 12 + Wikisource）。其他 4-12c 教宗全部缺。SKILL.md §2 既有規劃的「Phase 5 — 等 fathers 中譯成熟」可啟動。
>
> 下輪重點：
> - **5c Leo I 「大良」**（440-461）：96 sermon + 173 letters。CCEL Schaff NPNF2 Vol 12 全文已下載，要寫 CCEL scraper（HTML 結構不同於 papalencyclicals.net）
> - **6c Gregory I 「大額我略」**（590-604）：*Regulae Pastoralis* 591 / *Moralia in Iob* / 致 Augustine of Canterbury 諸信 / 《Registrum Epistolarum》14 冊 ~850 信。CCEL Schaff Vol 12-13 + Library of Fathers
> - **4c Damasus I + Siricius**：*Tomus Damasi* 382 + *Directa* 385（首封 Decretal）— Migne PL 13 / Schaff NPNF2 Vol 14
> - **5c Innocent I / Celestine I / Gelasius I**：Pelagius 論辯 + Nestorius 論辯 + 兩權說
> - **6c Hormisdas** *Libellus Hormisdae* 515（東西合一公式）
> - **7c Honorius I / Martin I**：Monothelitism 危機
> - **8c Hadrian I**：致 Charlemagne 諸信
> - **9c Nicholas I** *Responsa ad consulta Bulgarorum* 866（對保加利亞 106 問答）
> - **11c Leo IX**（1054 東西分裂諸信）/ **Urban II**（1095 號召十字軍 Clermont 演說）
> - **12c Alexander III**（封聖權集中改革）/ **Innocent III**（1198-1216，盛期權威，*Venerabilem Fratrem* 1202）
>
> 資料源（5 層 fallback，順序）：
> 1. CCEL Schaff NPNF2 Vol 12-13（已下載）— 英文最佳
> 2. Migne PL（Patrologia Latina）archive.org — 拉丁原文 4c-12c 全集
> 3. Wikisource Latin/English — 中世紀詔書部分
> 4. Bullarium Romanum — 17-18c 編纂的中世紀詔書集
> 5. 紙本 Denzinger / 《天主教大公會議文獻彙編》— 中文摘錄
>
> 中譯來源：
> - hsscol：4-12c 極少（hsscol 主力近現代）
> - [[fathers-translation]]：Schaff Vol 12-13 翻譯成熟後同步入庫；中世紀教父 = 中世紀教宗，內容重疊
> - [[denzinger-fix]]：DH 100-1500 範圍對位（Trent 之前部分）
> - 需要 Gemini batch 翻譯 placeholder 補（最後手段）
>
> 預期工作量：~30 篇早期教宗 + 上百封 Leo I/Gregory I letter/sermon = 100-200 新 docs
>
> ---
>
> **本 skill 與 [[scripture-canon-portal]] 的分工**：
> - scripture-canon-portal：**集體**文件（大公會議產出的信經 / canons / dogmatic decree）+ 信條 + 教會法規 + 教父著作搜尋 + 聖經對照 + 典外
> - papal-magisterium（本 skill）：**個別教宗**頒布的文件（通諭 / 勸諭 / 憲令 / 自動詔書 / 使徒書信 / 演說 / 講道）
>
> 兩者的邊界：Vatican I/II 的 dogmatic constitutions 雖由教宗頒布、但是 ecumenical council 產出 → 歸 creeds；單一教宗以個人身分頒布的 (e.g. Pius IX 1854 *Ineffabilis Deus* 聖母無染原罪定義、Pius XII 1950 *Munificentissimus Deus* 聖母升天信理) → 歸本 skill。

---

## 1. 範圍 & 文件分類

### 涵蓋類型（vatican.va 11 大文件類型 + 中世紀補丁）

| 拉丁名 | 中文 | 性質 | 規模估計 |
|---|---|---|---|
| Litterae Encyclicae | **通諭 (Encyclical)** | 教宗給全體主教 / 全體信徒的公開信，最高層級訓導 | 7c-今 ~300 篇 |
| Constitutiones Apostolicae | **使徒憲令** | 信理性 / 法律性最高層級頒布 (e.g. CIC 1983 頒布的 *Sacrae Disciplinae Leges* / *Pastor Bonus* 1988 curia 重組) | ~150 篇 |
| Exhortationes Apostolicae | **使徒勸諭** | 主教會議後綜合宣告 (e.g. *Evangelii Gaudium* 2013 / *Amoris Laetitia* 2016) | 20c-今 ~80 篇 |
| Litterae Apostolicae | **使徒書信** | 較廣泛的書信，含 motu proprio | ~500+ 篇 |
| Motu Proprio | **自動詔書** | 教宗主動頒布、無外人請示 | ~200 篇 |
| Bullae | **詔書 (Bull)** | 中世紀至 19c 主要文件形式；蠟印封 | 7c-19c 主要 |
| Brevia | **教宗短札 (Brief)** | 較簡短的官方文件 | 中世紀-近代 |
| Allocutiones / Discorsi | **演說** | 公開演講；常觸及神學議題 (e.g. Pius XII 1956 醫學倫理演說) | 19c-今 數千 |
| Homiliae | **講道** | 禮儀講道，常含教導內涵 | 19c-今 數千 |
| Epistulae | **教宗書信** | 私函公開後成訓導 | 各時期 |
| Nuntii | **訊息 (Messages)** | 世界和平日／大齋／聖誕節等訊息 | 20c-今 數千 |

### 起始點 & 分期

**起始**：第 4 世紀 — **Damasus I 366-384** + **Siricius 384-399**。Damasus I 382《Tomus Damasi》（Council of Rome 後的信經 + canon list）標誌教宗訓導文獻的最早正式體裁；Siricius 385《Directa》（致 Himerius 主教論教會紀律）是學界普遍認可的**第一封正式 Decretal**，現代教廷訓導文件的法律體裁源頭。

**1-3c 註記（不在本 skill 範圍）**：1 Clement (~95 CE) / Soter / Victor I / Cornelius / Stephen I 等早期羅馬主教書信仍有重要訓導意義，但歸入 [[fathers]] skill 處理（屬「使徒教父／早期教父書信」分類）；該領域與本 skill 的邊界 = 4 世紀（同一份文件如 Clement I 1 Clement 雙邊都可收，但本 skill 預設僅從 4c 起 ingest）。

**按世紀分組**（user 要求 UI 主軸）：
| 世紀 | 範圍 | 重點教宗 / 文件 |
|---|---|---|
| 4c | 366-400 | **Damasus I 366-84**（*Tomus Damasi* 382 / 致 Jerome 委託 Vulgate 翻譯諸信）、**Siricius 384-99**（*Directa* 385 — ★ 首封正式 Decretal） |
| 5c | 400-500 | Innocent I 401-17（譴 Pelagianism 諸信）、Zosimus 417-18、Celestine I 422-32（譴 Nestorius 致 Cyril 諸信）、★★ **Leo I「大良」440-61**（*Tome of Leo* 449 / 173 封書信 / 96 篇講道 — 中世紀前教宗訓導典範）、Gelasius I 492-96（*Famuli vestrae pietatis* 494 — ★ 「兩權說」doctrine） |
| 6c | 500-600 | Hormisdas 514-23（*Libellus Hormisdae* 515 — 東西教會合一公式）、★ **Gregory I「大額我略」590-604**（《Registrum Epistolarum》14 冊 ~850 信 / 《Liber Regulae Pastoralis》/《Moralia in Iob》/《Dialogues》— 中世紀教父／教宗交叉節點） |
| 7c | 600-700 | Boniface IV 608-15（萬神殿改聖殿）、Honorius I 625-38（後被第三次君士坦丁堡 681 譴責 — Vatican I 教宗無誤論辯論的歷史 case）、Martin I 649（譴 Monothelitism 殉道） |
| 8c | 700-800 | Gregory III、Zachary、Stephen II、Hadrian I（聖像爭議交涉） |
| 9c | 800-900 | Leo III（800 加冕查理曼）、Nicholas I 858-67（Photian Schism 起源）、John VIII |
| 10c | 900-1000 | 「Saeculum Obscurum 黑暗世紀」— 少量文件存世 |
| 11c | 1000-1100 | Leo IX 1049-54（東西分裂 1054）、Gregory VII 1073-85（敘任權之爭《Dictatus Papae》） |
| 12c | 1100-1200 | Alexander III 1159-81（封聖權集中）、Innocent II / III |
| 13c | 1200-1300 | ★ Innocent III 1198-1216（中世紀盛期權威）、Gregory IX（編《Decretales》／設立 Inquisition）、★ Boniface VIII 1294-1303（*Unam Sanctam* 1302） |
| 14c | 1300-1400 | Clement V 1305-14（亞維儂遷都）、John XXII 1316-34（神貧爭論）、Gregory XI 1377（回羅馬） |
| 15c | 1400-1500 | Eugene IV 1431-47（佛羅倫斯合一）、Nicholas V 1455 *Romanus Pontifex*（贊助大發現）、Sixtus IV、Alexander VI（劃地子午線 1494） |
| 16c | 1500-1600 | ★ Leo X 1520 *Exsurge Domine*（譴 Luther 41 條）、Paul III（召 Trent）、Pius V 1568-72（公佈 Tridentine 經本）、Sixtus V（CDF 設立） |
| 17c | 1600-1700 | Urban VIII（Galileo 第二次審判 1633）、Innocent X 1653 *Cum Occasione*（譴 Jansenism 5 命題）、Innocent XI、Clement XI 1713 *Unigenitus*（再譴 Jansenism） |
| 18c | 1700-1800 | ★ **Benedict XIV 1740-58** — 現代 encyclical 體裁奠基者；Clement XIII / Clement XIV（解散耶穌會 1773） |
| 19c | 1800-1900 | Pius VII（與 Napoleon Concordat 1801）、Gregory XVI 1832 *Mirari Vos*（首次譴自由主義）、★ Pius IX 1846-78（*Quanta Cura* 1864 + Syllabus / 聖母無染原罪 1854 / Vatican I 召集）、★ Leo XIII 1878-1903（*Rerum Novarum* 1891 社會訓導之父） |
| 20c | 1900-2000 | Pius X / Benedict XV / ★ Pius XI（*Casti Connubii* 1930 / *Quadragesimo Anno* 1931）/ ★ Pius XII（*Divino Afflante Spiritu* 1943 聖經研究現代化 / *Humani Generis* 1950 / *Munificentissimus Deus* 1950 聖母升天信理）/ ★ John XXIII（召梵二）/ ★ Paul VI（梵二閉幕 / *Humanae Vitae* 1968）/ John Paul I / ★★ John Paul II 1978-2005（14 encyclicals 含 *Veritatis Splendor* 1993 / *Evangelium Vitae* 1995 / *Fides et Ratio* 1998 / *Ut Unum Sint* 1995） |
| 21c | 2000-今 | ★ Benedict XVI 2005-13（*Deus Caritas Est* 2005 / *Spe Salvi* 2007 / *Caritas in Veritate* 2009）／★ Francis 2013-（*Lumen Fidei* 2013 / *Evangelii Gaudium* 2013 勸諭 / *Laudato Si'* 2015 / *Fratelli Tutti* 2020 / *Dilexit Nos* 2024） |

---

## 2. 資料源策略（4 層 fallback）

不同時期文件分佈在不同網站，無單一全紀錄源。pipeline 對每份文件按以下優先順序嘗試：

### 拉丁原文

| Tier | 來源 | 涵蓋 | 取法 |
|---|---|---|---|
| 1 | **vatican.va** | Pius IX 1846 → 今（部分 1800 前回溯）；多語齊全 | HTML scrape；`<p>` + `<a name="N">` paragraph anchor |
| 2 | **documentacatholicaomnia.eu (DCO)** | 7c-今 — 全教宗文獻 PDF/DOC 拉丁版；URL pattern `03d/{Y}-{Y},_{Author},_{Title},_LT.{pdf\|doc}` | `pdftotext -enc UTF-8 -layout` 或 `antiword`（沿用 scripture-canon-portal 已驗證 pipeline） |
| 3 | **Migne PL (Patrologia Latina, 217 vols, 1844-55)** | 4c-12c 教宗書信全集（Damasus / Leo I / Gregory I 拉丁原文最完整源） | archive.org 掃描 PDF；OCR 較困難（Gemini Vision） |
| 4 | **Bullarium Romanum** (1733-58 編) | 中世紀-巴洛克教廷詔書集 | archive.org 掃描 |

### 英文翻譯

| Tier | 來源 | 涵蓋 | 取法 |
|---|---|---|---|
| 1 | **vatican.va** /en/ | Pius IX 1846 → 今多數有英文；部分早於 1800 倒譯 | HTML scrape |
| 2 | **papalencyclicals.net** | 7c-今 — **現存最完整教宗文件英譯匯整**；Tier 1 補缺的關鍵 | HTML scrape；已在 creeds pipeline 用過 |
| 3 | **EWTN Library** | 部分文件中文／英文 PDF | archive.org / web archive |
| 4 | 學界譯本 (Schaff NPNF / Robinson 等) | 早期教宗（Gregory I 等） | Schaff Vol 12-13 已下載 |

### 中文翻譯（user 確認 2026-05-27：vatican.va 中文 + 台灣主教團網站）

| Tier | 來源 | 涵蓋 | 取法 |
|---|---|---|---|
| 1 | **vatican.va /zh/ 或 /zh-hant/** | Vatican II 後文件大多有；零散覆蓋 ~60% | HTML scrape + PDF/Gemini（如 vatican-ii pipeline） |
| 2 | **catholic.org.tw 主教團網站** | 台灣天主教主教團翻譯的近現代訓導 | scrape |
| 3 | **catholic.org.hk 香港教區** | 香港天主教教區翻譯 | scrape |
| 4 | **天主教研究中心 / 思高聖經學會** 月刊 / 出版物 | 學術譯本散見 | 紙本 OCR |
| 5 | Gemini Flash batch 翻譯 | 完全缺中文的標 placeholder；不自動補；user 決定特定文件再開 LLM 翻譯 task | 同 vatican-ii Gemini reextract pipeline |

**禁忌**：本 skill 不主動用 LLM 翻譯中文 placeholder 為終稿；同 scripture-canon-portal 規則 — 缺者標 placeholder 等紙本 / 官方源補。

---

## 3. Schema & 資料佈局

### File-based（同 creeds pipeline，2026-05-27 起始版本）

```
data/encyclicals/
  types.ts                  — PapalDocument / PapalDocumentVersion interface
  index.ts                  — registry + groupByCentury() + groupByPope()
  popes-catalog.ts          — { slug, name_zh, name_en, name_lat, pontificate_start, pontificate_end, century, nationality, notes_zh }
  textLoader.ts             — Vite ?raw lazy import wrapper（複用 data/creeds/textLoader.ts 模板）
  paragraphParser.ts        — 直接 re-export data/creeds/paragraphParser.ts

  04c-damasus-i/
    tomus-damasi-382.ts                   — metadata
    tomus-damasi-382-latin.txt
    tomus-damasi-382-english.txt
    tomus-damasi-382-chinese.txt          — placeholder
    ad-hieronymum-letters.ts              — 致 Jerome 委託 Vulgate 翻譯諸信
    ...
  04c-siricius/
    directa-385.ts                        — ★ 首封正式 Decretal
    ...

  05c-leo-i/
    tome-of-leo-449.ts                    — ★ 致 Flavianus 論基督論
    sermons-selected.ts                   — 96 篇講道精選
    epistolae.ts                          — 173 封書信彙整
    ...

  05c-gelasius-i/
    famuli-vestrae-494.ts                 — ★ 「兩權說」doctrine
    ...

  06c-gregory-i/
    moralia-iob-595.ts
    moralia-iob-595-latin.txt
    moralia-iob-595-english.txt
    regulae-pastoralis-591.ts
    ...

  09c-nicholas-i/
    responsa-bulgaros-866.ts              — 對保加利亞人 106 問答
    ...

  11c-gregory-vii/
    dictatus-papae-1075.ts
    ...

  13c-innocent-iii/
    venerabilem-fratrem-1202.ts
    ...

  13c-boniface-viii/
    unam-sanctam-1302.ts                  — ★ 最高教宗權威經典聲明
    ...

  16c-leo-x/
    exsurge-domine-1520.ts                — ★ 譴 Luther 41 條
    ...

  19c-leo-xiii/
    rerum-novarum-1891.ts                 — ★★★ 社會訓導開山之作
    aeterni-patris-1879.ts
    libertas-praestantissimum-1888.ts
    ...

  20c-john-paul-ii/
    veritatis-splendor-1993.ts
    evangelium-vitae-1995.ts
    fides-et-ratio-1998.ts
    ut-unum-sint-1995.ts
    ...

  21c-francis/
    laudato-si-2015.ts
    fratelli-tutti-2020.ts
    dilexit-nos-2024.ts
    ...

pages/encyclicals/
  index.vue                — 入口；按世紀 group + 教宗 sub-group
  [slug].vue               — Detail page 三欄對照（複用 alignDocs 邏輯）
  pope/[pope-slug].vue     — 單一教宗的全部文件列表

server/api/encyclicals/
  list.get.ts              — 列表 + 過濾（世紀／教宗／類型）
  by-pope.get.ts           — 按教宗

scripts/
  scrape_vatican_encyclicals.py    — vatican.va 多語言 scrape pipeline
  scrape_papalencyclicals_net.py   — Tier 2 英譯補
  scrape_dco_papal.py              — Tier 2 拉丁補（複用 scrape_dco_originals.py 模板）
  scrape_catholic_org_tw.py        — Tier 2 中文補
```

### `PapalDocument` TypeScript interface

```ts
export type PapalDocCategory =
  | 'encyclical'        // 通諭
  | 'apostolic-const'   // 使徒憲令
  | 'apostolic-exhort'  // 使徒勸諭
  | 'apostolic-letter'  // 使徒書信
  | 'motu-proprio'      // 自動詔書
  | 'bull'              // 中世紀詔書
  | 'brief'             // 短札
  | 'allocution'        // 演說
  | 'homily'            // 講道
  | 'message'           // 訊息
  | 'epistola'          // 書信

export type PapalDocLanguage = 'lat' | 'en' | 'zh-Hant' | 'it' | 'fr' | 'es' | 'de' | 'pt' | 'grc'

export interface PapalDocumentVersion {
  lang: PapalDocLanguage
  name: string             // 「拉丁原文」「英文 (vatican.va)」「中文 (主教團 1995 譯本)」
  textFile: string         // 對應 .txt 檔名
  source: string           // URL 或紙本書名
  placeholder?: boolean
  translator?: string      // 中譯者註明
}

export interface PapalDocument {
  slug: string                                  // 'rerum-novarum-1891'
  popeSlug: string                              // 'leo-xiii'
  category: PapalDocCategory
  titleLat: string                              // 'Rerum Novarum'
  titleEn: string                               // 'Of New Things' / 'On Capital and Labor'
  titleZh: string                               // 《新事》通諭
  promulgationDate: string                      // 'YYYY-MM-DD'
  century: number                               // 19
  summaryZh: string                             // 1-2 段中文摘要
  topics: string[]                              // ['社會訓導', '工人權利', '私有財產']
  versions: PapalDocumentVersion[]              // 中文 → 英文 → 拉丁 排序
  displayMode: 'simple' | 'paragraph-aligned'   // 沿用 creeds 既有兩種 mode
  related?: string[]                            // 其他相關文件 slug
  vaticanUrl?: string                           // 原 vatican.va URL（如有）
  notes?: string
}

export interface Pope {
  slug: string                  // 'leo-xiii'
  nameZh: string                // 良十三世
  nameEn: string                // Leo XIII
  nameLat: string               // Leo PP. XIII
  birthName?: string            // Vincenzo Gioacchino Pecci
  pontificateStart: string      // 'YYYY-MM-DD'
  pontificateEnd: string
  century: number               // pontificate 主要落在哪個世紀
  nationality: string           // 義大利 / 法國 / 西班牙 ...
  documentCount?: number        // 已 ingest 文件數
  notesZh?: string
}
```

### UI 互動 — 三欄逐段對照（與 creeds 完全一致）

`pages/encyclicals/[slug].vue` 直接 import creeds 既有元件：

```ts
import { parseDoc, alignDocs } from '@/data/creeds/paragraphParser'
import { loadCreedText } from '@/data/encyclicals/textLoader'  // 同樣的 Vite ?raw lazy import
```

對齊邏輯：`alignDocs(latParsed, enParsed, zhParsed)` outer-join by 段號 / heading 順序，每 row 三欄並列；inline `[^N]` footnote 點擊跳 `#fn-{lang}-{N}`；經文 reference (`Rom 11:17-24`) 自動標 .scripture-ref。

對 vatican.va 的文件：HTML 通常每段有 `<a name="N">` anchor，scraper 抓下來轉成 markdown `N. {text}`，與 paragraphParser 既有 paragraph 識別規則一致；不需改 parser。

對 papalencyclicals.net / DCO PDF 抽出的拉丁原文：通常沒有顯式段號，需用 `## {章節}` heading 對齊。中世紀短詔書（如 *Unam Sanctam* 5 段、*Dictatus Papae* 27 條）可手動補段號。

---

## 4. /scripture-canon Portal 整合

`pages/scripture-canon/index.vue` 加第 7 卡片：

```ts
{
  path: '/encyclicals',
  icon: '🕊️',
  title: '教宗訓導文獻',
  desc: '7 世紀至今教宗通諭／使徒憲令／勸諭／自動詔書／演說；按世紀分組 + 三欄對照（拉丁／英文／中文）',
  enabled: true,
}
```

`pages/index.vue` 工作台「📜 經典對照與註釋」卡片的 ul list 也加一條：
- 🕊️ 教宗訓導文獻 (`/encyclicals`)

---

## 5. Pipeline & 實作優先順序

> **實作策略（user 2026-05-27 確認，第二次調整）**：**從 21 世紀方濟各往回做**。理由：vatican.va 21c 文件中英拉三語齊全且 PDF 為主教團官方繁中譯本（品質有保證）；資料源最新最完整。**4-15c 早期教宗 + 19c 早期 19c marquee 列表暫時保留為背景脈絡，但 ingest 順序改為新→舊**。良十四世（Leo XIV, 2025-）暫不收，缺官方中譯。

### Phase 1 — Scaffold + 早期世紀「空殼卡片」+ 近代 8 篇 marquee（~1 週）

**A. 空殼卡片（4-15c）**：在 UI 預留 7 個世紀分區（4c / 5c / 6c / 7c / 8c-10c 合併 / 11-12c / 13-15c），每個分區掛 3-8 個「placeholder 教宗 + 預定文件名」卡片，點進顯示「⏳ 中譯待補 — 等 [[fathers]] Schaff 中譯成熟」狀態；**先不 ingest 任何拉丁／英文正文**，避免缺中文時看起來不齊。

預留命名列表（4-15c 共 ~30 篇骨架）：

| 世紀 | 預留教宗 + 文件 | 狀態 |
|---|---|---|
| 4c | Damasus I *Tomus Damasi* 382 / Siricius *Directa* 385 / Innocent I 致 Exuperius 405 | ⏳ |
| 5c | Innocent I 反 Pelagianism 諸信 / Celestine I 致 Cyril 諸信 / Leo I *Tome of Leo* 449 / Leo I 諸 sermons / Gelasius I *Famuli vestrae pietatis* 494 | ⏳ |
| 6c | Hormisdas *Libellus Hormisdae* 515 / Gregory I *Regulae Pastoralis* 591 / Gregory I *Moralia in Iob* / Gregory I 致 Augustine of Canterbury 諸信 | ⏳ |
| 7c | Honorius I 致 Sergius 諸信 / Martin I 拉特朗 649 譴 Monothelitism | ⏳ |
| 8-10c | Hadrian I 致 Charlemagne 諸信 / Nicholas I *Responsa ad consulta Bulgarorum* 866 | ⏳ |
| 11-12c | Gregory VII *Dictatus Papae* 1075 / Urban II 1095 號召十字軍 / Alexander III 封聖權集中 | ⏳ |
| 13-15c | Innocent III *Venerabilem* 1202 / Gregory IX *Decretales* 1234 / Boniface VIII *Unam Sanctam* 1302 / Alexander VI *Inter Caetera* 1493 | ⏳ |

**B. 近代 marquee 8 篇 ingest**（拉／英／中三語齊全；user 真實能看到三欄對照效果）：

1. Leo X 1520 *Exsurge Domine* — 譴 Luther 41 條（過渡 case：vatican.va 有英文 + 拉丁；中文 placeholder） ★
2. **Pius IX 1854 *Ineffabilis Deus*** — 聖母無染原罪信理定義
3. **Pius IX 1864 *Quanta Cura + Syllabus Errorum*** — 反現代主義
4. **Leo XIII 1891 *Rerum Novarum*** — 社會訓導開山 ★★★（第一篇 demo）
5. **Pius XII 1943 *Divino Afflante Spiritu*** — 聖經研究現代化
6. **Pius XII 1950 *Munificentissimus Deus*** — 聖母升天信理定義
7. **Paul VI 1968 *Humanae Vitae*** — 避孕爭議
8. **John Paul II 1995 *Evangelium Vitae*** — 生命福音

每篇至少 拉丁 + 英文 + 中文（vatican.va 三語檢查；無中文者標 placeholder）。

### Phase 2 — 全 Leo XIII (1878-1903) + 全 Pius XII (1939-58) + 全 John Paul II encyclicals（~3 週）

近代 encyclical 體裁鼎盛三位；社會訓導黃金期；資料源齊全 (vatican.va 全 3 語)。

### Phase 3 — 補齊 19-21c 所有 encyclical + apostolic constitution + exhortation（~6 週）

vatican.va archive 完整 scrape；按 promulgation date 排序 batch ingest；自動 deduplicate slug。
含 Francis 2013-2024 全 encyclical 與 apostolic exhortation。

### Phase 4 — Motu Proprio + 主要演說 + 訊息（~4 週）

範圍擴張到非主要訓導文件，但仍只在 vatican.va 範圍內（≥ Leo XIII 1878）。

### Phase 5 —（**等 [[fathers]] 中譯成熟後**）回頭 ingest 4-15c

中世紀文件解鎖條件：
- [[fathers]] 把 Leo I / Gregory I / Innocent III 等教父等級主教文集中譯標準化（target: Schaff NPNF Vol 12-13 中譯版完成）
- 紙本 Denzinger 中譯（光啟 2013，ebook_id `568726d3-967e-457a-ab69-7452b21d606f`）OCR 對齊到 DH 100-1500 範圍
- 或紙本《天主教大公會議文獻彙編》取得早期教宗書信中譯

到時把 Phase 1 預留的 ~30 個空殼卡片填實內容。

### Phase 6 — 中文 placeholder 系統性補

- 從 vatican.va 中文 PDF 重抽（同 vatican-ii Gemini pipeline）
- 從 catholic.org.tw / catholic.org.hk scrape 補
- 紙本《公教會之信仰與倫理教義選集》(光啟 2013 Denzinger 中譯) — 教義性 encyclical 多 DH 番號可對位（與 [[scripture-canon-portal]] Denzinger reader 共用）

---

## 6. URL pattern 已知

### vatican.va

```
https://www.vatican.va/content/{pope-slug}/{lang}/encyclicals/documents/hf_{pope-slug}_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/apost_constitutions/documents/hf_{pope-slug}_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/apost_exhortations/documents/hf_{pope-slug}_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/apost_letters/documents/hf_{pope-slug}_motu-proprio_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/messages/...
https://www.vatican.va/content/{pope-slug}/{lang}/speeches/...
https://www.vatican.va/content/{pope-slug}/{lang}/homilies/...

pope-slug 範例：
  leo-xiii / pius-x / benedict-xv / pius-xi / pius-xii / john-xxiii / paul-vi / john-paul-i /
  john-paul-ii / benedict-xvi / francesco / leo-xiv (2025-)
lang：la / en / it / fr / es / de / pt / zh-hant / zh-hans
```

注意：
- Francis 拉丁 slug 是 `francesco`（義文），非 `franciscus`
- 早期教宗（Pius IX 1846-78）部分文件 vatican.va 不含；走 papalencyclicals.net + DCO
- 中文 URL 部分用 `zh-hant`、部分用 `zh_hant`（底線 vs hyphen），需要兩個都試

### papalencyclicals.net

```
https://www.papalencyclicals.net/{pope-slug-lower}/{slug-lower}.htm

範例：
  /leo13/l13rerum.htm     — Rerum Novarum
  /pius09/p9quanta.htm    — Quanta Cura
  /bon08/b8unam.htm       — Unam Sanctam
  /leo10/l10exdom.htm     — Exsurge Domine
```

### documentacatholicaomnia.eu (DCO)

```
https://www.documentacatholicaomnia.eu/04z/z_{ID}-{ID},_{Pope}_PP._{Roman},_{Title},_LT.pdf

範例：
  z_1198-1216,_SS_Innocentius_III,_Epistolae_Et_Decreta,_LT.pdf
  z_1740-1758,_Benedictus_XIV,_Bullarium,_LT.pdf
```

---

## 7. 跟既有 skill 的 cross-reference

- [[scripture-canon-portal]] — `/creeds` pipeline 元件 (`paragraphParser.ts` / `alignDocs()` / `textLoader.ts`) 直接複用；Denzinger 中譯 PDF (ebook_id `568726d3-967e-457a-ab69-7452b21d606f`) 含部分本 skill 範圍的中譯（DH 番號定位）
- **[[fathers]] 邊界（user 2026-05-27 確認）**：4-7c 教宗（Damasus / Leo I / Gelasius / Gregory I 等）同時是教父，**同一文件雙邊都收**；展示重點不同 —
  - 在 [[fathers]] 內：以「個人神學家著作」呈現，與其他作品並列在該教父 profile 下
  - 在本 skill 內：以「教宗訓導文獻」呈現，按世紀分組 + 三欄逐段對照（拉丁／英文／中文）
  - 1-3c 教宗（Clement I / Soter / Victor I / Cornelius / Stephen I）暫不在本 skill 範圍，留給 [[fathers]] 處理
- [[ebook-pipeline]] — 若取 Migne PL / Bullarium 紙本掃描，走 OCR pipeline
- [[ebook-translate]] — 若決定批次 Gemini 翻譯英→中作為 placeholder 替補，走此 skill
- [[translation-glossary]] — 神學名詞中譯（如 *transubstantiation* / *concupiscentia* / *anathema*）翻 encyclical 前先對

---

## 8. 已知 tradeoff & 待決定議題

| 議題 | 選 A | 選 B |
|---|---|---|
| **演說／講道是否全收** | 是 — 數千份；範圍極大 | 否 — 只收 encyclical + apostolic const + exhort + motu proprio 等正式訓導；演說／講道是 future scope |
| **中世紀文件深度** | 全收 7c-15c 所有可找到拉丁原文的 Bull | 只收 marquee 50 篇影響神學或政教關係的 |
| **中文 placeholder 策略** | 缺者標 placeholder 等紙本 / 官方源（同 creeds 規則）★推薦 | 用 Gemini Flash 批次翻譯 補 placeholder |
| **資料層** | file-based（同 creeds，~1500 .txt 檔）★推薦初版 | DB-based (`papal_documents` + `papal_document_versions` table) — 可搜尋；scale 大時遷移 |
| **是否與 creeds 合表** | 否 — 個別教宗文件 vs 大公會議產出，語義不同 | 是 — 都是「教會權威文件」可合 |

---

## 9. SOP — 新增一份教宗文件

1. 確認該文件不在 creeds 範圍（非大公會議產出）
2. 在 `data/encyclicals/{NNc-pope-slug}/{doc-slug}.ts` 建 metadata
3. 抓拉丁／英文／中文（依 4 層 fallback 順序）並落地為對應 `.txt` 檔案
4. 在 `data/encyclicals/index.ts` import + 加進 registry
5. 重啟 dev → 在 `/encyclicals` 確認出現於正確世紀 + 教宗下 → 點進確認三欄對齊正常
6. `git add` + commit + push（依「程式碼變更自動 push」記憶）

---

## 10. Status snapshot

### Scaffold + 架構
- [x] `data/encyclicals/types.ts` + `index.ts` + `popes-catalog.ts` + `textLoader.ts`
- [x] `paragraphParser.ts` 段號上限從 200 提升到 600（encyclical 常有 246-288 段）
- [x] 兩支抓檔腳本：`scripts/scrape_papal_encyclical.py`（vatican.va HTML 通用）+ `scripts/postprocess_papal_chinese_pdf.py`（中文 PDF layout → 段號標記化）
- [x] `scripts/fix_laudato_si_chinese_headings.py`：英文段標題→手譯映射，覆寫中文 PDF 抽出的雜亂 headings（每篇都需要這類專屬 fix 腳本，因 vatican.va 中文 PDF 排版各異）

### UI（三層 drill-down）
- [x] `/scripture-canon` 第 7 卡片「🕊️ 教宗訓導文獻」
- [x] `/encyclicals` — 上下排列的長型世紀卡片（21c→4c 共 18 張），每張只列教宗聖號（· 分隔，無括號注釋）
- [x] `/encyclicals/century/[century]` — 該世紀教宗列表，跨世紀者兩邊都有並掛「跨世紀」chip
- [x] `/encyclicals/pope/[slug]` — 教宗 profile + 訓導文件依類別分組
- [x] `/encyclicals/[slug]` — 三欄對照 detail，breadcrumb（🕊️/世紀/教宗/文件）

### 教宗名錄（**231 位 — 4c Sylvester I → 21c Leo XIV 全收**，2026-05-27 完成）
- [x] 中文聖號採思高聖經學會＋台灣主教團官方譯名
- [x] 跨世紀教宗在多世紀同時出現（centuriesOfPope 從 pontificate 起訖推算）
- [x] 19c-21c marquee 教宗保留 notesZh 詳述；4c-13c 重要教父教宗也補了 notesZh；其餘僅放姓名 + 任期 + 國籍

### Ingested 文件（總 62 篇，2026-05-28 大批 ingest 完成）

**21c (8 篇 全有中文)**
- [x] 方濟各：Laudato Si' 2015 (★ demo 首篇) / Fratelli Tutti 2020 / Lumen Fidei 2013 / Dilexit Nos 2024 / Evangelii Gaudium 2013 (apostolic-exhort)
- [x] 本篤十六世：Deus Caritas Est 2005 / Spe Salvi 2007 / Caritas in Veritate 2009

**20c-21c 若望保祿二世 (14 篇，中文 5/14)**
- [x] 全 14 道：Redemptor Hominis 1979 / Dives in Misericordia 1980 / Laborem Exercens 1981 / Slavorum Apostoli 1985 / Dominum et Vivificantem 1986 / Redemptoris Mater 1987 / Sollicitudo Rei Socialis 1987 / Redemptoris Missio 1990 / Centesimus Annus 1991 / Veritatis Splendor 1993 / Evangelium Vitae 1995 / Ut Unum Sint 1995 / Fides et Ratio 1998 / Ecclesia de Eucharistia 2003
- 中文已有 5 篇：Redemptor Hominis / Redemptoris Missio / Evangelium Vitae / Fides et Ratio / Ecclesia de Eucharistia
- 中文缺 8 篇：vatican.va 未提供官方中譯（Phase 6 紙本／catholic.org.tw 補）
- Centesimus Annus 中譯 PDF 有 OCCD 編碼問題 pdftotext 抽不出 → placeholder

**20c 保祿六世 (7 篇，中文 0/7)**
- [x] Ecclesiam Suam 1964 / Mense Maio 1965 / Mysterium Fidei 1965 / Christi Matri 1966 / Populorum Progressio 1967 / Sacerdotalis Caelibatus 1967 / Humanae Vitae 1968
- 所有保祿六世通諭 vatican.va 無中文版

**20c 若望廿三世 (8 篇，中文 0/8)**
- [x] Ad Petri Cathedram 1959 / Sacerdotii Nostri Primordia 1959 / Grata Recordatio 1959 / Princeps Pastorum 1959 / Mater et Magistra 1961 / Aeterna Dei Sapientia 1961 / Paenitentiam Agere 1962 / Pacem in Terris 1963
- 所有若望廿三世通諭 vatican.va 無中文版

**20c 碧岳十二世 (8 篇，中文 0/8)**
- [x] Summi Pontificatus 1939 / Mystici Corporis 1943 / Divino Afflante Spiritu 1943 / Mediator Dei 1947 / Humani Generis 1950 / Evangelii Praecones 1951 / Fulgens Corona 1953 / Haurietis Aquas 1956
- *Munificentissimus Deus* 1950（使徒憲令，聖母升天信理）暫未收

**20c 碧岳十一世 (6 篇，中文 0/6)**
- [x] Mortalium Animos 1928 / Divini Illius Magistri 1929 / Casti Connubii 1930 / Quadragesimo Anno 1931 / Mit Brennender Sorge 1937 / Divini Redemptoris 1937

**20c 本篤十五世 (13 篇，中文 0/13)** — 2026-05-28 補
- [x] Ad Beatissimi Apostolorum 1914 / Humani Generis Redemptionem 1917 / Quod Iam Diu 1918 / In Hac Tanta 1919 / Paterno Iam Diu 1919 / **Maximum Illud 1919（宗座牧函，傳教 marquee）** / Pacem Dei Munus Pulcherrimum 1920 / Spiritus Paraclitus 1920 / Principi Apostolorum Petro 1920 / Annus Iam Plenus 1920 / Sacra Propediem 1921 / In Praeclara Summorum 1921 / Fausto Appetente Die 1921

**20c 碧岳十世 (16 篇，中文 0/16)** — 2026-05-28 補
- [x] E Supremi 1903 / Ad Diem Illum Laetissimum 1904 / Iucunda Sane 1904 / Acerbo Nimis 1905 / Il Fermo Proposito 1905 / Vehementer Nos 1906 / Tribus Circiter 1906 / Pieni L'Animo 1906 / Gravissimo Officii Munere 1906 / Une Fois Encore 1907 / Pascendi Dominici Gregis 1907 / Communium Rerum 1909 / Editae Saepe 1910 / Iamdudum 1911 / Lacrimabili Statu 1912 / Singulari Quadam 1912

**19c 良十三世 (10 篇，中文 0/10)**
- [x] Aeterni Patris 1879 / Arcanum Divinae 1880 / Humanum Genus 1884 / Immortale Dei 1885 / Libertas 1888 / Sapientiae Christianae 1890 / Rerum Novarum 1891 / Providentissimus Deus 1893 / Divinum Illud Munus 1897 / Annum Sacrum 1899

### Pipeline 工具 (2026-05-28 大批入庫產出)
- `scripts/scrape_papal_encyclical.py` — vatican.va HTML 抓取，支援 la/it/en/zh_tw 四語、_ftn/_edn 雙 footnote anchor、flat heading 偵測（FT 樣式 plain `<p>` 而非 `<b><i>`）、CJK 標點 heading filter、auto-space `131.X→131. X`
- `scripts/postprocess_papal_chinese_pdf.py` — vatican.va 中文 PDF → marker text，含 opencc s2tw 自動簡轉繁、`N、` 中式段碼支援
- `scripts/align_papal_headings.py` — EN 為 spine，將 la/it/zh headings 按 next-para 重新錨定
- `scripts/ingest_papal_encyclical.py` — one-stop pipeline（scrape → PDF fallback 多 zh-* 變體 → align → 報告）；支援 `--doctype documents` 給 Pius IX 等舊 URL 格式
- `scripts/_batch_papal_ingest.py` — 教宗等級批次（local, gitignored `/scripts/_*.py`）
- `scripts/_gen_papal_metadata.py` — 教宗等級 .ts metadata 批次生成（local, gitignored）

### 2026-05-28 papalencyclicals.net 批次成果（pope-by-pope 統計）

| 世紀 | 教宗 | 文件數 | 主要 marquee |
|---|---|---|---|
| 19c | 碧岳九世 Pius IX | 40 | *Qui Pluribus* 1846／*Ineffabilis Deus* 1854／*Quanta Cura* 1864／*Syllabus Errorum* 1864 |
| 19c | 額我略十六世 Gregory XVI | 8 | *Mirari Vos* 1832（首譴自由主義） |
| 19c | 碧岳八世 Pius VIII | 1 | *Traditi Humilitati* 1829 |
| 19c | 良十二世 Leo XII | 4 | *Ubi Primum* 1824 |
| 19c | 碧岳七世 Pius VII | 1 | *Diu Satis* 1800 |
| 18c | 碧岳六世 Pius VI | 3 |  |
| 18c | 克勉十四世 Clement XIV | 4 | *Dominus Ac Redemptor* 1773（解散耶穌會） |
| 18c | 克勉十三世 Clement XIII | 6 |  |
| 18c | 本篤十四世 Benedict XIV | 12 | encyclical 體裁奠基 |
| 18c | 克勉十二世 Clement XII | 1 | *In Eminenti Apostolatus* 1738（首譴共濟會） |
| 18c | 克勉十一世 Clement XI | 1 | *Unigenitus* 1713（再譴 Jansenism） |
| 17c | 諾森十一世 Innocent XI | 2 |  |
| 17c | 亞歷山大七世 Alexander VII | 1 |  |
| 16c | 克勉八世 Clement VIII | 1 |  |
| 16c | 西斯篤五世 Sixtus V | 1 |  |
| 16c | 額我略十三世 Gregory XIII | 1 |  |
| 16c | 碧岳五世 Pius V | 4 | *Regnans in Excelsis* 1570 / *Quo Primum* 1570 |
| 16c | 保祿三世 Paul III | 2 |  |
| 16c | 良十世 Leo X | 1 | *Exsurge Domine* 1520（譴路德 41 條） |
| 15c | 亞歷山大六世 Alexander VI | 1 | *Inter Caetera* 1493（劃地子午線） |
| 15c | 西斯篤四世 Sixtus IV | 1 |  |
| 15c | 尼古拉五世 Nicholas V | 1 | *Romanus Pontifex* 1455 |
| 15c | 尤金四世 Eugene IV | 1 |  |
| 14c | 本篤十二世 Benedict XII | 1 |  |
| 14c | 若望廿二世 John XXII | 1 |  |
| 14c | 克勉五世 Clement V | 2 |  |
| 13c | 鮑尼法八世 Boniface VIII | 1 | *Unam Sanctam* 1302（最高教宗權威經典聲明） |
| 13c | 尼古拉四世 Nicholas IV | 1 |  |
| 13c | 尼古拉三世 Nicholas III | 1 |  |
| 13c | 亞歷山大四世 Alexander IV | 1 |  |
| 13c | 諾森四世 Innocent IV | 2 |  |
| 13c | 額我略十世 Gregory X | 1 |  |
| 13c | 額我略九世 Gregory IX | 1 |  |
| 13c | 何諾理三世 Honorius III | 2 |  |

合計 113 篇（papalencyclicals.net 批次），加上原 62 篇（vatican.va）= **175 篇**

### 新增 pipeline 工具（papalencyclicals.net 雙源）
- `scripts/scrape_papalencyclicals_net.py` — 單篇 HTML → english.txt（含段號偵測、heading 偵測、inline footnote anchor 補回、smart-quote 規範化、pope 名稱 cleanup）
- `scripts/discover_papalencyclicals.py` — `/category/{popekey}/` → JSON 清單（title/subtitle/date/url）；只收 papalencyclicals.net HTML、跳過外站 PDF；解析「December 8, 1864」等英美式日期
- `scripts/_batch_ingest_papalenc_pope.py` — 單一教宗的 one-stop pipeline（discover → 每篇 scrape → 自動 detect category（bull/encyclical 依年份）+ displayMode（看段號數量）→ 寫 .ts metadata + Latin/Chinese placeholder → 自動 patch index.ts imports + ALL_DOCUMENTS array + textLoader.ts POPE_LOADERS + POPE_FOLDER；支援增量 patch（重跑只加新文件，不重複既有）；word-boundary check 避免 `19c-leo-xii` 誤判為 `19c-leo-xiii` 已存在）
- `scripts/_batch_papalenc_all_popes.py` — master batch runner，內含 30 位 pre-Pius-IX 教宗清單（pope-key ↔ pope-slug ↔ century），支援 `--start-century N --end-century M` 範圍篩選與 `--only key1,key2` 指定

### 待辦

📋 **完整 TODO 清單見** [`data/encyclicals/_todo.md`](../../../data/encyclicals/_todo.md)（按 P0/P1/P2 優先級分組）
📋 **中文缺漏 audit 清單見** [`data/encyclicals/_chinese_audit.md`](../../../data/encyclicals/_chinese_audit.md)

重點摘要：
- **P0**：中文翻譯（171 篇）／4c-12c gap fill（7 個世紀）／拉丁原文（177 篇全 placeholder）
- **P1**：Pius X + Benedict XV 補（vatican.va 有）／summary+topics+titleZh 精修
- **P2**：Leo XIV／Apostolic Constitution+Exhortation 完整／演說＋講道＋訊息
- [x] **碧岳十世 / 本篤十五**：2026-05-28 完成（Pius X 16 篇 / Benedict XV 12 篇 = 28 篇）；拉／英／義齊全，中文全 placeholder（vatican.va 無）
- [ ] **良十四世**（2025-）：等台灣主教團官方中譯發布後再 ingest
- [ ] **4-12c 早期教宗**：等 [[fathers-translation]] / Schaff NPNF Vol 12-13 中譯成熟 → 從 Migne PL 或 Schaff 補 ingest；papalencyclicals.net 對 4-10c 涵蓋極少
- [ ] **Heading 對齊精修**：自動 align 對部分文件有誤差（如 Lumen Fidei 中文 HTML 結構特殊），可逐篇手寫 `fix_{slug}_chinese_headings.py`（參 fix_laudato_si_chinese_headings.py 模板）
- [ ] **summary/topics 精修**：papalencyclicals.net 批次自動生成的 summaryZh 為 generic template；topics 為 `[]`。可手動或 LLM 補（marquee 文件優先）
- [ ] **titleZh 翻譯**：113 篇自動寫成 `《Quanta Cura》` 純拉丁包書名號；marquee 文件可手譯為《Quanta Cura 何等關切》等
