
> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（`https://integrate.api.nvidia.com/v1`，`deepseek-ai/deepseek-v4-flash-0731`，4 key 輪流＋間隔節流避 429）→ Haiku（最後救急）**。視覺／OCR 走 Gemini Vision／Haiku Vision。見 [[feedback_engine_nvidia_no_haiku]]。

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

## ✅ 第一波：青空文庫 11 篇（2026-07-17 啟動，2026-09-06 確認全譯完成 866 段）

**Pipeline 已建成（test-first）**：
- 解析器 `scripts/uchimura_build.py`（+ `scripts/tests/test_uchimura_build.py` 18 例綠）：青空 XHTML cp932/utf-8 解碼、ruby 注音剝除（保 rb）、`span.notes`［＃…］注記剝除、gaiji img（`U+XXXX` alt→真字元、`※(…)`→※）、`*midashi*` 標題→分節、一行=一段、行首全形空白剝除、底本區塊排除、長段落句界切分（≤1500 字）。
- Worker `scripts/uchimura_auto.py`（仿 panikkar_auto）：per-段 checkpoint（`uchimura_data/<slug>/secN.json`）可續傳、Gemini→NVIDIA→Haiku 鏈、≤10 段/chunk、cover+`build_section_chunk`（`sources={ja}`、`source_order=["ja"]`）→ JSONL+R2+DB previews。**跑法：repo 根目錄 `python scripts/uchimura_auto.py --run-queue`，長跑一律 PowerShell `Start-Process` 分離式，log `scripts/logs/uchimura_translate.log`**。
- 詞庫 [uchimura_glossary.md](uchimura_glossary.md)（28 詞鎖定，PROMPT 內嵌；神→神 沿 hub 慣例）。
- 快取 `c:/tmp/uchimura_cache/`（11 篇 XHTML＋卡片頁，節流抓於 2026-07-16，別清）。

**Registry（[uchimura_registry.json](uchimura_registry.json)，命名空間 `d0000000-…`）— 11 篇 → 6 個 ebook rows**：

| slug | ebook_id 尾碼 | 卷 | 篇 |
|---|---|---|---|
| consolations | …0001 | 基督信徒的安慰 | 55507（11 節 293 段） |
| greatest-legacy | …0002 | 給後世的最大遺物 | 519（6 節 56 段） |
| denmark-story | …0003 | 丹麥國的故事 | 233（1 節 40 段） |
| how-to-read-bible | …0004 | 聖經的讀法 | 1218（1 節 39 段） |
| job-lectures | …0005 | 約伯記講演 | 56908（41 節 346 段） |
| short-pieces | …0006 | 雜文短篇集 | 六短篇合卷：1216/1215/1212/1214/1217/1213（6 節 92 段） |

store `works[]` 六卷已填 `ebookId`＋`status: in-progress`（翻完逐卷改 done）。NVIDIA 輸出偶發 U+FFFD 雜訊字元已在 `_clean` 過濾。

## ✅ 第二波：兩部英文原著（2026-09-06 啟動）

內村三大名著裡有兩部是**他自己用英文寫的**，所以這一波是 en＋繁中，不是 ja＋繁中。
取源 archive.org djvu 文字層（兩本 metadata 皆 open、無 access-restricted）。

| slug | ebook_id 尾碼 | 卷 | 來源 | 段數 |
|---|---|---|---|---|
| representative-men | …0007 | 代表的日本人 | `representativeme00uchirich`（警醒社 1908 增訂版） | 6 節 322 段 |
| how-i-became | …0008 | 我如何成為基督徒 | `howibecamechrist00uchi`（警醒社 1922 東京版） | 12 節 496 段 |

**《我如何成為基督徒》為什麼取 1922 而不是 1895 初版**：1895 Revell 本
（`japaneseconvert00uchiuoft`）題名是《The Diary of a Japanese Convert》，
1922 東京版才是作者親自改題的定本，與 store 的卷名一致；且 1895 那份掃描的斷字
連字號整個被 OCR 吃掉（"Ameri can"、"As sociation"），無從程式化復原，1922 那份
連字號完整（"in- vited"）反而好接。

**Pipeline**：`scripts/uchimura_en_build.py`（+ `scripts/tests/test_uchimura_en_build.py`
13 例綠），reflow 直接沿用 `mueller_build.reflow`（同樣是 archive.org djvu 形狀）。
translate/build/upload 走既有的 `uchimura_auto.py --author uchimura-en`
（該檔加了三處通用化：`SOURCE_LANG` 決定原文欄語言、section 可自帶 `title_zh`、
AUTHOR_MODULES 多一筆）。

**這批 OCR 的三個坑**：
1. **書眉抓法不要拼字面**。「38 REPRESENTATIVE」「MEN OF JAPAN. 39」被 OCR 成
   十幾種樣子（KEPKESENTATIVE／BEPEESENTATIVB／MEN OF PA JAN／MEN OB' JAPAN／
   MEN OF JA<PAN），寫 regex 去追是白費工。改抓它們**唯一共同的特徵：整行沒有
   小寫字母**——`HEAD_RE = ^[^a-z]*$`。正文行幾乎必有小寫，章名行本來就要丟。
2. **章名行不一定是大寫**。第一章的 `heathenism.` 被 OCR 成小寫，逃過書眉過濾會
   變成一個段落，所以那一節的 start 要跳過它（211 而非 207）。同理
   CHAPTER SECOND／SEVENTH 兩個 heading 整行被 OCR 吃掉，靠章名行（
   `INTRODUCTION TO CHRISTIANITY.`）定位。
3. **章首花體大寫字全毀**：`\X7HEN`＝WHEN、`DELIGION`＝RELIGION、`fS`＝IS、
   `6 6 A GRICULTURE`＝AGRICULTURE、`ifi\X7HAT`＝WHAT。這類 prompt 講清楚就好，
   模型從上下文推得回來；唯獨**作者自己的署名** `IvAN.25 UCHIMURA`＝KANZO
   UCHIMURA 推不回來（會譯成「伊凡‧二五」），走 `OCR_FIXES` 硬改。
   1922 本另有開引號被讀成小寫 u 的通病（`uO just tell us how.”`），
   `fix_ocr_quotes` 只在 u 後接大寫時才改，才不會誤傷 unusual／U. 這種。

跑法（引擎依使用者指定用 Haiku；免費層 Gemini 額度撐不住這種量）：

    python scripts/uchimura_auto.py --author uchimura-en --list
    python scripts/uchimura_auto.py --author uchimura-en --run-queue --backend haiku

## 🚀 新 session 接手清單

1. 看 worker 進度：`python scripts/uchimura_auto.py --list`（或 tail `scripts/logs/uchimura_translate.log`）；斷了就重新分離式啟動 `--run-queue`（checkpoint 自動續傳）。
2. 每卷翻完（`--list` done=True 且已 upload）→ store `status→done`；reader `/collected-works/uchimura/<ebookId>` 截圖驗證。
3. 第二波跑完（`--author uchimura-en --list` done=True）→ store 兩卷 `status→done`；
   reader `/collected-works/uchimura/<ebookId>` 截圖驗證。
4. 青空「作業中」二篇：**2026-09-06 再查仍是作業中**（一日一生 60832／求安録 60471），
   青空那邊沒動靜。要提前收就只能走 NDL 掃描 OCR，別再空等青空。
5. 剩下的兩部只有掃描本，工程量級不同，動工前先跟 user 確認：
   《羅馬書之研究》（向山堂 1924，NDL）與《聖書之研究》357 號全誌
   （岩波全集精華卷 archive.org 有掃描）——後者是否入 corpus 或只收精華卷。
