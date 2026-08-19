# 前蘇格拉底／辯士殘篇：來源與編號政策

## 可合法使用的底本

- 希臘文基線：Hermann Diels, *Die Fragmente der Vorsokratiker*, vol. 1 (1922)。採 Open Greek and Latin / First1KGreek 的 TEI 轉錄，轉錄檔明載 CC BY-SA 4.0。Diels 1922 與 1903 初版均已進入公有領域；實際機讀檔的編號以其標示的 1922 Diels 版為準。
- 英譯基線：John Burnet, *Early Greek Philosophy*, 3rd ed. (1920)，English Wikisource 公有領域轉錄；Arthur Fairbanks, *The First Philosophers of Greece* (1898)，Project Gutenberg 公有領域版，作為後續交叉核對來源。
- 赫拉克利特：Burnet 明言英譯按 Bywater 排列，故 `Bywater n` 與 `DK 22 Bn` 分欄保存，只能透過顯式 crosswalk 對齊。
- 巴門尼德：Burnet 明言按 Diels 排列；但 Burnet 有 `(4, 5)`、`(10, 11)` 等合併單元，registry 必須保存群組，不得把一段英譯硬複製成兩個獨立對譯。

## A／B 分型（不可互換）

| 類型 | 顯示名稱 | 性質 | 翻譯規則 |
|---|---|---|---|
| A | A類見證 | 後世作者對哲學家生平、學說的報告或轉述 | 保留見證作者與作品，以第三人稱翻；不得標成哲學家原話 |
| B | B類引文殘篇 | Diels 編者歸入殘篇的古代引文 | 仍不是作者手稿；只有引文邊界經 TEI 或人工 registry 確認後才可進翻譯 |

TEI 中一個 `B` 條目常同時含「引述者的上下文」與「被引文字」。parser 必須分存 `witness_context` 與 `quotation_text`。無法可靠切出引文時，狀態為 `unreviewed-witness-context`，不產生 reader chunk。

## 14 個 hub 的首輪盤點

| hub | DK | 狀態 |
|---|---:|---|
| thales | 11 | Diels 希臘文＋Burnet/Fairbanks 英譯候選待逐條 crosswalk |
| anaximander | 12 | 同上 |
| anaximenes | 13 | 同上 |
| pythagoras | 58 | 同上；需特別區分早期見證與後世偽託文獻 |
| xenophanes | 21 | 同上 |
| heraclitus | 22 | pilot-ready：Diels TEI＋Burnet/Bywater 英譯 |
| parmenides | 28 | pilot-ready：Diels TEI quote markup＋Burnet/Diels 英譯 |
| anaxagoras | 59 | Diels 希臘文＋Burnet/Fairbanks 英譯候選待逐條 crosswalk |
| zeno-elea | 29 | 同上 |
| empedocles | 31 | 同上 |
| protagoras | 80 | 希臘文可從 Diels 盤點；公有領域英譯仍需逐項權利核對 |
| gorgias | 82 | 同上；不得把柏拉圖《高爾吉亞》當作高爾吉亞本人殘篇 |
| socrates | — | 不屬 DK 前蘇格拉底編號；須另建 Plato/Xenophon/Aristophanes 來源語料架構 |
| democritus | 68 | Diels 希臘文＋Burnet/Fairbanks 英譯候選待逐條 crosswalk |

