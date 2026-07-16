
> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（`https://integrate.api.nvidia.com/v1`，`deepseek-ai/deepseek-v4-flash`，4 key 輪流＋間隔節流避 429）→ Haiku（最後救急）**。視覺／OCR 走 Gemini Vision／Haiku Vision。見 [[feedback_engine_nvidia_no_haiku]]。

# 內村鑑三全集 — 案例盡職調查（版權 / 書目 / 來源）

神學學科開區案例之一（與弟子矢內原忠雄一同開「神學」分區，2026-07-16）。**先讀本檔再開工。**

## 一句話結論

內村鑑三（Uchimura Kanzō, 1861–1930）是**日本無教會主義（無教会主義）的創始者**、近代日本最具影響力的基督教思想家。卒於 1930 → **全部著作全球公有領域**（含美國：全數 1930 年及以前出版；日本舊法卒後 50 年早已過期）。青空文庫有 11 篇公開全文（乾淨電子文本，零 OCR）、archive.org 有《內村鑑三全集》（岩波 1932–33）多倫多大學掃描與兩部英文原著初版——**穆勒級的乾淨案例**，無任何版權閃避。

**特殊點：兩部主著是英文原著**（《How I Became a Christian》《Representative Men of Japan》）→ 這兩部走 en＋繁中；其餘日文著作走 ja＋繁中。是本 portal 第一個「日文 → 繁中」對照案例。

## 版權表

| 項目 | 卒年/出版 | 地位 | 備註 |
|---|---|---|---|
| 內村本人全部著作（日文＋英文） | 卒 1930 | **全球公有領域** | 日本：舊法卒後 50 年（1980 年底過期）；歐盟 life+70（2000 年底過期）；美國：全數 1930 年及以前出版 → 過期 |
| 《内村鑑三全集》岩波 1932–33（20 卷） | 出版 1932–33 | 文本 PD；編輯本身無獨立創作 | archive.org 有 uoft 掃描多卷，公開可下載 |
| 《内村鑑三信仰著作全集》教文館（1962–）等戰後編輯本 | 出版 1960s | 文本 PD，但**校訂／注解可能有編者權** | 取源以明治—昭和初原版或青空文庫為準，避開戰後編輯本 |
| 既有第三方中譯（若有） | — | 不論版權，**一律不入庫** | 沿用本 skill 姿態；只當校對 transient 參考 |

## 語言策略（pipeline ① 多語對照，實際多為雙語）

- 日文著作：**ja＋繁中**兩欄（無平行他語版本；reader `source_order=["ja"]`）。
- 英文原著兩部：**en＋繁中**兩欄。《余は如何にして基督信徒となりし乎》的日譯出自門人（非作者自譯），不當第二來源欄；若日後要做 en＋ja＋繁中三欄，需另行對齊、非必要。
- 日文舊字舊假名 → 翻譯時直接餵原文即可（青空文庫多數已是新字新假名整理本，更省事）。
- 譯名先查 [[translation-glossary]]；「內村鑑三」「矢內原忠雄」漢字名直接沿用（繁體寫「內」）。聖經人名地名依 `/translation-glossary` 聖經人物表。

## 書目（stores/collectedWorks.ts 已收 10 部，status 全 planned）

| 分類 | 著作 | 年 | 語 | 來源速記 |
|---|---|---|---|---|
| 信仰三部作 | 基督信徒のなぐさめ | 1893 | ja | 青空文庫公開 ✅ |
| | 求安録 | 1893 | ja | 青空文庫作業中；NDL 原版 |
| | 余は如何にして基督信徒となりし乎（How I Became a Christian） | 1895 | **en** | archive.org 1895/1922 版 ✅ |
| 英文著作 | Representative Men of Japan（代表的日本人） | 1894/1908 | **en** | archive.org 1908 版 ✅ |
| 講演與信仰文集 | 後世への最大遺物 | 1897（1894 講演） | ja | 青空文庫公開 ✅ |
| | デンマルク国の話 | 1911 | ja | 青空文庫公開 ✅ |
| | 一日一生 | 1926 | ja | 青空文庫作業中 |
| 聖書研究 | 聖書之研究（誌，全 357 號） | 1900–1930 | ja | 全集掃描（archive.org） |
| | ロマ書の研究 | 1924（1921–22 講演） | ja | 向山堂原版（NDL）／全集 |
| | ヨブ記講演 | 1925（1920 講演） | ja | 青空文庫公開 ✅ |

年份查證來源：日文 Wikipedia＋青空文庫圖書卡（ヨブ記講演＝1920 講演‧向山堂 1925 刊，card56908 已查）＋CiNii。

## 來源盤點（2026-07-16 逐一驗證）

| 來源 | 內容 | 驗證 | 備註 |
|---|---|---|---|
| 青空文庫 [person34](https://www.aozora.gr.jp/index_pages/person34.html) | **公開 11 篇**：寡婦の除夜／寒中の木の芽／基督信徒のなぐさめ／後世への最大遺物／時事雑評二三／聖書の読方／楽しき生涯／デンマルク国の話／ネルソン伝に序す／問答二三／ヨブ記講演。**作業中 2 篇**：一日一生／求安録 | ✅ curl 200 | **首選來源**：乾淨電子文本（新字新假名）、零 OCR、可直抽 XHTML |
| archive.org `japaneseconvert00uchiuoft` | The Diary of a Japanese Convert（Revell 1895 初版） | ✅ metadata open、無 access-restricted | 英文原著甲本 |
| archive.org `howibecamechrist00uchi` | How I Became a Christian（1922 東京版） | ✅ 同上 | 英文原著乙本（改題後） |
| archive.org `representativeme00uchirich` | Representative Men of Japan（1908） | ✅ 同上 | 英文原著 |
| archive.org `uchimurakanzzens01uchiuoft` 等 | 《内村鑑三全集》岩波 1932–33 多卷（至少 vols 1, 6, 8, 12, 14–18 有掃描） | ✅ vol 1 metadata open | 日文著作備援源＋《聖書之研究》精華；掃描需 OCR |
| NDL 數位典藏 | 明治—昭和原版多數已數位化（例：後世への最大遺物・デンマルク国の話 pid 1157900） | ⚠️ pid 1157900 IIIF **404** → 可能送信限定 | 有青空文庫的篇目不需 NDL；需要時逐 pid 確認公開區分 |
| Project Gutenberg | — | ✅ 查無（"uchimura" 0 筆） | 英文著作走 archive.org |

## pipeline 判定

- **日文著作**（青空文庫有全文者優先）：青空文庫 XHTML 直抽 → 分章 → **ja＋繁中**逐段對照（`sources={ja:…}`，`source_order=["ja"]`）。零 OCR。
- **英文原著兩部**：archive.org djvu 文字層直抽（同穆勒流程）→ **en＋繁中**。
- **《聖書之研究》誌／《羅馬書之研究》**：只有掃描 → Gemini OCR（[[ebook-pipeline]]）→ ja＋繁中。工程大、後排。
- 起手卷建議：**《後世への最大遺物》**（青空文庫全文、篇幅小、最著名的講演）smoke test 日→繁中管線；次選《基督信徒のなぐさめ》（處女作＋「無教會」一詞初出）。英文線起手 **Representative Men of Japan**（台日讀者熟、章節獨立五人傳好切）。

## 🚀 新 session 接手清單

1. 讀本檔＋[SKILL.md](SKILL.md) §B1–B4。
2. 建 `uchimura_glossary.md`（無教會主義／不敬事件／再臨運動／聖書之研究／兩個 J…；聖經書卷名依思高/和合慣例查 [[translation-glossary]]）。
3. 起手卷《後世への最大遺物》：青空文庫 XHTML → 切段 → `--limit 2` smoke → 全卷 → 多語 JSONL（content=繁中、sources.ja）→ R2＋DB → reader 驗證。
4. hub works `status→done`＋填 `ebookId`（deterministic 命名空間建議 `d0000000-…`）。
5. 商 user：《聖書之研究》357 號全誌是否入 corpus（工程大）或只收全集精華卷。
