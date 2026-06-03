
> ⚙️ **引擎政策（2026-06-03 更新）**：所有 LLM 工作一律**優先用 NVIDIA（輝達，`https://integrate.api.nvidia.com/v1`，預設文字模型 `deepseek-ai/deepseek-v4-flash`）**，fallback 用 Gemini，**Haiku／Anthropic 全面停用**。下文若提到用 Haiku 翻譯／校對／視覺校對／OCR／清理／下標題，一律改用 NVIDIA（視覺類用 NVIDIA 視覺模型如 `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`）。

# Curia 部會文件資料層 (tier='curia')

> 三區命名（user 2026-05-28 訂正）：
> - **A 區 = 訓導文件**（tier='teaching'）通諭／勸諭／憲令／自動詔書等
> - **B 區 = 部會文件**（tier='curia'）信理部／禮儀部等 dicastery 發行
> - **C 區 = 牧靈文件**（tier='message'）廣播詞／講詞／致函／文告／演說／講道

## 目的
本資料區用於存放教廷部會（dicastery）頒布的文件 — 訓令 / 宣言 / 法令 / 通告 等。
與「教宗訓導」(tier='teaching') 區別在於：
- **頒布者**：dicastery（信理部／禮儀部／聖赦院／教育部 等），而非教宗個人
- **schema**：`PapalDocument.issuer` 欄填部會名（中文），`popeSlug` 仍可填當時教宗用於關聯展示

## 規劃中的資料來源
- archive.hsscol.org.hk 467 項 — **內容層掃描確認：0 個真正的 B 區 curia 文件**（hsscol 主要收教宗本人文件，不是部會發行）
- vatican.va `/roman_curia/` 子站 — 真正的 B 區資料來源（待下輪 ingest）
- vatican.va 各 dicastery 子站（e.g. `/cdf/` for 信理部）

## Status (2026-05-28 第三批 — hsscol 全面 ingest)

### 已完成 (本輪)
- ✅ **hsscol 全 467 P# 索引完成**（`data/encyclicals/_hsscol_index.json`）
- ✅ **hsscol → papal-doc 對位 + 批次 ingest**（registry: `_hsscol_ingested.json`）
  - 第二批：12 篇對位現有 slug 補中文（取代 placeholder + 新對位）
  - 第三批：322 篇新建 `.ts` metadata + 三語檔案（C 區 296 / A 區 marquee 26）
- ✅ **index.ts patch**：+322 imports + ALL_DOCUMENTS entries（vue-tsc 過）
- ✅ **B 區 curia 內容層掃描**（`_hsscol_b_zone_classify.py`）—— 6 candidates 全為 false positive；hsscol 實質沒有 B 區文件
- ✅ **A 區段對齊審計**（`data/encyclicals/_a_zone_alignment.md`）—— 206 篇審計，14 篇段號不齊（5 篇影響 UI）

### 2026-05-28（凌晨）續：Haiku OCR + B 區 vatican + A 區 hotfix

**A 區 hotfix（3 對齊好）**
- ✅ `redemptor-hominis-1979`：EN 拆 13kB 腳註串成 218 footnote-def + 修 `## 10.` heading → LA/EN/ZH 22 全齊
- ✅ `lumen-fidei-2013`：vatican.va 第 5 段缺 `N.` prefix 手補 → 60 全齊
- ⚠️ `redemptoris-missio-1990`：hsscol 譯本僅含 1-40，外部無完整 ZH，接受 partial
- ⚠️ `ecclesia-de-eucharistia-2003`：ZH 用獨立段號編排，結構 mismatch（deferred）

**B 區 vatican.va ingest 2 篇**
- `dignitas-infinita-2024`（信理部宣言，ZH 23kB）
- `iuvenescit-ecclesia-2016`（信理部訓令，ZH PDF 29kB）
- 其他 dicastery 確認 vatican.va ZH 文件極少（CDF 241 中只 2 篇有中文）

**88 hsscol 失敗條目 retry**
- 23 篇 UTF-16-LE 編碼救回（原 discovery 沒嘗試此 encoding）
- 6 篇 pope-by-year fallback
- **65 篇 Claude Haiku 4.5 OCR**（透過 Agent tool `model='haiku'` 並行處理 PDF）
- 8 篇早期 retry 編碼壞檔重 OCR + 5 篇未入庫補進

**slug rename 20 篇 A 區 marquee**（`hsscol-pXXX-YYYY` → kebab-Latin）：
- JP2：familiaris-consortio-1981 / vita-consecrata-1996 / pastores-dabo-vobis-1992 / ordinatio-sacerdotalis-1994 / ad-tuendam-fidem-1998 / fidei-depositum-1992 / ex-corde-ecclesiae-1990 / misericordia-dei-2002 / redemptoris-custos-1989 / reconciliatio-et-paenitentia-1984 等
- Francis：vos-estis-lux-mundi-2019 / patris-corde-2020
- Pius XII：sacra-virginitas-1954 / miranda-prorsus-1957 / cupimus-imprimis-1952 / christus-dominus-1953
- Paul VI：sacram-liturgiam-1964 / pro-comperto-sane-1967 / studia-latinitatis-1964

**經文標註規則**（user 訂正 2026-05-28）：
- 連續節：`*經文*（瑪5:3-7）`
- 同章跳節：`*經文*（瑪5:3, 7）`（半形逗號＋空格）
- 同卷跨章：`*經文*（瑪5:3, 8:4）`
- 跨卷：`*經文*（瑪5:3；弟2:3）`（中文分號 ；）
- 已正規化 47 篇既有 chinese.txt（、→ ,）

**系統總計**：~640+ 篇 papal-doc（vue-tsc 通過）

---

## 🟡 下輪 session — 中世紀（4-12c）⭐ user 標記
**user 2026-05-28：「我之後要開新的 session 做中世紀的」**

既有覆蓋的 4-12c 教宗只有 2 篇 marquee：
- 5c Leo I *Tome of Leo* 449（CCEL Schaff Vol 12）
- 11c Gregory VII *Dictatus Papae* 1075（Wikisource）

**下輪重點教宗 / 文件**：
- **5c Leo I「大良」**（440-461）：96 sermon + 173 letters。CCEL Schaff NPNF2 Vol 12 全文已下載
- **6c Gregory I「大額我略」**（590-604）：*Regulae Pastoralis* 591 / *Moralia in Iob* / 致 Augustine of Canterbury 諸信
- **4c Damasus I + Siricius**：*Tomus Damasi* 382 + *Directa* 385（首封 Decretal）
- **5c Innocent I / Celestine I / Gelasius I**：Pelagius / Nestorius 論辯 + 兩權說
- **6c Hormisdas** *Libellus Hormisdae* 515
- **7c Honorius I / Martin I**：Monothelitism 危機
- **8c Hadrian I**：致 Charlemagne 諸信
- **9c Nicholas I** *Responsa ad consulta Bulgarorum* 866
- **11c Leo IX**（1054 東西分裂諸信）/ **Urban II**（1095 號召十字軍 Clermont 演說）
- **12c Alexander III** / **Innocent III**

**資料源優先順序**：
1. **CCEL Schaff NPNF2 Vol 12-13**（英文最佳；已下載）
2. **Migne PL**（Patrologia Latina）archive.org — 拉丁原文 4c-12c 全集
3. **Wikisource Latin/English** — 中世紀詔書部分
4. **Bullarium Romanum** archive.org
5. 紙本 Denzinger / 《天主教大公會議文獻彙編》— 中文摘錄

**中譯來源**：
- hsscol 對 4-12c 極少（主力近現代）
- [[fathers-translation]] Schaff 翻譯成熟後同步入庫
- [[denzinger-fix]] DH 100-1500 範圍對位
- Gemini batch 翻譯 placeholder 補（最後手段）

**預期工作量**：~30 篇早期教宗 + 上百封 Leo I/Gregory I letter/sermon = 100-200 新 docs

**新 session 啟動 prompt 建議**：
> 「我要做中世紀（4-12c）的教宗訓導文獻入庫。先讀 `data/encyclicals/_CURIA_README.md` 的『下輪中世紀』段、`SKILL.md` 的 Phase 5 規劃、和 `data/encyclicals/_todo.md` 的 4-12c gap 清單，然後從 5c Leo I 開始：寫 CCEL Schaff scraper 抓他的 96 sermon + 173 letter（已下載的 Schaff Vol 12），新建 `5c-leo-i/` 下諸 doc。」

---

### 2026-05-28（傍晚）：ingest 分布（322 篇新建 + 12 篇補入）
- A 區 marquee teaching 新增 26 篇（含 Familiaris Consortio 1981 / Reconciliatio et Paenitentia 1984 / Vita Consecrata 1996 / Ex Corde Ecclesiae 1990 / Pastores Dabo Vobis 1992 / Fidei Depositum 1992 / Ordinatio Sacerdotalis 1994 / Patris Corde 2020 等）
- C 區 牧靈／訊息新增 296 篇（廣播詞 260 / 演說 34 / 自動詔書 6 / 憲令 5 / 勸諭 5 / 通諭 4 / 使徒書信 4 / 詔書 2 / 致函 2）
- B 區 curia：0 篇（hsscol 內容掃描確認無）

### 教宗分布
francis 87 / john-paul-ii 75 / pius-xii 62 / benedict-xvi 47 / paul-vi 45 / pius-xi 6

### 未入庫（88 篇 hsscol index_not_ok + 17 misc）
- 64 PDFs（pdftotext 無法抽出標題；可能 Gemini OCR 救援）
- 23 HTML（無 H1/H2 結構；可能標題在 body 內）
- 14 skip_unknown_tier（無教宗識別）
- 7 skip_leo_xiv（user 指令不收）
- 3 fetch_failed / 3 no_pope_match / 1 pope_folder_missing / 2 exists

### C 區（curia）識別挑戰
hsscol 將部會文件按**主題**（不按部會發行者）歸檔，標題從不出現「信理部訓令」之類字串。要識別 C 區需：
1. 逐篇下載內容 → 抽出版頁／凡例（前 1 頁） → 識別 dicastery 名稱
2. 或借助 vatican.va `/roman_curia/` 對照表（部會名 + 文件清單）逆向 mapping
3. 或人工瀏覽 hsscol 既有非標題類文件並標註

下輪 session 預計：
- 寫 `_hsscol_curia_classify.py` 對 hsscol unknowns 抽出版頁，識別 dicastery
- 同步爬 vatican.va `/roman_curia/` 部會清單，建立 dicastery → 文件對照
- 對識別出的 curia 文件，建立 tier='curia' 文件骨架

### B 區（新 teaching）待 ingest（~25 篇 marquee）
2026-05-28 第二批 hsscol 對位 + 手動 probe 後，識別出以下既有 papal-doc 系統**尚無**的 B-tier marquee（按重要性）：

| 拉丁名 | 中文 | 教宗 | 年份 | hsscol P# |
|---|---|---|---|---|
| Familiaris Consortio | 家庭團體 | JP2 | 1981 | P170 |
| Reconciliatio et Paenitentia | 論和好與懺悔 | JP2 | 1984 | P173 |
| Redemptoris Custos | 救主的監護人 | JP2 | 1989 | P184 |
| Ex Corde Ecclesiae | 天主教大學憲章 | JP2 | 1990 | P252 |
| Pastores Dabo Vobis | 我要給你們牧者 | JP2 | 1992 | P187 |
| Fidei Depositum | 信仰的寶庫 | JP2 | 1992 | P210 |
| Ordinatio Sacerdotalis | 司鐸聖秩 | JP2 | 1994 | P191 |
| Vita Consecrata | 奉獻生活 | JP2 | 1996 | P198 |
| Ad Tuendam Fidem | 為維護信仰 | JP2 | 1998 | P204 |
| Misericordia Dei | 論天主仁慈 | JP2 | 2002 | P214 |
| Sacrum Diaconatus | 六品聖職 | Paul VI | 1967 | P014 |
| Regimini Ecclesiae | 治理教會 | Paul VI | 1967 | P016 |
| Sacrarum Indulgentiarum Recognitio | 修正大赦 | Paul VI | 1967 | P021 |
| Patris Corde | 以父親的心 | Francis | 2020 | P484 |
| ... | ... | ... | ... | ... |

完整清單見 `_hsscol_mapping.md` 的 teaching 區塊（43 entries / 10 已對位 / 33 待新建）

### 第二批已 ingest 的 12 篇 hsscol 對位（既有 slug 補中文 / 取代 placeholder）
- ★ centesimus-annus-1991（OCCD PDF 抽不出 → hsscol html 取代 placeholder 成功）
- casti-connubii-1930 / divini-redemptoris-1937 / mysterium-fidei-1965 /
  slavorum-apostoli-1985 / dominum-et-vivificantem-1986 / mater-et-magistra-1961 /
  laborem-exercens-1981 / ut-unum-sint-1995 / maximum-illud-1919（取代 placeholder） /
  ecclesiam-suam-1964 / dives-in-misericordia-1980

## 規劃資料夾結構
```
data/encyclicals/curia/
  cdf/                              — 信理部 (Dicastery for the Doctrine of the Faith)
    fiducia-supplicans-2023.ts
    fiducia-supplicans-2023-{chinese,english,latin}.txt
    ...
  liturgy/                          — 禮儀及聖事部
    ...
  apostolic-penitentiary/           — 宗座聖赦院
    ...
```

或維持現有按教宗子資料夾，靠 `tier='curia'` + `issuer` 欄分流（簡單路徑）。
最終決定下輪 session 再定。
