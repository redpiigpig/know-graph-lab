# 古希臘哲學全集接手紀錄

更新：2026-07-14（Asia/Taipei）

## 範圍

- 19 位作家 hub，完整目錄共 79 個作品條目。
- 主欄為逐段繁中譯文；來源欄依可得性為古希臘文、英文，盧克萊修另含拉丁文。
- 柏拉圖引用採 Stephanus；亞里斯多德採 Bekker；前蘇格拉底採 DK；普羅提諾採《九章集》集／篇／節。
- 公有領域古典原文優先。英譯若仍受版權，只作 auth-gated 私人研究庫參考欄，繁中仍由原文自譯。

## 2026-07-14 精確基準

網站目錄共 79 個作品條目；已完成並實際上架 10 個：

- 柏拉圖：〈蘇格拉底的申辯〉、〈歐緒弗洛〉、〈克里同〉、〈斐多〉、〈克拉底魯〉、〈泰阿泰德〉、〈智者〉、〈政治家〉、〈巴門尼德〉。
- 亞里斯多德：《詩學》。

`scripts/plato_build.py` 目前列出柏拉圖 20 部、亞里斯多德 6 部，共 26 部。以可對齊的 Stephanus／Bekker 小節計：

- 總量：7,973 節。
- 已完成或有可續傳快取：3,272 節（41.0%）。
- 完整上架：10/26 部。
- 全目錄作品數口徑：10/79（12.7%）。

開始本輪續傳時的三個斷點：

| 作品 | 快取 | 總節數 | 狀態 |
|---|---:|---:|---|
| 柏拉圖《理想國》 | 1,156 | 1,355 | 續傳中 |
| 亞里斯多德《修辭學》 | 117 | 133 | 續傳中 |
| 柏拉圖《斐利布斯》 | 46 | 282 | 續傳中 |

三部必須各自一個 worker；不可對同一 slug 重複啟動。每節寫入 `c:/tmp/plato_cache/<slug>_zh/*.txt`，中斷後重跑只補缺節。

## 現行柏拉圖／亞里斯多德管線

- 驅動：`scripts/plato_build.py`
- 全集 queue：`scripts/greek_overnight.py`
- 快取：`c:/tmp/plato_cache`
- 成品：`c:/tmp/plato_<slug>.jsonl`
- 來源：Perseus canonical-greekLit TEI；希臘／英文以共同 milestone 對齊。
- 測試：`scripts/tests/test_plato_build.py` 與多語 chunk 契約測試。

已知缺口：

1. `eudemian-ethics` 現行 Perseus 組合解析為 0 節，必須先修來源識別，不可空跑。
2. 亞里斯多德另外 16 個 planned 作品尚未加入 `plato_build.py` 的來源表。
3. 柏拉圖 hub 有一個早期短篇集 placeholder，未對應 ebookId。
4. 完成後要把 `stores/collectedWorks.ts` 對應作品 `status` 改為 `done`；僅有 ebookId 不等於完成。

## 其餘作家管線

尚未上架的目錄：前蘇格拉底與辯士／蘇格拉底／德謨克利特共 14 個 hub，另有伊比鳩魯、愛比克泰德、普羅提諾。

本輪分工：

- 伊比鳩魯：三封書信、《主要教義》、《梵蒂岡格言集》獨立可續傳管線。
- 愛比克泰德：《手冊》、《談話錄》四卷、殘篇獨立可續傳管線。
- 普羅提諾：《九章集》六集＋波菲利《普羅提諾生平》獨立可續傳管線。
- 前蘇格拉底：另建 DK A/B 編號資料管線；不得把後人見證誤標為作者親筆。

所有新管線共用 [greek_philosophy_glossary.md](greek_philosophy_glossary.md)，並遵守 `multilang_chunks.py` 的來源鏡像、段數對齊與 JSONL 契約。

## 收尾閘

每部完成須同時滿足：

1. 翻譯快取數等於來源節數；段落數 zh=grc=en（或該卷實際來源語言）。
2. 寫出完整 JSONL 並通過 `validate_multilang_chunk`。
3. R2、ebooks row、chunk_count、previews 更新成功。
4. reader 可顯示導讀卡、引用號、繁中／對照／來源欄。
5. hub status 改 `done`，並補 `data/collectedWorksIntros.ts` 導讀；最後才算完成。
