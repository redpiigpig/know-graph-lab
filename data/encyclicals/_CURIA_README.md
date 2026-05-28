# Curia 部會文件資料層 (tier='curia')

## 目的
本資料區用於存放教廷部會（dicastery）頒布的文件 — 訓令 / 宣言 / 法令 / 通告 等。
與「教宗訓導」(tier='teaching') 區別在於：
- **頒布者**：dicastery（信理部／禮儀部／聖赦院／教育部 等），而非教宗個人
- **schema**：`PapalDocument.issuer` 欄填部會名（中文），`popeSlug` 仍可填當時教宗用於關聯展示

## 規劃中的資料來源
- archive.hsscol.org.hk 619 項中含 ~130 項部會文件
- vatican.va `/roman_curia/` 子站

## Status
- 框架已備（types.ts 加 tier='curia' + issuer 欄；UI pope page 加「部會文件」tab）
- 內容尚未 ingest（下輪 batch session 處理）

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
