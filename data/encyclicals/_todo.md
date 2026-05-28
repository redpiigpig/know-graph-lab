# 教宗訓導文獻 — 待辦清單

> 最後更新：2026-05-28（晚）
> 目前狀態：**205 篇 / 41 位教宗**（4c-21c）；popes-catalog 227 位（4c Damasus I 起，pre-Damasus 已刪除）
> 中文翻譯狀態見 [_chinese_audit.md](_chinese_audit.md)
>
> 2026-05-28 晚補：Pius X 16 篇 + Benedict XV 12 篇 = 28 篇（vatican.va 拉/英/義齊全，中文全 placeholder）

---

## 🔴 P0 — 重大缺漏（需排程做）

### 1. 中文翻譯補齊（171 篇 missing + partial）

完整清單見 [_chinese_audit.md](_chinese_audit.md)，按世紀 + 教宗分組。

| 來源 | 涵蓋範圍 | 預期收益 |
|---|---|---|
| 光啟《公教會之信仰與倫理教義選集》(Denzinger 中譯) ebook_id `568726d3-967e-457a-ab69-7452b21d606f` | 15 篇 marquee（Unam Sanctam / Ineffabilis Deus / Quanta Cura / Syllabus / Exsurge Domine / Humani Generis 等可按 DH 番號對位） | 高 — 教義性 marquee 文件 |
| 紙本《天主教大公會議文獻彙編》（user 預計轉錄） | 大公會議產出 + 周邊教宗訓導 | 高 — user 已表示之後會轉錄 |
| catholic.org.tw / catholic.org.hk scrape | 近現代 vatican.va 沒中文的 39 篇 | 中 — 須驗證可用性 |
| Gemini Flash 批次英→繁中（**最後手段**） | 無紙本可對的 113 篇 papalencyclicals.net 文件 | 低 — 機翻品質，需標註 |

**動作項**：
- [ ] user 把《天主教大公會議文獻彙編》OCR 轉錄完成後，按 audit 清單 marquee 15 篇優先套入 Denzinger DH 對位
- [ ] catholic.org.tw 寫 scraper（之後）
- [ ] 對無紙本對應的文件，最後再考慮 Gemini 機翻 + 明確標註

### 2. 4c-12c gap fill（7 個世紀無/少文件）

papalencyclicals.net 對 4-12c 完全無覆蓋。目前僅補了 2 篇 marquee：
- ✅ 5c 良一世 *Tome of Leo* 449（CCEL Schaff Vol 12）
- ✅ 11c 額我略七世 *Dictatus Papae* 1075（Wikisource）

**缺漏 marquee 文件清單**（按時序）：

| 世紀 | 教宗 | 文件 | 拉丁原文 | 英譯 |
|---|---|---|---|---|
| 4c | 達瑪穌一世 | *Tomus Damasi* 382（信經 + canon list） | Migne PL 13.347 | Schaff NPNF2 Vol 14 |
| 4c | 達瑪穌一世 | 致 Jerome 委託 Vulgate 翻譯諸信 | Migne PL 13 | Schaff |
| 4c | 西利修 | *Directa* 385（★ 首封正式 Decretal） | Migne PL 13.1131 | Schaff NPNF2 Vol 9 |
| 5c | 諾森一世 | 致 Exuperius 405、反 Pelagianism 諸信 | Migne PL 20 | Schaff |
| 5c | 切萊斯定一世 | 致 Cyril 諸信（反 Nestorius） | Migne PL 50 | Schaff |
| 5c | 良一世 | 173 封書信精選（除 Tome 之外） | Migne PL 54 | **CCEL Schaff NPNF2 Vol 12**（80+ 篇可挖） |
| 5c | 良一世 | 96 篇 sermon 精選 | Migne PL 54.137-468 | CCEL Schaff NPNF2 Vol 12 |
| 5c | 革拉修一世 | *Famuli vestrae pietatis* 494（兩權說） | PL 59.41-47 | 學界譯本 |
| 6c | 何彌斯達 | *Libellus Hormisdae* 515（東西合一公式） | PL 63 | Schaff |
| 6c | 額我略一世（大額我略） | *Regulae Pastoralis* 591（牧靈書） | PL 77 | **CCEL Schaff NPNF2 Vol 12**（全文 70+ 章） |
| 6c | 額我略一世 | *Moralia in Iob*（伯職論） | PL 75-76 | CCEL Library of Fathers 譯本 |
| 6c | 額我略一世 | 致 Augustine of Canterbury 諸信 | PL 77 | CCEL Schaff NPNF2 Vol 12 |
| 7c | 何諾理一世 | 致 Sergius 諸信（→ 後遭 681 譴責） | PL 80 | Hefele 翻譯 |
| 7c | 馬丁一世 | 拉特朗 649 譴 Monothelitism | PL 87 | Schaff |
| 8c | 哈德良一世 | 致 Charlemagne 諸信 | PL 96 | — |
| 9c | 尼閣一世 | *Responsa ad consulta Bulgarorum* 866（對保加利亞 106 問答） | PL 119 | Migne 學界譯本 |
| 9c | 良三世 | 為查理曼加冕 800 之相關書信 | PL 102 | — |
| 11-12c | 良九世 | 1054 與 Michael Cerularius 互擲絕罰 諸信 | PL 143 | Migne |
| 11c | 烏爾班二世 | 1095 Clermont 號召十字軍 演說 | RHC | Wikisource |
| 12c | Alexander III | 封聖權集中改革諸信 | PL 200 | — |

**動作項**：
- [ ] **5c 良一世**：跑 CCEL Schaff Vol 12 完整 letters/sermons scrape — 80+ 篇 letter + 96 sermon。需寫 CCEL scraper（HTML 結構不同於 papalencyclicals.net）
- [ ] **6c 額我略一世**：Pastoral Rule 全文 + Selected Epistles，CCEL 同 Vol 12 拉下半部
- [ ] **4c-12c 其他**：個案處理（Wikisource、Schaff Vol 9/14、Migne PL OCR）

### 3. 拉丁原文補齊（177 篇都缺 / 全 placeholder）

| 來源 | 涵蓋 |
|---|---|
| vatican.va `/la/` | 19c-21c 大多有 — 既有 scrape pipeline 可重跑 |
| documentacatholicaomnia.eu (DCO) Acta Sanctae Sedis | 全 |
| Migne PL（217 vols）archive.org | 4c-12c |
| Bullarium Romanum（1733-58 編）archive.org | 中世紀-巴洛克教廷詔書集 |

**動作項**：
- [ ] 19c-21c：重跑既有 vatican.va `scrape_papal_encyclical.py` 的 `--langs la` 部分（已被 papalenc 批次蓋過）
- [ ] 13c-18c：DCO 大型 PDF 拉下後切篇對位（複雜）— 或 Wikisource Latin 版逐篇
- [ ] 4c-12c：Migne PL OCR（Gemini Vision）

---

## 🟡 P1 — 補完整性（影響 UI 觀感）

### 4. ~~Pius X / Benedict XV（20c 早期）~~ ✅ 2026-05-28 完成

- Pius X 1903-14：**16 篇** encyclical（vatican.va 列表為 16，非原估 8）
- Benedict XV 1914-22：**12 篇** encyclical

合計 28 篇，拉/英/義齊全。**中文全 placeholder** — 確認 vatican.va 對碧岳十世/本篤十五世無中譯，需走紙本／catholic.org.tw 後補。

Marquee：
- Pius X *Pascendi Dominici Gregis* 1907（反現代主義雙峰文件，與《Lamentabili Sane》並列）
- Benedict XV *Pacem Dei Munus Pulcherrimum* 1920（戰後和平整體框架，*Pacem in Terris* 1963 歷史源頭）
- Benedict XV *Spiritus Paraclitus* 1920（聖經學三大通諭之一，承《Providentissimus Deus》1893 / 預《Divino Afflante Spiritu》1943）
- Pius X *Acerbo Nimis* 1905（推動 1908 碧岳十世要理書編纂）
- Benedict XV *In Praeclara Summorum* 1921（首道以俗世詩人但丁為主題的通諭）

### 5. summary / topics 精修（papalencyclicals.net 批次 113 篇）

目前 113 篇 `summaryZh` 都是 generic 模板：
> 教宗XXX於 YYYY-MM-DD 頒布的通諭（LatinTitle, English subtitle）。

**動作項**：
- [ ] marquee 文件（Pius IX 4 篇 / Leo X *Exsurge Domine* / Boniface VIII *Unam Sanctam* / Pius V 諸詔 / Benedict XIV 諸通諭等）手寫 2-3 段精修 summaryZh，類似 *Rerum Novarum* / *Laudato Si'* 既有風格
- [ ] topics 補上學科分類（避免 `[]` 空）

### 6. titleZh 中譯精修

目前 113 篇 `titleZh` 都是純拉丁包書名號（`《Quanta Cura》`）。

**動作項**：
- [ ] marquee 文件手譯（範例）：
  - `《Quanta Cura》何等關切` — 1864 反現代主義通諭
  - `《Ineffabilis Deus》不可言喻的天主` — 1854 聖母無染原罪信理
  - `《Syllabus Errorum》當代謬論彙集`
  - `《Exsurge Domine》主，請起來吧` — 譴 Luther 41 條
  - `《Unam Sanctam》唯一神聖（教會）` — 教宗權威經典
  - `《Mirari Vos》使你們驚奇` — 1832 譴自由主義
  - `《Dictatus Papae》教宗權威 27 條`（已做）
  - `《Tome of Leo》大良書信第 28 封——致 Flavianus`（已做）

### 7. Heading 對齊精修

`scripts/align_papal_headings.py` 對部分 vatican.va PDF 結構特殊的文件有誤差：
- *Lumen Fidei* 2013（中文 HTML 結構特殊）— 已知問題

**動作項**：
- [ ] 對誤差大的文件逐篇手寫 `fix_{slug}_chinese_headings.py`（模板：`fix_laudato_si_chinese_headings.py`）

---

## 🟢 P2 — 延伸範圍（之後再說）

### 8. 良十四世（Leo XIV, 2025-）

第一位來自美國的教宗。在位中，等台灣主教團官方中譯發布後再 ingest。

### 9. Apostolic Constitution / Exhortation 補完整

目前主要 ingest encyclical / bull；其他類型涵蓋不齊：
- Apostolic Constitution（信理／法律性最高層級）：如 *Sacrae Disciplinae Leges* 1983（CIC 頒布）、*Pastor Bonus* 1988（curia 重組）、*Praedicate Evangelium* 2022（方濟各 curia 改革）
- Apostolic Exhortation：方濟各 *Amoris Laetitia* 2016、*Christus Vivit* 2019、*Querida Amazonia* 2020 等
- Motu Proprio：方濟各 *Traditionis Custodes* 2021 等

### 10. 演說 / 講道 / 訊息

vatican.va `/speeches/`、`/homilies/`、`/messages/` — 數千份。範圍極大，多數非 core 訓導。決定：先不批次收，只在 marquee 場合（如 Pius XII 1956 醫學倫理演說）個案 ingest。

---

## 📁 工具狀態

### 已有的 pipeline
- `scripts/scrape_papal_encyclical.py` — vatican.va HTML/PDF 通用，la/it/en/zh_tw 四語
- `scripts/postprocess_papal_chinese_pdf.py` — vatican.va 中文 PDF → marker text
- `scripts/align_papal_headings.py` — EN spine 對齊 la/it/zh headings
- `scripts/ingest_papal_encyclical.py` — vatican.va one-stop pipeline
- `scripts/_batch_papal_ingest.py` — vatican.va 教宗等級批次（gitignored）
- `scripts/scrape_papalencyclicals_net.py` — papalencyclicals.net 單篇英文 HTML
- `scripts/discover_papalencyclicals.py` — papalencyclicals.net category page → JSON list
- `scripts/_batch_ingest_papalenc_pope.py` — papalencyclicals.net 單一教宗 one-stop（gitignored）
- `scripts/_batch_papalenc_all_popes.py` — papalencyclicals.net master batch（gitignored）

### 需要新建
- [ ] **CCEL Schaff NPNF scraper** — 給 5c 良一世 + 6c 額我略一世 批次拉 letter/sermon/pastoral rule
- [ ] **Wikisource Latin/English scraper** — 給 4c-12c 中世紀詔書（Wikisource 對部分中世紀文件有原始版本）
- [ ] **Migne PL OCR pipeline**（Gemini Vision）— 給沒有現成數位版本的 4-12c 原典
- [ ] **catholic.org.tw scraper** — 給中文補譯
- [ ] **Denzinger DH 對位工具** — 將光啟 Denzinger 中譯按 DH 番號自動套入對應教宗訓導文件
