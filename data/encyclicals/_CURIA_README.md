# Curia 部會文件資料層 (tier='curia')

## 目的
本資料區用於存放教廷部會（dicastery）頒布的文件 — 訓令 / 宣言 / 法令 / 通告 等。
與「教宗訓導」(tier='teaching') 區別在於：
- **頒布者**：dicastery（信理部／禮儀部／聖赦院／教育部 等），而非教宗個人
- **schema**：`PapalDocument.issuer` 欄填部會名（中文），`popeSlug` 仍可填當時教宗用於關聯展示

## 規劃中的資料來源
- archive.hsscol.org.hk 467 項中含部會文件（**標題不明確標示為「部會」**—— 需內容層掃描識別，見下）
- vatican.va `/roman_curia/` 子站

## Status (2026-05-28 第二批)

### 已完成
- ✅ **hsscol 全 467 P# 索引完成**（`data/encyclicals/_hsscol_index.json`）
- ✅ **hsscol tier 分類報告**（`data/encyclicals/_hsscol_mapping.md` / `.json`）
  - teaching (B 區)：43 篇含 marquee（10 對位現有 slug；33 為新 B-tier 待 ingest）
  - curia (C 區)：**0 自動偵測** —— hsscol 標題未標示「信理部」「禮儀部」等部會名（見下方說明）
  - message (D 區)：166 篇（廣播詞 / 講詞 / 致函 / 文告 等）
  - unknown：170 篇（標題不含分類關鍵字，多為主題化命名 e.g.「我們要熱愛一切人」）
- ✅ **A 區段對齊審計**（`data/encyclicals/_a_zone_alignment.md`）—— 206 篇審計，14 篇段號不齊（5 篇影響 UI）

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
