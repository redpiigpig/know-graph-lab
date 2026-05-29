# Papal Magisterium — 4c-21c 全教宗覆蓋審計

> 產出時間：2026-05-29
> 範圍：A 區 teaching 文件，排除 hsscol-pXXX (C 區) 與 the-holy-see-* (B 區)

## 總覽

| 指標 | 數值 |
|---|---|
| 教宗總數（4c-21c） | 228 |
| 已涵蓋（≥ 1 doc） | 57（25.1%） |
| A 區 doc 總數 | 288 |

## 按世紀統計

| 世紀 | 教宗數 | 已涵蓋 | docs | 缺漏教宗 |
|---|---|---|---|---|
| 4c | 3 | **0**（0%） | 0 | Damasus I★ / Siricius★（首封 decretal） / Anastasius I |
| 5c | 11 | 2（18%） | 16 | Innocent I★ / Sixtus III★ / Hilary / Simplicius / Felix III / Anastasius II / Zosimus / Boniface I / Celestine I★ |
| 6c | 14 | 1（7%） | 10 | Hormisdas★★（515 東西合一公式） / John III / Pelagius I / Vigilius / Boniface II 等 13 位 |
| 7c | 20 | **0**（0%） | 0 | Honorius I★（Monothelitism 危機） / Martin I★（拉特朗 649 殉道） / 其他 18 位 |
| 8c | 11 | **0**（0%） | 0 | Hadrian I★（致 Charlemagne） / Stephen II（Pippin Donation） / Zachary / Gregory III 等 |
| 9c | 21 | **0**（0%） | 0 | Nicholas I★★★（866 對保加利亞 106 問答 / Photian Schism） / Leo III★（800 加冕查理曼） / John VIII 等 |
| 10c | 22 | **0**（0%） | 0 | Sylvester II（999-1003）+ Saeculum Obscurum 黑暗世紀諸教宗 |
| 11c | 17 | 1（6%） | 1 | Leo IX★（1054 東西分裂）/ Urban II★★★（1095 Clermont 號召十字軍） / Alexander II 等 |
| 12c | 16 | **0**（0%） | 0 | Alexander III★（封聖權集中改革）/ Innocent II★ / Lucius III 等 |
| 13c | 18 | 9（50%） | 18 | 缺 Celestine V / Honorius IV / Martin IV / John XXI 等 |
| 14c | 10 | 3（30%） | 4 | 缺 Gregory XI★（1377 回羅馬）/ Urban V / Innocent VI / Clement VI 等 |
| 15c | 11 | 6（55%） | 6 | 缺 Martin V★（1417 終結 Western Schism）/ Paul II / Callixtus III 等 |
| 16c | 17 | 9（53%） | 15 | 缺 Hadrian VI / Clement VII★（Sack of Rome） / Paul IV★ / 其他 5 位 |
| 17c | 11 | 5（45%） | 6 | 缺 Urban VIII★★★（Galileo 1633）/ Paul V★ / Innocent X / Clement IX/X / Alexander VIII 等 |
| 18c | 8 | 6（75%） | 29 | 缺 Innocent XIII / Benedict XIII |
| 19c | 6 | 6（100%） | 70 | 全覆蓋 |
| 20c | 8 | 7（88%） | 99 | 缺 John Paul I（33 天教宗） |
| 21c | 3 | 2（67%） | 14 | 缺 Leo XIV（2025-，待官方中譯） |

## 重大缺口 priorities

### P0 — 大規模空白世紀

- **4c**：3 位全空（Damasus、Siricius、Anastasius I）
  - Damasus I *Tomus Damasi* 382 / *Confidimus* 376（致 Acholius）
  - Siricius *Directa* 385（★ 首封正式 Decretal）
- **7c-12c** ：~115 教宗，幾乎全空（僅 Gregory VII 1 篇）
- **5c-6c 早期 Christological 期**：Innocent I, Sixtus III, Celestine I, Hormisdas 等

### P1 — Marquee 中世紀文件

- **9c Nicholas I** *Responsa ad consulta Bulgarorum* 866（106 問答，東西關係）
- **11c Urban II** Clermont 1095 演說（號召第一次十字軍）
- **11c Leo IX** 1054 東西分裂相關書信
- **12c Alexander III** 封聖權集中諸 decretal

### P1 — 16-17c 散漏

- 16c Hadrian VI / Clement VII（Sack of Rome 1527 期間）/ Paul IV 散漏
- 17c Urban VIII（1623-1644 / Galileo 1633）★★★
- 17c Paul V（Galileo 第一次審判 1616）

## 資料源策略

### 已耗盡的源
- la.wikisource.org — 4-12c 覆蓋極稀疏
- en.wikisource.org — 4-12c 完全空
- papalencyclicals.net — 4-12c 無
- CCEL Schaff NPNF2 Vol 12 — Leo I + Gregory I 已抽取
- thelatinlibrary.com — 只有 Leo I Lent 1+2

### 可用但未開發
- **archive.org Migne PL volumes** —
  - PL 13 = Damasus + Siricius
  - PL 54 = Leo I（**已下載 to `c:/tmp/pl54/`** 5.4 MB djvu + 120 MB PDF）
  - PL 55 = Hilary + Felix + Simplicius
  - PL 63 = Hormisdas + early 6c
  - PL 75-79 = Gregory I（complete works）
  - PL 88-103 = 7-9c popes
  - PL 119 = Nicholas I（含 Responsa Bulgarorum）
  - PL 144-150 = 11c popes
  - PL 162-166 = 12c popes
  - PL 214-217 = Innocent III complete

- **Gemini Vision OCR** — 已驗證可從 PL 54 PDF 抽 clean Latin（4-7 KB/page，需 1.5s/page sleep）
- **Mansi *Sacrorum Conciliorum Nova Collectio*** — 4-15c 大公會議 + 教宗書信原文 archive.org 全集
- **Schaff NPNF2 Vol 14** — Damasus + Siricius 等 4c 教宗書信

### 下輪 work-plan

1. 從 PL 54 抽 Leo I 其他 ~80 letters + ~70 sermons（用 Gemini Vision 對 PDF 頁範圍批次）
2. 從 PL 75-79 抽 Gregory I Pastoral Rule + Moralia in Iob + Registrum Epistolarum 完整版
3. 從 PL 13 抽 Damasus + Siricius 全部 decretals
4. 從 PL 119 抽 Nicholas I Responsa Bulgarorum 106 問答
5. 對 11c Urban II Clermont 演說：找 Robert the Monk / Fulcher of Chartres / Baldric of Dol 等 4 個版本的中世紀 chronicler 紀錄
