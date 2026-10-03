# 交接：古近東大藏經（/near-east）——英譯已收齊，下一步切段對齊

2026-10-03。新 session 先讀本檔，再讀 skill `scripture-near-east`（體例、資料形狀、踩過的坑全在那裡）。

## 一、現在的狀態

| 項目 | 狀態 |
|---|---|
| 書目 | ✅ 9 藏 52 卷約 380 種（埃及／蘇美／阿卡德／赫梯與胡里特／烏加里特／迦南與亞蘭／阿拉伯／埃蘭與高地＋附錄） |
| 三欄正文 | ✅ 蘇美藏 69 條（ETCSL）、新亞述先知書 SAA 9 共 11 篇、亞述王子冥府夢 SAA 3 32（ORACC）——轉寫＋英譯，中譯欄空 |
| 其餘各藏 | ⏳ 只有書目，英譯書已到手（見二），**尚未切段對齊** |
| 中譯 | ❌ 全藏未動 |
| `intro` 簡介 | ❌ 全空 |
| 近東考古五百篇 | ✅ `/research-data/top-papers/near-east-archaeology`（策展 501＋OpenAlex 引用前 500） |

正文資料形狀與 manifest 機制見 skill §3。**書目頁的「已上架」與三欄色塊以 `data/near-east/sources/manifest.json` 為準，不要手改書目的 columns 欄。**

## 二、英譯書在哪裡

### A. 現代標準譯本（75 部，66 部到手）

- 獵表：`data/zlib-wanted/near-east-translations.jsonl`（source `near-east-translations`）
- 帳本：`scripts/state/zlib_ledger.jsonl`（`status: downloaded` 的那幾行有實際檔名）
- 檔案：先落 repo 的 `z-lib/` 收件夾，每日 16:00 `ingest_new_books.py` 分類搬進 Drive `電子圖書館\`。**要用之前先查它被分到哪一類**（`python -X utf8 scripts/holdings_inventory.py --find 書名關鍵字`），不要假設路徑。
- 到手的重點書（依藏）：
  - **埃及**：Lichtheim《古埃及文學》卷一、Faulkner《棺槨文》全卷、Allen《古埃及金字塔文》（WAW 2015）、Faulkner《亡靈書》、Quirke《出於白晝》、Hornung《冥界之書》《門之書》《阿姆杜阿特文本》（德）、Schweizer《太陽神穿越冥界》、Simpson 選集、Allen《中埃及文學》、Parkinson《辛奴亥》、J. L. Foster 頌詩集、M. Smith《穿越永恆》、Murnane 阿瑪納、Kitchen 拉美西斯二世銘文
  - **蘇美**：Black《古代蘇美文學》、Jacobsen《昔日的豎琴》、Cohen《正典哀歌》
  - **阿卡德**：Foster《繆斯之前》、Dalley、George《吉爾伽美什》（企鵝本＋校本卷一）、Lambert《巴比倫創世神話》《巴比倫智慧文學》、Lambert & Millard《阿特拉哈西斯》、Abusch《馬克盧》、Reiner《舒爾普》、Geller《烏都格》、Linssen《烏魯克與巴比倫祭儀》、Hunger《犁星》、Oppenheim《解夢書》、Freedman《城中兆書》、Leichty《異胎兆書》、Scurlock 醫學、Nissinen 先知、Roth 法律、Grayson 編年、Frahm 註釋、Livingstone 祕傳註釋、Dick《生於天、造於地》
  - **赫梯**：Hoffner《赫梯神話》、Singer《赫梯禱文》、Beckman《外交文獻》《生產儀式》《赫梯語吉爾伽美什》、Miller《王室訓令》、Hawkins 盧維銘文集卷一
  - **烏加里特**：Parker《烏加里特敘事詩》、Wyatt《烏加里特宗教文獻》、Pardee《儀式與祭祀》、Smith & Pitard《巴力史詩》卷二、Coogan & Smith《古迦南故事》
  - **迦南與亞蘭**：Gibson 銘文教本卷一、Ahituv《往昔的回聲》、Porten & Yardeni TAD、Moran《阿瑪納書信》
  - **附錄**：Verbrugghe《貝羅索斯與曼涅托》、Waddell《曼涅托》、Attridge《斐洛》、Griffiths《論伊西斯與奧西里斯》、Lightfoot《論敘利亞女神》、Ahbel-Rappe《達馬斯基烏斯》、Faris《偶像書》
  - **總集**：Pritchard ANET、Hallo《經文的脈絡》
- **缺 9 部**（所有管道都試過）：Walker & Dick《洗口儀式》、Koch《巴比倫肝兆》、Mouton《赫梯儀式》（法）、del Olmo Lete《迦南宗教》、Cooper《阿卡德之咒》、Gibson 卷二卷三、Assmann《埃及頌詩與禱文》、Lindenberger《阿希卡爾》。各卷已有替代來源，不擋工作；z-lib 每日排程會繼續試。

### B. 公有領域舊譯（可直接引用全文）

Drive `經典對照與註釋\古近東大藏經－公有領域英譯底本\`：古騰堡 9 部（txt＋epub）＋ archive.org 37 部及分卷（104 PDF／2 GB）。重點：Breasted《埃及古代記錄》五卷、Luckenbill《亞述與巴比倫古代記錄》兩卷、King《創世七泥板》（卷一是英譯）、Thompson《巴比倫的惡魔與惡靈》、Budge 亡靈書三卷／天堂與地獄三卷、Griffith 塞特納故事與倫敦—萊頓魔法紙草、Cowley《亞蘭文紙草》（象島、阿希卡爾）、Cooke 北閃族銘文、Cory《古代殘篇》、Gressmann（德）。
⚠ 夾裡有同書的不同掃描本（archive.org 一書多條目），用前挑最清楚的一份；ne_archive 那兩支是一次性腳本，不在 repo。

### C. 線上開放語料（可再擴）

- ETCSL（蘇美）：已全收。
- ORACC（CC BY-SA）：`scripts/near_east_oracc.py` 的 `ENTRIES` 加一行就能收新篇。可再收：RINAP 4（以撒哈頓巴比倫銘文）、SAA 3 其他宮廷詩、SAA 10 學者書信。🚨 ORACC json 包只有轉寫，英譯一定抓 html；HTTPS 憑證鏈不完整，腳本對該站關驗證。

## 三、下一步（建議順序）

1. **埃及藏切段對齊**（書最齊）。每篇照該書的段號（BD 章、CT 咒、PT 咒語、Lichtheim 的段落）切，`ref` 照抄原書編號，**不自編**。原文欄先空（TLA 轉寫另抓）、英譯欄填譯本、`source` 寫書名與頁碼。做完一篇寫 manifest。
   - 🚨 現代譯本在版權內但使用者明說私人網站不管版權（[[feedback_personal_research_ignore_copyright]]），照收。
   - 公有領域舊譯（Budge、Breasted）譯法過時，**只在現代譯本沒有時才用**，並在 reader 標註。
2. 阿卡德藏（Foster、Lambert、George、Abusch、Reiner）。
3. 赫梯、烏加里特（只有現代譯本，無轉寫來源時原文欄留空）。
4. 中譯：走站上引擎鏈（Gemini → NVIDIA → Haiku 救急），先過詞庫定名。

切段腳本建議仿 `scripts/near_east_etcsl.py` 的產出格式（`data/near-east/sources/text/<slug>.json`），每篇印「書中段數／入檔段數」分母。

## 四、不可違反的規矩

- **譯名**：已有通行譯法照通行（吉爾伽美什、涅伽爾、尼努爾塔、帕爾米拉…）；一般譯名不用聖經譯名（烏爾、埃蘭、蘇薩、杜牧茲）；赫梯；亞述爾（神）／亞述（國）；馬杜克、伊絲塔。全表見 `data/near-east/glossary-candidates.md`，已入 `/translation-glossary`。
- **段號照抄來源，不自編流水號**（測試釘住）。
- **Anna's Archive 的 Chrome 視窗不准關、不准停程序重開**——使用者點過驗證，10-03 我停掉重開一次被罵。它目前下載頁改版、下不到東西，但仍開著；要修 `annas_download.mjs` 先問使用者。
- commit 只加自己改的檔（多 session 共用 working tree）。push 常被同時在跑的 session 搶先（`cannot lock ref`），先 `git fetch` 看自己的 commit 是不是已被一起推上去。
- 推送有 pre-push 全套測試，要等幾分鐘。

## 五、相關檔案

`data/near-east/`（書目＋`sources/`）、`pages/near-east/`（索引／卷頁／`text/[slug]` reader／凡例）、`scripts/near_east_etcsl.py`、`scripts/near_east_oracc.py`、`test/near-east.spec.ts`（17 條）、skill `scripture-near-east`、`research-data-top-papers`、`ebook-zlib-harvest`（Anna's 改版與 LibGen 人工挑版本那兩段）。
