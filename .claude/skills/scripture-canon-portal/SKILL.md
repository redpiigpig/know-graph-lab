---
name: scripture-canon-portal
description: 五個基督教經典/傳統對照工具的入口（/scripture 聖經多版本+教父註釋+各教會次經第二正典 / /creeds 21 次大公會議+各教會尼西亞信經+新教信條全譜 / /canon-law 教會法規 / /fathers 教父著作搜索 / /apocrypha 典外文獻搜索）。Status: **設計階段（2026-05-21）**，下一個 session 接手實作。
---

# Scripture, Tradition, Canon, Fathers, Apocrypha Portal

> 🚨 **Status**: 設計階段 2026-05-21。本 skill 是 spec 文件，**尚未實作**。下一個 session 開始 build。
>
> 入口卡片 = home / 工作台多一張「📜 經典對照與註釋」卡片，點進 5 個子頁面。本文檔記錄範圍、方法、已有資料源、外部源頭清單。

---

## 五個子頁面總覽

| 路由 | 名稱 | 性質 | 規模 | 優先 |
|---|---|---|---|---|
| `/creeds` | 信條對照 | 文件式 (yml) | ~50 份信條 | ★★★ 最快 win |
| `/canon-law` | 教會法規查詢 | 文件式 + scrape | ~10 大法典 | ★★ |
| `/fathers` | 教父著作搜索 | DB | ~50 位教父 + 著作 cross-link | ★★ |
| `/apocrypha` | 典外文獻搜索 | DB | ~80 份 doc + 經節 | ★★ |
| `/scripture` | 聖經對照 + 教父逐節註釋 | DB（大）+ LLM mapping | ~31K 節 × N 版本 + ~15K verse-comment | ★★★ 最重 |

## 入口卡片

```
/   工作台
└── 📜 經典對照與註釋  ← 新卡片
      ├── 📖 聖經對照     (/scripture)
      ├── ⛪ 信條對照     (/creeds)
      ├── ⚖️ 教會法規     (/canon-law)
      ├── ✝️ 教父著作搜索 (/fathers)
      └── 📜 典外文獻搜索 (/apocrypha)
```

---

## 1. `/scripture` — 聖經對照 + 教父註釋 + 各教會次經

### 範圍

- 多版本平行對照（中文 / 英文 / 古典語 / 東方教會傳統語）
- IVP ACCS 27 卷教父經注逐節 mapping
- **各教會 OT/NT canon 範圍標記**（user 強調 — 包含次經與第二正典）
- 跨版本 / 跨教父 / 跨時期 全文檢索

### 各教會聖經次經與第二正典 (user 要求覆蓋)

| 教會 | OT 卷數 | NT 卷數 | 獨有書卷 |
|---|---|---|---|
| 新教 | 39 | 27 | 不含次經 / 第二正典 |
| 羅馬天主教 | **46** | 27 | 多 Tobit, Judith, Wisdom, Sirach, Baruch, 1-2 Macc, Esther/Daniel additions = 7 卷 |
| 東正教 | **49+** | 27 | 在天主教基礎 + 1 Esdras, 3 Macc, Prayer of Manasseh, Psalm 151 |
| 衣索匹亞 Tewahedo | **46+** | **27+** | OT 含 Jubilees, 1 Enoch, 4 Baruch; NT 含 Sinodos, Te'ezaza Sanbat — 廣義 81 卷 ★ 最廣 canon |
| 敘利亞 Peshitta | 39 | **22** | NT 不含 2 Pet, 2-3 John, Jude, Revelation |
| 亞美尼亞使徒 | 含天主教次經 | 27 + (3 Cor) | 中世紀加入 Rev；含 3 Cor 假信 |
| 科普特正教 | 同 Coptic Bohairic | 27 | 接近東正教 canon |
| 亞述東方教會 | 同 Peshitta | 22 | 同敘利亞東方傳統 |

### Schema

```sql
bible_books (
  code            -- 'gen' / 'exo' / ... / 'mat' / 'rev' / 'tob' / 'jdt' / 'wis' / 'sir' /
                  -- 'bar' / '1mac' / '2mac' / '1esd' / '3mac' / 'manas' / 'ps151' /
                  -- 'jub' / 'en1' / '4bar' (典外/第二正典)
  name_zh, name_en, name_lat, name_grc, name_heb
  canon_protestant BOOLEAN
  canon_catholic   BOOLEAN
  canon_orthodox   BOOLEAN
  canon_ethiopian  BOOLEAN
  canon_syriac     BOOLEAN
  canon_armenian   BOOLEAN
  canon_coptic     BOOLEAN
  canon_assyrian   BOOLEAN
  testament        -- 'ot' / 'nt' / 'deutero' / 'apocrypha'
  display_order INT
)

bible_versions (
  code             -- 'cuv1919' / 'cuv2010' / 'cnv' / 'sb' / 'lzz' /
                   -- 'niv' / 'esv' / 'nrsv' / 'kjv' / 'vul' / 'sblgnt' / 'wlc' /
                   -- 'pesh' / 'cop_bo' / 'cop_sa' / 'hye' / 'gez' / 'lxx'
  name_zh, name_en
  language         -- zh-Hant / zh-Hans / en / lat / grc / hbo / syr / cop / hye / gez
  type             -- chinese / english / source / ancient
  public_domain    BOOLEAN
  copyright_notice TEXT
  scope            -- 'ot_only' / 'nt_only' / 'full' / 'catholic_only' / ...
  source_url       -- 來源網站
)

bible_verses (
  book_code, chapter INT, verse INT,
  version_code, text TEXT,
  PRIMARY KEY (book_code, chapter, verse, version_code)
)
CREATE INDEX bible_verses_fts ON bible_verses USING GIN (to_tsvector('simple', text));

bible_commentary (
  id UUID PK,
  verse_ref VARCHAR(20)  -- 'gen.1.1' / 'mat.5.3' / 'tob.1.1' (含次經)
  ebook_id UUID FK,       -- 來自哪本書 (IVP ACCS / Schaff NPNF / 個別中譯)
  chunk_index INT,
  father_slug VARCHAR(50) -- 'augustine' / 'origen' / 'chrysostom'
  excerpt TEXT,
  era VARCHAR(20)         -- '教父時期' / '中世紀' / '改教' / '近現代'
  language VARCHAR(20)    -- excerpt 是中譯/英譯/原文
)
CREATE INDEX bible_commentary_verse ON bible_commentary (verse_ref);
```

### 資料源 — 已有 (Drive 上)

- ✓ **IVP ACCS 27 卷** — `世界宗教/基督教/IVP - 古代基督信仰聖經註釋叢書 (27 冊)/` — 教父對 OT/NT 逐節經注，主要源
- ✓ **基督教典外文獻 10 卷** — `世界宗教/基督教/基督教典外文獻 (10 冊)/` — OT 6 + NT 4，**作次經/第二正典中譯來源**
- ✓ **Schaff NPNF 28 卷** — `神學/教父著作/Schaff - NPNF Series 1 (14卷)/`, `Series 2 (14卷)/` — 含教父對聖經逐卷講道（Chrysostom Homilies on John/Matthew/Romans 等）

### 資料源 — 待下載（公版優先）

| 版本 | 語言 | 來源 | 版權 | 備註 |
|---|---|---|---|---|
| 和合本 1919 | zh-Hant | bible.com / digitalbible.io | **✓ 公版** | MVP |
| 和合本 2010 | zh-Hant | 香港聖經公會 | ❌ 版權 | 寫信申請 |
| 新譯本 CNV | zh-Hant | 漢語聖經協會 | ❌ 版權 | 商業 |
| 思高聖經 SB | zh-Hant | 思高聖經學會 | ❌ 版權 | 商業；天主教 |
| 呂振中譯本 LZZ | zh-Hant | bible.com | ✓ 公版 (作者 1970 過世 +50 = 公版) | |
| KJV | en | bible.org / bibleorg.com | **✓ 公版** | MVP |
| NIV | en | Biblica | ❌ 版權 | API only |
| ESV | en | Crossway | ❌ 版權 | |
| NRSV | en | NCC | ❌ 版權 | |
| Vulgate Clementine | lat | drbo.org / vulsearch | **✓ 公版** | MVP |
| SBL Greek NT | grc | sblgnt.com | **✓ CC BY-SA** | MVP |
| Westminster Leningrad | hbo (Hebrew OT) | tanach.us | **✓ 公版** | MVP |
| LXX 七十士譯本 (Greek OT) | grc | septuagint.bible | **✓ 公版** (Rahlfs 1935) | |
| Peshitta Syriac (NT) | syr | peshitta.org / dukhrana.com | **✓ 公版** | user 強調要 |
| Bohairic Coptic NT | cop | copticbible.org | **✓ 公版** | user 強調要 |
| Sahidic Coptic NT | cop-sa | coptic.bible | 部分 ✓ | |
| Armenian Bible | hye | digilibraries / armeniabible.com | **✓ 公版** | user 強調要 |
| Ge'ez 衣索匹亞 | gez | ethiopicbible.com / Senkessar | 部分 ✓ | user 強調要；數位化稀少 |
| Targum 亞蘭 OT | arc | sefaria.org | ✓ | 補充 |

### 教父註釋 mapping 流程

1. 對 IVP ACCS 27 卷每一 chunk，用 LLM (Gemini Flash) 抽取：
   - 經文 ref（"Genesis 1:1" / "創世記 1:1" / "創 1:1"）→ normalize 成 'gen.1.1'
   - 教父名（"Augustine" / "Origen" / "Chrysostom"）→ slug 'augustine' / 'origen'
   - 摘錄正文
2. 寫 `bible_commentary` table
3. 再對 Schaff NPNF Vol 9-14 (Chrysostom 全部 Homilies) + 個別中譯教父 (~25 本) 跑同樣抽取流程
4. 預估 total: ~15K-25K verse-comment rows

### UI 規劃

```
/scripture
  /[book]/[chapter]
    左面板：經文表
      Row 1 │ [v1] 和合本1919 │ KJV │ Vulgate │ SBL Greek │ ⊕
      Row 2 │ [v2] 和合本1919 │ KJV │ ...
    
    右面板：選中節 verse_ref 的教父註釋
      🟦 Augustine 教父時期 │ 〈論真福〉節錄...
      🟦 Origen 教父時期 │ 〈詩篇釋義〉節錄...
      🟧 Aquinas 中世紀 │ 〈神學大全 I,1〉節錄...
      ⊕ 按 era / 教父名 filter
    
    頂工具列：版本 toggle / canon view (各教會 OT/NT 範圍)
  
  /search?q=    GIN full-text 搜尋
  /canon        各教會 OT/NT canon 對照表
```

---

## 2. `/creeds` — 信條對照（21 次大公會議 + 各教會尼西亞 + 新教全譜）

### 範圍

- **21 次大公會議信經 / canons**（天主教定義）
- **各教會尼西亞信經版本**（user 強調 — 包含亞美尼亞 / 科普特 / 亞述 / 衣索匹亞 + 西方含 filioque 版）
- 各時期、各宗派信仰告白
- 各信條的原文 + 英譯 + 中譯三欄對照

### 21 次大公會議（天主教 official list）

| # | 名稱 | 年 | 主議題 | 信經產出 |
|---|---|---|---|---|
| 1 | 第一次尼西亞 | 325 | 亞流主義 | **尼西亞信經 325 原版** |
| 2 | 第一次君士坦丁堡 | 381 | 阿波利那留 / 聖靈論 | **尼西亞-君士坦丁堡信經 381 修訂** |
| 3 | 以弗所 | 431 | 涅斯多留 / 馬利亞 Theotokos | Cyril 12 章 |
| 4 | 迦克墩 | 451 | 一性論／兩性論 | **迦克墩信經 (Chalcedonian Definition)** |
| 5 | 第二次君士坦丁堡 | 553 | 三章案 | |
| 6 | 第三次君士坦丁堡 | 680-81 | 一志論 | |
| 7 | 第二次尼西亞 | 787 | 聖像敬拜 | 聖像敬拜決議 |
| 8 | 第四次君士坦丁堡 | 869-70 | Photios（天主教含、東正教不含 ⚠） | |
| 9 | 第一次拉特朗 | 1123 | 敘任權之爭 | |
| 10 | 第二次拉特朗 | 1139 | 反對教宗派 | |
| 11 | 第三次拉特朗 | 1179 | 教宗選舉法 | |
| 12 | 第四次拉特朗 | 1215 | 變質說 / 第四次十字軍 | |
| 13 | 第一次里昂 | 1245 | 教宗權威 / 神聖羅馬皇帝廢黜 | |
| 14 | 第二次里昂 | 1274 | 短暫東西合一 | |
| 15 | 維埃納 | 1311-12 | 聖殿騎士團 | |
| 16 | 康斯坦茲 | 1414-18 | 西方大分裂結束 | |
| 17 | 巴塞爾-費拉拉-佛羅倫斯 | 1431-45 | 東西合一嘗試 / Filioque | |
| 18 | 第五次拉特朗 | 1512-17 | 教宗 vs 公會議 | |
| 19 | 特倫多 | 1545-63 | 反宗教改革 / 七件聖事 | **Tridentine Profession of Faith** |
| 20 | 第一次梵蒂岡 | 1869-70 | 教宗無誤論 | Dei Filius / Pastor Aeternus |
| 21 | 第二次梵蒂岡 | 1962-65 | 禮儀改革 / 普世合一 | 16 份文件 (LG / DV / GS 等) |

不同教會接受度：
- 東正教：只承認 1-7（前 7 次大公會議）
- 新教：只承認 1-4
- 亞述東方教會（聶斯托利派）：只承認 1-2（拒以弗所 431 譴責聶斯托留）
- 東方東正教（科普特/亞美尼亞/敘利亞/衣索匹亞，反迦克墩派）：只承認 1-3

### 尼西亞信經各教會版本 (user 強調)

需要：
1. **原文希臘 325 版**（First Council of Nicaea 原文）
2. **原文希臘 381 修訂版**（First Council of Constantinople 增聖靈段）
3. **拉丁西方版**（含 filioque「和聖子」加插段 — 800 年加入）
4. **亞美尼亞使徒教會版**（Armenian Apostolic — 用古典亞美尼亞文 grabar）
5. **科普特正教版**（Coptic Orthodox — 用 Bohairic Coptic）
6. **亞述東方教會版**（Assyrian Church of the East — 用敘利亞文，東敘利亞傳統）
7. **衣索匹亞 Tewahedo 版**（Geez 古典衣索匹亞文）
8. **敘利亞東方版** (Syriac Orthodox — 西敘利亞傳統)
9. **中譯多版本**：思高（天主教）/ 聖經公會（信義）/ 改革宗中譯 / 東正教中華主教區譯本 / 浸信會譯本

### 新教信條 widening (user 強調)

除標準 Westminster / Heidelberg / Belgic / Dort / 39 Articles / Augsburg / Concord，**還要包含**：

**衛理宗 (Methodist)**:
- John Wesley's 25 Articles of Religion (1784) — 改自 Anglican 39 Articles
- Methodist Articles of Religion (UMC current)
- The Book of Discipline of the UMC

**浸信宗 (Baptist)**:
- 1644 First London Baptist Confession
- **1689 Second London Baptist Confession** ★★★ (基本同 Westminster + 浸信修訂)
- New Hampshire Confession of Faith (1833)
- Baptist Faith and Message (BFM 1925 / 1963 / **2000** 修訂版) — Southern Baptist Convention
- Abstract of Principles (1858) — Southern Baptist Theological Seminary

**Anabaptist 重洗禮派**:
- Schleitheim Confession (1527)
- Dordrecht Confession (1632) — 門諾派

**Quaker 公誼會**:
- George Fox 信仰宣言

**東正教正面信條**:
- Confession of Dositheus (1672) — Synod of Jerusalem
- Confession of Mogila (1640)

### 近代普世合一對話文獻 (Ecumenical Dialogue, user 強調)

20-21 世紀各教會之間 signed agreements / joint declarations / dialogue documents — 是近代 ecumenism 的核心。應與信條同列因為大多是「共同信仰告白」性質。

**WCC (World Council of Churches) 系列**:
- **BEM / Lima 文件** (Baptism, Eucharist and Ministry, 1982) — Faith and Order Commission 經典 ★★★
- WCC Faith and Order Papers 各份

**羅馬天主教 + 信義宗（Lutheran）**:
- **Joint Declaration on the Doctrine of Justification** (JDDJ 1999, Augsburg) ★★★ 重大里程碑
  - 後續 Methodist (2006) / Reformed (2017) / Anglican 加簽
- The Hope of Eternal Life (Round XI, 2010)
- Lutherans and Catholics in Dialogue series

**羅馬天主教 + 東方正統 (Oriental Orthodox)**:
- **Common Christological Declaration** Paul VI - Shenouda III 1973 (Coptic) ★
- Paul VI - Vasken I 1970 (Armenian)
- John Paul II - Mar Dinkha IV 1994 (Assyrian) ★
- John Paul II - Ignatius Zakka I 1984 (Syriac Orthodox)
- 解決 1500 年的「迦克墩派 vs 反迦克墩」基督論爭議

**羅馬天主教 + 東正教 (Eastern Orthodox)**:
- **Ravenna Document** (2007) ★ 教宗 primacy 議題突破
- Joint Commission on Theological Dialogue 各份報告 (1980-present)
- 1965 Common Declaration of Paul VI and Athenagoras (取消 1054 互革除)

**羅馬天主教 + 聖公宗 (Anglican)**:
- **ARCIC I 報告**: Eucharist (1971), Ministry and Ordination (1973), Authority I-II (1976/81)
- **ARCIC II 報告**: Salvation and the Church (1986), Church as Communion (1991), Mary (2005)
- ARCIC III ongoing

**羅馬天主教 + 改革宗 (Reformed)**:
- WARC-RC dialogue documents
- "The Church and Justification" (1994)

**East-East 對話**:
- Aleppo Conference 1995 — Common Statement on Christology (Oriental + Eastern)
- Pro Oriente Vienna dialogues

**梵蒂岡 II 普世合一相關文件**:
- **Unitatis Redintegratio** (UR 1964) — 普世合一法令 ★
- **Orientalium Ecclesiarum** (OE 1964) — 東方教會法令
- **Ut Unum Sint** (UUS, John Paul II 1995) — 普世合一通諭 ★
- **Dominus Iesus** (DI 2000) — Ratzinger CDF declaration

**Historical 反向參考**:
- **Mortalium Animos** (Pius XI 1928) — 早期反普世合一，史料 context

### 文件結構（接續上面）

```
content/creeds/
  ...
  ecumenical/                          ← 新加章節
    bem-lima-1982.yml                  # WCC BEM 文件
    jddj-1999-justification.yml        # Lutheran-Catholic JDDJ ★
    jddj-2006-methodist-adhesion.yml
    jddj-2017-reformed-adhesion.yml
    paul-vi-shenouda-1973.yml          # Catholic-Coptic Christology
    paul-vi-vasken-1970.yml            # Catholic-Armenian
    jp2-mar-dinkha-1994.yml            # Catholic-Assyrian Christology
    jp2-zakka-1984.yml                 # Catholic-Syriac
    ravenna-document-2007.yml          # Catholic-Orthodox primacy
    common-declaration-1965.yml        # Paul VI - Athenagoras
    arcic-1-eucharist-1971.yml
    arcic-1-ministry-1973.yml
    arcic-1-authority-1976.yml
    arcic-2-salvation-1986.yml
    arcic-2-church-communion-1991.yml
    arcic-2-mary-2005.yml
    aleppo-1995-christology.yml
    unitatis-redintegratio-1964.yml    # Vatican II
    orientalium-ecclesiarum-1964.yml
    ut-unum-sint-1995.yml              # John Paul II
    dominus-iesus-2000.yml
    mortalium-animos-1928.yml          # 反向史料
```

### 各信條檔案結構

每個信條 = 一個 yml 檔（不需 DB）：

```yaml
# content/creeds/01-nicaea-325.yml
slug: nicaea-325
name_zh: 尼西亞信經（325 原版）
name_en: Original Nicene Creed
council_no: 1
year: 325
council_name_en: First Council of Nicaea
council_name_zh: 第一次尼西亞大公會議
accepted_by: [catholic, orthodox, oriental_orthodox, assyrian, protestant, methodist, baptist, anglican]
length_lines: 16

versions:
  - lang: grc
    name: 原文希臘（325 版）
    text: |
      Πιστεύομεν εἰς ἕνα Θεὸν, Πατέρα παντοκράτορα...
    source: Schaff《Creeds of Christendom》Vol 2 p.27

  - lang: lat
    name: 拉丁譯（含 filioque）
    text: |
      Credo in unum Deum, Patrem omnipotentem...qui ex Patre Filioque procedit...
    source: Roman Missal

  - lang: hye  # Armenian Apostolic
    name: 亞美尼亞使徒教會版（古典亞美尼亞文 grabar）
    text: |
      ...
    source: Armenian Church liturgy

  - lang: cop  # Coptic
    name: 科普特正教版
    text: |
      ...
    source: Coptic Orthodox liturgy

  - lang: syr-east
    name: 亞述東方教會版（東敘利亞傳統）
    text: |
      ...

  - lang: gez  # Ge'ez
    name: 衣索匹亞 Tewahedo 版
    text: |
      ...

  - lang: zh-Hant-Catholic
    name: 思高中譯
    text: |
      我信唯一的天主，全能的聖父...

  - lang: zh-Hant-Protestant
    name: 信義中譯
    text: |
      ...

  - lang: zh-Hant-Orthodox
    name: 東正教中華主教區譯本
    text: |
      ...

notes: |
  - 325 原版只到「我們相信聖靈」就結束，沒有展開
  - 381 君士坦丁堡修訂版加長聖靈段 + 末日信仰段
  - filioque 800 年加入西方版本，為 1054 大分裂導火線之一
  - 亞美尼亞版 reception 在 4-5 世紀，使用 grabar 古典亞美尼亞文

related:
  - creeds/02-constantinople-381.yml  # 修訂版
  - creeds/04-chalcedonian-451.yml    # 後續 christology
```

### 文件結構

```
content/creeds/
  00-apostles-creed.yml                  # 使徒信經（無大公會議 source）
  01-nicaea-325.yml                      # 第 1 次大公會議
  02-constantinople-381.yml              # 第 2 次
  03-ephesus-431.yml                     # 第 3 次
  04-chalcedonian-451.yml                # 第 4 次
  ...
  19-trent-1545.yml                      # 第 19 次
  20-vatican-i-1869.yml                  # 第 20 次
  21-vatican-ii-1962.yml                 # 第 21 次

  protestant/
    augsburg-1530.yml                    # 信義宗
    formula-of-concord-1577.yml          # 信義宗
    book-of-concord-1580.yml             # 信義宗合集
    helvetic-confession-1566.yml         # 改革宗瑞士
    belgic-confession-1561.yml           # 改革宗荷蘭
    heidelberg-catechism-1563.yml        # 改革宗
    canons-of-dort-1619.yml              # 改革宗
    westminster-confession-1648.yml      # 改革宗英美
    westminster-larger-catechism.yml
    westminster-shorter-catechism.yml
    39-articles-1571.yml                 # 聖公宗
    methodist-25-articles-1784.yml       # 衛理宗 ★
    methodist-articles-of-religion.yml   # 衛理宗 UMC ★
    1644-first-london-baptist.yml        # 浸信宗
    1689-second-london-baptist.yml       # 浸信宗 ★★
    new-hampshire-baptist-1833.yml       # 浸信宗
    bfm-2000-southern-baptist.yml        # 浸信宗 SBC ★
    schleitheim-1527.yml                 # 重洗禮派
    dordrecht-1632.yml                   # 門諾派

  orthodox/
    confession-of-mogila-1640.yml
    confession-of-dositheus-1672.yml
```

### 資料源 — 已有

- ✓ **Schaff《Creeds of Christendom》3 卷** — `世界宗教/基督教/教會法典與信條/`
  - Vol 1: History of the Creeds
  - Vol 2: **Greek and Latin Creeds** — 尼西亞 + 君士坦丁堡 + 迦克墩 + Trent + Vatican I ★主要源
  - Vol 3: **Evangelical Protestant Creeds** — Westminster + Heidelberg + Belgic + Dort + 39 Articles + Augsburg + Concord + Helvetic ★主要源
- ✓ **Schaff NPNF2 Vol 14** — "The Seven Ecumenical Councils" — 前 7 次大公會議文獻
- ✓ **Schaff History of the Christian Church 8 卷** — `世界宗教/基督教/教會法典與信條/` — 歷史 context

### 資料源 — 待補

| 內容 | 來源 | 公版 |
|---|---|---|
| Vatican II 16 份文件 | vatican.va/archive/hist_councils/ii_vatican_council | ✓ 公開 |
| Vatican I (Dei Filius, Pastor Aeternus) | vatican.va | ✓ |
| Trent 全 decrees | vatican.va + Schroeder 1941 英譯（z-library）| 部分公版 |
| 拉特朗會議 (Lateran I-V) decrees | papalencyclicals.net / dailycatholic.com | ✓ |
| 衛理宗 25 Articles | umc.org | ✓ |
| 1689 LBC | 1689londonbaptistconfession.com | ✓ 公版 |
| BFM 2000 | sbc.net/bfm2000 | ✓ |
| Schleitheim / Dordrecht 重洗禮派 | gameo.org / anabaptistwiki | ✓ 公版 |
| 亞美尼亞尼西亞版 grabar | armenianchurch.org / Armenian liturgy text | ✓ 公開 |
| 科普特尼西亞版 Bohairic | copticchurch.net / copticbible.org | ✓ |
| 亞述東方尼西亞版 (Syriac east) | assyrianchurch.org / Holy Apostolic | ✓ |
| 衣索匹亞 Ge'ez 尼西亞版 | ethiopianorthodox.org / Tewahedo liturgy | 稀少 |
| Mogila / Dositheus 東正教信條 | orthodoxchristian.info / archive.org | ✓ 公版 |

---

## 3. `/canon-law` — 教會法規查詢

### 範圍

- **天主教 CIC 1983** (Codex Iuris Canonici, 1752 canons) — 拉丁公教會法典
- **CCEO 1990** (Codex Canonum Ecclesiarum Orientalium, 1546 canons) — 與羅馬合一的東方教會法典
- **天主教教理 CCC** (Catechism of the Catholic Church, 2865 段)
- **東正教 Pedalion** (Rudder) — Nicodemus the Hagiorite 編
- **Apostolic Canons 85 條** — 已在 Schaff ANF Vol 8 ★ 已有
- **新教教會章程**：
  - Westminster Form of Government (1645)
  - Westminster Directory for Public Worship (1645)
  - 衛理宗 Book of Discipline (各年度)
  - 信義宗 Kirchenordnung (各國分支)
  - 浸信宗 Church Covenant 範本

### 文件結構

```
content/canon-law/
  catholic/
    cic-1983.yml          # 拉丁公教會法典 — 7 books, 1752 canons
    cceo-1990.yml         # 東方教會法典 — 30 titles, 1546 canons
    catechism-cc.yml      # CCC 2865 paragraphs

  orthodox/
    pedalion-cummings.yml         # 1957 英譯（archive.org PD）
    apostolic-canons.yml          # 85 條使徒教規（Schaff ANF Vol 8 已有）
    canons-of-quinisext-trullo.yml  # 692 五六會議 canons
    canons-of-trullo-syriac.yml   # 含敘利亞訂正版本

  protestant/
    westminster-form-of-government.yml
    westminster-directory-of-worship.yml
    methodist-discipline-2016.yml
    sb-bcp-1928.yml               # 聖公宗 Book of Common Prayer
```

### 資料源 — 已有

- ✓ **Schaff ANF Vol 8** — 含 Apostolic Constitutions + 85 Apostolic Canons
- ✓ **Schaff NPNF2 Vol 14** — 含 Quinisext / Trullo canons

### 資料源 — 待補

| 內容 | 來源 | 取得方式 |
|---|---|---|
| CIC 1983 | vatican.va/archive/cod-iuris-canonici/cic_index_en.html | HTML scrape |
| CCEO 1990 | vatican.va/archive/eng0824/__P00.HTM | HTML scrape |
| CCC | vatican.va/archive/ENG0015/_INDEX.HTM | HTML scrape |
| Pedalion (Cummings 1957) | archive.org/details/pedalion | PDF download |
| 衛理宗 Discipline 2016 | umc.org/en/content/book-of-discipline-2016 | PDF |
| 聖公宗 BCP 1928 | episcopalchurch.org / archive.org | PDF |
| 1689 LBC + 章程 | 1689londonbaptistconfession.com | PDF / HTML |

---

## 4. `/fathers` — 歷代教父著作搜索系統

### 範圍

- 完整 Schaff 38 卷 + 中譯個別教父原典 + 教父研究 monograph 整合
- 按教父名 / 時期 / 地理區 / 語言 / 主題 / 經文 cross-search
- 與 `/scripture` 雙向 link（"這位教父對 Matthew 5 的講道" / "Matthew 5:3 被哪些教父註釋過"）

### 教父覆蓋目標（~50 位）

**使徒教父 (Apostolic Fathers, 70-160)**:
Clement of Rome, Hermas, Ignatius of Antioch, Polycarp of Smyrna, Didache, Letter of Barnabas

**護教士 (Apologists, 120-220)**:
Justin Martyr, Tatian, Athenagoras, Theophilus of Antioch, Minucius Felix

**Alexandrian 學派 (190-450)**:
Clement of Alexandria, **Origen**, Athanasius, Cyril of Alexandria, Didymus the Blind

**Antiochene 學派**:
Theodore of Mopsuestia, **John Chrysostom**

**Cappadocian Fathers (370s-380s)**:
Basil the Great, Gregory of Nyssa, Gregory of Nazianzus

**拉丁教父 (Latin Fathers, 200-600)**:
**Tertullian**, Cyprian, **Ambrose**, **Jerome**, **Augustine**, Leo the Great, Gregory the Great

**敘利亞東方教父**:
Aphrahat, **Ephrem the Syrian**, Jacob of Sarug, Babai the Great, Isaac of Nineveh

**埃及隱修運動**:
Anthony the Great, Pachomius, Macarius the Great, Evagrius Ponticus

**晚期/中世紀過渡**:
Maximus the Confessor, John of Damascus, Pseudo-Dionysius the Areopagite, Symeon the New Theologian

### Schema

```sql
fathers (
  slug VARCHAR(50) PK              -- 'augustine' / 'origen' / 'chrysostom'
  name_zh, name_en
  name_lat                          -- Aurelius Augustinus
  name_grc                          -- Greek-language fathers
  name_syr                          -- Syriac-language
  birth_year, death_year
  region_primary                    -- 北非 / 敘利亞 / 埃及 / 小亞細亞 / 巴勒斯坦 / 西方
  language                          -- lat / grc / syr / cop / hye
  era                               -- 使徒教父 / 護教士 / 尼西亞前 / 尼西亞後 / 晚期教父
  doctor_of_church BOOLEAN          -- 天主教「教會聖師」status
  bio_zh TEXT
  related_topics TEXT[]             -- ['三一論', '基督論', '修道', '聖事', ...]
)

father_works (
  id UUID PK,
  father_slug FK,
  work_slug,
  title_zh, title_en, title_lat
  composition_year                  -- 寫作年（估計）
  ebook_ids UUID[]                  -- 該作品的 ebooks rows
  related_verses VARCHAR[]          -- ['gen.1.1', 'mat.5.3', ...]
)

CREATE INDEX fathers_era ON fathers (era);
CREATE INDEX fathers_region ON fathers (region_primary);
```

### 資料源 — 已有 (Drive 上)

- ✓ **Schaff 38 卷英文** — `神學/教父著作/Schaff - ANF (10 卷)/`, `Schaff - NPNF1 (14 卷)/`, `Schaff - NPNF2 (14 卷)/`
- ✓ **中譯個別教父** ~25 本 — `神學/(各處)`：
  - 屈梭多模《金口若望雕像講道詞選集》
  - 安波羅修《論基督教信仰》《論責任》
  - 亞他那修《論道成肉身》
  - 俄利根《駁瑟蘇斯》
  - 馬克西穆斯《天主的人化與人的神化》
  - 納西盎的格列高利《神學演講錄》
  - 大格里高利《牧靈指南》
  - 安瑟莫《著作選》
  - 德爾圖良《護教篇》
  - 游斯丁《護教篇》
  - 亞歷山大克勉《勸勉希臘人》
  - 宗徒時代教父叢書 4 輯（公會、聖克來孟、問存七牘、牧者）
  - 使徒教父著作集
- ✓ **教父研究 monograph** — 教父學大綱上下冊 / 教父：從聖克勉到聖奧斯定 等

### 教父基礎資料整理（待做）

每位教父需手動或 Gemini 補：
- 中英拉希各種寫法
- 生卒年
- 主要 region / language
- 主要作品 list
- 在 ebooks DB 中所有相關 row IDs（含教父原典 + 教父研究）
- 在 IVP ACCS 中被引用過的 verse refs

---

## 5. `/apocrypha` — 典外文獻搜索系統

### 範圍

- **OT 偽典 (Pseudepigrapha)**：1 Enoch, Jubilees, Testament of 12 Patriarchs, Assumption of Moses, 2 Baruch, 4 Ezra, Lives of the Prophets, ...
- **OT 次經 / 第二正典 (Apocrypha / Deuterocanon)**：Tobit, Judith, Wisdom of Solomon, Sirach (Ecclesiasticus), Baruch, 1-2 Maccabees, Esther additions, Daniel additions (Susanna, Bel and Dragon, Prayer of Azariah), 1 Esdras, 3 Macc, 4 Macc, Prayer of Manasseh, Psalm 151
- **NT 偽典 (NT Apocrypha)**：使徒行傳偽作、福音書 (Gospel of Peter / Mary / Thomas / Judas) / Apocalypse of Peter / Diatessaron / Acts of Paul and Thecla / Pseudo-Clement letters
- **死海古卷 (Dead Sea Scrolls, Qumran)**：Community Rule (1QS), War Scroll (1QM), Hodayot, Temple Scroll (11QT), Damascus Document (CD), pesher commentaries
- **諾斯底 / Nag Hammadi Library**：Gospel of Truth, Treatise on Resurrection, Apocryphon of John, Hypostasis of the Archons, Trimorphic Protennoia, Gospel of Philip, ...
- **教父引用的失傳福音書**：Gospel of Hebrews, Gospel of Egyptians (Egerton Papyrus, P. Oxy. 840)

### Schema

```sql
apocrypha_documents (
  slug VARCHAR(50) PK        -- '1-enoch' / 'gospel-thomas' / 'dss-1qs' / 'nh-apocryphon-of-john'
  title_zh, title_en, title_orig
  category                    -- 'ot_apocrypha' / 'ot_pseudepigrapha' / 'nt_apocrypha' / 'qumran' / 'nag_hammadi' / 'lost_gospel'
  testament                   -- 'old' / 'new' / 'mixed'
  language_orig               -- hebrew / aramaic / greek / coptic / syriac / ethiopic
  composition_period          -- '2c BCE' / '1c CE' / '2-3c CE' etc.
  composition_low_year, composition_high_year INT
  canon_status_jsonb          -- 各教會 canon 狀態（OT 偽典在哪些教會被接受 — Ethiopian 接受 1 Enoch 等）
  ebook_ids UUID[]            -- DB ebooks 中的中譯/英譯/原文
  source_url
)

apocrypha_excerpts (
  doc_slug FK,
  section_ref                 -- chapter:verse 結構
  language                    -- zh / en / grc / heb / cop / syr
  text TEXT
)

CREATE INDEX apocrypha_documents_category ON apocrypha_documents (category);
CREATE INDEX apocrypha_excerpts_fts ON apocrypha_excerpts USING GIN (to_tsvector('simple', text));
```

### 資料源 — 已有 (Drive 上)

- ✓ **基督教典外文獻 10 卷**（黃根春主編）— `世界宗教/基督教/基督教典外文獻 (10 冊)/`
  - OT 篇 6 卷含：1 Enoch / Jubilees / Testament of 12 Patriarchs / 2 Baruch / 4 Ezra / Lives of the Prophets / Sibylline Oracles 等
  - NT 篇 4 卷含：Gospel of Thomas / Acts of Paul / Apocalypse of Peter / Didache / Letters of Pseudo-Clement / Pseudo-Ignatius 等
- ✓ **Schaff ANF Vol 8** — 部分（Pseudo-Clement 信件、Apostolic Constitutions）

### 資料源 — 待補

| 內容 | 來源 | 取得方式 |
|---|---|---|
| Charlesworth《OT Pseudepigrapha》2 卷 1983-85 (英文標準) | z-library | 已知英文標準 |
| Hennecke-Schneemelcher《NT Apocrypha》2 卷 (英文標準) | z-library | |
| Nag Hammadi Library (Robinson 1977) | archive.org/details/the-nag-hammadi-library | ✓ 公開 |
| DSS Reader (Eisenman/Wise 1992 OR García Martínez 1994) | z-library | |
| Qumran Cave 1-11 scrolls (online publications) | scrolls.dssenglish.org / orion.mscc.huji.ac.il | ✓ 部分 |
| Sefaria Jewish Library | sefaria.org | ✓ open |

---

## 整體實作優先順序

| 階段 | 子頁面 | 工作量 | 為什麼這個順序 |
|---|---|---|---|
| **1** | `/creeds` | 小 (~3-5 天) | Schaff Creeds 3 卷已下載，主要源齊全；file-based 不需 schema 設計；快速可看到成果 |
| **2** | `/canon-law` | 小到中 (~3-5 天) | Apostolic Canons 已有；CIC/CCEO/CCC 需 vatican.va HTML scrape |
| **3** | `/fathers` | 中 (~7 天) | 教父基礎資料整理工夫；Schaff + 中譯 25 本資料齊；schema 直接 |
| **4** | `/apocrypha` | 中 (~7 天) | 基督教典外文獻 10 卷已有；Nag Hammadi + Charlesworth 補充 |
| **5** | `/scripture` | 大 (~14-21 天) | 最複雜（公版聖經 import + LLM 抽 IVP ACCS commentary mapping）；最有價值的明星功能 |

**MVP 建議**：1-2 階段先做完上線，再開 3-5。

---

## 主要 Tradeoff 待 user 確認

| 議題 | 選 A | 選 B |
|---|---|---|
| **版權保守** | 只放公版聖經 / 信條 → 法律乾淨 | 全收（含 2010/NIV 等），放 auth gate 後限私人用 |
| **教父註釋 mapping 精細度** | LLM 自動掃 IVP ACCS 100% → ~15K rows | 手動 curate 重點 1K rows，其餘 link to ebook reader |
| **大公會議 21 次** | 全 cover (含 Lateran I-V 等內部教廷) | 只 cover 7 + 21 + 改教 / Vatican I-II 6 個 highlight |
| **次經第二正典 widescope** | 全 8 教會 canon 對照（含 Ethiopian 81 卷）| 主要 4 教會（新教 / 天主教 / 東正教 / 衣索匹亞）|

---

## 入口卡片 mockup

```vue
<!-- pages/index.vue 加 -->
<NuxtLink to="/scripture-canon" class="card">
  <div class="icon">📜</div>
  <div>
    <h3>經典對照與註釋</h3>
    <p>聖經多版本 + 教父逐節註釋 + 21 次大公會議信條 + 教會法規 + 典外文獻</p>
    <ul>
      <li>📖 聖經對照</li>
      <li>⛪ 信條對照</li>
      <li>⚖️ 教會法規</li>
      <li>✝️ 教父著作搜索</li>
      <li>📜 典外文獻搜索</li>
    </ul>
  </div>
</NuxtLink>

<!-- pages/scripture-canon/index.vue -->
<!-- 五個子頁面導覽 -->
```

---

## See also

- [ebook-pipeline](../ebook-pipeline/SKILL.md) — 書籍 ingest pipeline；本 portal 大量依賴 ebooks table
- [biblical-tradition-layer](../biblical-tradition-layer/SKILL.md) — 聖經族譜的「教會傳統」視角圖層；與 `/scripture` `/creeds` 互補
- 已有相關資料在 Drive：
  - `神學/教父著作/` — Schaff 38 卷
  - `世界宗教/基督教/教會法典與信條/` — Schaff Creeds 3 + History 8
  - `世界宗教/基督教/IVP - 古代基督信仰聖經註釋叢書 (27 冊)/` — 教父經注
  - `世界宗教/基督教/基督教典外文獻 (10 冊)/` — 典外文獻
- 待補資料源在各子頁面內列
