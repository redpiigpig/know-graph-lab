# 印順導師全集案例（collected-works 第一個「單一語言」案例）

> collected-works 系列至此都是外文→繁中多欄（榮格/穆勒/潘尼卡）。**印順全集本就是繁體中文** →
> 零翻譯、零跨語對齊，pipeline 砍剩「解析 CBETA TEI → JSONL → DB/R2 → 作家 hub」。
> reader 退化單欄（無 `sources`，[[multilang-sources]] 向後相容天然支援）。
> 這套方法同樣適用接下來的 **聖嚴法師（法鼓全集）** 與 **星雲大師全集**。

## 版權姿態
印順導師 1906–2005，2005 圓寂 → 非公有領域（台灣歿後 50 年至 2055）。可用，雙重合規：
1. 本站 auth-gate 私人研究圖書館，非 PD 可用（[[feedback_jung_nonpd_english_first]]）。
2. **來源 = CBETA**，CBETA 授權允許**非商業再散布**（比基金會官網爬蟲更乾淨且合法）。

## 來源定案：CBETA Y 系列 TEI P5 XML
- GitHub：`cbeta-org/xml-p5`，路徑 `Y/Y{NN}/Y{NN}n{NNNN}.xml`，**44 個 XML = 全集 42 部**
  （雜阿含經論會編上/中/下 = Y30n0030 / Y31n0030 / Y32n0030 三檔同 n 號）。
- raw：`https://raw.githubusercontent.com/cbeta-org/xml-p5/master/Y/Y08/Y08n0008.xml`
- ❌ 基金會官網 `yinshun-edu.org.tw` 已改版：book-level 代碼（y06/y08）302→404，books 頁是分頁 tab、章節連結不直出 → **不用**。
- 年譜權威源（hub timeline/contribution）：`https://www.yinshun.org.tw/yinshun/chronicle.html`（已下載 c:/tmp/ys_chron.html，1906–2005 逐年事件）。

## TEI 結構（已用 Y08《佛法概論》實證 2026-06-13）
- `<cb:mulu level="1|2|3">` → **三層章節樹**（章→節→目）。Y08：168 mulu / 170 head / 248 p。
- `<head>` = 標題文字（自序／緒言／第一章…／第一節…／子目）。
- `<lb n="a001a01" ed="Y"/>` = 印順著作集**邊碼**（引用格式 `Y08_p0001a01`）→ 保留成段碼錨點，符合 [[feedback_pdf_page_number]]。`type="old"` 的重複 lb 要丟。
- `<milestone unit="juan"/>` = 卷分界（Y08 有 20 juan）。
- `<note>` = 夾注/校注 → 解析時剝除。
- 驗證腳本：`c:/tmp/ys_validate.py`（待正式化為 `scripts/yinshun_build.py`，test-first 仿 panikkar_build）。

## 書目 → volume / parent_volume 樹（妙雲集24冊＋華雨集5冊＋專書11冊＋編纂選輯）
| parent_volume（分組） | 卷 | 書名（代碼） |
|---|---|---|
| 妙雲集‧上篇 | Y01–Y07 | 般若經講記/寶積經講記/勝鬘經講記/藥師經講記/中觀論頌講記/攝大乘論講記/大乘起信論講記 |
| 妙雲集‧中篇 | Y08–Y13 | 佛法概論/中觀今論/唯識學探源/性空學探源/成佛之道/太虛大師年譜 |
| 妙雲集‧下篇 | Y14–Y24 | 佛在人間/學佛三要/以佛法研究佛法/淨土與禪/青年的佛教/我之宗教觀/無諍之辯/教制教典與教學/佛教史地考論/華雨香雲/佛法是救世之光 |
| 華雨集 | Y25–Y29 | 華雨集一～五冊 |
| 專書 | Y30–Y44 | 雜阿含經論會編上中下/印度之佛教/印度佛教思想史/原始佛教聖典之集成/說一切有部為主的論書與論師之研究/初期大乘佛教之起源與開展/空之探究/如來藏之研究/中國禪宗史/永光集/大乘廣五蘊論講記/平凡的一生 |

（注：CBETA Y 編號與基金會 Y00xx 書號順序略有出入，正式化時以 XML 內 `<title level="m">` 為準逐卷對照。）

## 全量執行清單（✅ 完成 2026-06-13）
1. [x] `scripts/yinshun_build.py`：TEI→章節樹→單語 JSONL（`content`=正文；`chapter_path`/`volume`/`parent_volume`；無 `sources`；lb 邊碼/note 剝除；`_clean` 殺折行保 U+3000）。pure helpers + `scripts/tests/test_yinshun_build.py`（8 例綠）。
2. [x] REGISTRY：`yinshun_registry.json`，44 卷（CBETA 書名 + parent_volume + `ebook_id` = `a0000000-0000-4000-8000-0000000000NN`）。
3. [x] Y08《佛法概論》pilot：107 節 chunk → R2 + DB → reader 單欄截圖實證（章節樹側欄/正文/上下段）。
4. [x] 批 44 卷：`--all --upload`，**44/44 入庫、5324 chunks、0 R2 fail、0 error**。
5. [x] `stores/collectedWorks.ts` 加印順 `CwAuthor`（slug `yinshun`，amber，☸️；contribution 3 段＋timeline 13 條＋44 書目按妙雲集上/中/下篇‧華雨集‧專書分組）。
6. [x] portal/hub 截圖驗證（hub「44/44 卷已轉錄」、emoji 佔位降級）→ commit/push。

### 雷區/note
- ebooks.id 是 **UUID 型**，REST 不能 `like`，查全集用 `id=in.(...)`。
- `EBOOK_CHUNKS_DIR` 在 .env 是空字串 → 用 `te.CHUNKS_DIR`（已 fallback G: 雲端）。
- 印順**無公有領域肖像** → `portraitUrl:''`，portal/hub 已加 emoji 佔位降級（`v-else` 區塊）。
- 跑 `--all --upload` **務必在 repo 根目錄**（背景指令會繼承殘留 cwd 而失敗）。
- 截圖 reader 全頁高達 ~3800px > 2000px 硬限 → 讀前必裁（PIL crop top ≤1850）。

## 接續案例
- 聖嚴法師 → 法鼓全集 2020 紀念版（`ddc.shengyen.org`，doc id `輯-冊-篇`，HTML 可枚舉；2009 圓寂非 PD，私站可用）。
- 星雲大師 → 星雲大師全集（`books.masterhsingyun.org`，365 冊、偏 app 化，需先驗純 HTML vs API；2023 圓寂）。
