# 創生哲學‧每卷參考資料庫 — 接手交接文件（genesis reference DB）

> 給新 session：把這份讀完就能接著做，不用重推架構。本檔是**唯一真相**；架構細節另見本 skill SKILL.md「創生哲學叢書：每卷參考資料庫」段。記憶 [[project_genesis_reference_db]]。

## 目標
為 **創生哲學叢書 15 卷**（`/works/genesis-philosophy`，單一叢書專案）**每一卷**建一份「最新研究參考資料庫（研究回顧）」，依 **四領域：自然科學／心理學／哲學／宗教與神話**，供使用者**依此改寫每一卷**。DB-backed（lit_review_entries，`book_id` 逐卷 scope），書閱讀器 `/works/genesis-philosophy/book/<BID>` 有「研究回顧」分頁。

## 選書政策（使用者 2026-06-24 指定，務必遵守）
1. **優先經典／得獎／公認／教科書級**研究。
2. 前沿研究**只納公認里程碑**（例 Cogitate 2025 Nature 對抗式合作、Butlin et al. 2023 AI 意識評估報告）。
3. **避免未證實或爭議過大**者（已剔：IIT 偽科學公開信、academia.edu working paper、小型期刊 Levinas 篇）。
4. **每卷都要有中文（華語學界）研究**：英文一輪 + 中文一輪。
5. 卷內**跨領域同 ref_key 只留一筆**（去重，如 Foucault 異托邦曾同時出現在哲學與宗教）；**作者／出處不確定的條目寧缺**。
6. 中譯一律繁體（[[feedback_traditional_chinese_only]]）。

## 進度（2026-06-24 晚更新）
| 卷 | 章 | 英文 | 中文 | 狀態 |
|---|---|---|---|---|
| M1 愛的萬物論 | 7 | 37 | ✅ 6 | report `lit_review_genesis_M1.md` + `_zh` |
| M2 虛構的烏托邦 | 13 | 39 | ✅ 11 | `..._M2.md` + `_zh` |
| M3 人子 | 9 | 39 | ✅ 9 | `..._M3.md` + `_zh` |
| E1 本質的幽靈 | 8 | 31 | ✅ 8 | `..._E1.md` + `_zh` |
| E2 意向性與生成的邏輯 | 10 | 29 | ✅ 10 | `..._E2.md` + `_zh` |
| E3 他心、感質與AI | 6 | 31 | ✅ 9 | `..._E3.md` + `_zh` |
| O1 創生公式 | 8 | ✅ 36 | ✅ 8 | `..._O1.md` + `_zh` |
| O2 量子本體論 | 6 | ✅ 37 | ✅ 7 | `..._O2.md` + `_zh` |
| O3 主體的生成 | 7 | ✅ 37 | ✅ 8 | `..._O3.md` + `_zh` |
| V1 願然 | 6 | ✅ 37 | ✅ 8 | `..._V1.md` + `_zh` |
| V2 意義、愛與神聖 | 6 | ✅ 35 | ✅ 6 | `..._V2.md` + `_zh` |
| V3 世界理論 | 5 | ✅ 38 | ✅ 8 | `..._V3.md` + `_zh`（新卷，內容多為代擬） |
| B1 空無與創生前態 | 7 | ⛔ | ⛔ | **未做（下一步）** |
| B2 默然與不可言說 | 6 | ⛔ | ⛔ | 未做（在場世界論已移 V3） |
| B3 神聖、虛無與終極存在 | 7 | ⛔ | ⛔ | 未做 |

**累計約 584 筆 / 12 卷英文完成（M/E/O/V 四系列含中文）。只剩存有論三部曲 B1/B2/B3。**

## 剩餘工作
- **B1/B2/B3 共 3 卷**：每卷英文一輪（4 領域代理）＋中文一輪（1 代理覆蓋四領域），compose → ingest（英文無 offset、中文 `--display-offset 100`）。各卷章節與領域角度見下方「各卷章節」段（已含 B1/B2/B3）。
- B 系列領域提示重點：B1=空無/真空物理/海德格無/佛教空/creatio ex nihilo；B2=哥德爾不完備/維根斯坦不可說/維摩一默/否定神學語言；B3=宇宙終末熱寂/死亡哲學/恐懼管理/空無神學田立克/末世論。
- ⚠️ 卷內跨領域 ref_key 去重（B3 與 V2 神聖/虛無、B1 與 O1 海德格/空性 會跨卷重覆＝允許，只去**卷內**重覆）。

## 每卷標準流程（照做）
```bash
# 1) 英文：開 4 個 general-purpose agent（一領域一個），各回 ~10 筆真實近期/經典文獻（DOI/URL 驗證）
#    → 組成 scripts/data/lit_review_genesis_<BID>.md（## 自然科學 / ## 心理學 / ## 哲學 / ## 宗教與神話 四標頭）
python -X utf8 scripts/ingest_lit_review.py --seed --entries-only --book-id <BID> \
    --project genesis-philosophy --report scripts/data/lit_review_genesis_<BID>.md

# 2) 中文：開 1 個中文代理（覆蓋四領域）→ scripts/data/lit_review_genesis_<BID>_zh.md（同四標頭，只填有的）
python -X utf8 scripts/ingest_lit_review.py --seed --entries-only --book-id <BID> --display-offset 100 \
    --project genesis-philosophy --report scripts/data/lit_review_genesis_<BID>_zh.md

# 3) commit + push（pre-push 會跑 vitest，務必綠）；reader 在 /works/genesis-philosophy/book/<BID>「研究回顧」分頁
```
- **報告格式**：每筆 `【作者】（年）〈題〉，《刊/出版社》` + 四行 `語言：`／`所屬面向：<該卷章節名>`／`立場：支持|補充|反例`／`摘要：（繁中2-3句，關鍵發現+與本卷關聯）` + `> **全文**：[標籤](url)`。`所屬面向` 填**該卷章節**（reader 顯示為章節徽章）。
- **dry-parse 檢查**（入庫前）：`python -X utf8 -c "import sys;sys.path.insert(0,'scripts');import lit_review as lr;from collections import Counter;p=lr.parse_review_report(open('scripts/data/lit_review_genesis_<BID>.md',encoding='utf-8').read());e=p['entries'];print(len(e),dict(Counter(x['theme'] for x in e)),[k for k,c in Counter(x['ref_key'] for x in e).items() if c>1])"` — 確認筆數、四領域、**DUP=[]**。
- 中文文獻 `語言：中文` → ingest 自動標 `unavailable`（書目層，不抓全文），正常。

## 英文 4 領域代理 prompt 範本（替換 <…>）
> 你是替中文原創哲學叢書「創生哲學」建立參考資料庫的學術館員。這一卷是 **<BID 書名與副題>**（<系列>卷）。各章：<章節清單>。核心：<一句主旨>。
> 你的領域：**<自然科學/心理學/哲學/宗教與神話 其一>**。用 WebSearch/WebFetch 找 ~10 筆**真實、經典/得獎/公認/教科書級**（前沿只取公認里程碑）文獻，與本卷最相關。每筆**恰好**回傳：
> `【First-author Surname, Initials et al.】（YYYY）〈Title〉，《Journal/Publisher》` + `語言：英文` + `所屬面向：<本卷某章>` + `立場：支持/補充/反例` + `摘要：（繁體中文2-3句，關鍵發現+與本卷關聯）` + `> **全文**：[label](real-url-or-doi)`。優先 OA/DOI，權威 venue/SEP。只回 ~10 區塊。

中文代理 prompt：同上但「找 8–10 筆**中文（繁體優先）經典/公認/教科書級**華語學界文獻」，連結用華藝 Airiti／期刊官網／CBETA／臺大佛學數位圖書館／華文哲學百科／出版社頁，核實作者年份刊名。

## 各卷章節（寫 prompt 用）
- **M1 愛的萬物論**（倫理）：為何需要主體性倫理學／主體的誕生／召喚的結構／倫理陰影與補償／誠實作為萬德之綱與倫理的數學化／愛的公式／死亡倫理
- **M2 虛構的烏托邦**（倫理）：個人誠實度hi→社會平均誠實度H與意義／倫理能見度與可居性／暴政的解剖／民主的誠實度門檻／社會的起源與原始的倫理／宗教倫理與起源異托邦／政體的倫理史／極權政治與轉型正義／異化現代性與公共性／職業倫理場／人權批判與全球主體倫理憲章／制度性無政府主義與裂口異托邦
- **M3 人子**（倫理）：倫理的外推／日擇原理／性善的宇宙演化根基／生命倫理／動物倫理／環境與生態倫理／星球與宇宙倫理／AI倫理／熱寂與永續共生圈
- **O1 創生公式：生成的本體論**（本體論）：導論本體論作為生成的學問／生成三要素（關係性身體性歷時性）／創生公式（條件閾值自我循環）／存在的三態（創生前態態殘態）／創生剃刀／本體論=認識論／存在的譜系／結語（從存在者到世界生成、預告卷二）。領域角度：自然科學=複雜系統/突現/自我組織/耗散結構；心理學=自我與能動性的生成、發展；哲學=過程哲學(Whitehead)、生成vs存在、本體論基礎、新實在論；宗教神話=緣起/生成的宗教宇宙論、道家化生、創世論。
- **O2 觀察即創生：量子本體論**（本體論）：導論為何量子是本體論問題／坍縮即創生（觀察波函數共構）／退相干與巨觀世界穩定生成／量子邏輯與古典邏輯／反柏拉圖理型論：疊加態才是實在／結語生成的宇宙與待解的主體。領域：自然科學=量子測量問題/退相干/量子資訊/QBism/真空能/MEPP（注意 O2 原宇宙論結語已併入 M3，仍可收量子基礎研究）；心理學=觀察者效應的心理誤解、量子認知(quantum cognition)；哲學=量子力學詮釋哲學(哥本哈根/多世界/關係性RQM/QBism)、measurement problem；宗教神話=觀察/意識與實在的宗教觀、佛教唯識與量子的對話（謹慎、避免偽科學）。
- **O3 主體的生成：意識與自我的本體論**（本體論）：導論主體作為本體論問題／意識作為複合創生態／自指漩渦：主體性如何從關係性湧現／自我同一性（意向性身體歷時）／主體作為超限存在者／AI主體性的本體生成／結語神人互構與主體的創生。領域：自然科學=意識的神經科學/自我的神經基礎/自指與遞迴/IIT-GWT；心理學=自我的發展與構成、敘事自我、minimal self；哲學=人格同一性(personal identity)、自我的形上學、湧現emergence、Strawson/Zahavi/Dennett；宗教神話=無我anatta/阿特曼、神人互構、靈魂論。
- **V1 願然：意欲、秩序與美**（價值論）：導論價值論作為願然之學／願然與慾望：意欲的純化／願然的四象限與熵的宇宙方向性／美的共振生成論／美的相對客觀性與文化主觀性／真善美聖的四向度階層。領域：自然科學=情緒/動機/獎賞的神經科學、美感的神經美學neuroaesthetics、熵與秩序；心理學=慾望與意志、self-regulation、美感心理學、flow；哲學=意志哲學(Schopenhauer/Frankfurt willing)、美學(Kant/Dewey)、價值論axiology；宗教神話=慾望與解脫（佛教）、美與神聖、秩序宇宙觀。
- **V2 意義、愛與神聖**（價值論）：意義的困難問題／虛無主義的價值論診斷／愛作為願然的最高運動／神聖性與空無美學／主體作為最高價值／結語願然與第二軸心時代。領域：自然科學=意義感/目的感的心理生理、愛與依附的神經科學、宗教經驗神經科學neurotheology；心理學=meaning in life(Steger/Frankl)、虛無/疏離、愛的心理學、self-transcendence；哲學=虛無主義(Nietzsche)、意義哲學、愛的哲學、神聖(Otto聖秘)、軸心時代(Jaspers)；宗教神話=神聖the sacred(Eliade/Otto)、agape、空與神聖、第二軸心時代論。
- **V3 世界理論**（價值論，新卷）：在場世界論（潛生界意想界存在界）／心為工畫師：唯識心理學與世界生成／藝術與文學作為世界創造／科幻電影動畫：意想界的工程學／結語世界理論在價值論中的位置。領域：自然科學=知覺即建構/predictive processing、虛擬實境VR認知、世界模型world models(AI)；心理學=想像/心像、唯識與認知、夢、敘事與世界建構、沉浸immersion；哲學=可能世界、虛構實在論fictionalism、世界構造(Goodman)、現象學世界(Husserl/Heidegger)；宗教神話=心為工畫師（華嚴/唯識）、創世神話、宇宙論worldmaking、次創造(Tolkien)。
- **B1 空無與創生前態：存有的邊界**（存有論）：導論存有論作為默然之學／空無的本體地位／創生前態：存在的第三態／存有者的分類學／超限存在者與不可通約的臨在／創生剃刀／結語存有的邊界地形學。領域：自然科學=真空/虛無的物理(量子真空/零點能)、無與有的宇宙起源、數學的零與無限；心理學=空無經驗/虛空感、留白與潛在；哲學=無Nothingness(Heidegger/Sartre)、非存在nonexistence、形上學的虛無、Meinong對象論；宗教神話=空śūnyatā、無ex nihilo創造、道家無、否定神學。
- **B2 默然與不可言說：語言的邊界**（存有論）：默然向度／語言的自我創生與否定性自指／空無刺透存有：哥德爾縫隙／銜尾蛇：存有的動態自指實在／空無的數學形式化（零無限ת）／結語維摩一默。領域：自然科學=語言的神經基礎與界限、哥德爾與可計算性、自指與遞迴系統；心理學=不可言說經驗ineffability、默會知識tacit knowledge(Polanyi)；哲學=語言哲學界限(Wittgenstein 不可說)、否定性、自指悖論、沉默的哲學；宗教神話=不可言說(apophatic)、維摩一默、禪不立文字、神秘主義語言。
- **B3 神聖、虛無與終極存在**（存有論）：神聖性：空無以神聖方式臨在／空無神學：神是不存在但也是創生的／空無的三一結構與神聖語言／虛無主義的存有論診斷／永恆的不可能與死亡的存有論／宇宙的終末與自我創生／結語神人互構與默然的承擔。領域：自然科學=宇宙終末(熱寂/大撕裂)、永恆與時間的物理、死亡的生物學；心理學=死亡焦慮/terror management、神聖經驗、終極關懷；哲學=死亡哲學、永恆eternity、虛無主義、神聖the holy、否定神學/空無神學；宗教神話=神聖the sacred、空與神、末世論eschatology、死亡與重生神話、神人互構。

## 全文逐段轉錄（背景，OA only）
- 指令：`python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project genesis-philosophy --resume --engine gemini --pace 1`（可加 `--book-id <BID>` 只跑一卷）。log → `c:/tmp/lit_review_genesis_fulltext.log`。
- **只有 OA 抓得到全文**（SEP/IEP/arXiv-pdf/PMC/OA PDF）；付費牆（Nature/Science/Wiley/Annual Reviews）、擋 bot（MDPI）、版權書、中文 → 自動跳過維持書目層。Gemini 429 會降級 NVIDIA→Haiku、2-strike 自動停，再 `--resume` 接續。arXiv 連結要用 `/pdf/` 才抓得到。

## 架構檔（要改才看）
- schema：`database/lit-review-schema.sql`（含 `book_id`）；migration `scripts/apply-lit-review-book-id.mjs`（已套用，冪等）
- 四領域 theme：`scripts/lit_review.py` `GENESIS_THEMES`
- ingest：`scripts/ingest_lit_review.py`（`--book-id`、`--display-offset`、`--entries-only`）
- API：`server/api/lit-review/entries.get.ts`（`bookId` filter）
- reader：`pages/works/[slug]/book/[bid].vue`（「本文／研究回顧」分頁）
- ⚠️ pre-push 跑 vitest；提交只 `git add` 自己的檔。新卷代擬內容尚未回填 C-xxxxx 對話引用。
